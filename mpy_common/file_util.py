def file_exists(path: str) -> bool:
    import os
    """
    判断文件是否存在
    Args:
        path: 文件路径
    Returns:
        bool
    """
    try:
        os.stat(path)
        return True
    except OSError:
        return False

def read_file_by_chunk(file_path, chunk_size=512):
    """
    for chunk in read_file_by_chunk('log.txt'):
        print(chunk, end='')
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk