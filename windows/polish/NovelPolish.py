from config.GlobalMap import APP_STATE
from pojo.polish.PolishTransmit import Transmit
from pojo.table.Chapter import sqliteToChapter, ChapterPoint, ChapterStatus, ChapterType
from sqlite.ChapterDB import query_next_wait_polish_chapter, query_chapter_by_id, query_before_chapter, query_after_chapter, \
    update_chapter_status, update_chapter_sort, insert_extra_chapter, update_original_resume, update_polish_resume
from sqlite.ProjectDB import edit_project_status
from windows.polish.ChapterPolish import role_chapter_polish, relation_chapter_polish, process_chapter_polish, \
    original_scene_chapter_polish, original_framework_chapter_polish, extra_scene_chapter_plish, polish_chapter_polish, \
    extra_framework_chapter_polish, chapter_novel_resume, polish_chapter_repetition


def polish(transmit: Transmit):
    """润色小说"""
    # 循环润色章节，按序号获取
    while True:
        chapter_list = query_next_wait_polish_chapter(transmit.project_id)
        if chapter_list is None or len(chapter_list) <= 0:
            break

        chapter = chapter_list[0]
        # 初始化章节状态
        update_chapter_status(ChapterStatus.RUNNING.value, chapter['id'])
        ## 获取最新章节信息
        temp_chapter = query_chapter_by_id(chapter['id'])
        chapter_model = sqliteToChapter(temp_chapter)
        transmit.chapter_model = chapter_model
        # 更新列表
        transmit.reflushPolishPage()
        transmit.runningLog(f"开始处理新的章节：{transmit.chapter_model.title}")
        # 前述剧情简述
        if not transmit.isChapterPolishFail():
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理滑动窗口前述剧情内容")
            get_before_novel(transmit)
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成滑动窗口前述剧情内容，长度为：{len(transmit.chapter_model.before_content)}")

        # 后续剧情简述
        if not transmit.isChapterPolishFail():
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理滑动窗口后续剧情内容")
            get_after_novel(transmit)
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成滑动窗口后续剧情内容，长度为：{len(transmit.chapter_model.after_content)}")

        ## 角色分析
        if ChapterPoint.ROLE_ANALYSIS.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理角色分析节点")
            role_chapter_polish(transmit)
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成角色分析节点")
            transmit.reflushPolishPage()

        ## 流程控制
        is_extra = False
        if ChapterPoint.PROCESS_CHOOSES.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理流程控制节点")
            is_extra = process_chapter_polish(transmit)
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成流程控制节点")
            transmit.reflushPolishPage()

            ### 进行番外内容扩充
            if is_extra:
                transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外扩写处理开始")

                ### 更新全部章节序号
                update_chapter_sort(transmit.chapter_model.sort, transmit.project_id)
                transmit.runningLog(f"章节：{transmit.chapter_model.title} 后续章节序号处理完毕")

                ### 新增番外章节
                extra_chapter_id = insert_extra_chapter(transmit.chapter_model)
                transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外章节新增完成")
                transmit.reflushPolishPage()
                transmit.chapter_model.sort += 1

                ### 获取番外章节信息
                extra_chapter = query_chapter_by_id(extra_chapter_id)
                extra_model = sqliteToChapter(extra_chapter)

                ### 处理番外章节
                if extra_chapter:
                    transmit.runningLog(f"暂停 {transmit.chapter_model.title} 章节，开始处理番外章节：{extra_model.title}")
                    transmit.chapter_model = extra_model

                    # 更新新的当前章节
                    transmit.runningLog(f"章节：{extra_model.title} 开始处理滑动窗口前述剧情内容")
                    get_before_novel(transmit)
                    transmit.runningLog(f"章节：{extra_model.title} 处理完成滑动窗口前述剧情内容，长度为：{len(extra_model.before_content)}")

                    # 后续剧情-置空，重新处理
                    transmit.runningLog(f"章节：{extra_model.title} 开始处理滑动窗口后续剧情内容")
                    get_after_novel(transmit)
                    transmit.runningLog(f"章节：{extra_model.title} 处理完成滑动窗口后续剧情内容，长度为：{len(extra_model.after_content)}")

                    # 处理
                    after_chapter_polish(transmit)
                    extra_status_str = "处理失败" if transmit.isChapterPolishFail() else "处理完成"
                    transmit.runningLog(f"章节：{extra_model.title} {extra_status_str}")
                    # 更新会原来的章节
                    transmit.chapter_model = chapter_model

        #  滑动窗口内容更新
        if is_extra:
            transmit.runningLog(f"继续 {transmit.chapter_model.title} 章节，重新处理滑动窗口内容")
            transmit.chapter_model.before_content = None
            transmit.chapter_model.after_content = None

            # 前述剧情
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理滑动窗口前述剧情内容")
            get_after_novel(transmit)
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成滑动窗口前述剧情内容，长度为：{len(transmit.chapter_model.before_content)}")

            # 后续剧情
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理滑动窗口后续剧情内容")
            get_before_novel(transmit)
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成滑动窗口后续剧情内容，长度为：{len(transmit.chapter_model.after_content)}")

        ## 后续流程
        after_chapter_polish(transmit)
        original_status_str = "处理失败" if transmit.isChapterPolishFail() else "处理完成"
        transmit.runningLog(f"章节：{transmit.chapter_model.title} {original_status_str}")

        if transmit.isStopThread():
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理终止")
            return

    # 更新项目ID
    edit_project_status(transmit.project_id, 3)
    # 更行公共状态
    APP_STATE[transmit.project_id] = 3
    # 更新列表
    transmit.runningLog("项目章节全部处理完毕")
    transmit.reflushPolishPage()

