from langchain_openai import ChatOpenAI

from config.GlobalMap import APP_STOP_EVENT
from sqlite.Sqlite3Utils import query_wait_polish_chapter, query_chapter_by_id, query_before_chapter, \
    query_after_chapter, update_chapter_status, update_chapter_sort, insert_extra_chapter, update_chapter_success_num, \
    count_fail_chapter_num, update_chapter_fail_num, update_chapter_all_num
from windows.polish.ChapterPolish import role_chapter_polish, relation_chapter_polish, process_chapter_polish, \
    original_scene_chapter_polish, original_framework_chapter_polish, extra_scene_chapter_plish, polish_chapter_polish, \
    extra_framework_chapter_polish


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
        print(f"开始初始化章节信息")
        # 初始化章节状态
        update_chapter_status(2, chapter['id'])
        ## 获取最新章节信息
        temp_chapter = query_chapter_by_id(chapter['id'])
        print(f"最新章节信息：{str(temp_chapter)}")
        ## 获取前几章内容
        reference_before_text = ""
        chapter_before_list = query_before_chapter(temp_chapter['project_id'], temp_chapter['sort'], transmit['polish_before_num'])
        if chapter_before_list:
            for chapter_before in chapter_before_list:
                if chapter_before['new_content'] is None or len(chapter_before['new_content']) <= 0:
                    reference_before_text = reference_before_text + chapter_before['old_content']
                else:
                    reference_before_text = reference_before_text + chapter_before['new_content']
        else:
            reference_before_text = "-"

        print(f"前述章节字数：{len(reference_before_text)}")
        ## 获取后几章内容
        reference_after_text = ""
        chapter_after_list = query_after_chapter(temp_chapter['project_id'], temp_chapter['sort'], transmit['polish_after_num'])
        if chapter_after_list:
            for chapter_after in chapter_after_list:
                if chapter_after['new_content'] is None or len(chapter_after['new_content']) <= 0:
                    reference_after_text = reference_after_text + chapter_after['old_content']
                else:
                    reference_after_text = reference_after_text + chapter_after['new_content']
        else:
            reference_after_text = "-"

        print(f"后续章节字数：{len(reference_after_text)}")
        ## 角色分析
        temp_chapter100 = query_chapter_by_id(chapter['id'])
        if 100 == chapter['point']:
            role_chapter_polish(temp_chapter100, transmit, model_map, reference_before_text)
            print(f"角色分析-处理完成")
            if APP_STOP_EVENT.get(transmit['project_id']).is_set():
                print(f"角色分析-进入STOP-EVENT")
                return

        ## 关系分析
        temp_chapter200 = query_chapter_by_id(chapter['id'])
        if 200 == temp_chapter200['point'] and 4 != temp_chapter200['status']:
            relation_chapter_polish(temp_chapter200, transmit, model_map, reference_before_text)
            print(f"关系分析-处理完成")
            if APP_STOP_EVENT.get(transmit['project_id']).is_set():
                print(f"关系分析-进入STOP-EVENT")
                return

        ## 流程控制
        temp_chapter300 = query_chapter_by_id(chapter['id'])
        if 300 == temp_chapter300['point'] and 4 != temp_chapter300['status']:
            is_extra = process_chapter_polish(temp_chapter300, transmit, model_map, reference_before_text, reference_after_text)
            print(f"流程控制-处理完成，当前Chapter：{str(chapter)}")
            if is_extra:
                temp_extra = query_chapter_by_id(chapter['id'])
                chapter_sort = temp_extra['sort']
                ### 更新全部章节序号
                update_chapter_sort(chapter_sort, temp_extra['project_id'])
                ### 新增番外章节
                extra_chapter_id = insert_extra_chapter(temp_extra, chapter_sort)
                ### 获取番外章节信息
                extra_chapter = query_chapter_by_id(extra_chapter_id)
                if extra_chapter:
                    after_chapter_polish(progress_callback, extra_chapter, transmit, model_map, reference_before_text, reference_after_text)
                    # 更新章节数量
                    update_chapter_all_num(temp_extra['project_id'])
            if APP_STOP_EVENT.get(transmit['project_id']).is_set():
                print(f"流程控制-进入STOP-EVENT")
                return

        ## 后续流程
        after_chapter_polish(progress_callback, chapter, transmit, model_map, reference_before_text, reference_after_text)
        if APP_STOP_EVENT.get(transmit['project_id']).is_set():
            return

def after_chapter_polish(progress_callback, chapter, transmit, model_map, reference_before_text, reference_after_text):
    """剩余流程章节处理"""
    # 原文改写-场景分析
    temp_chapter400 = query_chapter_by_id(chapter['id'])
    if 400 == temp_chapter400['point'] and 4 != temp_chapter400['status']:
        original_scene_chapter_polish(temp_chapter400, transmit, model_map, reference_before_text, reference_after_text)
        print(f"原文改写-场景分析-处理完成")
        if APP_STOP_EVENT.get(transmit['project_id']).is_set():
            return

    # 原文改写-脉络改写
    temp_chapter401 = query_chapter_by_id(chapter['id'])
    if 401 == temp_chapter401['point'] and 4 != temp_chapter401['status']:
        original_framework_chapter_polish(temp_chapter401, transmit, model_map, reference_before_text, reference_after_text)
        print(f"原文改写-脉络改写-处理完成")
        if APP_STOP_EVENT.get(transmit['project_id']).is_set():
            return

    # 番外章节-场景分析
    temp_chapter410 = query_chapter_by_id(chapter['id'])
    if 410 == temp_chapter410['point'] and 4 != temp_chapter410['status']:
        extra_scene_chapter_plish(temp_chapter410, transmit, model_map, reference_before_text, reference_after_text)
        print(f"番外章节-场景分析-处理完成")
        if APP_STOP_EVENT.get(transmit['project_id']).is_set():
            return

    # 番外章节-脉络生成
    temp_chapter411 = query_chapter_by_id(chapter['id'])
    if 411 == temp_chapter411['point'] and 4 != temp_chapter411['status']:
        extra_framework_chapter_polish(temp_chapter411, transmit, model_map, reference_before_text, reference_after_text)
        print(f"番外章节-脉络生成-处理完成")
        if APP_STOP_EVENT.get(transmit['project_id']).is_set():
            return

    # 润色章节
    temp_chapter500 = query_chapter_by_id(chapter['id'])
    if 500 == temp_chapter500['point'] and 4 != temp_chapter500['status']:
        polish_chapter_polish(temp_chapter500, transmit, model_map)
        print(f"润色章节-处理完成")

    temp_chapter600 = query_chapter_by_id(chapter['id'])
    if 3 == temp_chapter600['status']:
        # 更新完成章节数
        update_chapter_success_num(chapter['project_id'])
    elif 4 == temp_chapter600['status']:
        # 获取失败章节
        fail_num = count_fail_chapter_num(chapter['project_id'])
        # 更新失败章节
        update_chapter_fail_num(fail_num, chapter['project_id'])


# 通用方法：转为 dict
def row_to_dict(row):
    """
    将各种 row 对象转为普通字典
    """
    res_items = {}
    for key in row.keys():
        res_items[key] = row[key]
    return res_items
