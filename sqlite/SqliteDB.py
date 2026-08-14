import sqlite3
import atexit
import os
from pathlib import Path

class SqliteDB:
    # 连接默认为空
    _conn = None

    # 获取SQLite连接
    @classmethod  # 使用类方法装饰器，表示这是一个类方法，可以通过类名直接调用
    def get_conn(cls, db_path="sqlite/db/app.db"):  # 定义一个获取数据库连接的类方法，默认数据库路径为"sqlite/db/app.db"
        # 检查文件是否存在  # 单行注释：检查指定路径的数据库文件是否存在
        db_exists = os.path.exists(db_path)

        # 未连接数据库时执行  # 单行注释：当数据库连接对象为None时，即未连接数据库时执行以下代码
        if cls._conn is None:  # 判断类的_conn属性是否为None
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # 创建数据库文件所需的目录结构，如果已存在则不创建
            cls._conn = sqlite3.connect(db_path, timeout=10.0)  # 连接数据库，设置超时时间为10秒
            cls._conn.row_factory = sqlite3.Row
            atexit.register(cls.close)

        # 表结构校验  # 单行注释：对数据库表结构进行校验
        cls._db_table_init(db_exists)
        return cls._conn

    @classmethod
    def _db_table_init(cls, db_exists):
        # 项目表校验
        if not db_exists or cls._is_database_empty("project"):
            cursor = cls._conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS project (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 项目ID
                    title TEXT NOT NULL,                            -- 小说名称
                    author TEXT NOT NULL,                           -- 作者
                    chapter_num INTEGER NOT NULL,                   -- 全部章节数
                    success_num INTEGER NOT NULL DEFAULT 0,         -- 已完成章节数
                    fail_num INTEGER NOT NULL DEFAULT 0,            -- 失败章节数
                    expansion_num INTEGER NOT NULL DEFAULT 0,       -- 新增扩写章节数
                    prompt_id INTEGER DEFAULT NULL,                 -- 提示词模版ID
                    role_model_id INTEGER DEFAULT NULL,             -- 角色分析模型ID
                    relation_model_id INTEGER DEFAULT NULL,         -- 角色关系模型ID
                    process_model_id INTEGER DEFAULT NULL,          -- 流程控制模型ID
                    extra_model_id INTEGER DEFAULT NULL,            -- 番外扩写模型ID
                    scene_model_id INTEGER DEFAULT NULL,            -- 场景规则模型ID
                    framework_model_id INTEGER DEFAULT NULL,        -- 脉络改写模型ID
                    polish_model_id INTEGER DEFAULT NULL,           -- 结果润色模型ID
                    polish_before_num INTEGER DEFAULT NULL,         -- 附带前n章节
                    polish_after_num INTEGER DEFAULT NULL,          -- 附带后n章节
                    word_count REAL NOT NULL,                       -- 字数（单位万）
                    status INTEGER NOT NULL DEFAULT 1               -- 状态（1：未开始，2：进行中，3：已完成）
                );
            """)

        # 章节目录
        if not db_exists or cls._is_database_empty("chapter"):
            cursor = cls._conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS chapter (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 章节ID
                    project_id INTEGER NOT NULL,                    -- 所属项目ID
                    title TEXT NOT NULL,                            -- 章节名称
                    old_len INTEGER DEFAULT 0,                      -- 原始章节字数
                    old_content TEXT DEFAULT NULL,                  -- 原始章节内容
                    role_content TEXT DEFAULT NULL,                 -- 角色分析内容
                    relation_content TEXT DEFAULT NULL,             -- 角色关系内容
                    process_content TEXT DEFAULT NULL,              -- 流程控制内容
                    scene_content TEXT DEFAULT NULL,                -- 场景规则内容
                    framework_content TEXT DEFAULT NULL,            -- 框架脉络内容
                    new_len INTEGER DEFAULT 0,                      -- 新章节字数
                    new_content TEXT DEFAULT NULL,                  -- 新章节内容
                    type INTEGER NOT NULL DEFAULT 1,                -- 章节类型（1：润色改写，2：内容扩写）
                    status INTEGER NOT NULL DEFAULT 1,              -- 状态（1：未开始，2：进行中，3：已完成，4：已失败）
                    point INTEGER NOT NULL DEFAULT 10,               -- 节点（100：分析角色模型，200：分析角色关系，300：流程控制判断，400：改写-匹配场景规则，401：改写-改写发展脉络，410：番外-匹配场景规则，411：番外-生成发展脉络，500：润色输出内容，600：已完成）
                    sort INTEGER NOT NULL DEFAULT 0                 -- 排序
                );
                CREATE INDEX IF NOT EXISTS idx_project_id ON chapter(project_id);
            """)

        # 模型配置表
        if not db_exists or cls._is_database_empty("model_info"):
            cursor = cls._conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS model_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 模型配置ID
                    name TEXT NOT NULL,                             -- 模型名称
                    type INTEGER NOT NULL DEFAULT 1,                -- 配置类型（1：网络模型，2：本地Ollama模型，3：本地oMLX模型）
                    api_key TEXT DEFAULT NULL,                      -- 模型API KEY
                    url TEXT NOT NULL,                              -- 模型地址
                    model_id TEXT NOT NULL,                         -- 模型ID
                    temperature REAL NOT NULL DEFAULT '0.7',        -- 模型温度
                    top_p REAL NOT NULL DEFAULT '0.9',              -- Top-P选择
                    max_token INTEGER NOT NULL DEFAULT 32768,       -- token长度
                    time_out INTEGER NOT NULL DEFAULT 300           -- 超时时间
                );
            """)

        # 提示词配置
        if not db_exists or cls._is_database_empty("prompt_info"):
            cursor = cls._conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS prompt_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 提示词配置ID
                    name TEXT NOT NULL                              -- 提示词配置名称
                );
            """)

        # 提示词规则配置
        if not db_exists or cls._is_database_empty("prompt_rules"):
            cursor = cls._conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS prompt_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 提示词规则ID
                    prompt_id INTEGER NOT NULL,                     -- 提示词配置ID
                    scene_name TEXT DEFAULT NULL,                   -- 场景提示词名称
                    scene_identify TEXT DEFAULT NULL,               -- 场景提示词识别规则
                    context TEXT DEFAULT NULL,                      -- 提示词规则    
                    point_type INTEGER NOT NULL DEFAULT 1,          -- 节点类型（1：角色分析，2：关系分析，3：改写-场景分析，4：改写-脉络改写，5：结果润色，6：流程控制，7：番外-场景分析，8：番外-脉络生成）
                    type INTEGER NOT NULL DEFAULT 1                 -- 提示词类型（1：系统提示词，2：用户提示词，3：场景提示词）
                );
                CREATE INDEX IF NOT EXISTS idx_prompt_id ON prompt_rules(prompt_id);
            """)



    @classmethod
    def _is_database_empty(cls, table):
        # 获取链接
        cursor = cls._conn.cursor()

        # 获取链接
        cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type = 'table' 
                AND name = ?
        """, (table,))
        # 如果没有用户表，认为数据库为空
        return len(cursor.fetchall()) == 0


    # 关闭SQLite连接
    @classmethod
    def close(cls):
        if cls._conn:
            cls._conn.close()
            cls._conn = None
            print("数据库已关闭")

    # 执行SQLite语句
    @classmethod
    def execute(cls, sql, params=None):
        conn = cls.get_conn()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor

    # 执行SQLite语句
    @classmethod
    def execute_batch(cls, sql, params=None):
        conn = cls.get_conn()
        cursor = conn.cursor()
        if params:
            cursor.executemany(sql, params)
        else:
            cursor.executemany(sql)
        conn.commit()
        return cursor