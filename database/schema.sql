-- ============================================================
-- AI育种项目申报书与预算智能生成系统 - PostgreSQL DDL
-- 数据库架构专家设计
-- ============================================================

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "ltree";

-- ============================================================
-- 1. 用户与权限 (RBAC)
-- ============================================================

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    status SMALLINT DEFAULT 1 CHECK (status IN (0, 1, 2)),  -- 0:禁用, 1:正常, 2:锁定
    last_login_at TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 角色表
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_code VARCHAR(50) UNIQUE NOT NULL,  -- reporter, reviewer, admin, super_admin
    role_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    perm_code VARCHAR(100) UNIQUE NOT NULL,
    perm_name VARCHAR(100) NOT NULL,
    module VARCHAR(50),  -- 对应功能模块
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户角色关联表
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    project_id UUID,  -- 特定项目的数据级权限
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id, project_id)
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    perm_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, perm_id)
);

-- ============================================================
-- 2. 项目管理
-- ============================================================

-- 项目表
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_name VARCHAR(255) NOT NULL,
    project_code VARCHAR(50) UNIQUE,
    description TEXT,
    construction_period_months INTEGER,  -- 建设周期（月）
    location VARCHAR(255),  -- 建设地点
    owner_unit VARCHAR(255),  -- 建设单位
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2, 3, 4)),  -- 0:草稿, 1:填报中, 2:审核中, 3:已完成, 4:已归档
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 项目成员表
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    member_role VARCHAR(50) DEFAULT 'member',  -- leader, member
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, user_id)
);

-- ============================================================
-- 3. 物种分类（支持动态扩展）
-- ============================================================

-- 物种分类表
CREATE TABLE species (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    species_code VARCHAR(50) UNIQUE NOT NULL,
    species_name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES species(id),  -- 自关联，支持多级分类
    category VARCHAR(50) NOT NULL,  -- crop(作物), horticulture(园艺), poultry(禽类), mushroom(食用菌), microorganism(微生物)等
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. 大纲树结构（动态配置）
-- ============================================================

-- 大纲节点表（使用ltree实现树形结构）
CREATE TABLE outline_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES outline_nodes(id),  -- 父节点ID，支持递归
    node_code VARCHAR(50) NOT NULL,  -- 如 "1.1.1", "2.3.4.1" 等
    node_title VARCHAR(500) NOT NULL,
    node_level INTEGER NOT NULL CHECK (node_level >= 1 AND node_level <= 10),  -- 1-10章
    path LTREE,  -- ltree路径，如 "1.1.1"
    species_ids UUID[],  -- 关联的物种分类ID数组
    content TEXT,  -- 手动填写的内容（不是AI生成的）
    is_leaf BOOLEAN DEFAULT FALSE,  -- 是否叶子节点（可编辑生成）
    sort_order INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,  -- 是否锁定（不允许编辑）
    is_expanded BOOLEAN DEFAULT TRUE,  -- 是否展开
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(project_id, node_code)
);

-- 大纲模板（预设模板，可复制到项目）
CREATE TABLE outline_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_name VARCHAR(100) NOT NULL,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    template_data JSONB NOT NULL,  -- 模板JSON结构
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. 数据采集系统
-- ============================================================

