# AI研发辅助平台 - 数据库设计文档

## 📊 数据库概述

### 技术选型
- **数据库**: PostgreSQL 15+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **迁移工具**: Alembic
- **连接池**: asyncpg + SQLAlchemy异步引擎

### 设计原则
- **规范化**: 遵循第三范式，减少数据冗余
- **性能优化**: 合理使用索引，优化查询性能
- **扩展性**: 支持水平和垂直扩展
- **安全性**: 敏感数据加密存储
- **审计**: 记录数据变更历史

## 🗃️ 数据表设计

### 1. 用户管理

#### users (用户表)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar TEXT,
    department VARCHAR(100),
    position VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'developer', 'tester', 'user')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
```

#### user_sessions (用户会话表)
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_refresh_token_hash ON user_sessions(refresh_token_hash);
```

### 2. AI模型配置

#### ai_model_configs (AI模型配置表)
```sql
CREATE TABLE ai_model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('openai', 'deepseek', 'spark', 'doubao', 'gemini', 'claude')),
    base_url TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_ai_model_configs_user_id ON ai_model_configs(user_id);
CREATE INDEX idx_ai_model_configs_provider ON ai_model_configs(provider);
CREATE INDEX idx_ai_model_configs_is_active ON ai_model_configs(is_active);
CREATE UNIQUE INDEX idx_ai_model_configs_user_default ON ai_model_configs(user_id) WHERE is_default = true;
```

### 3. Prompt模板

#### prompt_templates (Prompt模板表)
```sql
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    identifier VARCHAR(100) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL CHECK (category IN ('requirement', 'code_review', 'test_case', 'general')),
    tags JSONB DEFAULT '[]',
    variables JSONB DEFAULT '[]',
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_prompt_templates_user_id ON prompt_templates(user_id);
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_is_public ON prompt_templates(is_public);
CREATE INDEX idx_prompt_templates_identifier ON prompt_templates(identifier);
CREATE INDEX idx_prompt_templates_tags ON prompt_templates USING GIN(tags);
```

### 4. 需求管理

#### requirement_documents (需求文档表)
```sql
CREATE TABLE requirement_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    original_content TEXT NOT NULL,
    optimized_content TEXT,
    source VARCHAR(20) DEFAULT 'manual' CHECK (source IN ('upload', 'manual')),
    original_filename VARCHAR(255),
    file_path TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    parse_task_id UUID,
    error_message TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_requirement_documents_user_id ON requirement_documents(user_id);
CREATE INDEX idx_requirement_documents_status ON requirement_documents(status);
CREATE INDEX idx_requirement_documents_source ON requirement_documents(source);
CREATE INDEX idx_requirement_documents_created_at ON requirement_documents(created_at);
```

### 5. Git配置

#### git_credentials (Git凭证表)
```sql
CREATE TABLE git_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    git_username VARCHAR(100) NOT NULL,
    git_email VARCHAR(100) NOT NULL,
    access_token_encrypted TEXT NOT NULL,
    provider VARCHAR(20) DEFAULT 'github' CHECK (provider IN ('github', 'gitlab', 'gitee', 'bitbucket')),
    is_default BOOLEAN DEFAULT false,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_git_credentials_user_id ON git_credentials(user_id);
CREATE INDEX idx_git_credentials_provider ON git_credentials(provider);
CREATE UNIQUE INDEX idx_git_credentials_user_default ON git_credentials(user_id) WHERE is_default = true;
```

#### git_repositories (Git仓库表)
```sql
CREATE TABLE git_repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alias VARCHAR(100) NOT NULL,
    repository_url TEXT NOT NULL,
    branch VARCHAR(100) DEFAULT 'main',
    credential_id UUID REFERENCES git_credentials(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(20) DEFAULT 'pending' CHECK (sync_status IN ('pending', 'syncing', 'success', 'failed')),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_git_repositories_user_id ON git_repositories(user_id);
CREATE INDEX idx_git_repositories_credential_id ON git_repositories(credential_id);
CREATE INDEX idx_git_repositories_is_active ON git_repositories(is_active);
```

### 6. 代码差异

