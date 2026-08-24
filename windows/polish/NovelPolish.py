from langchain_openai import ChatOpenAI

from config.GlobalMap import APP_STOP_EVENT
from pojo.table.Chapter import sqliteToChapter, ChapterPoint, ChapterStatus, ChapterBO
from sqlite.ChapterDB import query_wait_polish_chapter, query_chapter_by_id, query_before_chapter, query_after_chapter, \
    update_chapter_status, update_chapter_sort, insert_extra_chapter, update_original_resume, update_polish_resume
from windows.polish.ChapterPolish import role_chapter_polish, relation_chapter_polish, process_chapter_polish, \
    original_scene_chapter_polish, original_framework_chapter_polish, extra_scene_chapter_plish, polish_chapter_polish, \
    extra_framework_chapter_polish, chapter_novel_resume


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
    # 角色分析
    role_model = transmit['model_map'][transmit['role_model_id']]
    model_map[ChapterPoint.ROLE_ANALYSIS.value] = ChatOpenAI(
        model=role_model['model_id'],
        api_key=role_model['api_key'],
        base_url=role_model['url'],
        temperature=role_model['temperature'],
        max_tokens=role_model['max_token'],
        top_p=role_model['top_p'],
        timeout=role_model['time_out'],
        streaming=True
    )
    # 关系分析
    relation_model = transmit['model_map'][transmit['relation_model_id']]
    model_map[ChapterPoint.RELATION_ANALYSIS.value] = ChatOpenAI(
        model=relation_model['model_id'],
        api_key=relation_model['api_key'],
        base_url=relation_model['url'],
        temperature=relation_model['temperature'],
        max_tokens=relation_model['max_token'],
        top_p=relation_model['top_p'],
        timeout=relation_model['time_out'],
        streaming=True
    )
    # 流程控制
    process_model = transmit['model_map'][transmit['process_model_id']]
    model_map[ChapterPoint.PROCESS_CHOOSES.value] = ChatOpenAI(
        model=process_model['model_id'],
        api_key=process_model['api_key'],
        base_url=process_model['url'],
        temperature=process_model['temperature'],
        max_tokens=process_model['max_token'],
        top_p=process_model['top_p'],
        timeout=process_model['time_out'],
        streaming=True
    )
    # 原文改写-场景分析
    original_scene_model = transmit['model_map'][transmit['scene_model_id']]
    model_map[ChapterPoint.ORIGINAL_SCENE.value] = ChatOpenAI(
        model=original_scene_model['model_id'],
        api_key=original_scene_model['api_key'],
        base_url=original_scene_model['url'],
        temperature=original_scene_model['temperature'],
        max_tokens=original_scene_model['max_token'],
        top_p=original_scene_model['top_p'],
        timeout=original_scene_model['time_out'],
        streaming=True
    )
    stop_list = [
        # 格式终止符
        "\n\n\n",                    # 三个换行

        # 防止总结性废话
        "总之",
        "综上所述",
        "通过以上描写可以看出",
        "这段文字主要描写了",

        # 防止内容重复/循环
        "如前所述",
        "正如前文所述",
        "再次强调",
        "值得一提的是",

        # 防止过度标点
        "！？",            # 连续的感叹+问号
        "？！",
        "......",          # 省略号过多
        "！！！！",          # 三个感叹号
        "？？？？",          # 三个问号
        "，，，，",
    ]
    # 原文改写-脉络改写
    original_framework_model = transmit['model_map'][transmit['framework_model_id']]
    model_map[ChapterPoint.ORIGINAL_FRAMEWORK.value] = ChatOpenAI(
        model=original_framework_model['model_id'],
        api_key=original_framework_model['api_key'],
        base_url=original_framework_model['url'],
        temperature=original_framework_model['temperature'],
        max_tokens=original_framework_model['max_token'],
        top_p=original_framework_model['top_p'],
        timeout=original_framework_model['time_out'],
        streaming=True,
        presence_penalty=0.5,      # 全局重复惩罚，防止车轱辘话
        frequency_penalty=0.4,     # 频率惩罚，抑制高频词
        stop=stop_list,
        extra_body={
            "repetition_penalty":1.05,  # 重复惩罚（注意：不同API参数名不同）
            "top_k": 40                 # 限制候选词数量
        }
    )
    # 番外生成-场景分析
    extra_scene_model = transmit['model_map'][transmit['extra_scene_model_id']]
    model_map[ChapterPoint.EXTRA_SCENE.value] = ChatOpenAI(
        model=extra_scene_model['model_id'],
        api_key=extra_scene_model['api_key'],
        base_url=extra_scene_model['url'],
        temperature=extra_scene_model['temperature'],
        max_tokens=extra_scene_model['max_token'],
        top_p=extra_scene_model['top_p'],
        timeout=extra_scene_model['time_out'],
        streaming=True
    )
    # 番外生成-脉络生成
    extra_framework_model = transmit['model_map'][transmit['extra_framework_model_id']]
    model_map[ChapterPoint.EXTRA_FRAMEWORK.value] = ChatOpenAI(
        model=extra_framework_model['model_id'],
        api_key=extra_framework_model['api_key'],
        base_url=extra_framework_model['url'],
        temperature=extra_framework_model['temperature'],
        max_tokens=extra_framework_model['max_token'],
        top_p=extra_framework_model['top_p'],
        timeout=extra_framework_model['time_out'],
        streaming=True,
        presence_penalty=0.7,      # 全局重复惩罚，防止车轱辘话
        frequency_penalty=0.5,     # 频率惩罚，抑制高频词
        stop=stop_list,
        extra_body={
            "repetition_penalty":1.08,  # 重复惩罚（注意：不同API参数名不同）
            "top_k": 60                 # 限制候选词数量
        }
    )
    # 结果润色
    polish_model = transmit['model_map'][transmit['polish_model_id']]
    model_map[ChapterPoint.POLISH_CONTENT.value] = ChatOpenAI(
        model=polish_model['model_id'],
        api_key=polish_model['api_key'],
        base_url=polish_model['url'],
        temperature=polish_model['temperature'],
        max_tokens=polish_model['max_token'],
        top_p=polish_model['top_p'],
        timeout=polish_model['time_out'],
        streaming=True,
        presence_penalty=0.15,      # 全局重复惩罚，防止车轱辘话
        frequency_penalty=0.1,     # 频率惩罚，抑制高频词
        stop=stop_list,
        extra_body={
            "repetition_penalty":1.01,  # 重复惩罚（注意：不同API参数名不同）
            "top_k": 30                 # 限制候选词数量
        }
    )

    # 循环处理
    for chapter in chapter_list:
        print(f"开始初始化章节信息")
        # 初始化章节状态
        update_chapter_status(ChapterStatus.RUNNING.value, chapter['id'])
        ## 获取最新章节信息
        temp_chapter = query_chapter_by_id(chapter['id'])
        print(f"最新章节信息：{str(temp_chapter)}")
        chapter_model = sqliteToChapter(temp_chapter)
        # 前述剧情简述
        print(9.01)
        if ChapterStatus.FAIL.value != chapter_model.status:
            print(9.02)
            get_before_novel(chapter_model, transmit, model_map)
        # 后续剧情简述
        print(9.03)
        if ChapterStatus.FAIL.value != chapter_model.status:
            print(9.04)
            get_after_novel(chapter_model, transmit, model_map)

        ## 角色分析
        print(10.01)
        if ChapterPoint.ROLE_ANALYSIS.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
            print(10.03)
            role_chapter_polish(chapter_model, transmit, model_map)
            print(f"角色分析-处理完成")
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            if stop_event and stop_event.is_set():
                return

        ## 关系分析
        print(10.04)
        if ChapterPoint.RELATION_ANALYSIS.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
            print(10.06)
            relation_chapter_polish(chapter_model, transmit, model_map)
            print(f"关系分析-处理完成")
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            if stop_event and stop_event.is_set():
                return

        ## 流程控制
        print(10.07)
        is_extra = False
        if ChapterPoint.PROCESS_CHOOSES.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
            print(10.09)
            is_extra = process_chapter_polish(chapter_model, transmit, model_map)
            print(f"流程控制-处理完成，当前Chapter：{str(chapter)}")
            if is_extra:
                print(13.10)
                ### 更新全部章节序号
                update_chapter_sort(chapter_model.sort, chapter_model.project_id)
                chapter_model.sort += 1
                print(13.13)
                ### 新增番外章节
                extra_chapter_id = insert_extra_chapter(chapter_model)
                print(13.14)
                ### 获取番外章节信息
                extra_chapter = query_chapter_by_id(extra_chapter_id)
                extra_model = sqliteToChapter(extra_chapter)
                print(13.16)
                if extra_chapter:
                    print(13.17)
                    # 后续剧情-置空，重新处理
                    chapter_model.after_content = None
                    get_after_novel(chapter_model, transmit, model_map)
                    # 处理
                    after_chapter_polish(progress_callback, extra_model, transmit, model_map)
                    print(13.18)
            print(13.19)
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            print(13.20)
            if stop_event and stop_event.is_set():
                print(13.21)
                return

        #  前述剧情更新
        if is_extra:
            chapter_model.before_content = None
            get_before_novel(chapter_model, transmit, model_map)
        ## 后续流程
        after_chapter_polish(progress_callback, chapter_model, transmit, model_map)
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