-- 场景表
CREATE TABLE scenes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    species_id UUID REFERENCES species(id),  -- 主要关联的物种
    scene_name VARCHAR(255) NOT NULL,
    scene_description TEXT,  -- 场景描述（对文本生成很重要）
    research_output_type VARCHAR(100),  -- 科研产出类型：论文、专利、品种等
    data_output_type VARCHAR(100),  -- 数据产出类型
    data_total_tb DECIMAL(10, 2),  -- 数据总量(TB)
    file_size_description VARCHAR(500),  -- 文件大小描述
    data_output_description TEXT,  -- 数据产出说明
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 设备表
CREATE TABLE equipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    scene_ids UUID[],  -- 关联场景ID数组
    equipment_name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(50) NOT NULL,  -- storage(存储), virtual(虚拟), computing(计算), sensor(传感), robot(机器人)等
    key_level SMALLINT DEFAULT 1 CHECK (key_level BETWEEN 1 AND 5),  -- 关键星级 1-5
    procurement_method VARCHAR(50),  -- 采购方式：公开招标、单一来源等
    usage_plan TEXT,  -- 使用计划情况
    unit_price DECIMAL(15, 2),  -- 单价（元）
    total_price DECIMAL(15, 2) NOT NULL,  -- 总价（元）
    supplier VARCHAR(255),  -- 供应商
    is_imported BOOLEAN DEFAULT FALSE,  -- 是否进口
    need_quote_seal BOOLEAN DEFAULT FALSE,  -- 是否需要报价盖章
    origin_country VARCHAR(50),  -- 国产或进口
    supplier_1 VARCHAR(255),
    supplier_2 VARCHAR(255),
    supplier_3 VARCHAR(255),
    final_supplier VARCHAR(255),
    plan_usage_value DECIMAL(10, 2),  -- 计划使用数值
    plan_usage_unit VARCHAR(20),  -- 计划使用单位
    plan_usage_description TEXT,  -- 计划使用说明
    necessity_description TEXT,  -- 必要性与匹配性说明
    purchase_time DATE,  -- 计划购置时间
    commissioning_time DATE,  -- 计划投用时间
    data_output_type VARCHAR(100),  -- 数据输出类型
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 数据集表
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    data_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(50) NOT NULL,  -- 图像、文本、基因组、表型等
    other_data_type VARCHAR(100),  -- 其他数据类型
    data_total_tb DECIMAL(10, 2),  -- 数据总量(TB)
    access_permission VARCHAR(50) DEFAULT 'public',  -- 访问权限
    is_shared_with_lab BOOLEAN DEFAULT FALSE,  -- 是否与实验室共享
    source_equipment_ids UUID[],  -- 来源设备ID数组
    scene_ids UUID[],  -- 关联场景ID数组
    data_description TEXT,  -- 数据描述
    processing_fee DECIMAL(15, 2) DEFAULT 0,  -- 数据处理费（万元）
    compute_cycle_value INTEGER,  -- 计算周期数值
    compute_cycle_unit VARCHAR(20),  -- 计算周期单位：小时、天、月等
    compute_cycle_total_days INTEGER,  -- 总计（天）
    source_cycle_months INTEGER,  -- 来源周期（月）
    cycle_data_gb DECIMAL(10, 2),  -- 周期数据量(GB)
    need_purchase BOOLEAN DEFAULT FALSE,  -- 是否需要购买
    purchase_fee DECIMAL(15, 2) DEFAULT 0,  -- 购买费用（万元）
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- AI模型表
CREATE TABLE ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    model_name VARCHAR(255) NOT NULL,
    model_description TEXT,
    model_type VARCHAR(50) NOT NULL,  -- deep_learning, machine_learning, llm, foundation_model等
    model_scale VARCHAR(50),  -- 模型规模
    parameter_count VARCHAR(50),  -- 参数量：如 7B, 70B
    function_type VARCHAR(50),  -- 功能类型：training(训练), inference(推理)
    related_data_ids UUID[],  -- 关联数据ID数组
    scene_ids UUID[],  -- 关联场景ID数组
    estimated_total_fee DECIMAL(15, 2) NOT NULL,  -- 预计总费用（万元）
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 研发项目表
CREATE TABLE rd_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    rd_name VARCHAR(255) NOT NULL,  -- 项目名称
    rd_direction VARCHAR(100),  -- 研发方向
    rd_content TEXT,  -- 研发内容
    expected_output TEXT,  -- 预期成果
    estimated_fee DECIMAL(15, 2) NOT NULL,  -- 预估费用（万元）
    scene_ids UUID[],  -- 关联场景ID数组
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- ============================================================
-- 6. DocAgent 相关
-- ============================================================

-- 引用类型表
CREATE TABLE reference_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_code VARCHAR(50) UNIQUE NOT NULL,  -- core(核心引用), background(参考背景), budget(预算关联)
    type_name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 节点引用表（场景、设备、数据、AI模型与大纲节点的关联）
CREATE TABLE node_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    node_id UUID NOT NULL REFERENCES outline_nodes(id) ON DELETE CASCADE,
    ref_type_id UUID NOT NULL REFERENCES reference_types(id),
    ref_entity_type VARCHAR(50) NOT NULL,  -- scene, equipment, dataset, ai_model, rd_project
    ref_entity_id UUID NOT NULL,  -- 关联的实体ID
    reference_note TEXT,  -- 引用备注
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(node_id, ref_entity_type, ref_entity_id, ref_type_id)
);

