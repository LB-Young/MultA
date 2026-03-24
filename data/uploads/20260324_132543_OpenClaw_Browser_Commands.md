# OpenClaw Browser 命令速查表

## 浏览器操作命令对比表

| 功能介绍 | Chrome 命令 (openclaw) | Browser Relay 命令 | 可配参数 |
|---------|----------------------|-------------------|---------|
| 查看状态 | `openclaw browser status` | `openclaw browser --browser-profile chrome-relay status` | `--json` (JSON格式输出) |
| 启动浏览器 | `openclaw browser start` | `openclaw browser --browser-profile chrome-relay start` | `--browser-profile <name>` |
| 停止浏览器 | `openclaw browser stop` | `openclaw browser --browser-profile chrome-relay stop` | |
| 查看标签页 | `openclaw browser tabs` | `openclaw browser --browser-profile chrome-relay tabs` | |
| 新建标签页 | `openclaw browser tab new` | `openclaw browser --browser-profile chrome-relay tab new` | |
| 选择标签页 | `openclaw browser tab select <n>` | `openclaw browser --browser-profile chrome-relay tab select <n>` | `<n>`: 标签页序号 |
| 关闭标签页 | `openclaw browser tab close <n>` | `openclaw browser --browser-profile chrome-relay tab close <n>` | `<n>`: 标签页序号 |
| 打开URL | `openclaw browser open <url>` | `openclaw browser --browser-profile chrome-relay open <url>` | `<url>`: 目标网址 |
| 聚焦标签页 | `openclaw browser focus <targetId>` | `openclaw browser --browser-profile chrome-relay focus <targetId>` | `<targetId>`: 标签页ID |
| 关闭标签页 | `openclaw browser close <targetId>` | `openclaw browser --browser-profile chrome-relay close <targetId>` | `<targetId>`: 标签页ID |
| 获取快照 | `openclaw browser snapshot` | `openclaw browser --browser-profile chrome-relay snapshot` | `--format ai\|aria`, `--interactive`, `--compact`, `--depth <n>`, `--labels`, `--selector <css>` |
| 页面截图 | `openclaw browser screenshot` | `openclaw browser --browser-profile chrome-relay screenshot` | `--full-page`, `--ref <ref>`, `--labels` |
| 导出PDF | `openclaw browser pdf` | `openclaw browser --browser-profile chrome-relay pdf` | |
| 导航 | `openclaw browser navigate <url>` | `openclaw browser --browser-profile chrome-relay navigate <url>` | `<url>`: 目标网址 |
| 调整窗口 | `openclaw browser resize <w> <h>` | `openclaw browser --browser-profile chrome-relay resize <w> <h>` | `<w>`: 宽度, `<h>`: 高度 |
| 点击元素 | `openclaw browser click <ref>` | `openclaw browser --browser-profile chrome-relay click <ref>` | `<ref>`: 元素引用, `--double` (双击) |
| 输入文字 | `openclaw browser type <ref> <text>` | `openclaw browser --browser-profile chrome-relay type <ref> <text>` | `<ref>`: 元素引用, `--submit` (提交) |
| 按键 | `openclaw browser press <key>` | `openclaw browser --browser-profile chrome-relay press <key>` | `<key>`: 键名如 Enter/Escape/Backspace |
| 悬停 | `openclaw browser hover <ref>` | `openclaw browser --browser-profile chrome-relay hover <ref>` | `<ref>`: 元素引用 |
| 滚动到元素 | `openclaw browser scrollintoview <ref>` | `openclaw browser --browser-profile chrome-relay scrollintoview <ref>` | `<ref>`: 元素引用 |
| 拖拽 | `openclaw browser drag <ref1> <ref2>` | `openclaw browser --browser-profile chrome-relay drag <ref1> <ref2>` | `<ref1>`: 源元素, `<ref2>`: 目标元素 |
| 选择选项 | `openclaw browser select <ref> <opt1> <opt2>` | `openclaw browser --browser-profile chrome-relay select <ref> <opt1> <opt2>` | `<ref>`: 元素引用, `<optN>`: 选项值 |
| 填充表单 | `openclaw browser fill --fields '<json>'` | `openclaw browser --browser-profile chrome-relay fill --fields '<json>'` | `--fields`: JSON数组 ` [{"ref":"1","type":"text","value":"Ada"}]` |
| 等待 | `openclaw browser wait --text <text>` | `openclaw browser --browser-profile chrome-relay wait --text <text>` | `--text`, `--url <pattern>`, `--load <state>`, `--fn <js>`, `--timeout-ms <ms>` |
| 执行JS | `openclaw browser evaluate --fn '<js>'` | `openclaw browser --browser-profile chrome-relay evaluate --fn '<js>'` | `--fn`: JS函数, `--ref <ref>` |
| 高亮元素 | `openclaw browser highlight <ref>` | `openclaw browser --browser-profile chrome-relay highlight <ref>` | `<ref>`: 元素引用 |
| 查看控制台 | `openclaw browser console --level <level>` | `openclaw browser --browser-profile chrome-relay console --level <level>` | `--level`: error/warn/log/debug |
| 查看错误 | `openclaw browser errors` | `openclaw browser --browser-profile chrome-relay errors` | `--clear` (清除) |
| 查看请求 | `openclaw browser requests --filter <pattern>` | `openclaw browser --browser-profile chrome-relay requests --filter <pattern>` | `--filter`, `--clear` |
| 开始追踪 | `openclaw browser trace start` | `openclaw browser --browser-profile chrome-relay trace start` | |
| 结束追踪 | `openclaw browser trace stop` | `openclaw browser --browser-profile chrome-relay trace stop` | |

