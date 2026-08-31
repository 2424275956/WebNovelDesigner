import asyncio
import re
from itertools import combinations
from typing import List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import Field, BaseModel
from json_repair import repair_json

from config.GlobalMap import APP_STOP_EVENT
from pojo.process.ProcessPromptResult import ProcessPromptResult
from pojo.relation import RelationPromptResult
from pojo.role import RolePromptResult
from pojo.scene.ScenePromptResult import ScenePromptResult
from pojo.table.Chapter import ChapterBO, ChapterPoint, ChapterStatus, ChapterType
from sqlite.ChapterDB import update_chapter_role, update_chapter_status, update_chapter_relation, \
    update_chapter_process, update_chapter_scene, update_chapter_framework, update_chapter_polish, \
    update_chapter_relation_and_point, update_chapter_success, update_chapter_repetition
from sqlite.RoleRelationDB import query_role_model, \
    query_role_relation, remove_old_role_model, insert_role_model, remove_old_role_relation, insert_role_relation, \
    query_family_role, query_family_relation_name_a, query_family_relation_name_b
from windows.polish.DynamicPromptTemplate import get_role_prompt_template, get_relation_prompt_template, \
    get_process_prompt_template, get_original_scene_prompt_template, get_original_framework_prompt_template, \
    get_polish_prompt_template, get_extra_scene_prompt_template, get_extra_framework_prompt_template, \
    get_novel_resume_template, get_repetition_prompt_template
from stream.LlmStreamRetryable import RetryableStreamChain
from stream.LlmStreamValidator import StreamingValidator
import json

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

def role_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    """角色分析处理"""
    # 角色分析
    try:
        print("角色分析-LangChain链构建")
        role_chain = (
                RunnableLambda(get_role_prompt_template) |
                transmit.role_llm.with_structured_output(RolePromptResult.RoleResult)
        )
        print(f"角色分析-LangChain链Invoke数据填充")
        role = role_chain.invoke({
            "original_text": chapter_model.old_content,
            "role_prompt_system": transmit.role_system,
            "role_prompt_user": transmit.role_user
        })
        print(101)
        role_data = RolePromptResult.RoleResult.model_validate(role)
        print(str(role_data))
        # 章节数据更新
        update_chapter_role(role_data.model_dump_json(), chapter_model.id)
        chapter_model.role_content = role_data.model_dump_json()
        chapter_model.point = ChapterPoint.PROCESS_CHOOSES.value
        print(f"角色分析-章节信息更新完成")
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
        else:
            role_chapter_polish(chapter_model, transmit, for_num + 1)

