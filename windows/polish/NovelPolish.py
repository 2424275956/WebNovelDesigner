from langchain_openai import ChatOpenAI

from config.GlobalMap import APP_STOP_EVENT
from pojo.table.Chapter import sqliteToChapter, ChapterPoint
from sqlite.ChapterDB import query_wait_polish_chapter, query_chapter_by_id, query_before_chapter, query_after_chapter, \
    update_chapter_status, update_chapter_sort, insert_extra_chapter, count_fail_chapter_num
from sqlite.ProjectDB import update_chapter_all_num, update_chapter_fail_num, update_chapter_success_num
from windows.polish.ChapterPolish import role_chapter_polish, relation_chapter_polish, process_chapter_polish, \
    original_scene_chapter_polish, original_framework_chapter_polish, extra_scene_chapter_plish, polish_chapter_polish, \
    extra_framework_chapter_polish, novel_before_polish
from windows.polish.ChapterRag import novel_rag_store


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
                         timeout=model['time_out'],
                         streaming=True)
        model_map[model_id] = llm

    # 循环处理
    for chapter in chapter_list:
        print(f"开始初始化章节信息")
        # 初始化章节状态
        update_chapter_status(2, chapter['id'])
        ## 获取最新章节信息
        temp_chapter = query_chapter_by_id(chapter['id'])
        print(f"最新章节信息：{str(temp_chapter)}")
        chapter_model = sqliteToChapter(temp_chapter)
        # 前述剧情简述
        if ChapterPoint.NOVEL_BEFORE_RESUME.value == chapter_model.point:
            get_before_novel(chapter_model, transmit, model_map)
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
        print(10.01)
        temp_chapter100 = query_chapter_by_id(chapter['id'])
        print(10.02)
        if 100 == chapter['point']:
            print(10.03)
            role_chapter_polish(temp_chapter100, transmit, model_map, reference_before_text)
            print(f"角色分析-处理完成")
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            if stop_event and stop_event.is_set():
                return

        ## 关系分析
        print(10.04)
        temp_chapter200 = query_chapter_by_id(chapter['id'])
        print(10.05)
        if 200 == temp_chapter200['point'] and 4 != temp_chapter200['status']:
            print(10.06)
            relation_chapter_polish(temp_chapter200, transmit, model_map, reference_before_text)
            print(f"关系分析-处理完成")
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            if stop_event and stop_event.is_set():
                return

        ## 流程控制
        print(10.07)
        temp_chapter300 = query_chapter_by_id(chapter['id'])
        print(10.08)
        is_extra = False
        if 300 == temp_chapter300['point'] and 4 != temp_chapter300['status']:
            print(10.09)
            is_extra = process_chapter_polish(temp_chapter300, transmit, model_map, reference_before_text, reference_after_text)
            print(f"流程控制-处理完成，当前Chapter：{str(chapter)}")
            if is_extra:
                print(13.10)
                temp_extra = query_chapter_by_id(chapter['id'])
                print(13.11)
                chapter_sort = temp_extra['sort']
                print(13.12)
                ### 更新全部章节序号
                update_chapter_sort(chapter_sort, temp_extra['project_id'])
                print(13.13)
                ### 新增番外章节
                extra_chapter_id = insert_extra_chapter(temp_extra, chapter_sort)
                print(13.14)
                # 更新章节数量
                update_chapter_all_num(temp_extra['project_id'])
                print(13.15)
                ### 获取番外章节信息
                extra_chapter = query_chapter_by_id(extra_chapter_id)
                print(13.16)
                if extra_chapter:
                    print(13.17)
                    after_chapter_polish(progress_callback, extra_chapter, transmit, model_map, reference_before_text, reference_after_text)
                    print(13.18)
            print(13.19)
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            print(13.20)
            if stop_event and stop_event.is_set():
                print(13.21)
                return

        if is_extra:
            temp_chapter_novel = query_chapter_by_id(chapter['id'])
            reference_before_text = get_before_novel(temp_chapter_novel, transmit, model_map)
            print(f"前述章节字数：{len(reference_before_text)}")
        ## 后续流程
        after_chapter_polish(progress_callback, chapter, transmit, model_map, reference_before_text, reference_after_text)
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

