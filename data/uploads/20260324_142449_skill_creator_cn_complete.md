---
name: skill-creator
description: 创建或更新 AgentSkills。用于设计、构建或打包包含脚本、参考资料和资源文件的技能。
---

# Skill Creator

该技能提供了创建高效技能的指导。

## 关于 Skills

Skills 是模块化、独立的功能包，通过提供专门的知识、工作流和工具来扩展 Codex 的能力。可以把它们看作针对特定领域或任务的“入门指南”——它们会将 Codex 从一个通用型代理转变为一个具备程序性知识的专业代理，而这些知识是任何模型本身都无法完全具备的。

### Skills 提供什么

1. 专门化工作流 - 面向特定领域的多步骤流程
2. 工具集成 - 关于如何使用特定文件格式或 API 的说明
3. 领域专业知识 - 公司特定知识、模式、业务逻辑
4. 打包资源 - 用于复杂和重复性任务的脚本、参考资料和资源文件

## 核心原则

### 简洁是关键

上下文窗口是公共资源。Skills 需要与 Codex 运行所需的其他所有内容共享上下文窗口：系统提示词、对话历史、其他 Skills 的元数据，以及实际的用户请求。

**默认假设：Codex 已经非常聪明。** 只添加 Codex 本身不具备的上下文。对每一条信息都提出质疑：“Codex 真的需要这个解释吗？”以及“这段文字是否值得它消耗的 token 成本？”

优先使用简洁的示例，而不是冗长的解释。

### 设定合适的自由度

根据任务的脆弱性和变化性来匹配指令的具体程度：

**高自由度（文本型说明）**：当多种方法都有效、决策依赖上下文，或需要依靠启发式方法来指导时使用。

**中等自由度（伪代码或带参数的脚本）**：当存在一种优选模式、允许一定变化，或配置会影响行为时使用。

**低自由度（具体脚本、很少参数）**：当操作脆弱且容易出错、一致性至关重要，或必须遵循特定顺序时使用。

把 Codex 想象成在探索一条路径：狭窄的悬崖桥需要具体的护栏（低自由度），而开阔的田野则允许多条路线（高自由度）。

### Skill 的结构

每个 skill 都由一个必需的 SKILL.md 文件和可选的打包资源组成：

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - 可执行代码（Python/Bash/等）
    ├── references/       - 计划在需要时加载到上下文中的文档
    └── assets/           - 在 Codex 生成的输出中使用的文件（模板、图标、字体等）