def relation_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    """关系分析处理"""
    try:
        # 番外章节无需进行分析
        if chapter_model.type == ChapterType.EXTRA_GENERATE.value:
            update_chapter_success(chapter_model.id)
            chapter_model.point = ChapterPoint.SUCCESS.value
            chapter_model.status = ChapterStatus.SUCCESS.value
            return

        # 关系分析
        print("关系分析-LangChain链构建")
        relation_chain = (
            RunnableLambda(get_relation_prompt_template) |
            transmit.relation_llm |
            StrOutputParser()
        )
        # 查询角色信息
        relation_json = get_current_role_relation(chapter_model)
        # 查询
        print(f"关系分析-LangChain链Invoke数据填充")
        relation = relation_chain.invoke({
            "relation_prompt_system": transmit.relation_system,
            "relation_prompt_user": transmit.relation_user,
            "original_text": chapter_model.old_content,
            "db_role_json": str(relation_json),
            "male_lead": str(transmit.male_lead),
            "heroine": str(transmit.heroine)
        })
        print(2.22)
        raw_text = relation.content if hasattr(relation, 'content') else str(relation)
        raw_text = raw_text.replace("```json", "").replace("```", "")
        print(raw_text)
        try:
            relation_data = RelationPromptResult.RelationPromptResult.model_validate_json(raw_text)
        except:
            # 手动尝试解析
            raw_text = repair_json(raw_text)
            relation_data = RelationPromptResult.RelationPromptResult.model_validate_json(raw_text)
        # 更新角色关联信息
        if relation_data.角色数组:
            for role in relation_data.角色数组:
                # 删除旧的角色信息
                remove_old_role_model(chapter_model.project_id, role.名称)
                # 新增角色信息
                is_family = 1
                if role.主角女性亲友 is None:
                    is_family = 2
                elif not role.主角女性亲友:
                    is_family = 2
                insert_role_model(chapter_model.project_id, role.名称, is_family, role.model_dump_json())
        # 关联关系更新
        if relation_data.角色关系:
            for relation in relation_data.角色关系:
                # 删除旧的关系
                remove_old_role_relation(chapter_model.project_id, relation.角色A, relation.角色B)
                # 新增角色关系
                insert_role_relation(chapter_model.project_id, relation.角色A, relation.角色B, relation.model_dump_json())
        # 更新
        update_chapter_relation_and_point(relation_data.model_dump_json(), chapter_model.id)
        chapter_model.point = ChapterPoint.SUCCESS.value
        chapter_model.status = ChapterStatus.SUCCESS.value
        chapter_model.relation_content = relation_data.model_dump_json()
        print(f"关系分析-章节信息更新完成")
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return
        if 3 == for_num:
            update_chapter_status(4, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            relation_chapter_polish(chapter_model, transmit, for_num + 1)

def get_current_role_relation(chapter_model: ChapterBO):
    """
    获取角色信息
    """
    # 获取角色信息
    print(321.01)
    relation_data = RelationPromptResult.RelationPromptResult(角色数组=[], 角色关系=[])
    ## 角色信息与关系补充
    role_data = RolePromptResult.RoleResult.model_validate_json(chapter_model.role_content)
    print(321.02)
    if role_data and role_data.character_list:
        print(321.03)
        role_names = []
        print(321.04)
        ### 抽取全部角色
        for character in role_data.character_list:
            print(character.character_name)
            if character:
                print(321.05)
                character_name = character.character_name
                print(321.06)
                if character_name:
                    print(321.07)
                    role_names.append(character_name)
        ### 循环查询
        print(321.08)
        if role_names:
            print(321.09)
            role_list = query_role_model(chapter_model.project_id, role_names)
            print(321.10)
            if role_list:
                print(321.11)
                for role in role_list:
                    print(321.12)
                    if role and role['role_json']:
                        print(321.13)
                        relation_data.角色数组.append(RelationPromptResult.CharacterResult.model_validate_json(role['role_json']))
                        print(321.14)
        ### 关联关系补充
        print(321.15)
        if role_names and len(role_names) > 1:
            print(321.16)
            pairs = list(combinations(role_names, 2))
            print(321.17)
            for a, b in pairs:
                print(321.18)
                relation_json = query_role_relation(chapter_model.project_id, a, b)
                print(321.19)
                if relation_json:
                    print(321.2)
                    relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(relation_json['relation']))
                    print(321.21)
    return relation_data.model_dump_json()

def process_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    try:
        """流程控制处理"""
        # 若小于流程直接跳到原文改写
        if chapter_model.sort <= transmit.extra_start_num:
            update_chapter_process("{}", ChapterPoint.ORIGINAL_SCENE.value, chapter_model.id)
            chapter_model.point = ChapterPoint.ORIGINAL_SCENE.value
            chapter_model.process_content = "{}"
            return False
        relation_json = get_current_role_relation(chapter_model)
        # 更新关联关系
        update_chapter_relation(relation_json, chapter_model.id)
        chapter_model.relation_content = relation_json
        print("流程控制-LangChain链构建")
        process_chain = (
            RunnableLambda(get_process_prompt_template) |
            transmit.process_llm |
            StrOutputParser()
        )
        print(f"流程控制-LangChain链Invoke数据填充")
        process = process_chain.invoke({
            "relation_analysis": relation_json,
            "process_prompt_system": transmit.process_system,
            "process_prompt_user": transmit.process_user,
            "reference_before_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "reference_after_text": chapter_model.after_content
        })
        print(str(process))
        raw_text = process.content if hasattr(process, 'content') else str(process)
        process_data = ProcessPromptResult.model_validate_json(raw_text)
        # 判断
        if process_data is None:
            update_chapter_status(4, chapter_model.id)
            return False
        # 更新
        print(3.01)
        extra = process_data.extra
        if chapter_model.sort <= transmit.extra_start_num:
            extra = "false"
        print(3.02)
        # 更新文本
        update_chapter_process(process_data.model_dump_json(), ChapterPoint.ORIGINAL_SCENE.value, chapter_model.id)
        chapter_model.point = ChapterPoint.ORIGINAL_SCENE.value
        chapter_model.process_content = process_data.model_dump_json()
        print(f"流程控制-章节信息更新完成")
        # 状态判断
        if "true" in str(extra).lower():
            return True
        else:
            return False
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return False
        if 3 == for_num:
            update_chapter_status(4, chapter_model.id)
            return False
        else:
            return process_chapter_polish(chapter_model, transmit, for_num + 1)

