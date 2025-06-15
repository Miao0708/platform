
### **一、 技术选型与架构总览**

1.  **后端框架: FastAPI**
    *   **优势**:
        *   **高性能**: 基于 Starlette 和 Pydantic，拥有接近 NodeJS 和 Go 的性能。
        *   **异步支持**: 天然支持 `async/await`，非常适合处理 I/O 密集型任务，如调用外部 LLM API、Git 操作、数据库读写。
        *   **开发效率**: 自动生成交互式 API 文档 (Swagger UI / ReDoc)，极大方便前后端联调。
        *   **类型提示**: 强制使用 Python 类型提示，结合 Pydantic 进行数据验证，代码更健壮、错误更少。

2.  **数据库 ORM: SQLModel**
    *   **优势**: 由 FastAPI 作者创建，完美结合了 SQLAlchemy 的强大功能和 Pydantic 的数据验证。可以用一套代码同时定义数据库模型和 API 数据模式，减少代码冗余。

3.  **数据库**: PostgreSQL
    *   **优势**: 功能强大，性能稳定，支持 JSONB 类型，非常适合存储用例模板 `schema` 或 LLM 返回的非结构化/半结构化数据。

4.  **后台任务队列: Celery + Redis**
    *   **优势**:
        *   **Celery**: 成熟、稳定、功能丰富的分布式任务队列，是处理耗时任务（如执行 LLM 调用、`git diff`）的最佳选择。
        *   **Redis**: 作为 Celery 的 Broker (消息中间件) 和 Result Backend (结果存储)，速度极快且配置简单。

5.  **安全**:
    *   **认证**: 使用 JWT (JSON Web Tokens) 进行用户认证。
    *   **加密**: 使用 `cryptography` 库的 Fernet 对称加密算法来存储 Git Token 等敏感信息。密钥必须通过环境变量加载，绝不硬编码。

6.  **向量数据库**: ChromaDB
    *   **优势**: 开源，易于上手和部署，与 Python 生态结合紧密，非常适合作为 RAG 功能的起点。

### **二、 后端项目结构**

采用分层架构，确保职责分离、易于维护。

```
ai-dev-platform/
├── app/
│   ├── api/                  # API 层 (Routers)
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── git_config.py         # Git 配置相关 API
│   │       │   ├── prompt_templates.py   # Prompt 模板管理 API
│   │       │   ├── knowledge_base.py     # 知识库管理 API
│   │       │   ├── code_review.py        # 代码评审流水线 API
│   │       │   └── test_case.py          # 用例生成流水线 API
│   │       └── deps.py             # FastAPI 依赖项 (如获取当前用户)
│   ├── core/                   # 核心功能与配置
│   │   ├── config.py           # 应用配置 (从环境变量加载)
│   │   ├── security.py         # 加密、密码哈希、JWT 相关
│   │   ├── llm_client.py       # 封装对不同 LLM API 的调用
│   │   ├── vector_store.py     # 封装对 ChromaDB 的操作
│   │   ├── git_utils.py        # 封装 Git 命令的工具函数
│   │   └── tasks.py            # Celery 任务定义
│   ├── crud/                   # 数据访问层 (Create, Read, Update, Delete)
│   │   ├── base.py             # CRUD 基类
│   │   ├── crud_git.py
│   │   ├── crud_prompt.py
│   │   ├── crud_kb.py
│   │   └── crud_pipeline.py    # 管理任务、Diff、需求文本等
│   ├── models/                 # 数据库模型 (SQLModel)
│   │   ├── git.py
│   │   ├── prompt.py
│   │   ├── knowledge_base.py
│   │   └── pipeline.py
│   ├── schemas/                # API 数据模式 (Pydantic)
│   │   ├── git.py
│   │   ├── prompt.py
│   │   ├── knowledge_base.py
│   │   ├── pipeline.py
│   │   └── common.py           # 通用 Schema
│   ├── services/               # 业务逻辑层
│   │   ├── prompt_service.py     # 处理 Prompt 链式调用等复杂逻辑
│   │   └── rag_service.py        # 处理文件解析、切片、嵌入
│   └── main.py                 # FastAPI 应用入口
├── celery_worker.py          # Celery Worker 启动脚本
├── requirements.txt
└── .env.example              # 环境变量示例文件
```

### **三、 核心功能实现思路**

#### **3.1 基础配置模块 (Configuration Center)**

