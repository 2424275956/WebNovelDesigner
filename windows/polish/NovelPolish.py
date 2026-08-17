from contextlib import closing

from langchain_openai import ChatOpenAI

from sqlite.Sqlite3Utils import query_wait_polish_chapter, query_chapter_by_id, query_before_chapter, \
    query_after_chapter, update_chapter_status, update_chapter_sort, insert_extra_chapter, update_chapter_success_num, \
    count_fail_chapter_num, update_chapter_fail_num, update_chapter_all_num
from windows.polish.ChapterPolish import role_chapter_polish, relation_chapter_polish, process_chapter_polish, \
    original_scene_chapter_polish, original_framework_chapter_polish, extra_scene_chapter_plish, polish_chapter_polish, \
    extra_framework_chapter_polish
from windows.project.NovelChapterList import novel_chapter, update_chapter_num


def polish(params, progress_callback=None):
    """润色小说"""
    self, transmit = params
    # 获取项目ID
    project_id = transmit['project_id']
    # 获取全部待完成章节
    chapter_list = query_wait_polish_chapter(project_id)
    # 没有待处理章节
    if chapter_list is None or len(chapter_list) <= 0:
        return

    # 模型数组
    model_map = {}
    # 循环初始化模型
    for model_id, model in transmit['model_map'].items():
        llm = ChatOpenAI(model=model['model_id'],
                         api_key=model['api_key'],
                         base_url=model['url'],
                         temperature=model['temperature'],
                         max_tokens=model['max_token'],
                         top_p=model['top_p'],
                         timeout=model['time_out'])
        model_map[model_id] = llm

    # 循环处理
    for chapter in chapter_list:
        row_dict = row_to_dict(chapter)
        # 初始化章节状态
        update_chapter_status(2, row_dict['id'])
        row_dict['status'] = 2
        # 调用进度回调,刷新页面
        if progress_callback:
            progress_callback(row_dict['project_id'])
        ## 获取最新章节信息
        row_dict = row_to_dict(query_chapter_by_id(row_dict['id']))
        ## 获取前几章内容
        reference_before_text = ""
        chapter_before_list = query_before_chapter(row_dict['project_id'], row_dict['sort'], transmit['polish_before_num'])
        if chapter_before_list:
            for chapter_before in chapter_before_list:
                if chapter_before['new_content'] is None or len(chapter_before['new_content']) <= 0:
                    reference_before_text = reference_before_text + chapter_before['old_content']
                else:
                    reference_before_text = reference_before_text + chapter_before['new_content']
        else:
            reference_before_text = "-"

        ## 获取后几章内容
        reference_after_text = ""
        chapter_after_list = query_after_chapter(row_dict['project_id'], row_dict['sort'], transmit['polish_after_num'])
        if chapter_after_list:
            for chapter_after in chapter_after_list:
                if chapter_after['new_content'] is None or len(chapter_after['new_content']) <= 0:
                    reference_after_text = reference_after_text + chapter_after['old_content']
                else:
                    reference_after_text = reference_after_text + chapter_after['new_content']
        else:
            reference_after_text = "-"

        ## 角色分析
        if 100 == row_dict['point']:
            role_chapter_polish(row_dict, transmit, model_map, reference_before_text)

        ## 关系分析
        if 200 == row_dict['point'] and 4 != row_dict['status']:
            relation_chapter_polish(row_dict, transmit, model_map, reference_before_text)

        ## 流程控制
        if 300 == row_dict['point'] and 4 != row_dict['status']:
            is_extra = process_chapter_polish(row_dict, transmit, model_map, reference_before_text, reference_after_text)
            if is_extra:
                chapter_sort = row_dict['sort']
                ### 更新全部章节序号
                update_chapter_sort(chapter_sort, row_dict['project_id'])
                row_dict['sort'] = row_dict['sort'] + 1
                ### 新增番外章节
                extra_chapter_id = insert_extra_chapter(row_dict, chapter_sort)
                ### 获取番外章节信息
                extra_chapter = query_chapter_by_id(extra_chapter_id)
                if extra_chapter:
                    after_chapter_polish(self, extra_chapter, transmit, model_map, reference_before_text, reference_after_text)
                    # 更新章节数量
                    update_chapter_all_num(row_dict['project_id'])
                    # 刷新页面
                    if progress_callback:
                        progress_callback(chapter['project_id'])

        ## 后续流程
        after_chapter_polish(self, row_dict, transmit, model_map, reference_before_text, reference_after_text)

def after_chapter_polish(progress_callback, chapter, transmit, model_map, reference_before_text, reference_after_text):
    """剩余流程章节处理"""
    # 原文改写-场景分析
    if 400 == chapter['point'] and 4 != chapter['status']:
        original_scene_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text)

    # 原文改写-脉络改写
    if 401 == chapter['point'] and 4 != chapter['status']:
        original_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text)

    # 番外章节-场景分析
    if 410 == chapter['point'] and 4 != chapter['status']:
        extra_scene_chapter_plish(chapter, transmit, model_map, reference_before_text, reference_after_text)

    # 番外章节-脉络生成
    if 411 == chapter['point'] and 4 != chapter['status']:
        extra_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text)

    # 润色章节
    if 500 == chapter['point'] and 4 != chapter['status']:
        polish_chapter_polish(chapter, transmit, model_map)

    if 3 == chapter['status']:
        # 更新完成章节数
        update_chapter_success_num(chapter['project_id'])
    elif 4 == chapter['status']:
        # 获取失败章节
        fail_num = count_fail_chapter_num(chapter['project_id'])
        # 更新失败章节
        update_chapter_fail_num(fail_num, chapter['project_id'])

    # 刷新页面
    if progress_callback:
        progress_callback(chapter['project_id'])

# 通用方法：转为 dict
def row_to_dict(row):
    """
    将各种 row 对象转为普通字典
    """
    res_items = {}
    for key in row.keys():
        res_items[key] = row[key]
    return res_items