def original_scene_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    try:
        """原文改写-场景分析"""
        print("原文改写-场景分析-LangChain链构建")
        original_chain = (
            RunnableLambda(get_original_scene_prompt_template) |
            transmit.original_scene_llm.with_structured_output(ScenePromptResult)
        )
        print(4.01)
        print(f"原文改写-场景分析-LangChain链Invoke数据填充")
        original_scene = original_chain.invoke({
            "relation_analysis": chapter_model.relation_content,
            "original_scene_prompt_system": transmit.original_scene_system,
            "original_scene_prompt_user": transmit.original_scene_user,
            "reference_before_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "reference_after_text": chapter_model.after_content,
            "scene_list": str(transmit.original_scene_identity)
        })
        print(4.02)
        # 格式校验
        scene = ScenePromptResult.model_validate(original_scene)
        print(f"原文改写-场景分析-推理结果完成：{scene.model_dump_json()}")
        # 更新状态
        update_chapter_scene(scene.model_dump_json(), ChapterPoint.ORIGINAL_FRAMEWORK.value, chapter_model.id)
        chapter_model.point = ChapterPoint.ORIGINAL_FRAMEWORK.value
        chapter_model.scene_content = scene.model_dump_json()
        print(f"原文改写-场景分析-章节信息更新完成")
        return True
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return False
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
            return False
        else:
            return original_scene_chapter_polish(chapter_model, transmit, for_num + 1)

async def generate_stream_polish(chain, inputs, old_len, project_id, msg):
    print(f"{msg}-流式链启动")
    stream_chain = RetryableStreamChain(
        chain=chain,
        validator_factory=lambda : StreamingValidator(
            window_size=20,
            similarity_threshold=0.75,
            max_repeat_streak=2
        ),
        on_chunk=lambda text: print(text, end="", flush=True), # 实时打印
        on_retry=lambda attempt, reason: print(f"\n{msg}【{attempt}] {reason}\n"),
        project_id=project_id
    )
    try:
        result = await stream_chain.ainvoke_with_retry(inputs, old_len=old_len)
        print(f"\n生成完成，总长度: {len(result)} 字")
        return result

    except RuntimeError as e:
        print(f"生成最终失败: {e}")
        # 兜底：返回空或返回最后一次的有效部分
        return ""

def original_framework_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    try:
        """原文改写-脉络改写"""
        print(5.01)
        scene = ScenePromptResult.model_validate_json(chapter_model.scene_content)
        # 获取场景map
        print(5.02)
        original_analysis_text = {}
        for analysis in scene.scene_list:
            print(5.03)
            scene = transmit.original_scene_polish.get(analysis)
            print(5.04)
            original_analysis_text[analysis] = scene
            print(5.05)
        # 脉络修改
        print("原文改写-脉络改写-LangChain链构建")
        original_framework_chain = (
            RunnableLambda(get_original_framework_prompt_template) |
            transmit.original_framework_llm |
            StrOutputParser()
        )
        print(f"原文改写-脉络改写-LangChain链Invoke数据填充")
        inputs = {
            "relation_analysis": chapter_model.relation_content,
            "framework_analysis": str(original_analysis_text),
            "system_prompt": transmit.original_framework_system,
            "user_prompt": transmit.original_framework_user,
            "reference_before_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "reference_after_text": chapter_model.after_content,
            "male_lead": transmit.male_lead,
            "heroine": transmit.heroine
        }
        print(5.06)
        old_len = len(chapter_model.old_content) if chapter_model.old_content is not None else 0
        raw_text = asyncio.run(generate_stream_polish(original_framework_chain, inputs, old_len, chapter_model.project_id, "原文改写-脉络改写"))
        # 英文含量校验
        print(f"原文改写-脉络改写-推理结果转换完成")
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        print(5.08)
        if not is_valid:
            print(f"原文改写-脉络改写-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                original_framework_chapter_polish(chapter_model, transmit, for_num + 1)
            return
        print(f"原文改写-脉络改写-推理结果完成：{raw_text}")
        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == chapter_model.type and len(raw_text) < len(chapter_model.old_content):
            print(f"原文改写-脉络改写-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                original_framework_chapter_polish(chapter_model, transmit, for_num + 1)
            return
        # 更新状态
        update_chapter_framework(raw_text, ChapterPoint.POLISH_CONTENT.value, chapter_model.id)
        chapter_model.point = ChapterPoint.POLISH_CONTENT.value
        chapter_model.framework_content = raw_text
        print(f"原文改写-脉络改写-章节信息更新完成")
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            original_framework_chapter_polish(chapter_model, transmit, for_num + 1)

def get_family_json(project_id):
    relation_data = RelationPromptResult.RelationPromptResult(角色关系=[], 角色数组=[])
    # 获取主角女性亲友信息
    family_list = query_family_role(project_id)
    if family_list:
        ## 循环处理
        role_names = []
        for family in family_list:
            role_names.append(family['role_name'])
            relation_data.角色数组.append(RelationPromptResult.CharacterResult.model_validate_json(family['role_json']))
        ## 关系补充
        if role_names and len(role_names) > 0:
            names_a = query_family_relation_name_a(project_id, role_names)
            if names_a:
                for item in names_a:
                    relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(item['relation']))
            names_b = query_family_relation_name_b(project_id, role_names)
            if names_b:
                for item in names_b:
                    relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(item['relation']))
    return relation_data.model_dump_json()

