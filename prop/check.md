# Check.md — 已知问题与修改注意事项

## 1. CTA+Footer（Get in Touch）模块反复丢失

### 问题描述

`solutions.html` 的 CTA+Footer 模块曾多次被意外删除。原因是对该文件进行其他修改（如添加 Industry Solutions / Ecosystem Solutions 卡片跳转链接、修复导航栏 Developer Center 链接等）时，脚本读取了旧版本文件内容并回写，导致之前插入的 CTA 模块被覆盖。

### 受影响文件

- `solutions.html`（连续丢失两次）

### 根本原因

1. 使用 Python 脚本对文件做 read → modify → write 操作时，如果多个修改步骤之间没有重新读取最新文件内容，后一步会覆盖前一步的改动。
2. `solutions.html` 的 CTA 模块位于文件末尾（`</body>` 前），而导航栏修改、卡片链接修改等操作也涉及文件全量回写，容易在不知情的情况下把末尾新增内容丢掉。

### 预防措施

- **每次修改前必须重新读取文件最新内容**，不能复用之前缓存的变量。
- **修改完成后验证关键模块是否存在**，特别是：
  - `id="get-in-touch"` — CTA section 锚点
  - `.git-input` / `.git-select` — CTA 表单样式
  - `initTypewriter('git-title', 'Get in Touch')` — 打字特效调用
- **对所有页面做批量修改时**，确认每个文件修改后仍保留完整的 CTA+Footer 模块。

---

## 2. 各页面必须包含的公共模块清单

每个页面（`home.HTML`、`core-products.html`、`teleoperation-network.html`、`data-services.html`、`solutions.html`、`about-us.html`、`developer-center.html`）都必须包含以下内容：

| 模块 | 关键标识 |
|------|---------|
| 导航栏 Developer Center 链接 | `href="developer-center.html"` |
| 导航栏 Contact Us 链接 | `href="#get-in-touch"` |
| CTA+Footer section | `id="get-in-touch"` |
| CTA 表单样式 | `<style>` 中包含 `.git-input, .git-select` |
| Get in Touch 打字特效 | `id="git-title"` + `initTypewriter('git-title', 'Get in Touch')` |

---

## 3. PowerShell 环境下的 Python 脚本注意事项

在 PowerShell 中直接用 `python -c "..."` 执行包含复杂 HTML 字符串的 Python 代码时，PowerShell 会错误解析分号、括号等字符，导致命令失败。

### 解决方案

对于包含复杂字符串的操作，**先写入 `.py` 文件再执行**，避免 PowerShell 解析干扰：

```
1. Write script to _fix_xxx.py
2. python _fix_xxx.py
3. Delete _fix_xxx.py
```
