from pojo.table.Chapter import ChapterBO, ChapterType, ChapterStatus, ChapterPoint
from sqlite.SqliteDB import SqliteDB

# 获取章节信息
def query_wait_polish_chapter(project_id):
    return SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE status in (1, 2, 4) and project_id = ? ORDER BY sort", (project_id,))

# 获取章节通过id
def query_chapter_by_id(chapter_id):
    return SqliteDB.query_execute("SELECT * FROM chapter WHERE id = ?", (chapter_id,))

# 获取前几章内容
def query_before_chapter(project_id, sort, before_num):
    return SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE project_id = ? and sort < ? ORDER BY sort DESC LIMIT ?", (project_id, sort, before_num))

# 获取后几章内容
def query_after_chapter(project_id, sort, after_num):
    return SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE project_id = ? and sort > ? ORDER BY sort LIMIT ?", (project_id, sort, after_num))

# 保存创建的章节信息
def insert_project_chapter(project_id, chapters):
    sql = "INSERT INTO chapter (project_id, title, old_len, old_content, sort) VALUES (?, ?, ?, ?, ?)"
    data = []
    # 根据数据数量处理
    for chapter in chapters:
        data.append((project_id, chapter['title'], chapter['old_len'], chapter['old_content'], chapter['sort']))
    SqliteDB.execute_batch(sql, data)

# 获取项目所有章节列表 并根据sort排序
def query_project_chapter_by_id(project_id):
    return SqliteDB.query_execute_batch("SELECT * FROM chapter WHERE project_id = ? ORDER BY sort", (project_id,))

# 更新章节-角色分析内容
def update_chapter_role(role_text, chapter_id):
    SqliteDB.execute("UPDATE chapter SET role_content = ?, status = 2, point = 200 WHERE id = ?", (role_text, chapter_id))

# 更新章节-关系分析内容
def update_chapter_relation(relation_text, chapter_id):
    SqliteDB.execute("UPDATE chapter SET relation_content = ?, point = 300 WHERE id = ?", (relation_text, chapter_id))

# 更新章节-状态
def update_chapter_status(status, chapter_id):
    SqliteDB.execute("UPDATE chapter SET status = ? WHERE id = ?", (status, chapter_id))

# 更新章节-流程判断
def update_chapter_process(process_content, point, chapter_id):
    SqliteDB.execute("UPDATE chapter SET process_content = ?, point = ? WHERE id = ?", (process_content, point, chapter_id))

# 更新章节-序号
def update_chapter_sort(sort, project_id):
    SqliteDB.execute("UPDATE chapter SET sort = sort + 1 WHERE sort >= ? and project_id = ?", (sort, project_id))

# 新增章节-番外章节
def insert_extra_chapter(chapter_model: ChapterBO):
    return SqliteDB.execute("INSERT INTO chapter (project_id, title, role_content, relation_content, process_content, type, status, point, sort) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (chapter_model.project_id,
                                   f"{chapter_model.title} - 序章",
                                   chapter_model.role_content,
                                   chapter_model.relation_content,
                                   chapter_model.process_content,
                                   ChapterType.EXTRA_GENERATE.value,
                                   ChapterStatus.WAIT.value,
                                   ChapterPoint.EXTRA_SCENE.value,
                                   chapter_model.sort))

# 更新章节-场景分析
def update_chapter_scene(scene_text, point, chapter_id):
    SqliteDB.execute("UPDATE chapter SET scene_content = ?, point = ? WHERE id = ?", (scene_text, point, chapter_id))

# 更新章节-脉络改写
def update_chapter_framework(framework_content, point, chapter_id):
    SqliteDB.execute("UPDATE chapter SET framework_content = ?, point = ? WHERE id = ?", (framework_content, point, chapter_id))

# 更新章节-完成润色
def update_chapter_polish(polish_text, chapter_id):
    SqliteDB.execute("UPDATE chapter SET new_len = ?, new_content = ?, status = 3, point = 600 WHERE id = ?", (len(polish_text), polish_text, chapter_id))

# 获取失败章节数
def count_fail_chapter_num(project_id):
    return SqliteDB.query_execute("SELECT count(*) FROM chapter WHERE status = 4 and project_id = ?", (project_id,))

# 更新章节-原文简述
def update_original_resume(original_resume, chapter_id):
    SqliteDB.execute("UPDATE chapter SET original_resume = ? WHERE id = ?", (original_resume, chapter_id))

# 更新章节-结果简述
def update_polish_resume(polish_resume, chapter_id):
    SqliteDB.execute("UPDATE chapter SET polish_resume = ? WHERE id = ?", (polish_resume, chapter_id))