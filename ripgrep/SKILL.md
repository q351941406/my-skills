---
name: ripgrep
description: 当需要使用 ripgrep (rg) 命令进行文件搜索、内容搜索、正则匹配、代码搜索时，此技能提供完整的选项参考和用法指南。涵盖基础搜索、自动过滤、glob/文件类型过滤、替换输出、配置文件、编码处理、二进制文件、预处理器等所有核心功能。
version: 0.1.0
---

# ripgrep 技能参考

ripgrep (`rg`) 是高性能命令行搜索工具，支持正则表达式，默认递归搜索当前目录。

## 基础用法

```bash
# 在指定文件中搜索
rg <pattern> <file>

# 递归搜索当前目录（默认行为）
rg <pattern>
rg <pattern> ./            # 等同于上一行
rg <pattern> src/          # 限定搜索目录
```

支持正则表达式语法（同 Rust regex）：https://docs.rs/regex/*/regex/#syntax

- `\w` 匹配单词字符，`\W` 匹配非单词字符
- `+` 一次或多次，`*` 零次或多次
- `-F` 将模式视为字面量字符串，不解析正则（如 `rg -F 'fn write('`）

## 自动过滤（默认行为）

默认搜索时会跳过：

| 跳过项 | 对应覆盖标志 |
|--------|-------------|
| `.gitignore` / `.ignore` / `.rgignore` 中的文件 | `--no-ignore` |
| 隐藏文件和目录 | `--hidden` 或 `-.` |
| 二进制文件（含 NUL 字节） | `--text` 或 `-a` |
| 符号链接 | `--follow` 或 `-L` |

快捷方式：`-u` 逐步放宽过滤 —— `-u` 忽略 gitignore，`-uu` 搜索隐藏文件，`-uuu` 搜索二进制文件。

### ignore 文件优先级

`.rgignore` > `.ignore` > `.gitignore`

可用 `.ignore` 白名单覆盖 `.gitignore` 规则，如 `.gitignore` 中有 `log/`，在 `.ignore` 中写 `!log/` 即可让 ripgrep 搜索该目录。

## 手动过滤

### Glob 模式

```bash
rg <pattern> -g '*.toml'       # 只搜索 *.toml 文件
rg <pattern> -g '!*.toml'      # 排除 *.toml 文件
rg <pattern> -g '!*.toml' -g '*.toml'  # 后面的 glob 覆盖前面的
```

注意：`!` 在命令行表示排除（黑名单），在 `.gitignore` 中表示白名单，语义相反。

### 文件类型

```bash
rg <pattern> -trust            # 只搜索 Rust 文件（等同于 --type rust）
rg <pattern> -tc               # 只搜索 C 文件（含 .c 和 .h）
rg <pattern> -Trust            # 排除 Rust 文件（大写 T = 排除）
rg --type-list                 # 查看所有预定义类型及其 glob
```

自定义类型（仅当前命令生效）：

```bash
rg --type-add 'web:*.{html,css,js}' -tweb <pattern>
```

持久化方式：写入配置文件或设置 shell alias。

特殊类型 `all` 匹配所有已注册类型对应的文件；`--type-not all` 搜索所有未匹配任何类型的文件。

## 替换输出

```bash
rg <pattern> -r <replacement>          # 替换匹配部分（不影响文件）
rg <pattern> -r 'prefix-$1-suffix'     # 使用捕获组 $1, $2, ...
rg <pattern> -r 'prefix-$word'         # 使用命名捕获组 (?P<word>...)
rg <pattern> -o -r <replacement>       # 只输出替换后的匹配部分
```

**ripgrep 不会修改文件**，`-r` 仅影响输出。

## 配置文件

通过 `RIPGREP_CONFIG_PATH` 环境变量指定配置文件路径。

格式规则：每行一个参数，`#` 开头为注释，无转义。

```
# 示例 ~/.ripgreprc
--max-columns=150
--max-columns-preview
--type-add
web:*.{html,css,js}
--hidden
--glob=!.git/*
--smart-case
```

- 带值的参数用 `=` 连接（`--max-columns=150`）或分两行写
- 命令行参数会覆盖配置文件（配置文件参数被前置，后出现的优先）
- `--no-config` 可强制禁止读取配置文件
- `--debug` 可查看加载了哪个配置文件

## 文件编码

默认 `--encoding auto`：
- 假定输入为 ASCII 兼容编码（ASCII / latin1 / UTF-8）
- 正则引擎支持 Unicode（`\w` 匹配 Unicode 单词字符，`.` 匹配 Unicode 码点）
- 自动检测 UTF-16 BOM 并转码
- `-E <encoding>` 指定编码，`-E none` 禁用所有编码处理

正则中可局部关闭 Unicode：`(?-u:.)` 让 `.` 匹配任意字节而非码点。

## 二进制文件处理

三种模式：

| 模式 | 行为 | 启用方式 |
|------|------|---------|
| 默认 | 检测到 NUL 字节即停止搜索 | （默认） |
| 二进制模式 | 继续搜索直到找到匹配或文件结尾 | `--binary` |
| 文本模式 | 完全禁用二进制检测 | `-a` / `--text` |

注意：使用 mmap 时二进制检测仅在文件开头和匹配行上执行，可能导致检测结果不一致。`--no-mmap` 可禁用 mmap 保持一致性。

## 预处理器

```bash
# 用 --pre 指定预处理命令，对每个文件执行转换后再搜索
rg --pre ./preprocess <pattern> <file>

# 用 --pre-glob 限定预处理器只处理匹配的文件，避免不必要的开销
rg --pre ./preprocess --pre-glob '*.pdf' <pattern>
```

预处理器脚本接收文件路径作为参数，文件内容通过 stdin 传入。

示例（搜索 PDF）：

```sh
#!/bin/sh
case "$1" in
*.pdf)
  if [ -s "$1" ]; then exec pdftotext - -; else exec cat; fi ;;
*) exec cat ;;
esac
```

## 常用选项速查

| 选项 | 简写 | 说明 |
|------|------|------|
| `--ignore-case` | `-i` | 忽略大小写 |
| `--smart-case` | `-S` | 模式含大写字母时自动区分大小写 |
| `--fixed-strings` | `-F` | 将模式视为字面量 |
| `--word-regexp` | `-w` | 匹配完整单词（词边界） |
| `--count` | `-c` | 只输出匹配行数 |
| `--files` | — | 列出会搜索的文件，不执行搜索 |
| `--text` | `-a` | 将二进制文件当文本搜索 |
| `--multiline` | `-U` | 允许跨行匹配 |
| `--search-zip` | `-z` | 搜索压缩文件 |
| `--context` | `-C` | 显示匹配行的上下文 |
| `--sort path` | — | 按文件名排序输出（禁用并行，较慢） |
| `--follow` | `-L` | 跟随符号链接 |
| `--max-columns` | `-M` | 限制输出行宽 |
| `--debug` | — | 调试输出（查看过滤原因、配置来源） |
| `--no-config` | — | 禁止读取配置文件 |
