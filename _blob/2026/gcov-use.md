---
layout: lecture
title: "Gcov Use"
date: 2026-02-02
ready: true
---

## 覆盖率工具的两个关键细节

gcov 的覆盖率计数全部存放在 `.gcda` 中，文件存在就累加，不存在就从 0 开始。删除 `.gcda` 等价于重置 coverage，这也是 CI 和测试前常见的清理步骤。

lcov 在生成 `.info` 时决定源码路径的形态（绝对或相对），路径以 `SF:` 字符串形式写入。genhtml 不会修正或推导路径，只会按当前工作目录原样查找源码文件；相对路径是否可用，完全取决于生成 info 时的设计。

## 以 test.c 为例

```bash
gcc -fprofile-arcs -ftest-coverage test.c -o test
./test
```

生成 test.gcda 文件，这是执行记录，记录了每段代码的实际执行次数。

```bash
lcov -c -d . -o test.info
genhtml test.info -o coverage_report
```

这个过程就像是先绘制地图（gcno），再记录行程（gcda），最后用 lcov 整理成游记（info），最终生成 HTML 报告。

