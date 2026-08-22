from sqlite.SqliteDB import SqliteDB

# 查询全部提示词
def query_all_prompt():
    return SqliteDB.query_execute_batch("SELECT * FROM prompt_info")

# 根据id获取模版提示词项目
def query_prompt_info_by_id(prompt_id):
    return SqliteDB.query_execute_batch("SELECT * FROM prompt_info WHERE id = ?", (prompt_id,))

# 新增提示词配置
def insert_prompt_conf(name):
    return SqliteDB.execute("INSERT INTO prompt_info (name) VALUES (?)", (name,))

# 查询场景提示词
def query_prompt_template(prompt_id, point_type, prompt_type):
    return SqliteDB.query_execute_batch("SELECT * FROM prompt_rules WHERE prompt_id = ? and point_type = ? and type = ?", (prompt_id,point_type, prompt_type))

# 保存提示词信息
def save_prompt_info(req_json):
    prompt_id = req_json['id']
    # 清除提示词配置
    SqliteDB.execute("DELETE FROM prompt_rules WHERE prompt_id = ?", (prompt_id,))
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
    SqliteDB.execute_batch("INSERT INTO prompt_rules (prompt_id, scene_name, scene_identify, context, point_type, type) VALUES (?, ?, ?, ?, ?, ?)"
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
    SqliteDB.execute_batch("INSERT INTO prompt_rules (prompt_id, scene_name, scene_identify, context, point_type, type) VALUES (?, ?, ?, ?, ?, ?)"
                                 , extra_scene_data)
    """番外-脉络生成"""
    save_prompt(prompt_id, req_json['extra_framework_system'], req_json['extra_framework_user'], 8)
    """结果润色"""
    save_prompt(prompt_id, req_json['polish_system'], req_json['polish_user'], 5)

# 保存提示词规则
def save_prompt(prompt_id, system, user, point_type):
    # 保存系统提示词
    SqliteDB.execute("INSERT INTO prompt_rules (prompt_id, context, point_type, type) VALUES (?, ?, ?, ?)", (prompt_id, system, point_type, 1))
    # 用户提示词
    SqliteDB.execute("INSERT INTO prompt_rules (prompt_id, context, point_type, type) VALUES (?, ?, ?, ?)", (prompt_id, user, point_type, 2))

# 导入提示词信息
def import_prompt_template(req_json):
    # 获取名称
    prompt_id = insert_prompt_conf(req_json['name'])
    req_json['id'] = prompt_id
    save_prompt_info(req_json)

# 删除提示词模版
def remove_prompt(prompt_id):
    # 删除提示词规则
    SqliteDB.execute("DELETE FROM prompt_rules WHERE prompt_id = ?", (prompt_id,))
    # 提示词信息
    SqliteDB.execute("DELETE FROM prompt_info WHERE id = ?", (prompt_id,))