def extra_scene_chapter_plish(chapter_model: ChapterBO, transmit, for_num=1):
    try:
        """番外章节-场景分析"""
        print("555.11")
        relation_json = get_family_json(chapter_model.project_id)
        print("555.12")
        # 更新relation
        update_chapter_relation(relation_json, chapter_model.id)
        chapter_model.relation_content = relation_json
        print("番外章节-场景分析-LangChain链构建")
        extra_scene_chain = (
            RunnableLambda(get_extra_scene_prompt_template) |
            transmit.extra_scene_llm.with_structured_output(ScenePromptResult)
        )
        print(f"番外章节-场景分析-LangChain链Invoke数据填充")
        extra_scene = extra_scene_chain.invoke({
                "extra_scene_prompt_system": transmit.extra_scene_system,
                "extra_scene_prompt_user": transmit.extra_scene_user,
                "reference_before_text": chapter_model.before_content,
                "reference_after_text": chapter_model.after_content,
                "relation_analysis": chapter_model.relation_content,
                "process_analysis": chapter_model.process_content,
                "scene_list": str(transmit.extra_scene_identify)
        })
        # 格式校验
        print(234)
        scene = ScenePromptResult.model_validate(extra_scene)
        print(f"番外章节-场景分析-推理结果完成：{scene.model_dump_json()}")
        # 更新信息
        update_chapter_scene(scene.model_dump_json(), ChapterPoint.EXTRA_FRAMEWORK.value, chapter_model.id)
        chapter_model.scene_content = scene.model_dump_json()
        chapter_model.point = ChapterPoint.EXTRA_FRAMEWORK.value
        print(f"番外章节-场景分析-章节信息更新完成")
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            extra_scene_chapter_plish(chapter_model, transmit, for_num + 1)