---

## Cookie 与存储管理

| 功能介绍 | Chrome 命令 (openclaw) | Browser Relay 命令 | 可配参数 |
|---------|----------------------|-------------------|---------|
| 查看Cookie | `openclaw browser cookies` | `openclaw browser --browser-profile chrome-relay cookies` | `--json` |
| 设置Cookie | `openclaw browser cookies set <name> <value>` | `openclaw browser --browser-profile chrome-relay cookies set <name> <value>` | `--url <url>` |
| 清除Cookie | `openclaw browser cookies clear` | `openclaw browser --browser-profile chrome-relay cookies clear` | |
| 获取LocalStorage | `openclaw browser storage local get` | `openclaw browser --browser-profile chrome-relay storage local get` | |
| 设置LocalStorage | `openclaw browser storage local set <key> <value>` | `openclaw browser --browser-profile chrome-relay storage local set <key> <value>` | |
| 清除LocalStorage | `openclaw browser storage local clear` | `openclaw browser --browser-profile chrome-relay storage local clear` | |
| 获取SessionStorage | `openclaw browser storage session get` | `openclaw browser --browser-profile chrome-relay storage session get` | |
| 清除SessionStorage | `openclaw browser storage session clear` | `openclaw browser --browser-profile chrome-relay storage session clear` | |

---

## 环境模拟设置

| 功能介绍 | Chrome 命令 (openclaw) | Browser Relay 命令 | 可配参数 |
|---------|----------------------|-------------------|---------|
| 离线模式 | `openclaw browser set offline on/off` | `openclaw browser --browser-profile chrome-relay set offline on/off` | `on`, `off` |
| 自定义Headers | `openclaw browser set headers --headers-json '<json>'` | `openclaw browser --browser-profile chrome-relay set headers --headers-json '<json>'` | `--headers-json`: JSON对象 |
| 基本认证 | `openclaw browser set credentials <user> <pass>` | `openclaw browser --browser-profile chrome-relay set credentials <user> <pass>` | `--clear` 清除 |
| 地理位置 | `openclaw browser set geo <lat> <lon>` | `openclaw browser --browser-profile chrome-relay set geo <lat> <lon>` | `--origin <url>`, `--clear` |
| 媒体主题 | `openclaw browser set media dark` | `openclaw browser --browser-profile chrome-relay set media dark` | `dark`, `light`, `no-preference`, `none` |
| 时区 | `openclaw browser set timezone <zone>` | `openclaw browser --browser-profile chrome-relay set timezone <zone>` | 如 `America/New_York` |
| 语言 | `openclaw browser set locale <code>` | `openclaw browser --browser-profile chrome-relay set locale <code>` | 如 `en-US` |
| 设备预设 | `openclaw browser set device "<name>"` | `openclaw browser --browser-profile chrome-relay set device "<name>"` | 如 `"iPhone 14"`, `"Pixel 7"` |
| 视口大小 | `openclaw browser set viewport <w> <h>` | `openclaw browser --browser-profile chrome-relay set viewport <w> <h>` | `<w>`: 宽度, `<h>`: 高度 |

---

## 上传与下载

