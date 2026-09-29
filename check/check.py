#!/usr/bin/env python3
"""pathcanon 固定验收入口（确定性，勿改）。

逐场景打印：
    PASS <组>/<名>
    FAIL <组>/<名>  期望=… 实际=…

结尾打印：
    结果：通过 x/N

全过 exit 0，否则 exit 1。支持：
    python check/check.py -list           列出全部场景
    python check/check.py --only <组名>   只跑某一组（便于验证各判据轴互相独立）

判据完全确定性：不依赖墙钟、随机源、哈希/字典迭代顺序。
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

try:
    import pathcanon  # noqa: E402
except Exception as exc:  # pragma: no cover - 导入失败则全部场景失败
    pathcanon = None
    _IMPORT_ERROR = repr(exc)


def _norm(path):
    if pathcanon is None:
        raise RuntimeError("pathcanon 导入失败: " + _IMPORT_ERROR)
    return pathcanon.normpath(path)


def _join(*paths):
    if pathcanon is None:
        raise RuntimeError("pathcanon 导入失败: " + _IMPORT_ERROR)
    return pathcanon.join(*paths)


def _show(v):
    """可判定的展示：bytes 用 repr，str 直接用。"""
    if isinstance(v, bytes):
        return repr(v)
    return repr(v)


# ---------------------------------------------------------------------------
# 场景定义：每个场景返回 (passed: bool, expected: str, actual: str)
# ---------------------------------------------------------------------------

def s_norm_rel_abs():
    exp = [("a/b", "a/b"), ("/a/b", "/a/b"), ("rel", "rel"), ("/rel", "/rel")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_dot():
    exp = [("a/./b", "a/b"), ("a/.", "a"), ("./a", "a")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_dotdot_within():
    exp = [("a/../b", "b"), ("d/e/../f", "d/f")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_dotdot_root():
    exp = [("/../a", "/a"), ("a/../../b", "../b"), ("/a/../b", "/b")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_slash_internal():
    exp = [("a//b", "a/b"), ("a///b", "a/b")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_slash_leading():
    exp = [("//x", "//x"), ("///x", "/x")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_trailing():
    exp = [("a/", "a/"), ("/a/", "/a/"), ("a", "a")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_norm_special():
    exp = [("", ""), ("/", "/"), ("//", "//")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_bytes_same_type():
    exp = [(b"a/b", b"a/b"), (b"x", b"x")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want or not isinstance(got, bytes):
            return False, _show(want), _show(got)
    return True, "", ""


def s_bytes_abs():
    exp = [(b"/a", b"/a"), (b"a/b", b"a/b")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want or not isinstance(got, bytes):
            return False, _show(want), _show(got)
    return True, "", ""


def s_bytes_nonutf8():
    # 非 UTF-8 字节必须原样保留，且不得抛 UnicodeDecodeError
    inp = b"a/\xff/b"
    want = b"a/\xff/b"
    got = _norm(inp)
    if got != want or not isinstance(got, bytes):
        return False, _show(want), _show(got)
    return True, "", ""


def s_bytes_dotdot():
    exp = [(b"/../a", b"/a"), (b"a/../../b", b"../b")]
    for inp, want in exp:
        got = _norm(inp)
        if got != want or not isinstance(got, bytes):
            return False, _show(want), _show(got)
    return True, "", ""


def s_join_basic():
    exp = [("a", "b/c", "a/b/c"), ("a/", "b", "a/b"), ("a", "b", "c", "a/b/c")]
    for entry in exp:
        parts, want = entry[:-1], entry[-1]
        got = _join(*parts)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_join_abs_override():
    exp = [("a", "/b", "/b"), ("a/b", "/c/d", "/c/d"), ("a", "b", "/c", "d", "/c/d")]
    for entry in exp:
        parts, want = entry[:-1], entry[-1]
        got = _join(*parts)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_join_edge():
    exp = [("", "x", "x"), ("x", "", "x"), ("/a", "", "/a")]
    for entry in exp:
        parts, want = entry[:-1], entry[-1]
        got = _join(*parts)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_eng_determinism():
    # 跨调用不得污染：先算相对路径，再算同段绝对路径，结果必须独立正确。
    seq = [("a/b", "a/b"), ("/a/b", "/a/b"), ("c", "c"), ("/c", "/c")]
    for inp, want in seq:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    # 颠倒顺序再算一次，结果必须一致
    seq2 = [("/c", "/c"), ("c", "c"), ("/a/b", "/a/b"), ("a/b", "a/b")]
    for inp, want in seq2:
        got = _norm(inp)
        if got != want:
            return False, _show(want), _show(got)
    return True, "", ""


def s_eng_scale():
    # 规模/边界：超长路径必须正确且不得报错（线性算法，不依赖墙钟）。
    k = 20000
    big = "/".join(["a"] * k)
    got = _norm(big)
    if got != big:
        return False, "len=%d 一致" % len(big), _show(got[:40]) + "..."
    big_b = big.encode("ascii")
    got_b = _norm(big_b)
    if got_b != big_b or not isinstance(got_b, bytes):
        return False, _show(big_b[:20]) + "...", _show(got_b[:20])
    return True, "", ""


SCENARIOS = [
    ("norm", "rel_abs", s_norm_rel_abs),
    ("norm", "dot", s_norm_dot),
    ("norm", "dotdot_within", s_norm_dotdot_within),
    ("norm", "dotdot_root", s_norm_dotdot_root),
    ("norm", "slash_internal", s_norm_slash_internal),
    ("norm", "slash_leading", s_norm_slash_leading),
    ("norm", "trailing", s_norm_trailing),
    ("norm", "special", s_norm_special),
    ("bytes", "same_type", s_bytes_same_type),
    ("bytes", "abs", s_bytes_abs),
    ("bytes", "nonutf8", s_bytes_nonutf8),
    ("bytes", "dotdot", s_bytes_dotdot),
    ("join", "basic", s_join_basic),
    ("join", "abs_override", s_join_abs_override),
    ("join", "edge", s_join_edge),
    ("engineering", "determinism", s_eng_determinism),
    ("engineering", "scale", s_eng_scale),
]


def main(argv):
    args = argv[1:]
    only_group = None
    list_only = False
    if "-list" in args:
        list_only = True
    if "--only" in args:
        idx = args.index("--only")
        if idx + 1 < len(args):
            only_group = args[idx + 1]

    selected = [(g, n, f) for (g, n, f) in SCENARIOS if only_group is None or g == only_group]

    if list_only:
        for g, n, _ in selected:
            print("%s/%s" % (g, n))
        return 0

    passed = 0
    total = len(selected)
    for g, n, fn in selected:
        try:
            ok, want, got = fn()
        except Exception as exc:  # 任何异常都算失败，绝不早退
            ok, want, got = False, "<no-exception>", repr(exc)
        if ok:
            print("PASS %s/%s" % (g, n))
            passed += 1
        else:
            print("FAIL %s/%s  期望=%s 实际=%s" % (g, n, want, got))

    print("结果：通过 %d/%d" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
