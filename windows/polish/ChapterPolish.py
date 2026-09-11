import asyncio
import re
from itertools import combinations

from json_repair import repair_json
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from pojo.polish.PolishTransmit import Transmit
from pojo.process.ProcessPromptResult import ProcessPromptResult
from pojo.relation import RelationPromptResult
from pojo.role import RolePromptResult
from pojo.scene.ScenePromptResult import ScenePromptResult
from pojo.table.Chapter import ChapterPoint, ChapterStatus, ChapterType
from sqlite.ChapterDB import update_chapter_role, update_chapter_status, update_chapter_relation, \
    update_chapter_process, update_chapter_scene, update_chapter_framework, update_chapter_polish, \
    update_chapter_relation_and_point, update_chapter_success, update_chapter_repetition, \
    update_chapter_scene_not_polish
from sqlite.RoleRelationDB import query_role_model, \
    query_role_relation, remove_old_role_model, insert_role_model, remove_old_role_relation, insert_role_relation, \
    query_family_role, query_family_relation_name_a, query_family_relation_name_b
from stream.LlmStreamRetryable import RetryableStreamChain
from stream.LlmStreamValidator import StreamingValidator
from windows.polish.DynamicPromptTemplate import get_role_prompt_template, get_relation_prompt_template, \
    get_process_prompt_template, get_original_scene_prompt_template, get_original_framework_prompt_template, \
    get_polish_prompt_template, get_extra_scene_prompt_template, get_extra_framework_prompt_template, \
    get_novel_resume_template, get_repetition_prompt_template


def is_valid_chinese_text(text: str, max_english_ratio: float = 0.3) -> tuple[bool, float]:
    """
    校验文本是否包含过多的英文字符。

    Args:
        text: 待校验的文本
        max_english_ratio: 允许的最大英文字符占比（0.0 - 1.0），默认 30%

    Returns:
        (是否通过校验, 实际的英文占比)
    """
    if not isinstance(text, str) or not text.strip():
        return False, 0.0

    # 去除所有的空白字符（空格、换行、制表符等），只计算有效字符
    clean_text = re.sub(r'\s+', '', text)
    total_chars = len(clean_text)

    if total_chars == 0:
        return False, 0.0

    # 统计英文字母（a-z, A-Z）的数量
    english_chars = len(re.findall(r'[a-zA-Z]', clean_text))
    english_ratio = english_chars / total_chars

    # 如果英文占比超过阈值，则判定为无效
    is_valid = english_ratio <= max_english_ratio
    return is_valid, english_ratio

def role_chapter_polish(transmit: Transmit, for_num=1):
    """角色分析处理"""
    # 角色分析
    try:
        role_chain = (
                RunnableLambda(get_role_prompt_template) |
                transmit.role_llm.with_structured_output(RolePromptResult.RoleResult)
        )
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 角色分析开始，尝试次数：{for_num}")
        role = role_chain.invoke({
            "original_text": transmit.chapter_model.old_content,
            "role_prompt_system": transmit.role_system,
            "role_prompt_user": transmit.role_user
        })
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 角色分析结束")
        role_data = RolePromptResult.RoleResult.model_validate(role)
        # 章节数据更新
        update_chapter_role(role_data.model_dump_json(), transmit.chapter_model.id)
        transmit.chapter_model.role_content = role_data.model_dump_json()
        transmit.chapter_model.point = ChapterPoint.PROCESS_CHOOSES.value
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 角色分析异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return
        else:
            role_chapter_polish(transmit, for_num + 1)
            return