| 功能介绍 | Chrome 命令 (openclaw) | Browser Relay 命令 | 可配参数 |
|---------|----------------------|-------------------|---------|
| 上传文件 | `openclaw browser upload <path>` | `openclaw browser --browser-profile chrome-relay upload <path>` | `--input-ref <ref>`, `--element <css>` |
| 下载文件 | `openclaw browser download <ref> <filename>` | `openclaw browser --browser-profile chrome-relay download <ref> <filename>` | `<ref>`: 元素引用, `<filename>`: 文件名 |
| 等待下载 | `openclaw browser waitfordownload <filename>` | `openclaw browser --browser-profile chrome-relay waitfordownload <filename>` | `<filename>`: 文件名 |
| 处理对话框 | `openclaw browser dialog --accept` | `openclaw browser --browser-profile chrome-relay dialog --accept` | `--accept`, `--dismiss` |

---

## Profile 常用命令

| 功能介绍 | 命令 | 可配参数 |
|---------|------|---------|
| 查看所有Profile | `openclaw browser profiles` | |
| 创建Profile | `openclaw browser create-profile --name <name> --driver <driver>` | `--name`, `--driver extension\|remote\|existing-session`, `--cdp-url`, `--color` |
| 查看Profile状态 | `openclaw browser --browser-profile <name> status` | `<name>`: openclaw/user/chrome-relay |
| 安装扩展 | `openclaw browser extension install` | |
| 扩展路径 | `openclaw browser extension path` | |

---

## 常用参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--browser-profile <name>` | 指定浏览器Profile | `chrome-relay`, `user`, `openclaw` |
| `--json` | JSON格式输出 | `openclaw browser status --json` |
| `--ref <ref>` | 元素引用ID | `12`, `e12` (从snapshot获取) |
| `--format ai\|aria` | 快照格式 | `ai` (AI快照带引用), `aria` (无障碍树) |
| `--interactive` | 交互式快照 | 返回可操作元素列表 |
| `--compact` | 紧凑快照 | 减少输出内容 |
| `--depth <n>` | 快照深度 | `<n>`: 数字如 6 |
| `--labels` | 带标签截图 | 显示元素引用标签 |
| `--full-page` | 全页截图 | 截取整个页面 |
| `--double` | 双击操作 | 用于click/type |
| `--submit` | 提交表单 | 输入后回车 |
| `--timeout-ms <ms>` | 超时毫秒 | 默认 15000ms |
| `--url <pattern>` | URL匹配模式 | 支持 glob 如 `**/dash` |
| `--load <state>` | 加载状态 | `domcontentloaded`, `load`, `networkidle` |
| `--fn <js>` | JS函数 | `window.ready===true` |
| `--headers-json <json>` | 自定义Headers | `'{"X-Debug":"1"}'` |
| `--clear` | 清除操作 | 用于cookies/storage/credentials |

---

## 快照引用说明

- **AI快照 (数字引用)**: `openclaw browser snapshot` → 返回 `1`, `2`, `3`... 引用
  - 操作: `click 12`, `type 23 "hello"`
- **Role快照 (角色引用)**: `openclaw browser snapshot --interactive` → 返回 `e12`, `e13`... 引用
  - 操作: `click e12`, `hover e13`

> ⚠️ 注意: 引用在页面导航后会失效，每次操作前建议重新获取快照

---

## XPath 使用方式

> ⚠️ 注意：OpenClaw 官方推荐使用快照引用 (ref) 进行操作，不支持直接使用 XPath/CSS 选择器进行 click/type 等操作。
> 
> 文档明确说明："CSS selectors are intentionally not supported for actions."
>
> 以下 XPath 用法是通过 `evaluate` 执行 JavaScript 实现的替代方案，非官方推荐方式。

### 使用场景

当需要精确控制元素时，可使用 `evaluate` 命令配合 JavaScript XPath API：

```bash
# 基础语法
openclaw browser evaluate --fn "document.evaluate('XPath表达式', document, null, XPathResult.常量, null).singleNodeValue.操作()"
```

### XPath 常用常量

| 常量 | 说明 |
|------|------|
| `XPathResult.FIRST_ORDERED_NODE_TYPE` | 返回第一个匹配的节点 |
| `XPathResult.ORDERED_NODE_ITERATOR_TYPE` | 返回节点迭代器 |
| `XPathResult.ANY_UNORDERED_NODE_TYPE` | 返回任意一个匹配的节点 |

### 常用 XPath 示例

#### 1. 点击元素

```bash
# 点击 id 为 submit 的按钮
openclaw browser evaluate --fn "document.evaluate('//button[@id=\"submit\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()"

# 点击第一个按钮
openclaw browser evaluate --fn "document.evaluate('//button[1]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()"

# 点击包含文本"提交"的按钮
openclaw browser evaluate --fn "document.evaluate('//button[contains(text(),\"提交\")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()"

# 点击 class 包含 btn 的元素
openclaw browser evaluate --fn "document.evaluate('//*[contains(@class,\"btn\")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()"
```