def after_chapter_polish(progress_callback, chapter, transmit, model_map, reference_before_text, reference_after_text):
    """剩余流程章节处理"""
    # 原文改写-场景分析
    print(10.10)
    temp_chapter400 = query_chapter_by_id(chapter['id'])
    print(10.11)
    if 400 == temp_chapter400['point'] and 4 != temp_chapter400['status']:
        print(10.12)
        original_scene_chapter_polish(temp_chapter400, transmit, model_map, reference_before_text, reference_after_text)
        print(f"原文改写-场景分析-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 原文改写-脉络改写
    print(10.13)
    temp_chapter401 = query_chapter_by_id(chapter['id'])
    print(10.14)
    if 401 == temp_chapter401['point'] and 4 != temp_chapter401['status']:
        print(10.15)
        original_framework_chapter_polish(temp_chapter401, transmit, model_map, reference_before_text, reference_after_text)
        print(f"原文改写-脉络改写-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 番外章节-场景分析
    print(10.16)
    temp_chapter410 = query_chapter_by_id(chapter['id'])
    print(10.17)
    if 410 == temp_chapter410['point'] and 4 != temp_chapter410['status']:
        print(10.18)
        extra_scene_chapter_plish(temp_chapter410, transmit, model_map, reference_before_text, reference_after_text)
        print(f"番外章节-场景分析-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 番外章节-脉络生成
    print(10.19)
    temp_chapter411 = query_chapter_by_id(chapter['id'])
    print(10.20)
    if 411 == temp_chapter411['point'] and 4 != temp_chapter411['status']:
        print(10.21)
        extra_framework_chapter_polish(temp_chapter411, transmit, model_map, reference_before_text, reference_after_text)
        print(f"番外章节-脉络生成-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 润色章节
    print(10.22)
    temp_chapter500 = query_chapter_by_id(chapter['id'])
    print(10.23)
    if 500 == temp_chapter500['point'] and 4 != temp_chapter500['status']:
        print(10.24)
        polish_chapter_polish(temp_chapter500, transmit, model_map)
        print(f"润色章节-处理完成")

    print(10.25)
    temp_chapter600 = query_chapter_by_id(chapter['id'])
    print(10.26)
    if 3 == temp_chapter600['status']:
        # 更新完成章节数
        print(10.27)
        update_chapter_success_num(chapter['project_id'])
        print(10.28)
        # RAG内容分析存储
        try:
            novel_rag_store(temp_chapter600)
        except Exception as e:
            print(f"RAG存储失败：{e}")
    elif 4 == temp_chapter600['status']:
        print(10.29)
        # 获取失败章节
        result = count_fail_chapter_num(chapter['project_id'])
        print(10.30)
        fail_num = result[0] if result else 0
        print(10.31)
        # 更新失败章节
        update_chapter_fail_num(fail_num, chapter['project_id'])
        print(10.32)

def get_before_novel(chapter_model, transmit, model_map):
    """
    获取前述剧情
    """
    # 获取前几章内容
    reference_before_text = ""
    chapter_before_list = query_before_chapter(chapter_model.project_id, chapter_model.sort, transmit['polish_before_num'])
    if chapter_before_list:
        for chapter_before in chapter_before_list:
            if chapter_before['new_content'] is None or len(chapter_before['new_content']) <= 0:
                if chapter_before['old_content']:
                    reference_before_text = reference_before_text + chapter_before['old_content']
            else:
                reference_before_text = reference_before_text + chapter_before['new_content']
    else:
        reference_before_text = "-"

    # 长度大于1万的话，进行精简来保证token长度与思考长度
    if len(reference_before_text) > 4000:
        before_novel = novel_before_polish(transmit, model_map, reference_before_text)
    else:
        123
    return reference_before_text