import _thread
import select
import socket
import time
from collections import deque

from simple_log import log

EOT = '\x04'

# 检测端口是否使用


def check_port_in_use(port, host='127.0.0.1') -> bool:
    s = None
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((host, int(port)))
        print(port, ' has been used')
        return True
    except OSError:
        print(port, ' don\'t use')
        return False
    finally:
        if s:
            s.close()


class SocketServer(object):

    def __init__(self, ip, port, parse_def, need_send: bool = True, on_client_connect=None, on_client_disconnect=None, recive_size=1024) -> None:
        """
                        Socket服务端
                        初始状态占用两个线程，一个用来接待客户端，另一个用来发送数据（排队），如果 need_send 为 False, 则只有一个线程。
                        每增加一个客户端，则增加一个线程。

                        Args:
                                                        ip: 服务ip
                                                        port: 服务端口
                                                        parse_def: (socket, data) 解析接受到的客户端数据
                                                        need_send: 是否需要发送数据功能（需要新开线程）
                                                        on_client_connect: (socket, addrstr) 客户端连接事件
                                                        on_client_disconnect: (socket, addrstr) 客户端断开连接事件
        """
        self.ip = ip
        self.port = port
        self.parse_def = parse_def
        self.client_max = 3
        self.client_list = []
        self.is_run = False
        self.server_socket: socket.socket = None
        self._send_queue = deque((), 20)
        self.need_send = need_send
        self.on_client_connect = on_client_connect
        self.on_client_disconnect = on_client_disconnect
        self.recive_size = recive_size

    def sendloop(self):
        print('发送线程启动')
        while self.is_run:
            while self._send_queue:
                client, msg = self._send_queue.popleft()
                try:
                    client.send(msg)
                except OSError:
                    print('send msg failed!')
            time.sleep(0.1)
        print('发送线程结束')

    def start(self):
        """启动服务
        """
        if not self.is_run:
            _thread.start_new_thread(self.do_create_server, (socket.socket(),))            
            if self.need_send:
                _thread.start_new_thread(self.sendloop, ())

            print(self, 'start server win!')
        else:
            print(self, 'start server lose!')

    def stop(self):
        """停止服务
        """
        print(self, 'stop server ... start!')
        if self.client_list:
            for item in self.client_list:
                print(item)
                try:
                    item[0].close()
                    print(item[1], 'client close win!')
                except OSError:
                    print(item[1], 'client close lose!')
        else:
            print('client list is null')
        if self.server_socket:
            try:
                self.server_socket.close()
                print(self.server_socket, 'server close win!')
            except OSError:
                print(self.server_socket, 'server close lose!')
        self.is_run = False
        print(self, 'stop server ... end!')

    def do_create_server(self, s: socket.socket):
        self.is_run = True
        if not check_port_in_use(self.port):
            print('server ip:', self.ip, ' port:', self.port)
            self.server_socket = s
            self.server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(0)
            self.server_socket.settimeout(1.0)
            while self.is_run:
                try:
                    conn, address = self.server_socket.accept()
                    for c, a in self.client_list:
                        if address[0] == a[0]:
                            print('client already exist! try remove it!')
                            self.client_list.remove((c, a))
                except OSError:
                    continue
                if len(self.client_list) < self.client_max:
                    _thread.start_new_thread(self.do_client_read, (conn, address))
                    print('client list add ', address)
                else:
                    print('client size > ', self.client_max)
                    try:
                        conn.close()
                    except OSError:
                        pass
        self.is_run = False

    def do_client_read(self, conn: socket.socket, address):
        self.client_list.append((conn, address))
        print('client list size = ', len(self.client_list))
        print('start read ', address)
        if self.on_client_connect:
            self.on_client_connect(conn, address)
        while self.is_run and self.client_list.index((conn, address)) >= 0:
            try:
                r, _, _ = select.select([conn], [], [])
                do_read = bool(r)
            except socket.error:
                pass
            if do_read:
                try:
                    data = conn.recv(self.recive_size)
                    if len(data) == 0:
                        log('client close by data len == 0')
                        break
                    # data = str(data, 'utf-8')
                    # print(address, 'read data str = ', data)
                    if self.parse_def(conn, data) != True:
                        log('client close by parse data error')
                        break
                except Exception as e:
                    print(e)
                    # 记录异常
                    log(f'client close by error: {e}')
                    break
            time.sleep(0.1)

        self.client_list.remove((conn, address))
        print('client close from:', address)
        conn.close()
        if self.on_client_disconnect:
            self.on_client_disconnect(conn, address)

    def send(self, client: socket.socket, msg: str):
        self._send_queue.append((client, msg + EOT))

    def send_raw(self, client: socket.socket, msg: bytes):
        self._send_queue.append((client, msg))

    def send_all(self, msg: str):
        for client, address in self.client_list:
            self.send(client, msg)


if __name__ == '__main__':
    server = SocketServer('0.0.0.0', 8123, lambda client, msg: print('ok'))
    server.start()
    time.sleep(1000)
    server.stop()
