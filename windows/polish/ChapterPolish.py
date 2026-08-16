from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from sqlite.Sqlite3Utils import update_chapter_role, update_chapter_relation, update_chapter_status, \
    update_chapter_process, update_chapter_scene, update_chapter_framework, update_chapter_polish
from windows.polish.DynamicPromptTemplate import get_role_prompt_template, get_relation_prompt_template, \
    get_process_prompt_template, get_original_scene_prompt_template, get_original_framework_prompt_template, \
    get_polish_prompt_template, get_extra_scene_prompt_template, get_extra_framework_prompt_template
import json


def role_chapter_polish(chapter, transmit, model_map, reference_text):
    """角色分析处理"""
    # 角色分析
    role_chain = (
            RunnableLambda(get_role_prompt_template) |
            model_map.get(transmit['role_model_id']) |
            StrOutputParser()
    )
    role = role_chain.invoke({
        "reference_text": reference_text,
        "original_text": chapter['old_content'],
        "role_prompt_system": transmit['role_system'],
        "role_prompt_user": transmit['role_user']
    })
    # 章节数据更新
    update_chapter_role(str(role), chapter['id'])
    # 数据更新
    chapter['point'] = 200
    chapter['role_content'] = str(role)

def relation_chapter_polish(chapter, transmit, model_map, reference_text):
    """关系分析处理"""
    # 关系分析
    relation_chain = (
        RunnableLambda(get_relation_prompt_template) |
        model_map.get(transmit['relation_model_id']) |
        StrOutputParser()
    )
    # todo 查询向量角色信息
    db_role = "-"
    # 查询
    relation = relation_chain.invoke({
        "role_analysis": chapter['role_content'],
        "relation_prompt_system": transmit['relation_system'],
        "relation_prompt_user": transmit['relation_user'],
        "reference_text": reference_text,
        "original_text": chapter['old_content'],
        "db_role_json": db_role
    })
    # 更新
    update_chapter_relation(str(relation), chapter['id'])
    # 数据更新
    chapter['point'] = 300
    chapter['relation_content'] = str(relation)

def process_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text):
    """流程控制处理"""
    process_chain = (
        RunnableLambda(get_process_prompt_template) |
        model_map.get(transmit['process_model_id']) |
        StrOutputParser()
    )
    process = process_chain.invoke({
        "relation_analysis": chapter['relation_content'],
        "process_prompt_system": transmit['process_system'],
        "process_prompt_user": transmit['process_user'],
        "reference_before_text": reference_before_text,
        "original_text": chapter['old_content'],
        "reference_after_text": reference_after_text
    })
    # 判断
    if process is None:
        update_chapter_status(4, chapter['id'])
        chapter['status'] = 4
        return False
    # 更新
    process_obj = json.loads(process)
    extra = process_obj['extra']
    # 判断
    if extra is None:
        update_chapter_status(4, chapter['id'])
        chapter['status'] = 4
        return False
    # 更新文本
    update_chapter_process(str(process), 400, chapter['id'])
    chapter['point'] = 400
    chapter['process_content'] = str(process)
    # 状态判断
    if "true" in str(extra).lower():
        return True
    elif "false" in str(extra).lower():
        return False
    else:
        update_chapter_status(4, chapter['id'])
        chapter['status'] = 4
        return False

def original_scene_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text):
    """原文改写-场景分析"""
    original_chain = (
        RunnableLambda(get_original_scene_prompt_template) |
        model_map.get(transmit['scene_model_id']) |
        StrOutputParser()
    )
    scene_identify_list = transmit['scene_identify']
    original_scene = original_chain.invoke({
        "relation_analysis": chapter['relation_content'],
        "original_scene_prompt_system": transmit['scene_system'],
        "original_scene_prompt_user": transmit['scene_user'],
        "reference_before_text": reference_before_text,
        "original_text": chapter['old_content'],
        "reference_after_text": reference_after_text,
        "scene_list": scene_identify_list
    })
    # 更新状态
    update_chapter_scene(str(original_scene), 401, chapter['id'])
    chapter['scene_content'] = str(original_scene)
    chapter['point'] = 401

def original_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text):
    """原文改写-脉络改写"""
    original_analysis_json = json.loads(chapter['scene_content'])
    # 获取场景map
    scene_polish_list = transmit['scene_polish']
    original_analysis_text = {}
    for analysis in original_analysis_json:
        scene = scene_polish_list.get(analysis)
        original_analysis_text[analysis] = scene
    # 脉络修改
    original_framework_chain = (
        RunnableLambda(get_original_framework_prompt_template) |
        model_map.get(transmit['framework_model_id']) |
        StrOutputParser()
    )
    original_framework = original_framework_chain.invoke({
            "relation_analysis": chapter['relation_content'],
            "framework_analysis": str(original_analysis_text),
            "original_framework_prompt_system": transmit['framework_system'],
            "original_framework_prompt_user": transmit['framework_user'],
            "reference_before_text": reference_before_text,
            "original_text": chapter['old_content'],
            "reference_after_text": reference_after_text
    })
    # 更新状态
    update_chapter_framework(str(original_framework), 500, chapter['id'])
    chapter['framework_content'] = str(original_framework)
    chapter['point'] = 500

def extra_scene_chapter_plish(chapter, transmit, model_map, reference_before_text, reference_after_text):
    """番外章节-场景分析"""
    extra_scene_chain = (
        RunnableLambda(get_extra_scene_prompt_template) |
        model_map.get(transmit['extra_scene_model_id']) |
        StrOutputParser()
    )
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
    # 更新信息
    update_chapter_scene(str(extra_scene), 411, chapter['id'])
    chapter['scene_content'] = str(extra_scene)
    chapter['point'] = 411

def extra_framework_chapter_polish(chapter, transmit, model_map, reference_before_text, reference_after_text):
    """番外章节-脉络生成"""
    extra_scene_list = json.loads(chapter['scene_content'])
    # 获取场景map
    extra_scene_polish_list = transmit['extra_scene_polish']
    extra_analysis_text = {}
    for extra_scene in extra_scene_list:
        scene = extra_scene_polish_list.get(extra_scene)
        extra_analysis_text[extra_scene] = scene

    extra_framework_chain = (
            RunnableLambda(get_extra_framework_prompt_template) |
            model_map.get(transmit['framework_model_id']) |
            StrOutputParser()
    )
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
    # 更新状态
    update_chapter_framework(str(extra_framework), 500, chapter['id'])
    chapter['framework_content'] = str(extra_framework)
    chapter['point'] = 500

def polish_chapter_polish(chapter, transmit, model_map):
    polish_chain = (
        RunnableLambda(get_polish_prompt_template) |
        model_map.get(transmit['polish_model_id']) |
        StrOutputParser()
    )
    polish = polish_chain.invoke({
                "polish_prompt_system": transmit['polish_system'],
                "polish_prompt_user": transmit['polish_user'],
                "original_text": chapter['old_content'],
                "original_framework_text": chapter['framework_content']
    })
    # 更新状态
    update_chapter_polish(str(polish), chapter['id'])
    chapter['new_content'] = str(polish)
    chapter['new_len'] = len(str(polish))
    chapter['point'] = 600
    chapter['status'] = 3