def extra_framework_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    try:
        """番外章节-脉络生成"""
        scene = ScenePromptResult.model_validate_json(chapter_model.scene_content)
        # 获取场景map
        extra_analysis_text = {}
        for extra_scene in scene.scene_list:
            scene = transmit.extra_scene_polish.get(extra_scene)
            extra_analysis_text[extra_scene] = scene

        print("番外章节-脉络生成-LangChain链构建")
        extra_framework_chain = (
                RunnableLambda(get_extra_framework_prompt_template) |
                transmit.extra_framework_llm |
                StrOutputParser()
        )
        print(f"番外章节-脉络生成-LangChain链Invoke数据填充")
        # 英文含量校验
        inputs = {
            "system_prompt": transmit.extra_framework_system,
            "user_prompt": transmit.extra_framework_user,
            "framework_analysis": str(extra_analysis_text),
            "reference_before_text": chapter_model.before_content,
            "reference_after_text": chapter_model.after_content,
            "relation_analysis": chapter_model.relation_content,
            "create_framework_text": chapter_model.process_content,
            "male_lead": transmit.male_lead,
            "heroine": transmit.heroine
        }
        print(5.06)
        old_len = len(chapter_model.old_content) if chapter_model.old_content is not None else 0
        raw_text = asyncio.run(generate_stream_polish(extra_framework_chain, inputs, old_len, chapter_model.project_id, "番外章节-脉络生成"))
        print(f"番外章节-脉络生成-推理结果转换完成")
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            print(f"番外章节-脉络生成-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                extra_framework_chapter_polish(chapter_model, transmit, for_num + 1)
            return
        print(f"番外章节-脉络生成-推理结果完成：{raw_text}")
        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == chapter_model.type and len(raw_text) < len(chapter_model.old_content):
            print(f"番外章节-脉络生成-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                extra_framework_chapter_polish(chapter_model, transmit, for_num + 1)
            return
        # 更新状态
        update_chapter_framework(raw_text, ChapterPoint.POLISH_CONTENT.value, chapter_model.id)
        chapter_model.framework_content = raw_text
        chapter_model.point = ChapterPoint.POLISH_CONTENT.value
        print(f"番外章节-脉络生成-章节信息更新完成")
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            extra_framework_chapter_polish(chapter_model, transmit, for_num + 1)

def polish_chapter_polish(chapter_model: ChapterBO, transmit, for_num=1):
    try:
        print("结果润色-LangChain链构建")
        polish_chain = (
            RunnableLambda(get_polish_prompt_template) |
            transmit.polish_llm |
            StrOutputParser()
        )
        print(f"结果润色-LangChain链Invoke数据填充")
        # 英文含量校验
        inputs = {
            "system_prompt": transmit.polish_system,
            "user_prompt": transmit.polish_user,
            "original_framework_text": chapter_model.framework_content,
            "male_lead": transmit.male_lead,
            "heroine": transmit.heroine
        }
        print(5.06)
        old_len = len(chapter_model.old_content) if chapter_model.old_content is not None else 0
        raw_text = asyncio.run(generate_stream_polish(polish_chain, inputs, old_len, chapter_model.project_id, "结果润色"))
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            print(f"结果润色-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_polish(chapter_model, transmit, for_num + 1)
            return
        print(f"结果润色-推理结果完成：{raw_text}")
        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == chapter_model.type and len(raw_text) < len(chapter_model.old_content):
            print(f"结果润色-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_polish(chapter_model, transmit, for_num + 1)
            return
        # 更新状态
        update_chapter_polish(raw_text, chapter_model.id)
        chapter_model.point = ChapterPoint.RELATION_ANALYSIS.value
        chapter_model.new_content = raw_text
        print(f"结果润色-章节信息更新完成")
    except Exception as e:
        print(e)
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            polish_chapter_polish(chapter_model, transmit, for_num + 1)

def polish_chapter_repetition(chapter_model: ChapterBO, transmit, for_num=1):
    """去重整理"""
    try:
        print("去重整理-LangChain链构建")
        repetition_chain = (
            RunnableLambda(get_repetition_prompt_template) |
            transmit.polish_llm |
            StrOutputParser()
        )
        print("去重整理-LangChain链Invoke数据填充")
        repetition = repetition_chain.invoke({
            "polish_text": chapter_model.new_content
        })
        print(str(repetition))
        raw_text = repetition.content if hasattr(repetition, 'content') else str(repetition)
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            print(f"去重整理-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_repetition(chapter_model, transmit, for_num + 1)
            return
        # 长度判断
        if ChapterType.ORIGINAL_POLISH.value == chapter_model.type and len(raw_text) < len(chapter_model.old_content):
            print(f"去重整理-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_repetition(chapter_model, transmit, for_num + 1)
            return
        # 结果处理
        update_chapter_repetition(raw_text, chapter_model.id)
        chapter_model.new_content = raw_text
        chapter_model.point = ChapterPoint.RELATION_ANALYSIS.value
    except Exception as e:
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            polish_chapter_repetition(chapter_model, transmit, for_num + 1)



def chapter_novel_resume(chapter_model: ChapterBO, novel_content, transmit, for_num=1):
    """
    文本简述
    """
    try:
        print(22.01)
        novel_resume_chain = (
                RunnableLambda(get_novel_resume_template) |
                transmit.polish_llm |
                StrOutputParser()
        )
        print(22.02)
        novel_resume = novel_resume_chain.invoke({
            "reference_text": novel_content
        })
        print(22.03)
        raw_text = novel_resume.content if hasattr(novel_resume, 'content') else str(novel_resume)
        # 英文含量校验
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            print(f"剧情简述-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                chapter_model.status = ChapterStatus.FAIL.value
                return novel_content
            else:
                return chapter_novel_resume(chapter_model, novel_content, transmit, for_num + 1)
        print(f"剧情简述-推理结果完成：{raw_text}")
        return raw_text
    except Exception as e:
        print(f"剧情简述-文本压缩失败：{e}")
        # 退出循环
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event and stop_event.is_set():
            chapter_model.status = ChapterStatus.FAIL.value
            return None
        if 3 == for_num:
            chapter_model.status = ChapterStatus.FAIL.value
            return novel_content
        else:
            return chapter_novel_resume(chapter_model, novel_content, transmit, for_num + 1)