*   **F-GIT-01: 全局凭证管理**
    *   **`models/git.py`**: 定义 `GlobalGitCredential` 模型，其中 `token` 字段为 `String` 类型，用于存储**加密后**的令牌。
    *   **`core/security.py`**: 实现 `encrypt(plain_text: str) -> str` 和 `decrypt(encrypted_text: str) -> str` 函数。
    *   **`crud/crud_git.py`**:
        *   `create`: 在存入数据库前，调用 `security.encrypt()`。
        *   `get`: 获取时，数据保持加密状态。
    *   **`api/v1/endpoints/git_config.py`**:
        *   `POST /git/credentials`: 接收明文 token，调用 `crud.create`（内部加密）。
        *   `POST /git/credentials/test`:
            1.  从数据库获取加密的 token。
            2.  在内存中调用 `security.decrypt()` 解密。
            3.  调用 `core/git_utils.py` 中的函数，如 `test_connection(url, username, token)`，该函数使用 `subprocess` 执行 `git ls-remote`。
            4.  **绝不**将解密后的 token 返回给前端或记入日志。

*   **F-PRMT-02: Prompt 链式调用 ("闭环"功能)**
    *   **`services/prompt_service.py`**: 这是实现此功能的关键。
    ```python
    # in services/prompt_service.py
    import re
    from app.core import llm_client
    from app.crud import crud_prompt

    async def resolve_prompt_content(db, content: str, variables: dict) -> str:
        # 正则匹配 {{GENERATE_FROM:identifier}}
        pattern = re.compile(r"\{\{GENERATE_FROM:(\w+)\}\}")

        while match := pattern.search(content):
            identifier = match.group(1)
            # 1. 查找子 Prompt
            sub_prompt_template = crud_prompt.get_by_identifier(db, identifier=identifier)
            if not sub_prompt_template:
                # 处理错误：子 Prompt 不存在
                raise ValueError(f"Prompt with identifier '{identifier}' not found.")

            # 2. (递归)解析并执行子 Prompt
            # 注意：这里简化为子 Prompt 不再包含变量，如果需要，需传递相关变量
            resolved_sub_prompt = await resolve_prompt_content(db, sub_prompt_template.content, {})
            sub_prompt_output = await llm_client.generate(prompt=resolved_sub_prompt)

            # 3. 替换占位符
            content = content.replace(match.group(0), sub_prompt_output)

        # 4. 最后替换常规变量 {{var}}
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))

        return content
    ```
    *   这个 `resolve_prompt_content` 函数将在后台任务中被调用，用于组装最终发给 LLM 的完整 Prompt。

*   **F-KB-02: 知识库内容管理 (RAG)**
    *   **`services/rag_service.py`**:
        *   `process_and_embed_document(file, kb_id, embedding_model_name)`:
            1.  **解析**: 根据文件后缀（.pdf, .md, .txt）选择不同的解析器（如 `pypdf`, `unstructured`）。
            2.  **切片**: 使用 `langchain` 或 `llama-index` 的 `RecursiveCharacterTextSplitter` 等工具将文本切块 (Chunks)。
            3.  **嵌入**: 调用 `llm_client` 中封装的嵌入模型 API，将 Chunks 转换为向量。
            4.  **存储**: 调用 `core/vector_store.py` 中的函数，将 (文本块, 向量, metadata) 存入与 `kb_id` 关联的 ChromaDB collection 中。
    *   **`core/vector_store.py`**:
        *   封装与 ChromaDB 的交互，提供 `add_documents` 和 `search` 等接口。

#### **3.2 流水线模块 (Pipelines)**

流水线的核心是**解耦**和**异步化**。

*   **数据模型 (`models/pipeline.py`)**:
    *   `CodeDiff`: 存储 Diff 信息，包括 `repo_id`, `base_ref`, `head_ref`, `diff_file_path`, `status`。
    *   `RequirementText`: 存储需求文本，包括 `original_content`, `refined_content`。
    *   `PipelineTask`: 核心模型，记录一次执行。字段包括 `name`, `type` ('CODE_REVIEW' or 'TEST_CASE'), `status` ('PENDING', 'QUEUED', 'RUNNING', 'COMPLETED', 'FAILED'), `code_diff_id` (FK), `requirement_text_id` (FK), `prompt_template_id` (FK), `knowledge_base_id` (FK), `result` (JSONB 或 Text 类型)。