def relation_chapter_polish(transmit: Transmit, for_num=1):
    """关系分析处理"""
    try:
        # 番外章节无需进行分析
        if transmit.chapter_model.type == ChapterType.EXTRA_GENERATE.value:
            update_chapter_success(transmit.chapter_model.id)
            transmit.chapter_model.point = ChapterPoint.SUCCESS.value
            transmit.chapter_model.status = ChapterStatus.SUCCESS.value
            return

        # 关系分析
        relation_chain = (
            RunnableLambda(get_relation_prompt_template) |
            transmit.relation_llm |
            StrOutputParser()
        )
        # 查询角色信息
        relation_json = get_current_role_relation(transmit)
        # 查询
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 关系分析开始，尝试次数：{for_num}")
        relation = relation_chain.invoke({
            "relation_prompt_system": transmit.relation_system,
            "relation_prompt_user": transmit.relation_user,
            "original_text": transmit.chapter_model.old_content,
            "db_role_json": str(relation_json),
            "male_lead": str(transmit.male_lead),
            "heroine": str(transmit.heroine)
        })
        raw_text = relation.content if hasattr(relation, 'content') else str(relation)
        raw_text = raw_text.replace("```json", "").replace("```", "")
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 关系分析结束")
        try:
            relation_data = RelationPromptResult.RelationPromptResult.model_validate_json(raw_text)
        except Exception as e:
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 关系分析解析异常：{e}")
            # 手动尝试解析
            raw_text = repair_json(raw_text)
            relation_data = RelationPromptResult.RelationPromptResult.model_validate_json(raw_text)
        # 更新角色关联信息
        if relation_data.角色数组:
            for role in relation_data.角色数组:
                # 删除旧的角色信息
                remove_old_role_model(transmit.project_id, role.名称)
                # 新增角色信息
                is_family = 1
                if role.主角女性亲友 is None:
                    is_family = 2
                elif not role.主角女性亲友:
                    is_family = 2
                insert_role_model(transmit.project_id, role.名称, is_family, role.model_dump_json())
        # 关联关系更新
        if relation_data.角色关系:
            for relation in relation_data.角色关系:
                # 删除旧的关系
                remove_old_role_relation(transmit.project_id, relation.角色A, relation.角色B)
                # 新增角色关系
                insert_role_relation(transmit.project_id, relation.角色A, relation.角色B, relation.model_dump_json())
        # 更新
        update_chapter_relation_and_point(relation_data.model_dump_json(), transmit.chapter_model.id)
        transmit.chapter_model.point = ChapterPoint.SUCCESS.value
        transmit.chapter_model.status = ChapterStatus.SUCCESS.value
        transmit.chapter_model.relation_content = relation_data.model_dump_json()
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 关系分析异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return
        if 3 == for_num:
            update_chapter_status(4, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return
        else:
            relation_chapter_polish(transmit, for_num + 1)
            return

def get_current_role_relation(transmit: Transmit):
    """
    获取角色信息
    """
    transmit.runningLog(f"章节：{transmit.chapter_model.title} 开始获取最新角色与关联信息")
    # 获取角色信息
    relation_data = RelationPromptResult.RelationPromptResult(角色数组=[], 角色关系=[])
    ## 角色信息与关系补充
    role_data = RolePromptResult.RoleResult.model_validate_json(transmit.chapter_model.role_content)
    if role_data and role_data.character_list:
        role_names = []

        ### 抽取全部角色
        for character in role_data.character_list:
            if character:
                character_name = character.character_name
                if character_name:
                    role_names.append(character_name)
        ### 循环查询
        if role_names:
            role_list = query_role_model(transmit.project_id, role_names)
            if role_list:
                for role in role_list:
                    if role and role['role_json']:
                        relation_data.角色数组.append(RelationPromptResult.CharacterResult.model_validate_json(role['role_json']))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 获取到{len(relation_data.角色数组)}条角色信息")

        ### 关联关系补充
        if role_names and len(role_names) > 1:
            pairs = list(combinations(role_names, 2))
            for a, b in pairs:
                relation_json = query_role_relation(transmit.project_id, a, b)
                if relation_json:
                    relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(relation_json['relation']))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 获取到{len(relation_data.角色关系)}条关系信息")
    return relation_data.model_dump_json()