def after_chapter_polish(transmit):
    """剩余流程章节处理"""

    # 原文改写-场景分析
    if ChapterPoint.ORIGINAL_SCENE.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理原文改写-场景分析节点")
        original_scene_chapter_polish(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成原文改写-场景分析节点")
        transmit.reflushPolishPage()

    # 原文改写-脉络改写
    if ChapterPoint.ORIGINAL_FRAMEWORK.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理原文改写-脉络改写节点")
        original_framework_chapter_polish(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成原文改写-脉络改写节点")
        transmit.reflushPolishPage()

    # 番外章节-场景分析
    if ChapterPoint.EXTRA_SCENE.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理番外撰写-场景分析节点")
        extra_scene_chapter_plish(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成番外撰写-场景分析节点")
        transmit.reflushPolishPage()

    # 番外章节-脉络生成
    if ChapterPoint.EXTRA_FRAMEWORK.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理番外撰写-脉络生成节点")
        extra_framework_chapter_polish(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成番外撰写-脉络生成节点")
        transmit.reflushPolishPage()

    # 润色章节
    if ChapterPoint.POLISH_CONTENT.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理结果润色节点")
        polish_chapter_polish(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成结果润色节点")
        transmit.reflushPolishPage()

    # 内容重复整理
    if ChapterPoint.REPETITION_ORGANIZE.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理内容重复整理节点")
        polish_chapter_repetition(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成内容重复整理节点")
        transmit.reflushPolishPage()

    ## 关系分析
    if ChapterPoint.RELATION_ANALYSIS.value == transmit.chapter_model.point and not transmit.isChapterPolishFail():
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始处理关系分析整理节点")
        relation_chapter_polish(transmit)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 处理完成关系分析整理节点")
        transmit.reflushPolishPage()



def get_before_novel(transmit):
    """
    获取前述剧情
    """
    # 获取前几章内容
    transmit.chapter_model.before_content = ""
    chapter_before_list = query_before_chapter(transmit.project_id, transmit.chapter_model.sort, transmit.polish_before_num)
    if chapter_before_list:
        # 附带章节数
        before_len = len(chapter_before_list)
        for chapter_before in chapter_before_list:
            # 章节数
            before_len -= 1
            # 转换
            transmit.temp_model = sqliteToChapter(chapter_before)
            # 判断是否最后一个章节
            if before_len < 1 and ChapterType.EXTRA_GENERATE.value == transmit.chapter_model.type:
                if transmit.temp_model.new_content is None or len(transmit.temp_model.new_content) < 1:
                    ## 不存在原文信息
                    if transmit.temp_model.old_content is None or len(transmit.temp_model.old_content) < 1:
                        continue
                    else:
                        transmit.runningLog(f"番外章节：{transmit.chapter_model.title} 前述章节：{transmit.temp_model.title} 原文内容长度：{len(transmit.temp_model.old_content)}")
                        transmit.chapter_model.before_content += transmit.temp_model.old_content
                else:
                    transmit.runningLog(f"番外章节：{transmit.chapter_model.title} 前述章节：{transmit.temp_model.title} 改写内容长度：{len(transmit.temp_model.new_content)}")
                    transmit.chapter_model.before_content += transmit.temp_model.new_content
                continue

            # 不存在润色结果内容
            if transmit.temp_model.new_content is None or len(transmit.temp_model.new_content) < 1:
                ## 不存在原文信息
                if transmit.temp_model.old_content is None or len(transmit.temp_model.old_content) < 1:
                    continue
                ## 存在原文信息
                else:
                    ### 不存在原文简述
                    if transmit.temp_model.original_resume is None or len(transmit.temp_model.original_resume) < 1:
                        #### 对原文进行简述
                        transmit.runningLog(f"前述章节：{transmit.temp_model.title} 原文内容简述开始，原始长度：{len(transmit.temp_model.old_content)}")
                        novel_resume = chapter_novel_resume(transmit.temp_model.old_content, transmit)
                        if transmit.isChapterPolishFail():
                            return
                        else:
                            ##### 更新原文简述
                            transmit.runningLog(f"前述章节：{transmit.temp_model.title} 原文内容简述完成，简述长度：{len(novel_resume)}")
                            update_original_resume(novel_resume, transmit.temp_model.id)
                            transmit.chapter_model.before_content += novel_resume
                            continue
                    ### 存在原文简述
                    else:
                        transmit.chapter_model.before_content += transmit.temp_model.original_resume
                        continue
            # 存在润色结果内容
            else:
                ## 不存在润色简述
                if transmit.temp_model.polish_resume is None or len(transmit.temp_model.polish_resume) < 1:
                    ### 对结果进行简述
                    transmit.runningLog(f"前述章节：{transmit.temp_model.title} 改写内容简述开始，原始长度：{len(transmit.temp_model.new_content)}")
                    novel_resume = chapter_novel_resume(transmit.temp_model.new_content, transmit)
                    if transmit.isChapterPolishFail():
                        return
                    else:
                        #### 更新结果简述
                        transmit.runningLog(f"前述章节：{transmit.temp_model.title} 改写内容简述完成，简述长度：{len(novel_resume)}")
                        update_polish_resume(novel_resume, transmit.temp_model.id)
                        transmit.chapter_model.before_content += novel_resume
                        continue
                ## 存在润色简述
                else:
                    transmit.chapter_model.before_content += transmit.temp_model.polish_resume
                    continue

def get_after_novel(transmit):
    """
    获取后续剧情简述
    """
    transmit.chapter_model.after_content = ""
    chapter_after_list = query_after_chapter(transmit.project_id, transmit.chapter_model.sort, transmit.polish_after_num)
    if chapter_after_list:
        # 是否首条内容，番外章节 首个章节内容不使用简述剧情，否则世界观会出现错误
        first_chapter = ChapterType.EXTRA_GENERATE.value == transmit.chapter_model.type
        for chapter_after in chapter_after_list:
            # 转换
            transmit.temp_model = sqliteToChapter(chapter_after)

            # 首条处理
            if first_chapter:
                # 不存在润色结果内容
                if transmit.temp_model.new_content is None or len(transmit.temp_model.new_content) < 1:
                    ## 不存在原文信息
                    if transmit.temp_model.old_content is None or len(transmit.temp_model.old_content) < 1:
                        continue
                    else:
                        transmit.runningLog(f"番外章节：{transmit.chapter_model.title} 后续章节：{transmit.temp_model.title} 原文内容长度：{len(transmit.temp_model.old_content)}")
                        transmit.chapter_model.after_content += transmit.temp_model.old_content
                else:
                    transmit.runningLog(f"番外章节：{transmit.chapter_model.title} 后续章节：{transmit.temp_model.title} 改写内容长度：{len(transmit.temp_model.new_content)}")
                    transmit.chapter_model.after_content += transmit.temp_model.new_content
                first_chapter = False
                continue

            # 不存在润色结果内容
            if transmit.temp_model.new_content is None or len(transmit.temp_model.new_content) < 1:
                ## 不存在原文信息
                if transmit.temp_model.old_content is None or len(transmit.temp_model.old_content) < 1:
                    continue
                ## 存在原文信息
                else:
                    ### 不存在原文简述
                    if transmit.temp_model.original_resume is None or len(transmit.temp_model.original_resume) < 1:
                        #### 对原文进行简述
                        transmit.runningLog(f"后续章节：{transmit.temp_model.title} 原文内容简述开始，原始长度：{len(transmit.temp_model.old_content)}")
                        novel_resume = chapter_novel_resume(transmit.temp_model.old_content, transmit)
                        if transmit.isChapterPolishFail():
                            return
                        else:
                            ##### 更新原文简述
                            transmit.runningLog(f"后续章节：{transmit.temp_model.title} 原文内容简述完成，简述长度：{len(novel_resume)}")
                            update_original_resume(novel_resume, transmit.temp_model.id)
                            transmit.chapter_model.after_content += novel_resume
                            continue
                    ### 存在原文简述
                    else:
                        transmit.chapter_model.after_content += transmit.temp_model.original_resume
                        continue
            # 存在润色结果内容
            else:
                ## 不存在润色简述
                if transmit.temp_model.polish_resume is None or len(transmit.temp_model.polish_resume) < 1:
                    ### 对结果进行简述
                    transmit.runningLog(f"后续章节：{transmit.temp_model.title} 改写内容简述开始，原始长度：{len(transmit.temp_model.new_content)}")
                    novel_resume = chapter_novel_resume(transmit.temp_model.new_content, transmit)
                    if transmit.isChapterPolishFail():
                        return
                    else:
                        #### 更新结果简述
                        transmit.runningLog(f"后续章节：{transmit.temp_model.title} 改写内容简述完成，简述长度：{len(novel_resume)}")
                        update_polish_resume(novel_resume, transmit.temp_model.id)
                        transmit.chapter_model.after_content += novel_resume
                        continue
                ## 存在润色简述
                else:
                    transmit.chapter_model.after_content += transmit.temp_model.polish_resume
                    continue