-- 生成记录表
CREATE TABLE doc_generations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    node_id UUID NOT NULL REFERENCES outline_nodes(id) ON DELETE CASCADE,
    generation_content TEXT NOT NULL,  -- AI生成的内容
    prompt_template_id UUID,  -- 使用的Prompt模板ID
    prompt_version VARCHAR(50),  -- Prompt版本
    input_tokens INTEGER,  -- 输入token数
    output_tokens INTEGER,  -- 输出token数
    model_used VARCHAR(100),  -- 使用的模型
    generation_source VARCHAR(50) DEFAULT 'ai',  -- ai(AI生成), manual(手动填写), hybrid(混合)
    is_current_version BOOLEAN DEFAULT TRUE,  -- 是否当前版本
    parent_generation_id UUID REFERENCES doc_generations(id),  -- 父版本（用于版本溯源）
    entity_snapshot JSONB,  -- 实体快照（血缘溯源）
    generation_time_ms INTEGER,  -- 生成耗时（毫秒）
    cost_usd DECIMAL(10, 6),  -- 成本（美元）
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 生成历史版本表
CREATE TABLE generation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    generation_id UUID NOT NULL REFERENCES doc_generations(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    entity_snapshot JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(generation_id, version_number)
);

-- ============================================================
-- 7. 预算相关
-- ============================================================

-- 预算汇总表
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    budget_type VARCHAR(50) NOT NULL,  -- total(总预算), hardware(硬件), software(软件), data(数据), ai_model(AI模型), rd(研发)
    budget_amount DECIMAL(18, 2) NOT NULL,  -- 预算金额
    currency VARCHAR(10) DEFAULT 'CNY',
    fiscal_year INTEGER,  -- 财年
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2)),  -- 0:草稿, 1:已提交, 2:已审核
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预算明细表（可追溯）
CREATE TABLE budget_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_id UUID NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL,  -- equipment, dataset, ai_model, rd_project, custom_software, cloud_service等
    item_name VARCHAR(255) NOT NULL,
    item_id UUID,  -- 关联的实体ID（如设备ID、AI模型ID等）
    entity_type VARCHAR(50),  -- equipment, dataset, ai_model, rd_project
    quantity INTEGER DEFAULT 1,
    unit VARCHAR(20),  -- 单位
    unit_price DECIMAL(15, 2),  -- 单价
    total_price DECIMAL(18, 2) NOT NULL,  -- 总价
    budget_category VARCHAR(50),  -- 预算科目
    necessity_description TEXT,  -- 必要性与匹配性说明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 设备预算汇总（去重展示用）
CREATE TABLE equipment_budget_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    equipment_id UUID REFERENCES equipments(id),
    equipment_name VARCHAR(255) NOT NULL,
    equipment_type VARCHAR(50),
    unit_price DECIMAL(15, 2),
    total_price DECIMAL(15, 2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    supplier VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 8. Prompt 模板
-- ============================================================

-- Prompt模板表
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_code VARCHAR(100) UNIQUE NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    template_category VARCHAR(50),  -- outline(大纲生成), optimize(内容优化), translate(翻译)等
    template_content TEXT NOT NULL,  -- Prompt模板内容
    variables JSONB,  -- 变量定义
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prompt模板版本历史
CREATE TABLE prompt_template_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES prompt_templates(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    template_content TEXT NOT NULL,
    change_log TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(template_id, version)
);

-- ============================================================
-- 9. 大模型调用日志
-- ============================================================

-- LLM调用日志表
CREATE TABLE llm_call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    node_id UUID REFERENCES outline_nodes(id),
    model_name VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    latency_ms INTEGER,
    cost_usd DECIMAL(10, 6),
    status VARCHAR(20) DEFAULT 'success',  -- success, error, timeout
    error_message TEXT,
    request_data JSONB,
    response_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 10. 系统配置与字典
-- ============================================================

-- 字典表（用于动态扩展）
CREATE TABLE dictionaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dict_type VARCHAR(50) NOT NULL,  -- equipment_type, data_type, model_type等
    dict_code VARCHAR(50) NOT NULL,
    dict_label VARCHAR(100) NOT NULL,
    dict_value VARCHAR(500),
    parent_id UUID REFERENCES dictionaries(id),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(dict_type, dict_code)
);

-- 系统配置表
CREATE TABLE system_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(50),  -- string, number, boolean, json
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 11. 审计日志
-- ============================================================

-- 操作审计日志表
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- create, update, delete, generate, approve等
    entity_type VARCHAR(50) NOT NULL,  -- project, scene, equipment等
    entity_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 索引创建
-- ============================================================

-- 用户相关索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_email ON users(email);

