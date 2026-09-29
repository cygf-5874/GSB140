# pathcanon

POSIX 子集路径规范化库。纯计算，**不触碰文件系统**；Python 3，标准库，**零第三方依赖**。

- 入口：`src/pathcanon.py`（导出 `normpath` / `join`）；字节层工具 `src/pathbytes.py`。
- 既有用例：`python tests/run.py`（12 个，起点全绿）。
- 固定验收程序：`bash scripts/check.sh`（`check/` 是固定验收程序，**勿改**）。

```bash
python tests/run.py
bash scripts/check.sh -list
bash scripts/check.sh --only engineering
```

## 语言版本前提

- Python 3（仓库内已验证 3.13）。
- **只用标准库**；不引入任何第三方依赖。
- 实现本身**不得**调用 `os.path`（可对照，但不得直接调用）。

## 对外保证（8 条）

下面 8 条是 `pathcanon` 的**对外契约**，实现必须全部守住；它们是本题验收点的唯一出处。

1. `normpath(path)` 接受 `str` 或 `bytes`，返回**同类型**结果；区分相对与绝对：以 `/` 开头的绝对路径
   结果仍为绝对，相对路径结果仍相对。
2. `.` 段忽略；`..` 段弹出上一层；**没有上一层可弹时（绝对路径的根处）必须丢弃该 `..`，
   结果不得离开根**（如 `/../a` 应为 `/a`）；相对路径的 `..` 允许保留（可上溯，如 `a/../../b` 为 `../b`）。
3. 连续 `/` 折叠为单个，但**前导**斜杠数有语义：恰好两个前导斜杠（`//x`）归一后**保留**为 `//x`，
   三个及以上（`///x`）折叠为 `/x`。输入末尾带一个以上 `/` 时，结果**保留一个**末尾 `/`
   （文件与目录的区分）；输入不带末尾 `/` 时不添加。
4. **字节安全**：`bytes` 路径按字节处理，**不得**对非 UTF-8 字节做 `decode` / `encode` 往返
   （不得抛 `UnicodeDecodeError`）；非 UTF-8 字节原样保留。
5. `join(*paths) -> str`：从左到右拼接；若某一段自身是**绝对路径**（以 `/` 开头），它**覆盖**
   左侧已拼接的结果，以它重新起算（如 `join("a", "/b") == "/b"`）。
6. **纯函数**：不触碰文件系统；同一输入多次调用结果相同；**不依赖全局可变状态**（不得跨调用污染）。
7. `normpath("") == ""`；`normpath("/") == "/"`；`normpath("//") == "//"`。
8. 对不含末尾斜杠、不含前导双斜杠的输入，`normpath` 与 `os.path.normpath` 结果一致
   （可对照，但实现**不得**直接调用 `os.path`）。

## 本次任务

修 `src/pathcanon.py` 与 `src/pathbytes.py`，让上述 8 条保证全部成立，并满足确定性、
规模与边界的工程化要求。`check/check.py` 会逐场景校验路径规范化的正确性与工程化能力；
`tests/run.py` 的既有用例必须保持全绿。

## 目录

```
src/pathcanon.py    库代码（有缺陷，待修复）
src/pathbytes.py    字节层工具（有缺陷，待修复）
tests/run.py        既有用例（unittest，起点全绿）
check/check.py      固定验收程序（17 个场景，勿改）
scripts/check.sh    自检入口
```
