"""pathcanon 既有用例（unittest）。

起点：本文件当前**全绿**；它只覆盖常规相对/绝对路径，不触碰需要修复的那些角落。
**勿改本文件。**
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))

from pathcanon import join, normpath  # noqa: E402


class PathCanonTests(unittest.TestCase):
    def test_relative_simple(self):
        self.assertEqual(normpath("a/b"), "a/b")

    def test_dot_segment(self):
        self.assertEqual(normpath("a/./b"), "a/b")

    def test_dotdot_within_tree(self):
        self.assertEqual(normpath("a/../b"), "b")

    def test_internal_double_slash(self):
        self.assertEqual(normpath("a//b"), "a/b")

    def test_leading_dot_slash(self):
        self.assertEqual(normpath("./a/b"), "a/b")

    def test_absolute(self):
        self.assertEqual(normpath("/x/y"), "/x/y")

    def test_plain_name(self):
        self.assertEqual(normpath("abc"), "abc")

    def test_empty(self):
        self.assertEqual(normpath(""), "")

    def test_dotdot_in_middle(self):
        self.assertEqual(normpath("d/e/../f"), "d/f")

    def test_join_relative(self):
        self.assertEqual(join("a", "b/c"), "a/b/c")

    def test_join_strips_slash(self):
        self.assertEqual(join("a/", "b"), "a/b")

    def test_returns_str(self):
        result = normpath("p/q")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "p/q")


if __name__ == "__main__":
    unittest.main(verbosity=2)