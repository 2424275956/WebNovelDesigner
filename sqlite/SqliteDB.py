import os
import sys
from contextlib import closing
from pathlib import Path
import sqlite_vss
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass
import sqlite3

class SqliteDB:

    # 获取SQLite连接
    @classmethod  # 使用类方法装饰器，表示这是一个类方法，可以通过类名直接调用
    def get_conn(cls, db_path="resources/db/app.db"):  # 定义一个获取数据库连接的类方法，默认数据库路径为"resources/db/app.db"
        # 检查文件是否存在  # 单行注释：检查指定路径的数据库文件是否存在
        db_exists = os.path.exists(db_path)

        # 未连接数据库时执行  # 单行注释：当数据库连接对象为None时，即未连接数据库时执行以下代码
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)  # 创建数据库文件所需的目录结构，如果已存在则不创建
        _conn = sqlite3.connect(db_path, timeout=10.0)  # 连接数据库，设置超时时间为10秒
        _conn.row_factory = sqlite3.Row

        # 开启向量数据库扩展
        # 开启扩展加载权限
        _conn.enable_load_extension(True)
        ## 1. 首先加载底层的 vector0 扩展
        _conn.load_extension(sqlite_vss.vector_loadable_path())
        ## 2. 然后再加载上层的 vss0 扩展
        _conn.load_extension(sqlite_vss.vss_loadable_path())
        ## 加载 sqlite-vss 扩展
        _conn.load_extension(sqlite_vss.vss_loadable_path())
        ## 关闭扩展加载权限（出于安全考虑）
        _conn.enable_load_extension(False)

        # 表结构校验  # 单行注释：对数据库表结构进行校验
        cls._db_table_init(db_exists, _conn)
        return _conn

    @classmethod
    def _db_table_init(cls, db_exists, _conn):
        # 项目表校验
        if not db_exists or cls._is_database_empty("project", _conn):
            with closing(_conn.cursor()) as cursor:
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS project (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 项目ID
                        title TEXT NOT NULL,                            -- 小说名称
                        author TEXT NOT NULL,                           -- 作者
                        prompt_id INTEGER DEFAULT NULL,                 -- 提示词模版ID
                        role_model_id INTEGER DEFAULT NULL,             -- 角色分析模型ID
                        process_model_id INTEGER DEFAULT NULL,          -- 流程控制模型ID
                        scene_model_id INTEGER DEFAULT NULL,            -- 场景规则模型ID
                        framework_model_id INTEGER DEFAULT NULL,        -- 脉络改写模型ID
                        extra_scene_model_id INTEGER DEFAULT NULL,      -- 番外扩写场景分析模型ID
                        extra_framework_model_id INTEGER DEFAULT NULL,  -- 番外扩写脉络生成模型ID
                        polish_model_id INTEGER DEFAULT NULL,           -- 结果润色模型ID
                        relation_model_id INTEGER DEFAULT NULL,         -- 角色关系模型ID
                        polish_before_num INTEGER DEFAULT 5,            -- 附带前n章节
                        polish_after_num INTEGER DEFAULT 1,             -- 附带后n章节
                        word_count REAL NOT NULL,                       -- 字数（单位万）
                        status INTEGER NOT NULL DEFAULT 1               -- 状态（1：未开始，2：进行中，3：已完成）
                    );
                """)

        # 章节目录
        if not db_exists or cls._is_database_empty("chapter", _conn):
            with closing(_conn.cursor()) as cursor:
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS chapter (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 章节ID
                        project_id INTEGER NOT NULL,                    -- 所属项目ID
                        title TEXT NOT NULL,                            -- 章节名称
                        original_resume TEXT DEFAULT NULL,              -- 原文剧情简述
                        polish_resume TEXT DEFAULT NULL,                -- 结果剧情简述
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
                        point INTEGER NOT NULL DEFAULT 100,             -- 节点（100：分析角色模型，200：流程控制判断，300：改写-匹配场景规则，310：改写-改写发展脉络，400：番外-匹配场景规则，410：番外-生成发展脉络，500：润色输出内容，600：角色关系更新，700：已完成）
                        sort INTEGER NOT NULL DEFAULT 0                 -- 排序
                    );
                    CREATE INDEX IF NOT EXISTS idx_project_id ON chapter(project_id);
                """)

        # 模型配置表
        if not db_exists or cls._is_database_empty("model_info", _conn):
            with closing(_conn.cursor()) as cursor:
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
        if not db_exists or cls._is_database_empty("prompt_info", _conn):
            with closing(_conn.cursor()) as cursor:
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS prompt_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 提示词配置ID
                        name TEXT NOT NULL                              -- 提示词配置名称
                    );
                """)

        # 提示词规则配置
        if not db_exists or cls._is_database_empty("prompt_rules", _conn):
            with closing(_conn.cursor()) as cursor:
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

        # 角色模型
        if not db_exists or cls._is_database_empty("role_model", _conn):
            with closing(_conn.cursor()) as cursor:
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS role_model (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 角色模型ID
                        project_id INTEGER NOT NULL,                    -- 项目ID
                        role_name TEXT NOT NULL,                        -- 角色名称
                        protagonist_family INTEGER NOT NULL DEFAULT 2,  -- 是否主角女性亲友(1-是 2-否)
                        role_json TEXT DEFAULT NULL                     -- 角色信息
                    );
                    CREATE INDEX IF NOT EXISTS idx_project_id ON role_model(project_id);
                    CREATE INDEX IF NOT EXISTS idx_role_name ON role_model(role_name);
                """)

        # 角色关联
        if not db_exists or cls._is_database_empty("role_relation", _conn):
            with closing(_conn.cursor()) as cursor:
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS role_relation (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,           -- 角色关联ID
                        project_id INTEGER NOT NULL,                    -- 项目ID
                        role_a_name TEXT NOT NULL,                      -- 角色A名称
                        role_b_name TEXT NOT NULL,                      -- 角色B名称
                        relation TEXT DEFAULT NULL                      -- 角色关联关系
                    );
                    CREATE INDEX IF NOT EXISTS idx_project_id ON role_relation(project_id);
                    CREATE INDEX IF NOT EXISTS idx_role_name ON role_relation(role_a_name, role_b_name);
                """)



    @classmethod
    def _is_database_empty(cls, table, _conn):
        # 获取链接
        with closing(_conn.cursor()) as cursor:
            # 获取链接
            cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type = 'table' 
                    AND name = ?
            """, (table,))
            # 如果没有用户表，认为数据库为空
            return len(cursor.fetchall()) == 0


    # 执行SQLite语句
    @classmethod
    def execute(cls, sql, params=None):
        with cls.get_conn() as conn:
            with closing(conn.cursor()) as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                conn.commit()
                return cursor.lastrowid

    # 执行SQLite语句
    @classmethod
    def query_execute(cls, sql, params=None):
        with cls.get_conn() as conn:
            with closing(conn.cursor()) as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return cursor.fetchone()

            # 执行SQLite语句
    @classmethod
    def execute_batch(cls, sql, params=None):
        with cls.get_conn() as conn:
            with closing(conn.cursor()) as cursor:
                if params:
                    cursor.executemany(sql, params)
                else:
                    cursor.executemany(sql)
                conn.commit()

    # 执行SQLite语句
    @classmethod
    def query_execute_batch(cls, sql, params=None):
        with cls.get_conn() as conn:
            with closing(conn.cursor()) as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                return cursor.fetchall()