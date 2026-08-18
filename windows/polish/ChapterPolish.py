import re
from itertools import permutations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from sqlite.Sqlite3Utils import update_chapter_role, update_chapter_relation, update_chapter_status, \
    update_chapter_process, update_chapter_scene, update_chapter_framework, update_chapter_polish, query_role_model, \
    query_role_relation, remove_old_role_model, insert_role_model, remove_old_role_relation, insert_role_relation
from windows.polish.DynamicPromptTemplate import get_role_prompt_template, get_relation_prompt_template, \
    get_process_prompt_template, get_original_scene_prompt_template, get_original_framework_prompt_template, \
    get_polish_prompt_template, get_extra_scene_prompt_template, get_extra_framework_prompt_template
import json

def json_parse(raw_text):
    cleaned_json = re.sub(r'^\s*```(?:json)?\s*', '', raw_text, flags=re.IGNORECASE)
    cleaned_json = re.sub(r'\s*```\s*$', '', cleaned_json)
    return cleaned_json

def is_valid_json(json_str, is_json=True):
    """
    校验字符串是否为有效的 JSON 格式
    """
    # 直接尝试解析，用解析结果来判断是否合法
    try:
        parsed_data = json.loads(json_str)

        # 3. 【可选】进一步校验解析出来的是不是字典
        if is_json:
            if not isinstance(parsed_data, dict):
                raise ValueError(f"期望返回字典，但实际返回了 {type(parsed_data)}")
        else:
            # 校验是否为数组（Python中的列表）
            if not isinstance(parsed_data, list):
                raise ValueError(f"期望返回数组(list)，但实际返回了 {type(parsed_data)}")

        return True
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"角色分析-json格式校验失败，原因: {e}")
        return False

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