-- 角色相关索引
CREATE INDEX idx_roles_code ON roles(role_code);

-- 项目相关索引
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_by ON projects(created_by);

-- 物种相关索引
CREATE INDEX idx_species_category ON species(category);
CREATE INDEX idx_species_parent ON species(parent_id);

-- 大纲节点索引
CREATE INDEX idx_outline_project ON outline_nodes(project_id);
CREATE INDEX idx_outline_parent ON outline_nodes(parent_id);
CREATE INDEX idx_outline_level ON outline_nodes(node_level);
CREATE INDEX idx_outline_path ON outline_nodes(path);
CREATE INDEX idx_outline_leaf ON outline_nodes(is_leaf);

-- 场景索引
CREATE INDEX idx_scenes_project ON scenes(project_id);
CREATE INDEX idx_scenes_species ON scenes(species_id);

-- 设备索引
CREATE INDEX idx_equipments_project ON equipments(project_id);
CREATE INDEX idx_equipments_type ON equipments(equipment_type);

-- 数据集索引
CREATE INDEX idx_datasets_project ON datasets(project_id);
CREATE INDEX idx_datasets_type ON datasets(data_type);

-- AI模型索引
CREATE INDEX idx_ai_models_project ON ai_models(project_id);
CREATE INDEX idx_ai_models_type ON ai_models(model_type);

-- 研发项目索引
CREATE INDEX idx_rd_projects_project ON rd_projects(project_id);

-- 节点引用索引
CREATE INDEX idx_node_refs_node ON node_references(node_id);
CREATE INDEX idx_node_refs_entity ON node_references(ref_entity_type, ref_entity_id);

-- 生成记录索引
CREATE INDEX idx_generations_node ON doc_generations(node_id);
CREATE INDEX idx_generations_current ON doc_generations(is_current_version);

-- 预算索引
CREATE INDEX idx_budgets_project ON budgets(project_id);
CREATE INDEX idx_budget_items_budget ON budget_items(budget_id);

-- LLM日志索引
CREATE INDEX idx_llm_logs_project ON llm_call_logs(project_id);
CREATE INDEX idx_llm_logs_node ON llm_call_logs(node_id);
CREATE INDEX idx_llm_logs_created ON llm_call_logs(created_at);

-- 字典索引
CREATE INDEX idx_dicts_type ON dictionaries(dict_type);

-- 审计日志索引
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ============================================================
-- 初始化数据
-- ============================================================

-- 初始化角色数据
INSERT INTO roles (role_code, role_name, description, is_system) VALUES
('reporter', '填报人', '可填写和编辑项目数据', TRUE),
('reviewer', '审核员', '可审核项目内容', TRUE),
('admin', '管理员', '可管理系统配置和用户', TRUE),
('super_admin', '超级管理员', '拥有所有权限', TRUE);

-- 初始化引用类型
INSERT INTO reference_types (type_code, type_name, description, sort_order) VALUES
('core', '核心引用', '作为核心内容引用的实体', 1),
('background', '参考背景', '作为背景参考的实体', 2),
('budget', '预算关联', '与预算相关的实体', 3);

-- 初始化物种分类（示例）
INSERT INTO species (species_code, species_name, parent_id, category, description, sort_order) VALUES
('crop', '作物', NULL, 'crop', '粮食作物、经济作物等', 1),
('horticulture', '园艺', NULL, 'horticulture', '蔬菜、水果、花卉等', 2),
('poultry', '禽类', NULL, 'poultry', '鸡、鸭、鹅等', 3),
('mushroom', '食用菌', NULL, 'mushroom', '香菇、平菇、木耳等', 4),
('microorganism', '微生物', NULL, 'microorganism', '微生物发酵、益生菌等', 5);

-- 作物子类
INSERT INTO species (species_code, species_name, parent_id, category, description, sort_order)
SELECT sub.code, sub.name, p.id, 'crop', sub.description, sub.sort_val
FROM (VALUES
    ('grain', '粮食作物', '水稻、小麦、玉米等', 1),
    ('economic', '经济作物', '棉花、油料、糖料等', 2),
    ('vegetable', '蔬菜作物', '叶菜类、根茎类等', 3),
    ('fruit', '果树', '热带水果、温带水果等', 4),
    ('forage', '饲料作物', '牧草、青贮玉米等', 5)
) AS sub(code, name, description, sort_val)
JOIN (SELECT id FROM species WHERE species_code = 'crop') AS p(id) ON TRUE;

