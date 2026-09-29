"""pathcanon 的字节层工具：拆分路径、判断绝对性。"""


def is_absolute(path):
    """判断路径是否以分隔符开头（``str`` 或 ``bytes``）。"""
    if isinstance(path, bytes):
        return path.startswith(b"/")
    return path.startswith("/")


def to_text(path):
    """把路径统一成 ``str``，便于后续按字符处理。"""
    if isinstance(path, bytes):
        return path.decode("utf-8")
    return path


def split_segments(path):
    """返回 ``(is_abs, segments, trailing)``。

    ``path`` 可以是 ``str`` 或 ``bytes``；``segments`` 是不含分隔符的段列表，
    ``trailing`` 表示输入是否以 ``/`` 结尾。
    """
    text = to_text(path)
    is_abs = text.startswith("/")
    trailing = text.endswith("/")
    body = text.strip("/")
    segments = [seg for seg in body.split("/") if seg != ""]
    return is_abs, segments, trailing