*   **工作流实现 (以代码评审为例)**:
    1.  **步骤一 (生成 Diff)**:
        *   `POST /api/v1/code-review/diffs`: 前端提交仓库 ID 和分支/commit 信息。
        *   **API 后端**: 创建一个 `CodeDiff` 记录，状态为 `GENERATING`。调用 `generate_diff_task.delay(diff_id)` 启动一个 Celery 任务。立即返回 `diff_id` 给前端。
        *   **Celery 任务 `generate_diff_task`**:
            *   在后台执行 `git diff`，将输出保存到服务器的特定路径。
            *   更新 `CodeDiff` 记录，填入 `diff_file_path` 并将状态改为 `COMPLETED`。

    2.  **步骤二 (导入需求)**: 类似，可以同步或异步处理。

    3.  **步骤三 (新建评审任务)**:
        *   `POST /api/v1/code-review/tasks`: 前端提交任务名称和已生成的 Diff ID、需求 ID、Prompt ID 等。
        *   **API 后端**: 在 `PipelineTask` 表中创建一条记录，状态为 `PENDING`。返回 `task_id`。

    4.  **步骤四 (执行与查看)**:
        *   `POST /api/v1/tasks/{task_id}/execute`: 用户点击“执行”。
        *   **API 后端**:
            *   将 `PipelineTask` 状态更新为 `QUEUED`。
            *   调用 `run_code_review_task.delay(task_id)` 启动核心 Celery 任务。
            *   返回 `202 Accepted`。
        *   **Celery 任务 `run_code_review_task`**: 这是业务逻辑的核心。
            a. 从数据库获取 `task` 及其关联的所有数据（Diff, 需求, Prompt, KB）。
            b. 更新任务状态为 `RUNNING`。
            c. **组装 Prompt**:
                i. 读取 Diff 文件内容。
                ii. 读取需求文本。
                iii. **RAG (如果需要)**: 调用 `rag_service.search(query=diff_content, kb_id=...)` 获取相关知识。
                iv. **Prompt 链式调用**: 调用 `prompt_service.resolve_prompt_content()`，传入所有变量（`code_diff`, `requirement_text`, `knowledge_context` 等）。
            d. **调用 LLM**: `llm_output = llm_client.generate(final_prompt)`。
            e. **保存结果**: 将 `llm_output` 保存到 `PipelineTask` 的 `result` 字段。
            f. **更新状态**: 将任务状态更新为 `COMPLETED`（或 `FAILED` 并记录错误信息）。
        *   **前端轮询**: 前端可以通过 `GET /api/v1/tasks/{task_id}` 定时轮询任务状态，直到状态变为 `COMPLETED` 或 `FAILED`，然后获取并展示结果。

*   **F-CASE-01: 用例模板配置**
    *   **`models/pipeline.py`**: 新增 `TestCaseTemplate` 模型，包含 `name` (String) 和 `schema` (JSONB) 字段。
    *   **`api/v1/endpoints/test_case.py`**: 提供对 `TestCaseTemplate` 的 CRUD 接口，仅限管理员访问。
    *   **用例生成 Prompt**: 在 Prompt 内容中，明确指示 LLM 使用 JSON 格式，并将模板的 `schema` 作为上下文注入。
        *   `... You MUST respond with a JSON array where each object strictly follows this JSON Schema: {{case_template_schema}}`
    *   **结果解析**: Celery 任务在收到 LLM 的输出后，尝试 `json.loads()` 解析，并可以根据 `schema` 进行验证，然后将结构化数据存入专门的 `TestCases` 表中。

---

### **四、 API 端点设计 (示例)**

**Git 配置 (`/api/v1/git`)**
*   `POST /credentials`: 新建全局凭证
*   `PUT /credentials/{id}`: 更新凭证
*   `POST /credentials/test`: 测试连接
*   `GET /repositories`: 获取仓库列表
*   `POST /repositories`: 添加仓库
*   `PUT /repositories/{id}`: 修改仓库
*   `DELETE /repositories/{id}`: 删除仓库

**Prompt 模板 (`/api/v1/prompt-templates`)**
*   `GET /`: 获取 Prompt 列表
*   `POST /`: 创建新 Prompt
*   `GET /{id}`: 获取 Prompt 详情
*   `PUT /{id}`: 更新 Prompt
*   `DELETE /{id}`: 删除 Prompt

**流水线任务 (`/api/v1/tasks`)**
*   `GET /`: 获取所有任务列表（支持按类型、状态过滤）
*   `GET /{task_id}`: 获取单个任务详情及其结果
*   `POST /{task_id}/execute`: 触发任务执行

**代码评审 (`/api/v1/code-review`)**
*   `POST /diffs`: 创建代码 Diff 实例
*   `GET /diffs`: 获取 Diff 列表
*   `POST /requirements`: 创建需求文本实例
*   `POST /tasks`: 创建代码评审任务

**用例生成 (`/api/v1/test-case`)**
*   `POST /tasks`: 创建用例生成任务
*   `GET /tasks/{task_id}/cases`: 获取任务生成的用例列表 (分页)
*   `PUT /cases/{case_id}`: 编辑单条用例
*   `DELETE /cases/{case_id}`: 删除单条用例
*   `GET /tasks/{task_id}/export`: 导出用例 (带 `format=xlsx` 等查询参数)