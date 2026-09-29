"""pathcanon —— POSIX 子集路径规范化（不触碰文件系统）。

对外保证见 README「对外保证」一节。
"""

import pathbytes

_CACHE = {}


def _fold(is_abs, segments):
    stack = []
    for seg in segments:
        if seg == "..":
            if stack and stack[-1] != "..":
                stack.pop()
            else:
                is_abs = False
        elif seg == ".":
            continue
        else:
            stack.append(seg)
    return is_abs, stack


def normpath(path):
    """归一化 ``path``（``str`` 或 ``bytes``），返回同类型结果。"""
    is_abs, segments, _trailing = pathbytes.split_segments(path)
    key = "/".join(segments)
    if key in _CACHE:
        return _CACHE[key]
    is_abs, stack = _fold(is_abs, segments)
    joined = "/".join(stack)
    if is_abs:
        joined = "/" + joined
    _CACHE[key] = joined
    return joined


def join(*paths):
    """把若干路径从左到右拼接成一个 ``str`` 路径。"""
    if not paths:
        return ""
    result = paths[0]
    for part in paths[1:]:
        result = result.rstrip("/") + "/" + part.lstrip("/")
    return result