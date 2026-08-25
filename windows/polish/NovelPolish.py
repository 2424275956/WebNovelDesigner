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
    # 获取全部待完成章节
    chapter_list = query_wait_polish_chapter(transmit.project_id)
    # 没有待处理章节
    if chapter_list is None or len(chapter_list) <= 0:
        return

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
            get_before_novel(chapter_model, transmit)
        # 后续剧情简述
        print(9.03)
        if ChapterStatus.FAIL.value != chapter_model.status:
            print(9.04)
            get_after_novel(chapter_model, transmit)

        ## 角色分析
        print(10.01)
        if ChapterPoint.ROLE_ANALYSIS.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
            print(10.03)
            role_chapter_polish(chapter_model, transmit)
            print(f"角色分析-处理完成")
            stop_event = APP_STOP_EVENT.get(transmit.project_id)
            if stop_event and stop_event.is_set():
                return

        ## 流程控制
        print(10.07)
        is_extra = False
        if ChapterPoint.PROCESS_CHOOSES.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
            print(10.09)
            is_extra = process_chapter_polish(chapter_model, transmit)
            print(f"流程控制-处理完成，当前Chapter：{str(chapter)}")
            if is_extra:
                print(13.10)
                ### 更新全部章节序号
                update_chapter_sort(chapter_model.sort, chapter_model.project_id)
                print(13.13)
                ### 新增番外章节
                extra_chapter_id = insert_extra_chapter(chapter_model)
                chapter_model.sort += 1
                print(13.14)
                ### 获取番外章节信息
                extra_chapter = query_chapter_by_id(extra_chapter_id)
                extra_model = sqliteToChapter(extra_chapter)
                print(13.16)
                if extra_chapter:
                    print(13.17)
                    get_before_novel(extra_model, transmit)
                    # 后续剧情-置空，重新处理
                    get_after_novel(extra_model, transmit)
                    # 处理
                    after_chapter_polish(progress_callback, extra_model, transmit)
                    print(13.18)
            print(13.19)
            stop_event = APP_STOP_EVENT.get(chapter_model.project_id)
            print(13.20)
            if stop_event and stop_event.is_set():
                print(13.21)
                return

        #  前述剧情更新
        if is_extra:
            chapter_model.before_content = None
            chapter_model.after_content = None
            get_after_novel(chapter_model, transmit)
            get_before_novel(chapter_model, transmit)
        ## 后续流程
        after_chapter_polish(progress_callback, chapter_model, transmit)
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            return

def after_chapter_polish(progress_callback, chapter_model: ChapterBO, transmit):
    """剩余流程章节处理"""
    # 原文改写-场景分析
    print(10.10)
    if ChapterPoint.ORIGINAL_SCENE.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.12)
        original_scene_chapter_polish(chapter_model, transmit)
        print(f"原文改写-场景分析-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            return

    # 原文改写-脉络改写
    print(10.13)
    if ChapterPoint.ORIGINAL_FRAMEWORK.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.15)
        original_framework_chapter_polish(chapter_model, transmit)
        print(f"原文改写-脉络改写-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            return

    # 番外章节-场景分析
    print(10.16)
    if ChapterPoint.EXTRA_SCENE.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.18)
        extra_scene_chapter_plish(chapter_model, transmit)
        print(f"番外章节-场景分析-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            return

    # 番外章节-脉络生成
    print(10.19)
    if ChapterPoint.EXTRA_FRAMEWORK.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.21)
        extra_framework_chapter_polish(chapter_model, transmit)
        print(f"番外章节-脉络生成-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            return

    # 润色章节
    print(10.22)
    if ChapterPoint.POLISH_CONTENT.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.24)
        polish_chapter_polish(chapter_model, transmit)
        print(f"润色章节-处理完成")
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            return

    ## 关系分析
    print(10.04)
    if ChapterPoint.RELATION_ANALYSIS.value == chapter_model.point and ChapterStatus.FAIL.value != chapter_model.status:
        print(10.06)
        relation_chapter_polish(chapter_model, transmit)
        print(f"关系分析-处理完成")



def get_before_novel(chapter_model: ChapterBO, transmit):
    """
    获取前述剧情
    """
    # 获取前几章内容
    chapter_model.before_content = ""
    chapter_before_list = query_before_chapter(chapter_model.project_id, chapter_model.sort, transmit.polish_before_num)
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
                        novel_resume = chapter_novel_resume(chapter_model, before_model.old_content, transmit)
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
                    novel_resume = chapter_novel_resume(chapter_model, before_model.new_content, transmit)
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

def get_after_novel(chapter_model, transmit):
    """
    获取后续剧情简述
    """
    chapter_model.after_content = ""
    chapter_after_list = query_after_chapter(chapter_model.project_id, chapter_model.sort, transmit.polish_after_num)
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
                        novel_resume = chapter_novel_resume(chapter_model, after_model.old_content, transmit)
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
                    novel_resume = chapter_novel_resume(chapter_model, after_model.new_content, transmit)
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