#### code_diff_tasks (代码差异任务表)
```sql
CREATE TABLE code_diff_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    repository_id UUID NOT NULL REFERENCES git_repositories(id) ON DELETE CASCADE,
    compare_type VARCHAR(20) NOT NULL CHECK (compare_type IN ('branch', 'commit')),
    source_ref VARCHAR(100) NOT NULL,
    target_ref VARCHAR(100) NOT NULL,
    diff_content TEXT,
    diff_stats JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_code_diff_tasks_user_id ON code_diff_tasks(user_id);
CREATE INDEX idx_code_diff_tasks_repository_id ON code_diff_tasks(repository_id);
CREATE INDEX idx_code_diff_tasks_status ON code_diff_tasks(status);
CREATE INDEX idx_code_diff_tasks_created_at ON code_diff_tasks(created_at);
```

### 7. 流水线任务

#### pipeline_tasks (流水线任务表)
```sql
CREATE TABLE pipeline_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('code_review', 'test_generation', 'requirement_analysis')),
    code_diff_task_id UUID REFERENCES code_diff_tasks(id) ON DELETE SET NULL,
    requirement_document_id UUID REFERENCES requirement_documents(id) ON DELETE SET NULL,
    prompt_template_id UUID REFERENCES prompt_templates(id) ON DELETE SET NULL,
    ai_model_config_id UUID REFERENCES ai_model_configs(id) ON DELETE SET NULL,
    knowledge_base_id UUID,
    config JSONB DEFAULT '{}',
    result JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    celery_task_id UUID,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_pipeline_tasks_user_id ON pipeline_tasks(user_id);
CREATE INDEX idx_pipeline_tasks_type ON pipeline_tasks(type);
CREATE INDEX idx_pipeline_tasks_status ON pipeline_tasks(status);
CREATE INDEX idx_pipeline_tasks_code_diff_task_id ON pipeline_tasks(code_diff_task_id);
CREATE INDEX idx_pipeline_tasks_requirement_document_id ON pipeline_tasks(requirement_document_id);
CREATE INDEX idx_pipeline_tasks_created_at ON pipeline_tasks(created_at);
```

### 8. AI对话

#### ai_conversations (AI对话表)
```sql
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    ai_model_config_id UUID NOT NULL REFERENCES ai_model_configs(id) ON DELETE CASCADE,
    total_tokens INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_ai_model_config_id ON ai_conversations(ai_model_config_id);
CREATE INDEX idx_ai_conversations_last_message_at ON ai_conversations(last_message_at);
```

#### ai_messages (AI消息表)
```sql
CREATE TABLE ai_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens INTEGER,
    prompt_template_id UUID REFERENCES prompt_templates(id) ON DELETE SET NULL,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_ai_messages_conversation_id ON ai_messages(conversation_id);
CREATE INDEX idx_ai_messages_role ON ai_messages(role);
CREATE INDEX idx_ai_messages_created_at ON ai_messages(created_at);
```

### 9. 知识库

#### knowledge_bases (知识库表)
```sql
CREATE TABLE knowledge_bases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    collection_name VARCHAR(100) UNIQUE NOT NULL,
    document_count INTEGER DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_knowledge_bases_user_id ON knowledge_bases(user_id);
CREATE INDEX idx_knowledge_bases_is_public ON knowledge_bases(is_public);
CREATE INDEX idx_knowledge_bases_collection_name ON knowledge_bases(collection_name);
```

#### knowledge_documents (知识文档表)
```sql
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100),
    content_hash VARCHAR(64),
    chunk_count INTEGER DEFAULT 0,
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_knowledge_documents_knowledge_base_id ON knowledge_documents(knowledge_base_id);
CREATE INDEX idx_knowledge_documents_user_id ON knowledge_documents(user_id);
CREATE INDEX idx_knowledge_documents_processing_status ON knowledge_documents(processing_status);
CREATE INDEX idx_knowledge_documents_content_hash ON knowledge_documents(content_hash);
```

### 10. 系统日志

#### system_logs (系统日志表)
```sql
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(10) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    request_id UUID,
    ip_address INET,
    user_agent TEXT,
    extra_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_system_logs_module ON system_logs(module);

-- 分区表（按月分区）
CREATE TABLE system_logs_y2024m01 PARTITION OF system_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## 🔧 数据库优化

### 1. 索引策略
```sql
-- 复合索引
CREATE INDEX idx_pipeline_tasks_user_status ON pipeline_tasks(user_id, status);
CREATE INDEX idx_ai_messages_conversation_created ON ai_messages(conversation_id, created_at);

