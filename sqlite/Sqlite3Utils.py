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

# 保存新创建的项目信息
def insert_project_info(project):
    title = project['title']
    author = project['author']
    chapter_num = project['chapter_num']
    word_count = project['word_count']
    cursor = SqlDB.SqliteDB.execute("INSERT INTO project (title, author, chapter_num, word_count) VALUES (?, ?, ?, ?)", (title, author, chapter_num, word_count))
    return cursor.lastrowid

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
    # 保存系统提示词
    system = req_json['system']
    SqlDB.SqliteDB.execute("INSERT INTO prompt_rules (prompt_id, context, type) VALUES (?, ?, ?)", (prompt_id, system, 1))
    # 用户提示词
    user = req_json['user']
    SqlDB.SqliteDB.execute("INSERT INTO prompt_rules (prompt_id, context, type) VALUES (?, ?, ?)", (prompt_id, user, 2))
    # 场景提示词
    scene_data = []
    scene_list = req_json['scene']
    for scene in scene_list:
        scene_data.append((prompt_id, scene['name'], scene['identify_text'], scene['rules_text'], 3))
    SqlDB.SqliteDB.execute_batch("INSERT INTO prompt_rules (prompt_id, scene_name, scene_identify, context, type) VALUES (?, ?, ?, ?, ?)"
                                 , scene_data)

# 导入提示词信息
def import_prompt_template(req_json):
    # 获取名称
    prompt_id = insert_prompt_conf(req_json['name'])
    save_req_json = {
        "id": prompt_id,
        "system": req_json['system'],
        "user": req_json['user'],
        "scene": req_json['scene']
    }
    save_prompt_info(save_req_json)

# 删除提示词模版
def remove_prompt(prompt_id):
    # 删除提示词规则
    SqlDB.SqliteDB.execute("DELETE FROM prompt_rules WHERE prompt_id = ?", (prompt_id,))
    # 提示词信息
    SqlDB.SqliteDB.execute("DELETE FROM prompt_info WHERE id = ?", (prompt_id,))