def process_chapter_polish(transmit: Transmit, for_num=1):
    try:
        """流程控制处理"""
        # 若小于流程直接跳到原文改写
        if transmit.chapter_model.sort <= transmit.extra_start_num:
            update_chapter_process("{}", ChapterPoint.ORIGINAL_SCENE.value, transmit.chapter_model.id)
            transmit.chapter_model.point = ChapterPoint.ORIGINAL_SCENE.value
            transmit.chapter_model.process_content = "{}"
            return False

        # 获取最新角色信息
        relation_json = get_current_role_relation(transmit)
        # 更新关联关系
        update_chapter_relation(relation_json, transmit.chapter_model.id)
        transmit.chapter_model.relation_content = relation_json
        process_chain = (
            RunnableLambda(get_process_prompt_template) |
            transmit.process_llm |
            StrOutputParser()
        )
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 流程控制开始，尝试次数：{for_num}")
        process = process_chain.invoke({
            "relation_analysis": relation_json,
            "process_prompt_system": transmit.process_system,
            "process_prompt_user": transmit.process_user,
            "reference_before_text": transmit.chapter_model.before_content,
            "original_text": transmit.chapter_model.old_content,
            "reference_after_text": transmit.chapter_model.after_content
        })
        raw_text = process.content if hasattr(process, 'content') else str(process)
        raw_text = raw_text.replace("```json", "").replace("```", "")
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 流程控制结束，长度为：{raw_text}")
        process_data = ProcessPromptResult.model_validate_json(raw_text)
        # 判断
        if process_data is None:
            update_chapter_status(4, transmit.chapter_model.id)
            return False
        # 更新
        extra = process_data.extra
        if transmit.chapter_model.sort <= transmit.extra_start_num:
            extra = "false"
        # 更新文本
        update_chapter_process(process_data.model_dump_json(), ChapterPoint.ORIGINAL_SCENE.value, transmit.chapter_model.id)
        transmit.chapter_model.point = ChapterPoint.ORIGINAL_SCENE.value
        transmit.chapter_model.process_content = process_data.model_dump_json()
        # 状态判断
        if "true" in str(extra).lower():
            return True
        else:
            return False
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 流程控制异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return False
        if 3 == for_num:
            update_chapter_status(4, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return False
        else:
            return process_chapter_polish(transmit, for_num + 1)

def original_scene_chapter_polish(transmit: Transmit, for_num=1):
    try:
        """原文改写-场景分析"""
        original_chain = (
            RunnableLambda(get_original_scene_prompt_template) |
            transmit.original_scene_llm.with_structured_output(ScenePromptResult)
        )
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-场景分析开始，尝试次数：{for_num}")
        original_scene = original_chain.invoke({
            "relation_analysis": transmit.chapter_model.relation_content,
            "original_scene_prompt_system": transmit.original_scene_system,
            "original_scene_prompt_user": transmit.original_scene_user,
            "original_text": transmit.chapter_model.old_content,
            "scene_list": str(transmit.original_scene_identity)
        })
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-场景分析结束")
        # 格式校验
        scene = ScenePromptResult.model_validate(original_scene)
        # 更新状态
        if scene.is_polish:
            update_chapter_scene(scene.model_dump_json(), ChapterPoint.ORIGINAL_FRAMEWORK.value, transmit.chapter_model.id)
            transmit.chapter_model.point = ChapterPoint.ORIGINAL_FRAMEWORK.value
            transmit.chapter_model.scene_content = scene.model_dump_json()
        else:
            update_chapter_scene_not_polish(scene.model_dump_json(), transmit.chapter_model.id)
            transmit.chapter_model.point = ChapterPoint.RELATION_ANALYSIS.value
            transmit.chapter_model.scene_content = scene.model_dump_json()
            transmit.chapter_model.polish_resume = transmit.chapter_model.original_resume
        return True
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-场景分析异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return False
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return False
        else:
            return original_scene_chapter_polish(transmit, for_num + 1)

async def generate_stream_polish(chain, inputs, old_len, transmit: Transmit, msg):
    stream_chain = RetryableStreamChain(
        chain=chain,
        validator_factory=lambda : StreamingValidator(
            window_size=150,
            similarity_threshold=0.75,
            max_repeat_streak=2
        ),
        on_chunk=lambda text, one_chunk: transmit.project_bridge.stream_out.emit(transmit.project_id, text, one_chunk), # 实时打印
        on_retry=lambda log: transmit.runningLog(f"章节：{transmit.chapter_model.title} {msg}流式输出：{log}"),
        project_id=transmit.project_id
    )
    try:
        result = await stream_chain.ainvoke_with_retry(inputs, old_len=old_len)
        transmit.runningLog(f"章节：{transmit.chapter_model.title} {msg}流式输出长度为：{len(result)}")
        return result

    except RuntimeError as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} {msg}流式输出异常：{e}")
        return ""

