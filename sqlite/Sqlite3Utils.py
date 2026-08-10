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