def after_chapter_polish(progress_callback, chapter_model: ChapterBO, transmit, model_map):
    """剩余流程章节处理"""
    # 原文改写-场景分析
    print(10.10)
    if ChapterPoint.ORIGINAL_SCENE.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.12)
        original_scene_chapter_polish(chapter_model, transmit, model_map)
        print(f"原文改写-场景分析-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 原文改写-脉络改写
    print(10.13)
    if ChapterPoint.ORIGINAL_FRAMEWORK.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.15)
        original_framework_chapter_polish(chapter_model, transmit, model_map)
        print(f"原文改写-脉络改写-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 番外章节-场景分析
    print(10.16)
    if ChapterPoint.EXTRA_SCENE.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.18)
        extra_scene_chapter_plish(chapter_model, transmit, model_map)
        print(f"番外章节-场景分析-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 番外章节-脉络生成
    print(10.19)
    if ChapterPoint.EXTRA_FRAMEWORK.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.21)
        extra_framework_chapter_polish(chapter_model, transmit, model_map)
        print(f"番外章节-脉络生成-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event and stop_event.is_set():
            return

    # 润色章节
    print(10.22)
    if ChapterPoint.POLISH_CONTENT.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.24)
        polish_chapter_polish(chapter_model, transmit, model_map)
        print(f"润色章节-处理完成")