def role_chapter_polish(chapter, transmit, model_map, reference_text, for_num=1):
    """角色分析处理"""
    # 角色分析
    try:
        print("角色分析-LangChain链构建")
        role_chain = (
                RunnableLambda(get_role_prompt_template) |
                model_map.get(transmit['role_model_id']) |
                StrOutputParser()
        )
        print(f"角色分析-LangChain链Invoke数据填充")
        role = role_chain.invoke({
            "reference_text": reference_text,
            "original_text": chapter['old_content'],
            "role_prompt_system": transmit['role_system'],
            "role_prompt_user": transmit['role_user']
        })
        # 格式校验
        raw_text = role.content if hasattr(role, 'content') else str(role)
        print(1.01)
        role_str = json_parse(raw_text)
        print(f"角色分析-推理结果转换完成")
        if not is_valid_json(role_str):
            print(f"角色分析-json格式校验失败：{for_num}")
            if 3 == for_num:
                print(1.02)
                update_chapter_status(4, chapter['id'])
                return
            else:
                print(1.03)
                role_chapter_polish(chapter, transmit, model_map, reference_text, for_num + 1)
        print(f"角色分析-推理结果完成：{str(role_str)}")
        # 章节数据更新
        update_chapter_role(role_str, chapter['id'])
        print(f"角色分析-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return
        else:
            role_chapter_polish(chapter, transmit, model_map, reference_text, for_num + 1)


def relation_chapter_polish(chapter, transmit, model_map, reference_text, for_num=1):
    """关系分析处理"""
    try:
        # 关系分析
        print("关系分析-LangChain链构建")
        relation_chain = (
            RunnableLambda(get_relation_prompt_template) |
            model_map.get(transmit['relation_model_id']) |
            StrOutputParser()
        )
        # 查询角色信息
        db_role = {}
        print(2.01)
        role_content = json.loads(chapter['role_content'])
        print(f"关系分析-角色信息查询: {role_content}")
        if role_content:
            print(2.02)
            character_list = role_content['character_list']
            character_list_db = []
            relation_list_db = []
            if character_list:
                print(2.03)
                role_names = []
                for chapter_role in character_list:
                    print(2.04)
                    if chapter_role:
                        print(2.05)
                        character_name = chapter_role.get('character_name')
                        print(2.06)
                        if character_name:
                            print(2.07)
                            role_names.append(character_name)
                # 查询角色信息
                print(2.08)
                if chapter['project_id'] and role_names:
                    print(2.09)
                    role_list = query_role_model(chapter['project_id'], role_names)
                    print(2.10)
                    if role_list:
                        print(2.11)
                        for role in role_list:
                            print(2.12)
                            if role and role.get('role_json'):
                                print(2.13)
                                character_list_db.append(role.get('role_json'))
                                print(2.14)
                # 关系
                print(2.15)
                if chapter['project_id'] and role_names and len(role_names) > 1:
                    print(2.16)
                    pairs = list(permutations(role_names, 2))
                    print(2.17)
                    for a, b in pairs:
                        print(2.18)
                        relation_json = query_role_relation(chapter['project_id'], a, b)
                        print(2.19)
                        if relation_json:
                            print(2.2)
                            relation_list_db.append(relation_json)
                            print(2.21)

            db_role['character_list'] = character_list_db
            db_role['relationships'] = relation_list_db
        # 查询
        print(f"关系分析-LangChain链Invoke数据填充")
        relation = relation_chain.invoke({
            "role_analysis": chapter['role_content'],
            "relation_prompt_system": transmit['relation_system'],
            "relation_prompt_user": transmit['relation_user'],
            "reference_text": reference_text,
            "original_text": chapter['old_content'],
            "db_role_json": str(db_role)
        })
        print(2.22)
        # 格式校验
        raw_text = relation.content if hasattr(relation, 'content') else str(relation)
        print(2.23)
        relation_str = json_parse(raw_text)
        print(f"关系分析-推理结果转换完成")
        if not is_valid_json(relation_str):
            print(f"关系分析-json格式校验失败：{for_num}")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                relation_chapter_polish(chapter, transmit, model_map, reference_text, for_num + 1)
        # 更新
        update_chapter_relation(relation_str, chapter['id'])
        print(f"关系分析-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return
        else:
            relation_chapter_polish(chapter, transmit, model_map, reference_text, for_num + 1)


def process_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num=1):
    try:
        """流程控制处理"""
        print("流程控制-LangChain链构建")
        process_chain = (
            RunnableLambda(get_process_prompt_template) |
            model_map.get(transmit['process_model_id']) |
            StrOutputParser()
        )
        print(f"流程控制-LangChain链Invoke数据填充")
        process = process_chain.invoke({
            "relation_analysis": chapter['relation_content'],
            "process_prompt_system": transmit['process_system'],
            "process_prompt_user": transmit['process_user'],
            "reference_before_text": reference_before_text,
            "original_text": chapter['old_content'],
            "reference_after_text": reference_after_text
        })
        print(123)
        # 格式校验
        raw_text = process.content if hasattr(process, 'content') else str(process)
        print(124)
        process_str = json_parse(raw_text)
        print(f"流程控制-推理结果转换完成")
        if not is_valid_json(process_str):
            print(f"流程控制-json格式校验失败：{for_num}")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return False
            else:
                process_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        print(f"流程控制-推理结果完成：{process_str}")
        # 判断
        if process_str is None:
            update_chapter_status(4, chapter['id'])
            return False
        # 更新
        print(3.01)
        process_obj = json.loads(process_str)
        print(3.02)
        extra = process_obj['extra']
        # 判断
        if extra is None:
            update_chapter_status(4, chapter['id'])
            return False
        # 更新文本
        update_chapter_process(process_str, 400, chapter['id'])
        print(f"流程控制-章节信息更新完成")
        # 状态判断
        if "true" in str(extra).lower():
            return True
        elif "false" in str(extra).lower():
            return False
        else:
            update_chapter_status(4, chapter['id'])
            return False
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return False
        else:
            process_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)

def original_scene_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num=1):
    try:
        """原文改写-场景分析"""
        print("原文改写-场景分析-LangChain链构建")
        original_chain = (
            RunnableLambda(get_original_scene_prompt_template) |
            model_map.get(transmit['scene_model_id']) |
            StrOutputParser()
        )
        print(4.01)
        scene_identify_list = transmit['scene_identify']
        print(f"原文改写-场景分析-LangChain链Invoke数据填充")
        original_scene = original_chain.invoke({
            "relation_analysis": chapter['relation_content'],
            "original_scene_prompt_system": transmit['scene_system'],
            "original_scene_prompt_user": transmit['scene_user'],
            "reference_before_text": reference_before_text,
            "original_text": chapter['old_content'],
            "reference_after_text": reference_after_text,
            "scene_list": scene_identify_list
        })
        print(4.02)
        # 格式校验
        raw_text = original_scene.content if hasattr(original_scene, 'content') else str(original_scene)
        print(4.03)
        scene_str = json_parse(raw_text)
        print(f"原文改写-场景分析-推理结果转换完成")
        if not is_valid_json(scene_str, is_json=False):
            print(f"原文改写-场景分析-json格式校验失败：{for_num}")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return False
            else:
                original_scene_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        print(f"原文改写-场景分析-推理结果完成：{scene_str}")
        # 更新状态
        update_chapter_scene(scene_str, 401, chapter['id'])
        print(f"原文改写-场景分析-章节信息更新完成")
        return True
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return False
        else:
            original_scene_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)

