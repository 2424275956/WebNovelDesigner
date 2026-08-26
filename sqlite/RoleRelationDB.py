from sqlite.SqliteDB import SqliteDB

# 项目详情
def query_role_model(project_id, role_names):
    if not role_names:
        return  [] # 如果列表为空，直接返回，避免生成无效的 SQL
    # 动态生成占位符：'?,?,?'
    placeholders = ','.join('?' * len(role_names))

    # 拼接正确的 SQL
    sql = f"SELECT * FROM role_model WHERE project_id = ? AND role_name IN ({placeholders})"

    # 注意：参数必须解包，project_id 和 role_names 中的每个元素都要作为独立参数传入
    params = [project_id] + role_names

    return SqliteDB.query_execute_batch(sql, tuple(params))

def query_role_relation(project_id, role_a, role_b):
    return SqliteDB.query_execute("SELECT relation FROM role_relation WHERE project_id = ? and role_a_name in (?, ?) and role_b_name in (?, ?)", (project_id, role_a, role_b, role_a, role_b))

def remove_old_role_model(project_id, role_name):
    # 注意：参数必须解包，project_id 和 role_names 中的每个元素都要作为独立参数传入
    SqliteDB.execute(f"DELETE FROM role_model WHERE project_id = ? and role_name = ?", [project_id, role_name])

def insert_role_model(project_id, role_name, is_family, role_json):
    SqliteDB.execute("INSERT INTO role_model (project_id, role_name, protagonist_family, role_json) VALUES (?, ?, ?, ?)", (project_id, str(role_name), is_family, str(role_json)))

def remove_old_role_relation(project_id, role_a, role_b):
    SqliteDB.execute("DELETE FROM role_relation WHERE project_id = ? and role_a_name = ? and role_b_name = ?", (project_id, role_a, role_b))

def insert_role_relation(project_id, role_a, role_b, relation):
    SqliteDB.execute("INSERT INTO role_relation (project_id, role_a_name, role_b_name, relation) VALUES (?, ?, ?, ?)", (project_id, str(role_a), str(role_b), str(relation)))

# 获取主角女性亲友信息
def query_family_role(project_id):
    return SqliteDB.query_execute_batch("SELECT * FROM role_model WHERE project_id = ? and protagonist_family = 1", (project_id,))

# 获取角色关联关系
def query_family_relation_name_a(project_id, names):
    placeholders = ','.join(['?'] * len(names))
    return SqliteDB.query_execute_batch(f"SELECT * FROM role_relation WHERE project_id = ? and role_a_name in ({placeholders})", (project_id,))
# 获取角色关联关系
def query_family_relation_name_b(project_id, names):
    placeholders = ','.join(['?'] * len(names))
    return SqliteDB.query_execute_batch(f"SELECT * FROM role_relation WHERE project_id = ? and role_b_name in ({placeholders})", (project_id, [names]))