```

#### SKILL.md（必需）

每个 SKILL.md 由以下内容组成：

- **Frontmatter**（YAML）：包含 `name` 和 `description` 字段。这是 Codex 用来判断何时使用该 skill 的唯一字段，因此必须清晰且全面地描述这个 skill 是什么，以及何时应当使用它。
- **Body**（Markdown）：用于说明如何使用该 skill 的指令与指导。只有在 skill 被触发后才会加载（如果真的触发的话）。

#### 打包资源（可选）

##### 脚本（`scripts/`）

可执行代码（Python/Bash/等），用于那些需要确定性可靠性，或者会被反复重写的任务。

- **何时包含**：当同样的代码会被反复重写，或需要确定性可靠性时
- **示例**：`scripts/rotate_pdf.py`，用于处理 PDF 旋转任务
- **优点**：节省 token、具备确定性，并且可能无需加载到上下文中即可执行
- **注意**：Codex 仍可能需要读取这些脚本，以便进行修改或适配具体环境

##### 参考资料（`references/`）

文档和参考材料，旨在按需加载到上下文中，以帮助 Codex 完成流程和思考。

- **何时包含**：当 Codex 在工作时应当参考这些文档时
- **示例**：`references/finance.md` 用于财务模式，`references/mnda.md` 用于公司 NDA 模板，`references/policies.md` 用于公司政策，`references/api_docs.md` 用于 API 规范
- **使用场景**：数据库模式、API 文档、领域知识、公司政策、详细工作流指南
- **优点**：让 SKILL.md 保持精简，只在需要时才加载
- **最佳实践**：如果文件很大（>10k 字），请在 SKILL.md 中包含 grep 搜索模式
- **避免重复**：信息应当只存在于 SKILL.md 或 references 文件中的一个地方，而不是两边都放。除非它确实是 skill 的核心内容，否则详细信息更适合放在 references 文件中——这样可以让 SKILL.md 保持精简，同时又能让信息在需要时被发现，而不至于占满上下文窗口。SKILL.md 中只保留必要的过程性指令和工作流指导；将详细参考资料、模式和示例移到 references 文件中。

##### 资源文件（`assets/`）

这些文件并不打算加载到上下文中，而是会在 Codex 生成的最终输出中被使用。

- **何时包含**：当 skill 需要使用某些文件来生成最终输出时
- **示例**：`assets/logo.png` 用于品牌资源，`assets/slides.pptx` 用于 PowerPoint 模板，`assets/frontend-template/` 用于 HTML/React 样板工程，`assets/font.ttf` 用于字体
- **使用场景**：模板、图片、图标、样板代码、字体、会被复制或修改的示例文档
- **优点**：将输出资源与文档分离，使 Codex 可以使用这些文件而无需把它们加载进上下文

#### 不应在 Skill 中包含什么

一个 skill 只应包含那些直接支持其功能的必要文件。**不要**创建多余的文档或辅助文件，包括：

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- 等等

skill 中只应包含 AI 代理完成该任务所必需的信息。它不应包含关于创建过程、设置与测试流程、面向用户的文档等辅助性上下文。创建额外文档只会增加混乱和困惑。

### 渐进式披露设计原则

Skills 使用三级加载系统来高效管理上下文：

1. **元数据（name + description）** - 始终在上下文中（约 100 词）
2. **SKILL.md 正文** - 当 skill 触发时加载（少于 5k 词）
3. **打包资源** - 根据 Codex 需要按需加载（理论上无限，因为脚本可以在不读入上下文窗口的情况下执行）

#### 渐进式披露模式

保持 SKILL.md 正文只包含必要内容，并控制在 500 行以内，以减少上下文膨胀。当接近这一限制时，将内容拆分到单独文件中。当把内容拆分到其他文件时，务必要在 SKILL.md 中引用它们，并清楚说明在何时需要读取它们，以确保 skill 的使用者知道这些文件存在，以及何时使用。

**关键原则：**当一个 skill 支持多种变体、框架或选项时，只在 SKILL.md 中保留核心工作流和选择指导。将具体变体的细节（模式、示例、配置）移动到单独的参考文件中。

**模式 1：带参考资料的高层级指南**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Codex 只会在需要时加载 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

**模式 2：按领域组织**

对于支持多个领域的 Skills，按领域组织内容，避免加载无关上下文：

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

当用户询问销售指标时，Codex 只需读取 sales.md。

类似地，对于支持多个框架或变体的 skills，也应按变体组织：

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

当用户选择 AWS 时，Codex 只需读取 aws.md。

**模式 3：条件性细节**

展示基础内容，并链接到高级内容：

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md)

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Codex 只有在用户需要这些功能时，才会读取 REDLINING.md 或 OOXML.md。

**重要指南：**

- **避免过深的引用嵌套** - 保持 references 与 SKILL.md 之间只有一层深度。所有参考文件都应从 SKILL.md 直接链接。
- **组织较长的参考文件** - 对于超过 100 行的文件，请在顶部加入目录，以便 Codex 在预览时能看到其完整范围。

## Skill 创建流程

Skill 创建包括以下步骤：

1. 通过具体示例理解该 skill
2. 规划可复用的 skill 内容（脚本、参考资料、资源文件）
3. 初始化该 skill（运行 init_skill.py）
4. 编辑该 skill（实现资源并编写 SKILL.md）
5. 打包该 skill（运行 package_skill.py）
6. 基于真实使用情况进行迭代

按顺序执行这些步骤，只有在有明确理由说明不适用时才跳过。

### Skill 命名

- 仅使用小写字母、数字和连字符；将用户提供的标题规范化为连字符形式（例如 `"Plan Mode"` -> `plan-mode`）。
- 生成名称时，长度应小于 64 个字符（字母、数字、连字符）。
- 优先使用简短的、以动词开头的短语来描述动作。
- 当按工具进行命名空间划分能提高清晰度或触发效果时，可使用命名空间（例如 `gh-address-comments`、`linear-address-issue`）。
- skill 文件夹名称必须与 skill 名称完全一致。

### 第 1 步：通过具体示例理解 Skill

只有在 skill 的使用模式已经清楚明了时才跳过这一步。即使是在处理已有 skill 时，这一步通常仍然很有价值。

为了创建一个有效的 skill，需要清晰理解实际的使用示例。这种理解既可以来自用户直接提供的示例，也可以来自生成的示例，并通过用户反馈进行验证。

例如，在构建一个 image-editor skill 时，相关问题包括：

- “image-editor skill 应支持哪些功能？编辑、旋转，还有别的吗？”
- “你能举一些这个 skill 的使用示例吗？”
- “我可以想象用户会提出类似‘去掉图片里的红眼’或‘旋转这张图片’这样的请求。你还能想到其他用法吗？”
- “用户会说什么样的话来触发这个 skill？”

为了避免让用户感到负担过重，不要在一条消息中问太多问题。先从最重要的问题开始，并根据需要继续追问，以提高效果。

当你已经清楚知道该 skill 应支持哪些功能时，这一步就可以结束。

### 第 2 步：规划可复用的 Skill 内容

要把具体示例转化为有效的 skill，请按以下方式分析每个示例：

1. 思考如果从零开始执行该示例，需要如何完成
2. 识别哪些脚本、参考资料和资源文件会对反复执行这些工作流有帮助

示例：当构建一个 `pdf-editor` skill 来处理类似“帮我旋转这个 PDF”这样的请求时，分析显示：

1. 旋转 PDF 需要每次都重写相同的代码
2. 一个 `scripts/rotate_pdf.py` 脚本会很有帮助，可用于保存这段逻辑

示例：当设计一个 `frontend-webapp-builder` skill，用于处理类似“帮我做一个待办事项应用”或“帮我做一个追踪步数的仪表盘”这样的请求时，分析显示：

1. 编写前端网页应用每次都需要相同的 HTML/React 样板代码
2. 一个包含 HTML/React 样板项目文件的 `assets/hello-world/` 模板会很有帮助

示例：当构建一个 `big-query` skill 来处理类似“今天有多少用户登录了？”这样的请求时，分析显示：

1. 查询 BigQuery 时，每次都需要重新发现表结构和关系
2. 一个记录表结构的 `references/schema.md` 文件会很有帮助

为了确定该 skill 应包含哪些内容，请分析每个具体示例，并列出要包含的可复用资源：脚本、参考资料和资源文件。

### 第 3 步：初始化 Skill

这时就该真正创建 skill 了。

只有当正在开发的 skill 已经存在，并且只需要迭代或打包时，才可以跳过这一步。在这种情况下，直接继续下一步。

当从零开始创建一个全新的 skill 时，始终运行 `init_skill.py` 脚本。该脚本会方便地生成一个新的模板 skill 目录，其中自动包含 skill 所需的一切内容，从而让 skill 创建过程更高效、更可靠。

用法：

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

示例：

```bash
scripts/init_skill.py my-skill --path skills/public
scripts/init_skill.py my-skill --path skills/public --resources scripts,references
scripts/init_skill.py my-skill --path skills/public --resources scripts --examples
```

该脚本将会：

- 在指定路径创建 skill 目录
- 生成带有正确 frontmatter 和 TODO 占位符的 SKILL.md 模板
- 根据 `--resources` 选项创建资源目录
- 如果设置了 `--examples`，则添加示例文件

初始化之后，按需自定义 SKILL.md 并添加资源。如果使用了 `--examples`，请替换或删除占位示例文件。

### 第 4 步：编辑 Skill

在编辑（新生成的或已有的）skill 时，请记住：这个 skill 是为另一个 Codex 实例创建的。请加入那些对另一个 Codex 实例有帮助且并不显而易见的信息。思考哪些过程性知识、领域特定细节或可复用资源，会帮助另一个 Codex 实例更高效地执行这些任务。

#### 学习经过验证的设计模式

根据你的 skill 需求，请参考以下有帮助的指南：

- **多步骤流程**：参见 references/workflows.md，了解顺序工作流和条件逻辑
- **特定输出格式或质量标准**：参见 references/output-patterns.md，了解模板和示例模式

这些文件包含构建高效 skill 的成熟最佳实践。

#### 从可复用的 Skill 内容开始

开始实现时，应先处理前面识别出的可复用资源：`scripts/`、`references/` 和 `assets/` 文件。注意，这一步可能需要用户输入。例如，在实现一个 `brand-guidelines` skill 时，用户可能需要提供品牌资源或模板以存放到 `assets/` 中，或提供文档以存放到 `references/` 中。

新增脚本必须通过**实际运行**来测试，以确保没有 bug，并且输出符合预期。如果存在很多相似的脚本，只需测试一个有代表性的样本，以在完成效率和验证信心之间取得平衡。

如果使用了 `--examples`，请删除不需要的占位文件。只创建那些真正需要的资源目录。

#### 更新 SKILL.md

**写作指南：**始终使用祈使式/不定式形式。

##### Frontmatter

编写包含 `name` 和 `description` 的 YAML frontmatter：

- `name`：skill 名称
- `description`：这是该 skill 的主要触发机制，它帮助 Codex 理解何时应使用该 skill。
  - 既要包含 Skill 做什么，也要包含何时使用它的具体触发场景。
  - 所有“何时使用”的信息都应放在这里——而不是正文中。正文只有在触发之后才会加载，因此在正文中写 “When to Use This Skill” 一节并不能帮助 Codex。
  - 一个 `docx` skill 的 description 示例：`Comprehensive document creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. Use when Codex needs to work with professional documents (.docx files) for: (1) Creating new documents, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other document tasks`

YAML 中不要包含任何其他字段。

##### Body

编写如何使用该 skill 及其打包资源的说明。

### 第 5 步：打包 Skill

一旦 skill 开发完成，就必须将其打包成一个可分发的 .skill 文件，以便分享给用户。打包流程会先自动验证，以确保它满足所有要求：

```bash
scripts/package_skill.py <path/to/skill-folder>
```

可选地指定输出目录：

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

打包脚本将会：

1. **自动验证**该 skill，检查：
   - YAML frontmatter 格式和必需字段
   - Skill 命名规范和目录结构
   - description 的完整性和质量
   - 文件组织和资源引用

2. **如果验证通过则进行打包**，创建一个以 skill 命名的 .skill 文件（例如 `my-skill.skill`），其中包含所有文件，并保持正确的目录结构以便分发。.skill 文件本质上是一个扩展名为 .skill 的 zip 文件。

   安全限制：如果存在符号链接，将被拒绝，且打包会失败。

如果验证失败，脚本会报告错误并退出，而不会创建打包文件。修复所有验证错误后，再次运行打包命令。

### 第 6 步：迭代

在测试该 skill 后，用户可能会请求改进。通常这会发生在实际使用该 skill 之后，因为此时最能直接感受到该 skill 的表现。

**迭代工作流：**

1. 在真实任务中使用该 skill
2. 注意它在哪些地方表现挣扎或效率低下
3. 识别应如何更新 SKILL.md 或打包资源
4. 实施修改并再次测试
