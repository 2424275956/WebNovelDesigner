from . import SqliteDB as SqlDB

# 查询所有项目信息的函数
def query_all_project():
    # 执行SQL查询语句，获取project表中的所有数据
    tables = SqlDB.SqliteDB.execute("SELECT * FROM project")
    # 返回查询结果
    return tables.fetchall()

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

# 新增提示词配置
def insert_prompt_conf(name):
    cursor = SqlDB.SqliteDB.execute("INSERT INTO prompt_info (name) VALUES (?)", (name,))
    return cursor.lastrowid

# 查询全部场景提示词
def query_all_scene_prompt():
    data_list = SqlDB.SqliteDB.execute("SELECT * FROM prompt_rules WHERE type = 3")
    return data_list.fetchall()