-- 初始化系统配置
INSERT INTO system_configs (config_key, config_value, config_type, description, is_system) VALUES
('default_llm_model', 'gpt-4o', 'string', '默认使用的大模型', TRUE),
('max_token_limit', '128000', 'number', '最大token限制', TRUE),
('default_currency', 'CNY', 'string', '默认货币', TRUE),
('system_name', 'AI育种项目申报书与预算智能生成系统', 'string', '系统名称', TRUE);

-- 初始化字典数据
INSERT INTO dictionaries (dict_type, dict_code, dict_label, dict_value, sort_order) VALUES
-- 设备类型
('equipment_type', 'storage', '存储设备', '存储设备', 1),
('equipment_type', 'computing', '计算设备', '计算设备', 2),
('equipment_type', 'virtual', '虚拟资源', '虚拟资源', 3),
('equipment_type', 'sensor', '传感器', '传感器', 4),
('equipment_type', 'robot', '机器人', '机器人', 5),
('equipment_type', 'network', '网络设备', '网络设备', 6),
('equipment_type', 'lab', '实验室设备', '实验室设备', 7),
-- 数据类型
('data_type', 'image', '图像数据', '图像数据', 1),
('data_type', 'text', '文本数据', '文本数据', 2),
('data_type', 'genomic', '基因组数据', '基因组数据', 3),
('data_type', 'phenotypic', '表型数据', '表型数据', 4),
('data_type', 'environmental', '环境数据', '环境数据', 5),
('data_type', 'spectral', '光谱数据', '光谱数据', 6),
-- AI模型类型
('model_type', 'deep_learning', '深度学习模型', '深度学习模型', 1),
('model_type', 'machine_learning', '机器学习模型', '机器学习模型', 2),
('model_type', 'llm', '大语言模型', '大语言模型', 3),
('model_type', 'foundation_model', '基础模型', '基础模型', 4),
('model_type', 'multi_modal', '多模态模型', '多模态模型', 5);

-- ============================================================
-- 视图创建（常用查询视图）
-- ============================================================

-- 项目预算汇总视图
CREATE VIEW v_project_budget_summary AS
SELECT
    p.id AS project_id,
    p.project_name,
    COUNT(DISTINCT s.id) AS scene_count,
    COUNT(DISTINCT e.id) AS equipment_count,
    COUNT(DISTINCT d.id) AS dataset_count,
    COUNT(DISTINCT m.id) AS ai_model_count,
    COUNT(DISTINCT r.id) AS rd_project_count,
    COALESCE(SUM(e.total_price), 0) AS equipment_budget,
    COALESCE(SUM(d.processing_fee + d.purchase_fee), 0) AS data_budget,
    COALESCE(SUM(m.estimated_total_fee), 0) AS ai_model_budget,
    COALESCE(SUM(r.estimated_fee), 0) AS rd_budget,
    COALESCE(SUM(e.total_price), 0) + COALESCE(SUM(d.processing_fee + d.purchase_fee), 0) +
    COALESCE(SUM(m.estimated_total_fee), 0) + COALESCE(SUM(r.estimated_fee), 0) AS total_budget
FROM projects p
LEFT JOIN scenes s ON s.project_id = p.id AND s.deleted_at IS NULL
LEFT JOIN equipments e ON e.project_id = p.id AND e.deleted_at IS NULL
LEFT JOIN datasets d ON d.project_id = p.id AND d.deleted_at IS NULL
LEFT JOIN ai_models m ON m.project_id = p.id AND m.deleted_at IS NULL
LEFT JOIN rd_projects r ON r.project_id = p.id AND r.deleted_at IS NULL
WHERE p.deleted_at IS NULL
GROUP BY p.id, p.project_name;

-- 节点引用统计视图
CREATE VIEW v_node_reference_stats AS
SELECT
    o.id AS node_id,
    o.node_code,
    o.node_title,
    o.node_level,
    COUNT(CASE WHEN nr.ref_entity_type = 'scene' THEN 1 END) AS scene_ref_count,
    COUNT(CASE WHEN nr.ref_entity_type = 'equipment' THEN 1 END) AS equipment_ref_count,
    COUNT(CASE WHEN nr.ref_entity_type = 'dataset' THEN 1 END) AS dataset_ref_count,
    COUNT(CASE WHEN nr.ref_entity_type = 'ai_model' THEN 1 END) AS ai_model_ref_count,
    COUNT(CASE WHEN nr.ref_entity_type = 'rd_project' THEN 1 END) AS rd_project_ref_count