-- 部分索引
CREATE INDEX idx_users_active_username ON users(username) WHERE is_active = true;
CREATE INDEX idx_ai_model_configs_active ON ai_model_configs(user_id) WHERE is_active = true;

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
CREATE INDEX idx_prompt_templates_search ON prompt_templates USING gin(to_tsvector('english', name || ' ' || description));
```

### 2. 分区策略
```sql
-- 按时间分区日志表
CREATE TABLE system_logs (
    id UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 其他字段...
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE system_logs_y2024m01 PARTITION OF system_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE system_logs_y2024m02 PARTITION OF system_logs
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 3. 性能优化
```sql
-- 启用统计信息自动收集
ALTER TABLE users SET (autovacuum_analyze_scale_factor = 0.05);
ALTER TABLE ai_messages SET (autovacuum_analyze_scale_factor = 0.02);

-- 设置表的填充因子
ALTER TABLE users SET (fillfactor = 90);
ALTER TABLE ai_conversations SET (fillfactor = 85);

-- 创建物化视图
CREATE MATERIALIZED VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT ac.id) as conversation_count,
    COUNT(DISTINCT pt.id) as template_count,
    COUNT(DISTINCT rd.id) as requirement_count,
    SUM(ac.total_tokens) as total_tokens_used
FROM users u
LEFT JOIN ai_conversations ac ON u.id = ac.user_id AND ac.is_deleted = false
LEFT JOIN prompt_templates pt ON u.id = pt.user_id AND pt.is_deleted = false
LEFT JOIN requirement_documents rd ON u.id = rd.user_id AND rd.is_deleted = false
WHERE u.is_deleted = false
GROUP BY u.id, u.username;

-- 创建唯一索引
CREATE UNIQUE INDEX idx_user_stats_id ON user_stats(id);

-- 定期刷新物化视图
CREATE OR REPLACE FUNCTION refresh_user_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;
END;
$$ LANGUAGE plpgsql;
```

## 🔒 安全设计

### 1. 数据加密
```sql
-- 启用行级安全
ALTER TABLE ai_model_configs ENABLE ROW LEVEL SECURITY;

-- 创建安全策略
CREATE POLICY user_ai_models_policy ON ai_model_configs
FOR ALL TO authenticated_users
USING (user_id = current_setting('app.current_user_id')::uuid);

-- 敏感字段加密存储
-- api_key_encrypted 字段使用应用层加密
-- access_token_encrypted 字段使用应用层加密
```

### 2. 审计日志
```sql
-- 创建审计触发器
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, new_data, user_id, created_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), 
                current_setting('app.current_user_id', true)::uuid, 
                CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data, new_data, user_id, created_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW),
                current_setting('app.current_user_id', true)::uuid,
                CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data, user_id, created_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD),
                current_setting('app.current_user_id', true)::uuid,
                CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 为重要表添加审计触发器
CREATE TRIGGER audit_users_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_ai_model_configs_trigger
AFTER INSERT OR UPDATE OR DELETE ON ai_model_configs
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

## 📊 监控和维护

### 1. 性能监控
```sql
-- 查询慢查询
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 2. 数据清理
```sql
-- 定期清理软删除的数据
CREATE OR REPLACE FUNCTION cleanup_soft_deleted_data()
RETURNS void AS $$
BEGIN
    -- 清理30天前软删除的数据
    DELETE FROM users WHERE is_deleted = true AND updated_at < NOW() - INTERVAL '30 days';
    DELETE FROM ai_model_configs WHERE is_deleted = true AND updated_at < NOW() - INTERVAL '30 days';
    DELETE FROM prompt_templates WHERE is_deleted = true AND updated_at < NOW() - INTERVAL '30 days';
    -- 其他表...
END;
$$ LANGUAGE plpgsql;

-- 定期清理过期的会话
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;
```

---

**文档版本**: v1.0  
**最后更新**: 2024年12月  
**负责人**: 数据库团队
