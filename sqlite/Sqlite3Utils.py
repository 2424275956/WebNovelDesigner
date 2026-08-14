from . import SqliteDB as SqlDB

# 查询所有项目信息的函数
def query_all_project():
    # 执行SQL查询语句，获取project表中的所有数据
    tables = SqlDB.SqliteDB.execute("SELECT * FROM project")
    # 返回查询结果
    return tables.fetchall()

# 项目详情
def query_project_by_id(project_id):
    tables = SqlDB.SqliteDB.execute("SELECT * FROM project WHERE id = ?", (project_id,))
    return tables.fetchone()

def edit_project_prompt_id(prompt_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET prompt_id = ? WHERE id = ?", (prompt_id, project_id))

def edit_project_role_model_id(role_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET role_model_id = ? WHERE id = ?", (role_model_id, project_id))

def edit_project_relation_model_id(relation_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET relation_model_id = ? WHERE id = ?", (relation_model_id, project_id))

def edit_polish_before_num(num, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET polish_before_num = ? WHERE id = ?", (num, project_id))

def edit_polish_after_num(num, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET polish_after_num = ? WHERE id = ?", (num, project_id))

def edit_project_scene_model_id(scene_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET scene_model_id = ? WHERE id = ?", (scene_model_id, project_id))

def edit_project_process_model_id(process_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET process_model_id = ? WHERE id = ?", (process_model_id, project_id))

def edit_project_extra_scene_model_id(extra_scene_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET extra_scene_model_id = ? WHERE id = ?", (extra_scene_model_id, project_id))

def edit_project_framework_model_id(framework_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET framework_model_id = ? WHERE id = ?", (framework_model_id, project_id))

def edit_project_extra_framework_model_id(extra_framework_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET extra_framework_model_id = ? WHERE id = ?", (extra_framework_model_id, project_id))

def edit_project_polish_model_id(polish_model_id, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET polish_model_id = ? WHERE id = ?", (polish_model_id, project_id))

# 保存新创建的项目信息
def insert_project_info(project):
    title = project['title']
    author = project['author']
    chapter_num = project['chapter_num']
    word_count = project['word_count']
    cursor = SqlDB.SqliteDB.execute("INSERT INTO project (title, author, chapter_num, word_count) VALUES (?, ?, ?, ?)", (title, author, chapter_num, word_count))
    return cursor.lastrowid

# 获取第一位章节信息
def query_wait_polish_chapter(project_id):
    chapter_list = SqlDB.SqliteDB.execute("SELECT * FROM chapter WHERE status in (1, 2, 4) and project_id = ? ORDER BY sort LIMIT 1", (project_id,))
    return chapter_list.fetchall()

# 保存创建的章节信息
def insert_project_chapter(project_id, chapters):
    sql = "INSERT INTO chapter (project_id, title, old_len, old_content, sort) VALUES (?, ?, ?, ?, ?)"
    data = []
    # 根据数据数量处理
    for chapter in chapters:
        data.append((project_id, chapter['title'], chapter['old_len'], chapter['old_content'], chapter['sort']))
    SqlDB.SqliteDB.execute_batch(sql, data)

# 删除项目信息
def remove_novel_info(project_id):
    # 删除章节信息
    SqlDB.SqliteDB.execute("DELETE FROM chapter WHERE project_id = ?", (project_id,))
    # 删除项目信息
    SqlDB.SqliteDB.execute("DELETE FROM project WHERE id = ?", (project_id,))

# 获取项目所有章节列表 并根据sort排序
def query_project_chapter_by_id(project_id):
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM chapter WHERE project_id = ? ORDER BY sort", (project_id,))
    return data_list.fetchall()

# 查询全部模型配置信息
def query_all_model():
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM model_info")
    return data_list.fetchall()

# 根据ID获取模型配置信息
def query_model_by_id(model_id):
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM model_info WHERE id = ?", (model_id,))
    return data_list.fetchone()

# 保存模型配置信息
def insert_model_conf(req_json):
    SqlDB.SqliteDB.execute("INSERT INTO model_info (name, type, api_key, url, model_id, temperature, top_p, max_token, time_out) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (req_json['name'], req_json['type'], req_json['api_key'], req_json['url'], req_json['model_id'],
                            req_json['temperature'] if req_json['temperature'] is not None else 0.7,
                            req_json['top_p'] if req_json['top_p'] is not None else 0.9,
                            req_json['max_token'] if req_json['max_token'] is not None else 32768,
                            req_json['time_out'] if req_json['time_out'] is not None else 300))

# 更新模型配置信息
def modify_model_conf(req_json):
    SqlDB.SqliteDB.execute("UPDATE model_info SET name = ?, type = ?, api_key = ?, url = ?, model_id = ?, temperature = ?, top_p = ?, max_token = ?, time_out = ? WHERE id = ?",
                           (req_json['name'], req_json['type'], req_json['api_key'], req_json['url'], req_json['model_id'],
                            req_json['temperature'] if req_json['temperature'] is not None else 0.7,
                            req_json['top_p'] if req_json['top_p'] is not None else 0.9,
                            req_json['max_token'] if req_json['max_token'] is not None else 32768,
                            req_json['time_out'] if req_json['time_out'] is not None else 300,
                            req_json['id']))

# 删除模型配置
def remove_model_conf(conf_id):
    SqlDB.SqliteDB.execute("DELETE FROM model_info WHERE id = ?", (conf_id,))

# 查询全部提示词
def query_all_prompt():
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM prompt_info")
    return data_list.fetchall()

# 根据id获取模版提示词项目
def query_prompt_info_by_id(prompt_id):
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM prompt_info WHERE id = ?", (prompt_id,))
    return data_list.fetchall()

# 新增提示词配置
def insert_prompt_conf(name):
    cursor = SqlDB.SqliteDB.execute("INSERT INTO prompt_info (name) VALUES (?)", (name,))
    return cursor.lastrowid

# 查询场景提示词
def query_prompt_template(prompt_id, point_type, prompt_type):
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM prompt_rules WHERE prompt_id = ? and point_type = ? and type = ?", (prompt_id,point_type, prompt_type))
    return data_list.fetchall()

# 保存提示词信息
def save_prompt_info(req_json):
    prompt_id = req_json['id']
    # 清除提示词配置
    SqlDB.SqliteDB.execute("DELETE FROM prompt_rules WHERE prompt_id = ?", (prompt_id,))
    """角色分析"""
    save_prompt(prompt_id, req_json['role_system'], req_json['role_user'], 1)
    """关系分析"""
    save_prompt(prompt_id, req_json['relation_system'], req_json['relation_user'], 2)
    """流程控制"""
    save_prompt(prompt_id, req_json['process_system'], req_json['process_user'], 6)
    """改写-场景分析"""
    save_prompt(prompt_id, req_json['scene_system'], req_json['scene_user'], 3)
    # 场景提示词
    scene_data = []
    scene_list = req_json['scene']
    for scene in scene_list:
        scene_data.append((prompt_id, scene['scene_name'], scene['scene_identify'], scene['scene_rules'], 3, 3))
    SqlDB.SqliteDB.execute_batch("INSERT INTO prompt_rules (prompt_id, scene_name, scene_identify, context, point_type, type) VALUES (?, ?, ?, ?, ?, ?)"
                                 , scene_data)
    """改写-脉络改写"""
    save_prompt(prompt_id, req_json['framework_system'], req_json['framework_user'], 4)
    """番外-场景分析"""
    save_prompt(prompt_id, req_json['extra_scene_system'], req_json['extra_scene_user'], 7)
    # 场景提示词
    extra_scene_data = []
    extra_scene_list = req_json['extra_scene']
    for extra_scene in extra_scene_list:
        extra_scene_data.append((prompt_id, extra_scene['scene_name'], extra_scene['scene_identify'], extra_scene['scene_rules'], 7, 3))
    SqlDB.SqliteDB.execute_batch("INSERT INTO prompt_rules (prompt_id, scene_name, scene_identify, context, point_type, type) VALUES (?, ?, ?, ?, ?, ?)"
                                 , extra_scene_data)
    """番外-脉络生成"""
    save_prompt(prompt_id, req_json['extra_framework_system'], req_json['extra_framework_user'], 8)
    """结果润色"""
    save_prompt(prompt_id, req_json['polish_system'], req_json['polish_user'], 5)

# 保存提示词规则
def save_prompt(prompt_id, system, user, point_type):
    # 保存系统提示词
    SqlDB.SqliteDB.execute("INSERT INTO prompt_rules (prompt_id, context, point_type, type) VALUES (?, ?, ?, ?)", (prompt_id, system, point_type, 1))
    # 用户提示词
    SqlDB.SqliteDB.execute("INSERT INTO prompt_rules (prompt_id, context, point_type, type) VALUES (?, ?, ?, ?)", (prompt_id, user, point_type, 2))

# 导入提示词信息
def import_prompt_template(req_json):
    # 获取名称
    prompt_id = insert_prompt_conf(req_json['name'])
    req_json['id'] = prompt_id
    save_prompt_info(req_json)

# 删除提示词模版
def remove_prompt(prompt_id):
    # 删除提示词规则
    SqlDB.SqliteDB.execute("DELETE FROM prompt_rules WHERE prompt_id = ?", (prompt_id,))
    # 提示词信息
    SqlDB.SqliteDB.execute("DELETE FROM prompt_info WHERE id = ?", (prompt_id,))