FROM outline_nodes o
LEFT JOIN node_references nr ON nr.node_id = o.id AND nr.is_active = TRUE
WHERE o.deleted_at IS NULL
GROUP BY o.id, o.node_code, o.node_title, o.node_level;

-- ============================================================
-- 函数创建
-- ============================================================

-- 获取大纲节点完整路径的函数
CREATE OR REPLACE FUNCTION get_outline_node_path(node_uuid UUID)
RETURNS TEXT AS $$
DECLARE
    path_text TEXT := '';
    current_node RECORD;
BEGIN
    LOOP
        SELECT id, parent_id, node_code, node_title
        INTO current_node
        FROM outline_nodes
        WHERE id = node_uuid;

        IF current_node IS NULL THEN
            EXIT;
        END IF;

        path_text := current_node.node_code || ' ' || current_node.node_title || COALESCE(' > ' || path_text, '');

        IF current_node.parent_id IS NULL THEN
            EXIT;
        END IF;

        node_uuid := current_node.parent_id;
    END LOOP;

    RETURN path_text;
END;
$$ LANGUAGE plpgsql;

-- 递归查询子节点的函数
CREATE OR REPLACE FUNCTION get_child_nodes(parent_uuid UUID)
RETURNS TABLE(id UUID, node_code VARCHAR(50), node_title VARCHAR(500), node_level INTEGER, depth INT) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE node_tree AS (
        SELECT id, node_code, node_title, node_level, 0 AS depth
        FROM outline_nodes
        WHERE parent_id = parent_uuid AND deleted_at IS NULL

        UNION ALL

        SELECT o.id, o.node_code, o.node_title, o.node_level, nt.depth + 1
        FROM outline_nodes o
        INNER JOIN node_tree nt ON o.parent_id = nt.id
        WHERE o.deleted_at IS NULL
    )
    SELECT node_tree.id, node_tree.node_code, node_tree.node_title, node_tree.node_level, node_tree.depth
    FROM node_tree;
END;
$$ LANGUAGE plpgsql;

-- 更新预算汇总的触发器函数
CREATE OR REPLACE FUNCTION update_budget_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- 设备预算汇总更新
    DELETE FROM equipment_budget_summary WHERE project_id = NEW.project_id;

    INSERT INTO equipment_budget_summary (project_id, equipment_id, equipment_name, equipment_type, unit_price, total_price, quantity)
    SELECT
        e.project_id,
        e.id,
        e.equipment_name,
        e.equipment_type,
        e.unit_price,
        e.total_price,
        1
    FROM equipments e
    WHERE e.project_id = NEW.project_id AND e.deleted_at IS NULL;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trg_update_budget_summary
AFTER INSERT OR UPDATE OR DELETE ON equipments
FOR EACH ROW EXECUTE FUNCTION update_budget_summary();

-- ============================================================
-- 注释说明
-- ============================================================

COMMENT ON TABLE users IS '用户表';
COMMENT ON TABLE roles IS '角色表';
COMMENT ON TABLE permissions IS '权限表';
COMMENT ON TABLE user_roles IS '用户角色关联表';
COMMENT ON TABLE role_permissions IS '角色权限关联表';
COMMENT ON TABLE projects IS '项目表';
COMMENT ON TABLE project_members IS '项目成员表';
COMMENT ON TABLE species IS '物种分类表（支持动态扩展）';
COMMENT ON TABLE outline_nodes IS '大纲节点表（使用ltree实现树形结构）';
COMMENT ON TABLE scenes IS '场景表';
COMMENT ON TABLE equipments IS '设备表';
COMMENT ON TABLE datasets IS '数据集表';
COMMENT ON TABLE ai_models IS 'AI模型表';
COMMENT ON TABLE rd_projects IS '研发项目表';
COMMENT ON TABLE node_references IS '节点引用表';
COMMENT ON TABLE doc_generations IS '生成记录表';
COMMENT ON TABLE generation_history IS '生成历史版本表';
COMMENT ON TABLE budgets IS '预算汇总表';
COMMENT ON TABLE budget_items IS '预算明细表（可追溯）';
COMMENT ON TABLE prompt_templates IS 'Prompt模板表';
COMMENT ON TABLE llm_call_logs IS 'LLM调用日志表';
COMMENT ON TABLE dictionaries IS '字典表（用于动态扩展）';
COMMENT ON TABLE audit_logs IS '操作审计日志表';

-- ============================================================
-- DDL 完成
-- ============================================================
