from . import SqliteDB as SqlDB

# 查询所有项目信息的函数
def query_all_project():
    # 执行SQL查询语句，获取project表中的所有数据
    # 返回查询结果
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM project")

# 项目详情
def query_project_by_id(project_id):
    return SqlDB.SqliteDB.query_execute("SELECT * FROM project WHERE id = ?", (project_id,))

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

def query_role_model(project_id, role_names):
    if not role_names:
        return  # 如果列表为空，直接返回，避免生成无效的 SQL
    # 动态生成占位符：'?,?,?'
    placeholders = ','.join('?' * len(role_names))

    # 拼接正确的 SQL
    sql = f"SELECT * FROM role_model WHERE project_id = ? AND role_name IN ({placeholders})"

    # 注意：参数必须解包，project_id 和 role_names 中的每个元素都要作为独立参数传入
    params = [project_id] + role_names

    SqlDB.SqliteDB.query_execute_batch(sql, params)

def query_role_relation(project_id, role_a, role_b):
    return SqlDB.SqliteDB.query_execute("SELECT relation FROM role_relation WHERE project_id = ? and role_a_name = ? and role_b_name = ?", (project_id, role_a, role_b))

def remove_old_role_model(project_id, role_names):
    if not role_names:
        return  # 如果列表为空，直接返回，避免生成无效的 SQL
    # 动态生成占位符：'?,?,?'
    placeholders = ','.join('?' * len(role_names))
    print(type(placeholders))
    # 注意：参数必须解包，project_id 和 role_names 中的每个元素都要作为独立参数传入
    params = [project_id] + role_names
    for p in params:
        print(type(p))
    SqlDB.SqliteDB.execute_batch(f"DELETE FROM role_model WHERE project_id = ? and role_name in ({placeholders})", [params])

def insert_role_model(project_id, role_name, role_json):
    SqlDB.SqliteDB.execute("INSERT INTO role_model (project_id, role_name, role_json) VALUES (?, ?, ?)", (project_id, str(role_name), str(role_json)))

def remove_old_role_relation(project_id, role_a, role_b):
    SqlDB.SqliteDB.execute("DELETE FROM role_relation WHERE project_id = ? and role_a_name = ? and role_b_name = ?", (project_id, role_a, role_b))

def insert_role_relation(project_id, role_a, role_b, relation):
    SqlDB.SqliteDB.execute("INSERT INTO role_relation (project_id, role_a_name, role_b_name, relation) VALUES (?, ?, ?, ?)", (project_id, str(role_a), str(role_b), str(relation)))

# 保存新创建的项目信息
def insert_project_info(project):
    title = project['title']
    author = project['author']
    chapter_num = project['chapter_num']
    word_count = project['word_count']
    return SqlDB.SqliteDB.execute("INSERT INTO project (title, author, chapter_num, word_count) VALUES (?, ?, ?, ?)", (title, author, chapter_num, word_count))

# 获取第一位章节信息
def query_wait_polish_chapter(project_id):
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE status in (1, 2, 4) and project_id = ? ORDER BY sort", (project_id,))

# 获取章节通过id
def query_chapter_by_id(chapter_id):
    return SqlDB.SqliteDB.query_execute("SELECT * FROM chapter WHERE id = ?", (chapter_id,))

# 获取前几章内容
def query_before_chapter(project_id, sort, before_num):
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE project_id = ? and sort < ? ORDER BY sort DESC LIMIT ?", (project_id, sort, before_num))

# 获取后几章内容
def query_after_chapter(project_id, sort, after_num):
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE project_id = ? and sort > ? ORDER BY sort DESC LIMIT ?", (project_id, sort, after_num))

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
    # 删除角色信息
    SqlDB.SqliteDB.execute("DELETE FROM role_model WHERE project_id = ?", (project_id,))
    # 删除关系信息
    SqlDB.SqliteDB.execute("DELETE FROM role_relation WHERE project_id = ?", (project_id,))

# 获取项目所有章节列表 并根据sort排序
def query_project_chapter_by_id(project_id):
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE project_id = ? ORDER BY sort", (project_id,))

# 查询全部模型配置信息
def query_all_model():
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM model_info")

# 根据ID获取模型配置信息
def query_model_by_id(model_id):
    return SqlDB.SqliteDB.query_execute("SELECT * FROM model_info WHERE id = ?", (model_id,))

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
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM prompt_info")

# 根据id获取模版提示词项目
def query_prompt_info_by_id(prompt_id):
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM prompt_info WHERE id = ?", (prompt_id,))

# 新增提示词配置
def insert_prompt_conf(name):
    return SqlDB.SqliteDB.execute("INSERT INTO prompt_info (name) VALUES (?)", (name,))

# 查询场景提示词
def query_prompt_template(prompt_id, point_type, prompt_type):
    return SqlDB.SqliteDB.query_execute_batch("SELECT * FROM prompt_rules WHERE prompt_id = ? and point_type = ? and type = ?", (prompt_id,point_type, prompt_type))

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

# 更新章节-角色分析内容
def update_chapter_role(role_text, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET role_content = ?, status = 2, point = 200 WHERE id = ?", (role_text, chapter_id))

# 更新章节-关系分析内容
def update_chapter_relation(relation_text, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET relation_content = ?, point = 300 WHERE id = ?", (relation_text, chapter_id))

# 更新章节-状态
def update_chapter_status(status, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET status = ? WHERE id = ?", (status, chapter_id))

# 更新章节-流程判断
def update_chapter_process(process_content, point, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET process_content = ?, point = ? WHERE id = ?", (process_content, point, chapter_id))

# 更新章节-序号
def update_chapter_sort(sort, project_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET sort = sort + 1 WHERE sort >= ? and project_id = ?", (sort, project_id))

# 新增章节-番外章节
def insert_extra_chapter(chapter, chapter_sort):
    return SqlDB.SqliteDB.execute("INSERT INTO chapter (project_id, title, role_content, relation_content, process_content, type, status, point, sort) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (chapter['project_id'],
                        "番外",
                        chapter['role_content'],
                        chapter['relation_content'],
                        chapter['process_content'],
                        2,
                        1,
                        410,
                        chapter_sort))

# 更新章节-场景分析
def update_chapter_scene(scene_text, point, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET scene_content = ?, point = ? WHERE id = ?", (scene_text, point, chapter_id))

# 更新章节-脉络改写
def update_chapter_framework(framework_content, point, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET framework_content = ?, point = ? WHERE id = ?", (framework_content, point, chapter_id))

# 更新章节-完成润色
def update_chapter_polish(polish_text, chapter_id):
    SqlDB.SqliteDB.execute("UPDATE chapter SET new_len = ?, new_content = ?, status = 3, point = 600 WHERE id = ?", (len(polish_text), polish_text, chapter_id))

# 更新项目-完成数
def update_chapter_success_num(project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET success_num = success_num + 1 WHERE id = ?", (project_id,))

# 获取失败章节数
def count_fail_chapter_num(project_id):
    return SqlDB.SqliteDB.query_execute("SELECT count(*) FROM chapter WHERE status = 4 and project_id = ?", (project_id,))

# 更新项目-失败数
def update_chapter_fail_num(num, project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET fail_num = ? WHERE id = ?", (num, project_id))

# 更新项目-章节数
def update_chapter_all_num(project_id):
    SqlDB.SqliteDB.execute("UPDATE project SET chapter_num = chapter_num + 1, expansion_num = expansion_num + 1 WHERE id = ?", (project_id,))