def original_framework_chapter_polish(transmit, for_num=1):
    try:
        """原文改写-脉络改写"""
        scene = ScenePromptResult.model_validate_json(transmit.chapter_model.scene_content)
        # 获取场景map
        original_analysis_text = {}
        for analysis in scene.scene_list:
            scene = transmit.original_scene_polish.get(analysis)
            original_analysis_text[analysis] = scene

        # 脉络修改
        original_framework_chain = (
            RunnableLambda(get_original_framework_prompt_template) |
            transmit.original_framework_llm |
            StrOutputParser()
        )
        old_len = len(transmit.chapter_model.old_content) if transmit.chapter_model.old_content is not None else 3500
        inputs = {
            "relation_analysis": transmit.chapter_model.relation_content,
            "framework_analysis": str(original_analysis_text),
            "system_prompt": transmit.original_framework_system,
            "user_prompt": transmit.original_framework_user,
            "reference_before_text": transmit.chapter_model.before_content,
            "original_text": transmit.chapter_model.old_content,
            "reference_after_text": transmit.chapter_model.after_content,
            "male_lead": transmit.male_lead,
            "heroine": transmit.heroine,
            "target_num": old_len
        }
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-脉络改写开始，尝试次数：{for_num}")
        raw_text = asyncio.run(generate_stream_polish(original_framework_chain, inputs, old_len, transmit, "原文改写-脉络改写"))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-脉络改写结束，长度为：{len(raw_text)}")

        # 英文含量校验
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-脉络改写英文占比校验失败，英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                original_framework_chapter_polish(transmit, for_num + 1)
            return

        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == transmit.chapter_model.type and len(raw_text) < len(transmit.chapter_model.old_content):
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-脉络生成内容长度低于阈值：{old_len}")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                original_framework_chapter_polish(transmit, for_num + 1)
            return

        # 更新状态
        update_chapter_framework(raw_text, ChapterPoint.POLISH_CONTENT.value, transmit.chapter_model.id)
        transmit.chapter_model.point = ChapterPoint.POLISH_CONTENT.value
        transmit.chapter_model.framework_content = raw_text
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 原文改写-脉络生成异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return
        else:
            original_framework_chapter_polish(transmit, for_num + 1)
            return

def get_family_json(transmit: Transmit):
    relation_data = RelationPromptResult.RelationPromptResult(角色关系=[], 角色数组=[])
    # 获取主角女性亲友信息
    family_list = query_family_role(transmit.project_id)
    if family_list:
        ## 循环处理
        role_names = []
        for family in family_list:
            role_names.append(family['role_name'])
            relation_data.角色数组.append(RelationPromptResult.CharacterResult.model_validate_json(family['role_json']))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-场景分析：获取到男主角{len(relation_data.角色数组)}位亲友信息")
        ## 关系补充
        if role_names and len(role_names) > 0:
            names_a = query_family_relation_name_a(transmit.project_id, role_names)
            if names_a:
                for item in names_a:
                    relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(item['relation']))
            names_b = query_family_relation_name_b(transmit.project_id, role_names)
            if names_b:
                for item in names_b:
                    relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(item['relation']))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-场景分析：获取到男主角亲友{len(relation_data.角色关系)}条关系信息")
    return relation_data.model_dump_json()