def get_before_novel(chapter_model: ChapterBO, transmit, model_map):
    """
    获取前述剧情
    """
    # 获取前几章内容
    chapter_model.before_content = ""
    chapter_before_list = query_before_chapter(chapter_model.project_id, chapter_model.sort, transmit['polish_before_num'])
    if chapter_before_list:
        for chapter_before in chapter_before_list:
            # 转换
            before_model = sqliteToChapter(chapter_before)

            # 不存在润色结果内容
            if before_model.new_content is None or len(before_model.new_content) < 1:
                ## 不存在原文信息
                if before_model.old_content is None or len(before_model.old_content) < 1:
                    continue
                ## 存在原文信息
                else:
                    ### 不存在原文简述
                    if before_model.original_resume is None or len(before_model.original_resume) < 1:
                        #### 对原文进行简述
                        novel_resume = chapter_novel_resume(chapter_model, before_model.old_content, transmit, model_map)
                        if ChapterStatus.FAIL.value == chapter_model.status:
                            return
                        else:
                            ##### 更新原文简述
                            update_original_resume(novel_resume, before_model.id)
                            chapter_model.before_content += novel_resume
                            continue
                    ### 存在原文简述
                    else:
                        chapter_model.before_content += before_model.original_resume
                        continue
            # 存在润色结果内容
            else:
                ## 不存在润色简述
                if before_model.polish_resume is None or len(before_model.polish_resume) < 1:
                    ### 对结果进行简述
                    novel_resume = chapter_novel_resume(chapter_model, before_model.new_content, transmit, model_map)
                    if ChapterStatus.FAIL.value == chapter_model.status:
                        return
                    else:
                        #### 更新结果简述
                        update_polish_resume(novel_resume, before_model.id)
                        chapter_model.before_content += novel_resume
                        continue
                ## 存在润色简述
                else:
                    chapter_model.before_content += before_model.polish_resume
                    continue

def get_after_novel(chapter_model, transmit, model_map):
    """
    获取后续剧情简述
    """
    chapter_model.after_content = ""
    chapter_after_list = query_after_chapter(chapter_model.project_id, chapter_model.sort, transmit['polish_after_num'])
    if chapter_after_list:
        for chapter_after in chapter_after_list:
            # 转换
            after_model = sqliteToChapter(chapter_after)

            # 不存在润色结果内容
            if after_model.new_content is None or len(after_model.new_content) < 1:
                ## 不存在原文信息
                if after_model.old_content is None or len(after_model.old_content) < 1:
                    continue
                ## 存在原文信息
                else:
                    ### 不存在原文简述
                    if after_model.original_resume is None or len(after_model.original_resume) < 1:
                        #### 对原文进行简述
                        novel_resume = chapter_novel_resume(chapter_model, after_model.old_content, transmit, model_map)
                        if ChapterStatus.FAIL.value == chapter_model.status:
                            return
                        else:
                            ##### 更新原文简述
                            update_original_resume(novel_resume, after_model.id)
                            chapter_model.after_content += novel_resume
                            continue
                    ### 存在原文简述
                    else:
                        chapter_model.after_content += after_model.original_resume
                        continue
            # 存在润色结果内容
            else:
                ## 不存在润色简述
                if after_model.polish_resume is None or len(after_model.polish_resume) < 1:
                    ### 对结果进行简述
                    novel_resume = chapter_novel_resume(chapter_model, after_model.new_content, transmit, model_map)
                    if ChapterStatus.FAIL.value == chapter_model.status:
                        return
                    else:
                        #### 更新结果简述
                        update_polish_resume(novel_resume, after_model.id)
                        chapter_model.after_content += novel_resume
                        continue
                ## 存在润色简述
                else:
                    chapter_model.after_content += after_model.polish_resume
                    continue