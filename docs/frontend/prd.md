AI 研发辅助平台 - 需求原型文档 (PRD) v1.0
愿景与目标
构建一个以 LLM 为核心的研发辅助平台，通过模块化的配置和可定制的流水线，为开发者提供代码评审和测试用例生成两大核心能力，旨在提升代码质量、测试覆盖率和整体研发效率。
基础配置模块 (Configuration Center)
2.1 Git 模块 (Git Configuration)
目标: 集中管理与 Git 仓库交互所需的凭证和仓库信息。
功能点:
F-GIT-01: 全局凭证管理 (Global Credential Management)
UI: 一个表单，包含字段：用户名 (Username)、个人访问令牌 (Personal Access Token)。
逻辑:
用户输入的令牌必须加密存储在数据库中。
提供“测试连接”按钮，后台通过 git ls-remote 等命令验证凭证有效性。
支持编辑和更新凭证。
安全提示: 界面需明确提示用户使用具有适当范围（repo read）的 Token，而非完整权限的密码。
F-GIT-02: 仓库配置列表 (Repository Configuration)
UI: 一个表格，展示所有已配置的仓库，支持增、删、改。
添加/编辑表单:
仓库别名 (Alias): 必填，用户内部使用的易记名称，如 "核心交易系统"。
仓库地址 (URL): 必填，HTTPS 或 SSH 格式的 Git URL。
默认基准分支 (Default Base Branch): 选填，如 main, master, develop。用于在代码评审时作为默认的原分支。
逻辑: 系统使用此处配置的仓库信息和全局凭证来执行后续的 Git 操作。
2.2 Prompt 模块 (Prompt Template Management)
目标: 创建、管理和复用高质量的 Prompt 模板，并支持高级的“元能力”。
功能点:
F-PRMT-01: Prompt 列表与 CRUD
UI: 表格展示 Prompt 列表，包含字段：ID, 名称 (Name), 唯一标识 (Identifier), 更新时间, 说明 (Description)。
添加/编辑表单:
名称: 方便用户理解，如 "代码评审-安全漏洞扫描"。
唯一标识: 必填，英文，用于程序调用，如 code_review_security。
Prompt 内容 (Content): 大文本框，支持变量占位符，如 {{code_diff}}, {{requirement_text}}。
说明: 解释该 Prompt 的用途、适用场景和变量说明。
F-PRMT-02: Prompt 链式调用与生成 (Prompt Chaining - "闭环"功能)
逻辑: 在 Prompt 内容中，允许使用特殊语法来调用另一个 Prompt。例如:
你是一个需求分析专家，请将以下原始需求文本优化和结构化。这是原始需求：{{requirement_text}}。请参考这个优化模板：{{GENERATE_FROM:requirement_optimize_template}}
实现: 系统在解析时，如果遇到 {{GENERATE_FROM:identifier}}，会先执行 identifier 对应的 Prompt，然后将其输出结果替换到当前位置，再执行主 Prompt。这实现了 Prompt 的动态组合和生成。
2.3 知识库模块 (RAG Knowledge Base)
目标: 将项目相关的非代码文档（如设计文档、API规范、FAQ）整合为 LLM 的背景知识，提升评审和生成的准确性。
具体方案:
F-KB-01: 新建知识库
UI: 表单，字段：知识库名称、说明。
F-KB-02: 知识库内容管理
UI: 进入某个知识库后，展示已上传的文档列表。
上传功能: 支持上传文件（.md, .txt, .pdf）。
后台逻辑:
解析与切片: 根据文件类型，解析文本内容，并将其切分为有意义的文本块 (Chunks)。
嵌入 (Embedding): 提示用户选择一个嵌入模型（如 BGE-large, M3E-base, OpenAI text-embedding-3-small 等，可在系统配置中预设）。调用模型将文本块转换为向量。
存储: 将“文本块 + 向量 + 源文件信息”存入一个与该知识库绑定的向量数据库（如 ChromaDB）集合中。
F-KB-03: 知识库的调用: 在后续的流水线中，可以额外选择一个知识库。系统会将用户的输入（如需求、代码片段）在知识库中进行相似度搜索，将最相关的知识片段作为额外的上下文送入 Prompt。
主模块 (Pipelines)
3.1 代码评审流水线 (Code Review Pipeline)
工作流: 生成Diff -> 导入需求 -> 创建评审任务 -> 执行与查看
步骤一: 代码 Diff 拉取 (Generate Code Diff)
UI: 点击“新建代码 Diff”，弹出表单。
表单字段:
下拉选择 代码仓库 (从 2.1 中选择)。
单选框 对比方式:
分支对比 (Branch-to-Branch): 出现两个输入框，原分支 (自动填充默认基准分支)、目标分支。输入框支持远程分支的模糊搜索和自动补全。
提交对比 (Commit-to-Commit): 出现两个输入框，Commit Hash 1、Commit Hash 2。提供一个按钮“查看近期提交”，可以拉取该仓库最近的提交历史（Hash, Author, Message）供用户选择。
后台逻辑: 点击“生成”后，系统在后台执行 git diff 命令，将结果保存为一个 .diff 文件在服务器上，并生成一个唯一的 Diff ID。
产出: 一个可被后续任务引用的 Diff 实例。
步骤二: 需求导入与优化 (Import & Refine Requirement)
UI: 独立的页面或弹窗。
功能:
方式一: 文件上传:
上传 PDF/Word/MD 文件。
下拉选择一个 解析Prompt (从 2.2 中选择，如 pdf_to_requirement_text)。
后台调用 LLM 解析，将结果填充到下方的文本框中。
方式二: 直接输入:
一个大文本框，用户直接粘贴需求文本。
优化迭代: 文本框下方提供一个 优化Prompt 的下拉选择框和一个“执行优化”按钮。用户可以反复选择不同的 Prompt (如“需求澄清”、“提取关键点”) 来迭代优化需求文本，直到满意为止。
产出: 一份优化后的、结构化的 需求文本实例。
步骤三: 新建代码评审任务 (Create Review Task)
UI: 点击“新建评审任务”，弹出表单。
表单字段:
任务名称 (必填)。
下拉选择 代码Diff (从步骤一的产出列表中选择)。
下拉选择 需求文本 (从步骤二的产出列表中选择)。
下拉选择 评审Prompt (从 2.2 中选择，如 code_review_full)。
(可选) 下拉选择 知识库 (从 2.3 中选择)。
逻辑: 点击“保存”后，在数据库中创建一条任务记录，状态为 待执行 (Pending)。
步骤四: 任务执行与查看 (Execute & View Report)
UI: 任务列表页，展示所有评审任务及其状态（待执行, 执行中, 已完成, 失败）。
操作:
每条任务后有“执行”按钮。点击后，任务状态变为 排队中 (Queued)，并被推送到后台任务队列（如 Celery）。
后台 Worker 执行任务（组装 Prompt -> 调用 LLM -> 保存结果）。
任务完成后，状态变为 已完成 (Completed)。
点击“查看详情”，跳转到评审报告页。报告以 Markdown 格式展示 LLM 生成的评审意见。
预留接口: 报告页预留“发送报告到...”的按钮，为未来集成企业微信、钉钉、邮件等通知方式做准备。
3.2 用例生成流水线 (Test Case Generation Pipeline)
工作流: 创建用例生成任务 -> 执行与查看 -> 管理与导出
步骤一: 新建用例生成任务 (Create Case Generation Task)
UI: 点击“新建用例生成任务”，弹出表单。
表单字段:
任务名称 (必填)。
下拉选择 需求文本 (从 3.1 步骤二的产出列表中选择)。
下拉选择 用例生成Prompt (从 2.2 中选择，如 generate_test_cases_from_requirement)。
(可选) 下拉选择 用例模板 (见下方 F-CASE-01)。
逻辑: 保存后，创建一条状态为 待执行 的任务。
步骤二: 任务执行与结果列表 (Execute & View Results)
UI/逻辑: 与代码评审任务的执行流程完全一致。
结果展示: 点击“查看详情”，进入用例结果列表页。此页面以表格形式展示所有生成的用例。
步骤三: 用例管理与导出 (Manage & Export Cases)
F-CASE-01: 用例模板配置 (Case Template Configuration)
背景: 为了让 LLM 生成结构化的、能直接入库的用例，我们需要定义模板。
实现: 在系统配置中，允许管理员定义用例的数据结构，如：{ "用例标题": "string", "前置条件": "string", "步骤": "string", "预期结果": "string", "优先级": "P0/P1/P2" }。用例生成 Prompt 中会指示 LLM 必须按此 JSON 格式返回。
F-CASE-02: 用例列表功能
UI: 表格展示，列与模板字段对应。
功能:
支持对单条用例进行编辑和删除。
支持分页浏览。
提供导出按钮，支持导出为 .md, .xlsx, .xmind 格式。
使用vue3+fastapi进行功能开发，设计后端框架
