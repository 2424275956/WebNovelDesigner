from sqlite.SqliteDB import SqliteDB

# 查询所有项目信息的函数
def query_all_project():
    # 执行SQL查询语句，获取project表中的所有数据
    # 返回查询结果
    return SqliteDB.query_execute_batch("SELECT * FROM project")

def query_project_by_id(project_id):
    return SqliteDB.query_execute("SELECT * FROM project WHERE id = ?", (project_id,))

def edit_project_prompt_id(prompt_id, project_id):
    SqliteDB.execute("UPDATE project SET prompt_id = ? WHERE id = ?", (prompt_id, project_id))

def edit_project_role_model_id(role_model_id, project_id):
    SqliteDB.execute("UPDATE project SET role_model_id = ? WHERE id = ?", (role_model_id, project_id))

def edit_project_relation_model_id(relation_model_id, project_id):
    SqliteDB.execute("UPDATE project SET relation_model_id = ? WHERE id = ?", (relation_model_id, project_id))

def edit_polish_before_num(num, project_id):
    SqliteDB.execute("UPDATE project SET polish_before_num = ? WHERE id = ?", (num, project_id))

def edit_polish_after_num(num, project_id):
    SqliteDB.execute("UPDATE project SET polish_after_num = ? WHERE id = ?", (num, project_id))

def edit_project_scene_model_id(scene_model_id, project_id):
    SqliteDB.execute("UPDATE project SET scene_model_id = ? WHERE id = ?", (scene_model_id, project_id))

def edit_project_process_model_id(process_model_id, project_id):
    SqliteDB.execute("UPDATE project SET process_model_id = ? WHERE id = ?", (process_model_id, project_id))

def edit_project_extra_scene_model_id(extra_scene_model_id, project_id):
    SqliteDB.execute("UPDATE project SET extra_scene_model_id = ? WHERE id = ?", (extra_scene_model_id, project_id))

def edit_project_framework_model_id(framework_model_id, project_id):
    SqliteDB.execute("UPDATE project SET framework_model_id = ? WHERE id = ?", (framework_model_id, project_id))

def edit_project_extra_framework_model_id(extra_framework_model_id, project_id):
    SqliteDB.execute("UPDATE project SET extra_framework_model_id = ? WHERE id = ?", (extra_framework_model_id, project_id))

def edit_project_polish_model_id(polish_model_id, project_id):
    SqliteDB.execute("UPDATE project SET polish_model_id = ? WHERE id = ?", (polish_model_id, project_id))

# 保存新创建的项目信息
def insert_project_info(project):
    title = project['title']
    author = project['author']
    word_count = project['word_count']
    return SqliteDB.execute("INSERT INTO project (title, author, word_count) VALUES (?, ?, ?)", (title, author, word_count))


# 删除项目信息
def remove_novel_info(project_id):
    # 删除关系信息
    SqliteDB.execute("DELETE FROM role_relation WHERE project_id = ?", (project_id,))
    # 删除角色信息
    SqliteDB.execute("DELETE FROM role_model WHERE project_id = ?", (project_id,))
    # 删除章节信息
    SqliteDB.execute("DELETE FROM chapter WHERE project_id = ?", (project_id,))
    # 删除项目信息
    SqliteDB.execute("DELETE FROM project WHERE id = ?", (project_id,))

# 更新项目-完成数
def update_chapter_success_num(project_id):
    SqliteDB.execute("UPDATE project SET success_num = success_num + 1 WHERE id = ?", (project_id,))

# 更新项目-失败数
def update_chapter_fail_num(num, project_id):
    SqliteDB.execute("UPDATE project SET fail_num = ? WHERE id = ?", (num, project_id))

# 更新项目-章节数
def update_chapter_all_num(project_id):
    SqliteDB.execute("UPDATE project SET chapter_num = chapter_num + 1, expansion_num = expansion_num + 1 WHERE id = ?", (project_id,))
    