#### 2. 输入文字

```bash
# 输入到 name 为 q 的输入框
openclaw browser evaluate --fn "document.evaluate('//input[@name=\"q\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value='hello world'"

# 输入到 id 为 username 的输入框
openclaw browser evaluate --fn "document.evaluate('//input[@id=\"username\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value='myname'"

# 输入到 textarea
openclaw browser evaluate --fn "document.evaluate('//textarea[@placeholder=\"请输入内容\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value='这是内容'"
```

#### 3. 获取元素文本

```bash
# 获取第一个 h1 的文本
openclaw browser evaluate --fn "document.evaluate('//h1', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.textContent"

# 获取所有链接文本
openclaw browser evaluate --fn "Array.from(document.evaluate('//a', document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null)).map(el => el.textContent).join('\\n')"
```

#### 4. 获取元素属性

```bash
# 获取第一个图片的 src
openclaw browser evaluate --fn "document.evaluate('//img[1]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.src"

# 获取链接的 href
openclaw browser evaluate --fn "document.evaluate('//a[@class=\"link\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.href"
```

#### 5. 悬停/聚焦

```bash
# 悬停到元素
openclaw browser evaluate --fn "document.evaluate('//div[@class=\"menu-item\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}))"

# 聚焦到输入框
openclaw browser evaluate --fn "document.evaluate('//input[@name=\"email\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.focus()"
```

#### 6. 勾选复选框

```bash
# 勾选
openclaw browser evaluate --fn "document.evaluate('//input[@type=\"checkbox\"][@id=\"agree\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.checked=true"

# 取消勾选
openclaw browser evaluate --fn "document.evaluate('//input[@type=\"checkbox\"][@id=\"agree\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.checked=false"
```

#### 7. 选择下拉选项

```bash
# 通过 value 选择
openclaw browser evaluate --fn "document.evaluate('//select[@name=\"city\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.value='beijing'"

# 通过索引选择
openclaw browser evaluate --fn "document.evaluate('//select[@name=\"city\"]/option[2]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.selected=true"
```

#### 8. 滚动到元素

```bash
# 滚动到元素可见
openclaw browser evaluate --fn "document.evaluate('//div[@id=\"footer\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.scrollIntoView()"
```

#### 9. 等待元素出现

```bash
# 配合 wait --fn 使用
openclaw browser wait --fn "document.evaluate('//div[@class=\"loaded\"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue !== null"
```

---

### 常用 XPath 表达式

| 表达式 | 说明 |
|--------|------|
| `//tag` | 任意标签 |
| `//*` | 任意元素 |
| `//tag[@id="xxx"]` | id 等于 xxx |
| `//tag[@class="xxx"]` | class 等于 xxx |
| `//tag[contains(@class,"xxx")]` | class 包含 xxx |
| `//tag[contains(text(),"xxx")]` | 文本包含 xxx |
| `//tag[@attr="value"]` | 属性等于 value |
| `//parent/child` | 子元素 |
| `//parent//descendant` | 后代元素 |
| `//tag[1]` | 第一个 |
| `//tag[last()]` | 最后一个 |
| `//tag[@id="xxx"]/child::tag` | 子节点 |

---

### XPath vs 快照引用对比

| 场景 | 快照引用 (推荐) | XPath (备选) |
|------|---------------|-------------|
| 稳定性 | 高 (基于语义角色) | 低 (依赖页面结构) |
| 易用性 | 简单 | 需编写 XPath |
| 维护性 | 好 | 差 (页面改就失效) |
| 适用场景 | 通用场景 | 精确元素定位 |

> 💡 建议：优先使用快照引用方式操作元素，XPath 仅作为备选方案。

---

## 使用场景快速查询

| 场景 | 推荐命令 |
|------|---------|
| 打开网页浏览 | `openclaw browser open https://example.com` |
| 获取可交互元素 | `openclaw browser snapshot --interactive` |
| 点击按钮/链接 | `openclaw browser click e12` |
| 输入搜索内容 | `openclaw browser type e12 "关键词" --submit` |
| 截取页面 | `openclaw browser screenshot --labels` |
| 查看JS错误 | `openclaw browser console --level error` |
| 模拟手机浏览 | `openclaw browser set device "iPhone 14"` |
| 调试网络请求 | `openclaw browser requests --filter api` |
| 录制操作 trace | `openclaw browser trace start` → 操作 → `openclaw browser trace stop` |

---

*文档生成时间: 2026-03-19*