def extra_scene_chapter_plish(transmit: Transmit, for_num=1):
    try:
        """番外章节-场景分析"""
        relation_json = get_family_json(transmit)
        # 更新relation
        update_chapter_relation(relation_json, transmit.chapter_model.id)
        transmit.chapter_model.relation_content = relation_json
        extra_scene_chain = (
            RunnableLambda(get_extra_scene_prompt_template) |
            transmit.extra_scene_llm.with_structured_output(ScenePromptResult)
        )
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-场景分析开始，尝试次数：{for_num}")
        extra_scene = extra_scene_chain.invoke({
                "extra_scene_prompt_system": transmit.extra_scene_system,
                "extra_scene_prompt_user": transmit.extra_scene_user,
                "reference_before_text": transmit.chapter_model.before_content,
                "reference_after_text": transmit.chapter_model.after_content,
                "relation_analysis": transmit.chapter_model.relation_content,
                "process_analysis": transmit.chapter_model.process_content,
                "scene_list": str(transmit.extra_scene_identify)
        })
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-场景分析结束")
        # 格式校验
        scene = ScenePromptResult.model_validate(extra_scene)
        # 更新信息
        update_chapter_scene(scene.model_dump_json(), ChapterPoint.EXTRA_FRAMEWORK.value, transmit.chapter_model.id)
        transmit.chapter_model.scene_content = scene.model_dump_json()
        transmit.chapter_model.point = ChapterPoint.EXTRA_FRAMEWORK.value
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-场景分析异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
        else:
            extra_scene_chapter_plish(transmit, for_num + 1)

def extra_framework_chapter_polish(transmit, for_num=1):
    try:
        """番外章节-脉络生成"""
        scene = ScenePromptResult.model_validate_json(transmit.chapter_model.scene_content)
        # 获取场景map
        extra_analysis_text = {}
        for extra_scene in scene.scene_list:
            scene = transmit.extra_scene_polish.get(extra_scene)
            extra_analysis_text[extra_scene] = scene

        extra_framework_chain = (
                RunnableLambda(get_extra_framework_prompt_template) |
                transmit.extra_framework_llm |
                StrOutputParser()
        )
        old_len = len(transmit.chapter_model.old_content) if transmit.chapter_model.old_content is not None else 3500
        # 英文含量校验
        inputs = {
            "system_prompt": transmit.extra_framework_system,
            "user_prompt": transmit.extra_framework_user,
            "framework_analysis": str(extra_analysis_text),
            "reference_before_text": transmit.chapter_model.before_content,
            "reference_after_text": transmit.chapter_model.after_content,
            "relation_analysis": transmit.chapter_model.relation_content,
            "create_framework_text": transmit.chapter_model.process_content,
            "male_lead": transmit.male_lead,
            "heroine": transmit.heroine,
            "target_num": old_len
        }
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-脉络生成开始，尝试次数：{for_num}")
        raw_text = asyncio.run(generate_stream_polish(extra_framework_chain, inputs, old_len, transmit, "番外章节-脉络生成"))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-脉络生成结束，长度为：{len(raw_text)}")

        # 英文校验
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-脉络生成英文占比校验失败，英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                extra_framework_chapter_polish(transmit, for_num + 1)
            return

        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == transmit.chapter_model.type and len(raw_text) < len(transmit.chapter_model.old_content):
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-脉络生成内容长度低于阈值：{old_len}")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                extra_framework_chapter_polish(transmit, for_num + 1)
            return

        # 更新状态
        update_chapter_framework(raw_text, ChapterPoint.POLISH_CONTENT.value, transmit.chapter_model.id)
        transmit.chapter_model.framework_content = raw_text
        transmit.chapter_model.point = ChapterPoint.POLISH_CONTENT.value
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 番外撰写-脉络生成异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return
        else:
            extra_framework_chapter_polish(transmit, for_num + 1)
            return