def original_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num=1):
    try:
        """原文改写-脉络改写"""
        print(5.01)
        original_analysis_json = json.loads(chapter['scene_content'])
        print(str(original_analysis_json))
        # 获取场景map
        scene_polish_list = transmit['scene_polish']
        print(5.02)
        original_analysis_text = {}
        for analysis in original_analysis_json:
            print(5.03)
            scene = scene_polish_list.get(analysis)
            print(5.04)
            original_analysis_text[analysis] = scene
            print(5.05)
        # 脉络修改
        print("原文改写-脉络改写-LangChain链构建")
        original_framework_chain = (
            RunnableLambda(get_original_framework_prompt_template) |
            model_map.get(transmit['framework_model_id']) |
            StrOutputParser()
        )
        print(f"原文改写-脉络改写-LangChain链Invoke数据填充")
        original_framework = original_framework_chain.invoke({
                "relation_analysis": chapter['relation_content'],
                "framework_analysis": str(original_analysis_text),
                "original_framework_prompt_system": transmit['framework_system'],
                "original_framework_prompt_user": transmit['framework_user'],
                "reference_before_text": reference_before_text,
                "original_text": chapter['old_content'],
                "reference_after_text": reference_after_text
        })
        # 英文含量校验
        print(5.06)
        raw_text = original_framework.content if hasattr(original_framework, 'content') else str(original_framework)
        print(5.07)
        framework_str = json_parse(raw_text)
        print(f"原文改写-脉络改写-推理结果转换完成")
        is_valid, english_ratio = is_valid_chinese_text(framework_str)
        print(5.08)
        if not is_valid:
            print(f"原文改写-脉络改写-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                original_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        print(f"原文改写-脉络改写-推理结果完成：{framework_str}")
        # 长度判断
        if len(framework_str) < 1500:
            print(f"原文改写-脉络改写-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                original_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        # 更新状态
        update_chapter_framework(framework_str, 500, chapter['id'])
        print(f"原文改写-脉络改写-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return
        else:
            original_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)

def extra_scene_chapter_plish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num=1):
    try:
        """番外章节-场景分析"""
        print("番外章节-场景分析-LangChain链构建")
        extra_scene_chain = (
            RunnableLambda(get_extra_scene_prompt_template) |
            model_map.get(transmit['extra_scene_model_id']) |
            StrOutputParser()
        )
        print(f"番外章节-场景分析-LangChain链Invoke数据填充")
        extra_scene = extra_scene_chain.invoke({
                "extra_scene_prompt_system": transmit['extra_scene_system'],
                "extra_scene_prompt_user": transmit['extra_scene_user'],
                "reference_before_text": reference_before_text,
                "original_text": chapter['old_content'],
                "reference_after_text": reference_after_text,
                "relation_analysis": chapter['relation_content'],
                "process_analysis": chapter['process_content'],
                "scene_list": str(transmit['extra_scene_identify'])
        })
        # 格式校验
        print(234)
        raw_text = extra_scene.content if hasattr(extra_scene, 'content') else str(extra_scene)
        print(235)
        scene_str = json_parse(raw_text)
        print(f"番外章节-场景分析-推理结果转换完成")
        if not is_valid_json(scene_str, is_json=False):
            print(f"番外章节-场景分析-json格式校验失败：{for_num}")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                extra_scene_chapter_plish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        print(f"番外章节-场景分析-推理结果完成：{scene_str}")
        # 更新信息
        update_chapter_scene(scene_str, 411, chapter['id'])
        print(f"番外章节-场景分析-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return
        else:
            extra_scene_chapter_plish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)

def extra_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num=1):
    try:
        """番外章节-脉络生成"""
        extra_scene_list = json.loads(chapter['scene_content'])
        # 获取场景map
        extra_scene_polish_list = transmit['extra_scene_polish']
        extra_analysis_text = {}
        for extra_scene in extra_scene_list:
            scene = extra_scene_polish_list.get(extra_scene)
            extra_analysis_text[extra_scene] = scene

        print("番外章节-脉络生成-LangChain链构建")
        extra_framework_chain = (
                RunnableLambda(get_extra_framework_prompt_template) |
                model_map.get(transmit['framework_model_id']) |
                StrOutputParser()
        )
        print(f"番外章节-脉络生成-LangChain链Invoke数据填充")
        extra_framework = extra_framework_chain.invoke({
            "extra_framework_prompt_system": transmit['extra_framework_system'],
            "extra_framework_prompt_user": transmit['extra_framework_user'],
            "framework_analysis": str(extra_analysis_text),
            "reference_before_text": reference_before_text,
            "original_text": chapter['old_content'],
            "reference_after_text": reference_after_text,
            "relation_analysis": chapter['relation_content'],
            "create_framework_text": chapter['process_content']
        })
        # 英文含量校验
        print(321)
        raw_text = extra_framework.content if hasattr(extra_framework, 'content') else str(extra_framework)
        print(322)
        framework_str = json_parse(raw_text)
        print(f"番外章节-脉络生成-推理结果转换完成")
        is_valid, english_ratio = is_valid_chinese_text(framework_str)
        if not is_valid:
            print(f"番外章节-脉络生成-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                extra_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        print(f"番外章节-脉络生成-推理结果完成：{framework_str}")
        # 长度判断
        if len(framework_str) < 1500:
            print(f"番外章节-脉络生成-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                extra_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)
        # 更新状态
        update_chapter_framework(framework_str, 500, chapter['id'])
        print(f"番外章节-脉络生成-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return
        else:
            extra_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text, for_num + 1)

def polish_chapter_polish(chapter, transmit, model_map, for_num=1):
    try:
        print("结果润色-LangChain链构建")
        polish_chain = (
            RunnableLambda(get_polish_prompt_template) |
            model_map.get(transmit['polish_model_id']) |
            StrOutputParser()
        )
        print(f"结果润色-LangChain链Invoke数据填充")
        polish = polish_chain.invoke({
                    "polish_prompt_system": transmit['polish_system'],
                    "polish_prompt_user": transmit['polish_user'],
                    "original_text": chapter['old_content'],
                    "original_framework_text": chapter['framework_content']
        }, config={
            "configurable": {
                "extra_body": {"enable_thinking": True}
            }
        })
        # 英文含量校验
        raw_text = polish.content if hasattr(polish, 'content') else str(polish)
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            print(f"结果润色-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                polish_chapter_polish(chapter, transmit, model_map, for_num + 1)
        print(f"结果润色-推理结果完成：{raw_text}")
        # 长度判断
        if len(raw_text) < 1500:
            print(f"结果润色-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(4, chapter['id'])
                return
            else:
                polish_chapter_polish(chapter, transmit, model_map, for_num + 1)
        # 更新状态
        update_chapter_polish(raw_text, chapter['id'])
        print(f"结果润色-章节信息更新完成")

        # 更新角色信息
        relation_content = json.loads(chapter["relation_content"])
        print(f"结果润色-角色信息：{relation_content}")
        if relation_content:
            character_list = relation_content["character_list"]
            if character_list:
                role_name = []
                for cha in character_list:
                    name = cha.get("character_name")
                    if name:
                        role_name.append(name)
                if role_name and len(role_name) > 0:
                    remove_old_role_model(chapter['project_id'], role_name)
                for cha in character_list:
                    name = cha.get("character_name")
                    if name:
                        insert_role_model(chapter['project_id'], name, cha)
                # 关系
                if len(role_name) > 1:
                    relation_list = list(permutations(role_name, 2))
                    # 清除关系信息
                    if relation_list:
                        for a, b in relation_list:
                            remove_old_role_relation(chapter['project_id'], a, b)
            # 新增关系
            relationships = relation_content.get("relationships")
            if relationships:
                for relation in relationships:
                    role_a = relation.get("character_a")
                    role_b = relation.get("character_b")
                    if role_a and role_b:
                        insert_role_relation(chapter['project_id'], role_a, role_b, relation)
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter['id'])
            return
        else:
            polish_chapter_polish(chapter, transmit, model_map, for_num + 1)