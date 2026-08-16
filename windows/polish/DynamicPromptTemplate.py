import re

from langchain_core.prompts import ChatPromptTemplate

def special_chars_parse(text):
    """检查文本中的特殊字符"""
    text = str(text)
    text = re.sub(r'(?<!\{)\{(?!\{)', '{{', text)
    text = re.sub(r'(?<!})}(?!})', '}}', text)
    return text

def get_role_prompt_template(inputs) -> ChatPromptTemplate:
    """获取用户分析提示词模版"""
    # 系统提示词
    system_template = (inputs['role_prompt_system'])
    user_template = (inputs['role_prompt_user'])
    reference_text = (inputs['reference_text'])
    original_text = (inputs['original_text'])
    system_template = system_template.replace("{reference_text}", reference_text).replace("{original_text}", original_text)
    system_template = special_chars_parse(system_template)
    # 用户提示词
    user_template = user_template.replace("{reference_text}", reference_text).replace("{original_text}", original_text)
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_relation_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['relation_prompt_system'])
    user_template = (inputs['relation_prompt_user'])
    reference_text = (inputs['reference_text'])
    original_text = (inputs['original_text'])
    role_analysis = (inputs['role_analysis'])
    db_role_json = (inputs['db_role_json'])
    # 系统提示词
    system_template = (system_template
                        .replace("{reference_text}", reference_text)
                        .replace("{original_text}", original_text)
                        .replace("{role_analysis}", role_analysis)
                        .replace("{db_role_json}", db_role_json))
    system_template = special_chars_parse(system_template)
    # 用户提示词
    user_template = (user_template
                        .replace("{reference_text}", reference_text)
                        .replace("{original_text}", original_text)
                        .replace("{role_analysis}", role_analysis)
                        .replace("{db_role_json}", db_role_json))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_process_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['process_prompt_system'])
    user_template = (inputs['process_prompt_user'])
    relation_analysis = (inputs['relation_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    # 系统提示词
    system_template = (system_template
                       .replace("{relation_analysis}", relation_analysis)
                       .replace("{reference_before_text}", reference_before_text)
                       .replace("{original_text}", original_text)
                       .replace("{reference_after_text}", reference_after_text))
    system_template = special_chars_parse(system_template)
    # 用户提示词
    user_template = (user_template
                     .replace("{relation_analysis}", relation_analysis)
                     .replace("{reference_before_text}", reference_before_text)
                     .replace("{original_text}", original_text)
                     .replace("{reference_after_text}", reference_after_text))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_original_scene_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['original_scene_prompt_system'])
    user_template = (inputs['original_scene_prompt_user'])
    relation_analysis = (inputs['relation_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    scene_list = (inputs['scene_list'])
    print(3.01)
    # 系统提示词
    system_template = (system_template
                       .replace("{relation_analysis}", relation_analysis)
                       .replace("{reference_before_text}", reference_before_text)
                       .replace("{original_text}", original_text)
                       .replace("{reference_after_text}", reference_after_text)
                       .replace("{scene_list}", str(scene_list)))
    print(3.03)
    system_template = special_chars_parse(system_template)
    print(3.02)
    # 用户提示词
    user_template = (user_template
                     .replace("{relation_analysis}", relation_analysis)
                     .replace("{reference_before_text}", reference_before_text)
                     .replace("{original_text}", original_text)
                     .replace("{reference_after_text}", reference_after_text)
                     .replace("{scene_list}", str(scene_list)))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_original_framework_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['original_framework_prompt_system'])
    user_template = (inputs['original_framework_prompt_user'])
    framework_analysis = (inputs['framework_analysis'])
    relation_analysis = (inputs['relation_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    print(3.01)
    # 系统提示词
    system_template = (system_template
                       .replace("{relation_analysis}", relation_analysis)
                       .replace("{reference_before_text}", reference_before_text)
                       .replace("{original_text}", original_text)
                       .replace("{reference_after_text}", reference_after_text)
                       .replace("{framework_analysis}", str(framework_analysis)))
    print(3.03)
    system_template = special_chars_parse(system_template)
    print(3.02)
    # 用户提示词
    user_template = (user_template
                     .replace("{relation_analysis}", relation_analysis)
                     .replace("{reference_before_text}", reference_before_text)
                     .replace("{original_text}", original_text)
                     .replace("{reference_after_text}", reference_after_text)
                     .replace("{framework_analysis}", str(framework_analysis)))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_polish_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['polish_prompt_system'])
    user_template = (inputs['polish_prompt_user'])
    original_framework_text = (inputs['original_framework_text'])
    original_text = (inputs['original_text'])
    print(3.01)
    # 系统提示词
    system_template = (system_template
                       .replace("{original_text}", original_text)
                       .replace("{original_framework_text}", str(original_framework_text)))
    print(3.03)
    system_template = special_chars_parse(system_template)
    print(3.02)
    # 用户提示词
    user_template = (user_template
                     .replace("{original_text}", original_text)
                     .replace("{original_framework_text}", str(original_framework_text)))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_extra_scene_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['extra_scene_prompt_system'])
    user_template = (inputs['extra_scene_prompt_user'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    relation_analysis = (inputs['relation_analysis'])
    process_analysis = (inputs['process_analysis'])
    scene_list = (inputs['scene_list'])
    print(3.01)
    # 系统提示词
    system_template = (system_template
                       .replace("{reference_before_text}", reference_before_text)
                       .replace("{original_text}", str(original_text))
                       .replace("{reference_after_text}", reference_after_text)
                       .replace("{relation_analysis}", relation_analysis)
                       .replace("{process_analysis}", process_analysis)
                       .replace("{scene_list}", scene_list))
    print(3.03)
    system_template = special_chars_parse(system_template)
    print(3.02)
    # 用户提示词
    user_template = (user_template
                     .replace("{reference_before_text}", reference_before_text)
                     .replace("{original_text}", str(original_text))
                     .replace("{reference_after_text}", reference_after_text)
                     .replace("{relation_analysis}", relation_analysis)
                     .replace("{process_analysis}", process_analysis)
                     .replace("{scene_list}", scene_list))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_extra_framework_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = (inputs['extra_framework_prompt_system'])
    user_template = (inputs['extra_framework_prompt_user'])
    framework_analysis = (inputs['framework_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    relation_analysis = (inputs['relation_analysis'])
    create_framework_text = (inputs['create_framework_text'])
    print(3.01)
    # 系统提示词
    system_template = (system_template
                       .replace("{reference_before_text}", str(reference_before_text))
                       .replace("{original_text}", str(original_text))
                       .replace("{reference_after_text}", str(reference_after_text))
                       .replace("{relation_analysis}", str(relation_analysis))
                       .replace("{create_framework_text}", str(create_framework_text))
                       .replace("{framework_analysis}", str(framework_analysis)))
    print(3.03)
    system_template = special_chars_parse(system_template)
    print(3.02)
    # 用户提示词
    user_template = (user_template
                     .replace("{reference_before_text}", str(reference_before_text))
                     .replace("{original_text}", str(original_text))
                     .replace("{reference_after_text}", str(reference_after_text))
                     .replace("{relation_analysis}", str(relation_analysis))
                     .replace("{create_framework_text}", str(create_framework_text))
                     .replace("{framework_analysis}", str(framework_analysis)))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template