def polish_chapter_polish(transmit, for_num=1):
    try:
        polish_chain = (
            RunnableLambda(get_polish_prompt_template) |
            transmit.polish_llm |
            StrOutputParser()
        )
        old_len = len(transmit.chapter_model.old_content) if transmit.chapter_model.old_content is not None else 3500
        # 英文含量校验
        inputs = {
            "system_prompt": transmit.polish_system,
            "user_prompt": transmit.polish_user,
            "original_framework_text": transmit.chapter_model.framework_content,
            "male_lead": transmit.male_lead,
            "heroine": transmit.heroine,
            "target_num": old_len
        }
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 结果润色开始，尝试次数：{for_num}")
        raw_text = asyncio.run(generate_stream_polish(polish_chain, inputs, old_len, transmit, "结果润色"))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 结果润色结束，长度为：{len(raw_text)}")

        # 英文校验
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 结果润色英文占比校验失败，英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                polish_chapter_polish(transmit, for_num + 1)
            return

        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == transmit.chapter_model.type and len(raw_text) < len(transmit.chapter_model.old_content):
            print(f"结果润色-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                polish_chapter_polish(transmit, for_num + 1)
            return

        # 更新状态
        update_chapter_polish(raw_text, transmit.chapter_model.id)
        transmit.chapter_model.point = ChapterPoint.RELATION_ANALYSIS.value
        transmit.chapter_model.new_content = raw_text
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 结果润色异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return
        else:
            polish_chapter_polish(transmit, for_num + 1)
            return

def polish_chapter_repetition(transmit, for_num=1):
    """去重整理"""
    try:
        repetition_chain = (
            RunnableLambda(get_repetition_prompt_template) |
            transmit.polish_llm |
            StrOutputParser()
        )
        inputs = {
            "polish_text": transmit.chapter_model.new_content
        }
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 内容重复整理开始，尝试次数：{for_num}")
        raw_text = asyncio.run(generate_stream_polish(repetition_chain, inputs, len(transmit.chapter_model.new_content), transmit, "内容重复整理"))
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 内容重复整理结束，长度为：{raw_text}")

        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 内容重复整理英文占比校验失败，英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_repetition(transmit, for_num + 1)
            return

        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == transmit.chapter_model.type and len(raw_text) < len(transmit.chapter_model.old_content):
            transmit.runningLog(f"章节：{transmit.chapter_model.title} 内容重复整理内容长度低于阈值：{len(transmit.chapter_model.new_content)}")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
                transmit.chapterParseFail()
            else:
                polish_chapter_repetition(transmit, for_num + 1)
            return

        # 结果处理
        update_chapter_repetition(raw_text, transmit.chapter_model.id)
        transmit.chapter_model.new_content = raw_text
        transmit.chapter_model.point = ChapterPoint.RELATION_ANALYSIS.value
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.chapter_model.title} 内容重复整理异常：{e}")
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, transmit.chapter_model.id)
            transmit.chapterParseFail()
            return
        else:
            polish_chapter_repetition(transmit, for_num + 1)
            return



def chapter_novel_resume(novel_content, transmit: Transmit, for_num=1):
    """
    文本简述
    """
    try:
        novel_resume_chain = (
                RunnableLambda(get_novel_resume_template) |
                transmit.polish_llm |
                StrOutputParser()
        )
        transmit.runningLog(f"章节：{transmit.temp_model.title} 内容简述开始，尝试次数：{for_num}")
        novel_resume = novel_resume_chain.invoke({
            "reference_text": novel_content
        })
        raw_text = novel_resume.content if hasattr(novel_resume, 'content') else str(novel_resume)
        transmit.runningLog(f"章节：{transmit.temp_model.title} 内容简述结束，长度为：{len(raw_text)}")
        # 英文含量校验
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            transmit.runningLog(f"章节：{transmit.temp_model.title} 简述内容英文占比校验失败，英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                transmit.chapterParseFail()
                return novel_content
            else:
                return chapter_novel_resume(novel_content, transmit, for_num + 1)
        return raw_text
    except Exception as e:
        transmit.runningLog(f"章节：{transmit.temp_model.title} 简述异常：{e}")
        # 退出循环
        if transmit.isStopThread():
            transmit.chapterParseFail()
            return None
        if 3 == for_num:
            transmit.chapterParseFail()
            return novel_content
        else:
            return chapter_novel_resume(novel_content, transmit, for_num + 1)