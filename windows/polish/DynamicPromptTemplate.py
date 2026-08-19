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
    system_template = str(inputs['role_prompt_system'])
    user_template = str(inputs['role_prompt_user'])
    user_template = user_template + """
            【输出内容规则】：
            - ‘chest’未提及时随机选择，男性角色为NULL。
            - ‘chest_colour’未提及按角色年龄匹配，男性角色为NULL。
            - ‘chest_size’未提及时模糊描述，男性角色为NULL。
            - ‘pubes’随机进行选择，男性角色为NULL。
            - ‘pubes_hair’以‘pubes’为基础进行推测，男性角色为NULL。
            - ‘pubes_colour’按年龄与身体状态匹配，男性角色为NULL。
            - ‘penis’随机进行选择，女性角色为NULL。
            - 禁止输出与JSON格式无关内容。
    """
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
    system_template = str(inputs['relation_prompt_system'])
    user_template = str(inputs['relation_prompt_user'])
    user_template = user_template + """
            【输出要求】：
            - 禁止输出与JSON格式无关内容。
            - character_a 与 character_b 只允许是单独的角色。
    """
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
    system_template = str(inputs['process_prompt_system'])
    user_template = str(inputs['process_prompt_user'])
    user_template = user_template + """
            【输出要求】：
            - 语言风格保持专业、客观、犀利且富有洞察力。多使用文学评论和心理学的专业术语进行支撑，但解释要通俗易懂。
            - 禁止输出与JSON格式无关内容。
            - 'extra' 必须是True或False
    """
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
    system_template = str(inputs['original_scene_prompt_system'])
    user_template = str(inputs['original_scene_prompt_user'])
    user_template = user_template + """
            【输出格式】：必须按照下述数据格式生成为有效的数组格式输出，禁止携带无关内容,根据匹配度排序选出最匹配的3个场景。
             ["场景名称","场景名称"]
    """
    relation_analysis = (inputs['relation_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    scene_list = (inputs['scene_list'])
    # 系统提示词
    system_template = (system_template
                       .replace("{relation_analysis}", relation_analysis)
                       .replace("{reference_before_text}", reference_before_text)
                       .replace("{original_text}", original_text)
                       .replace("{reference_after_text}", reference_after_text)
                       .replace("{scene_list}", str(scene_list)))
    system_template = special_chars_parse(system_template)
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
    system_template = str(inputs['original_framework_prompt_system'])
    user_template = str(inputs['original_framework_prompt_user'])
    user_template = user_template + """
            【输出内容】:只输出脉络内容，禁止携带与内容无关输出
            [脉络改写完成后的内容]
    """
    framework_analysis = (inputs['framework_analysis'])
    relation_analysis = (inputs['relation_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    # 系统提示词
    system_template = (system_template
                       .replace("{relation_analysis}", str(relation_analysis))
                       .replace("{reference_before_text}", str(reference_before_text))
                       .replace("{original_text}", str(original_text))
                       .replace("{reference_after_text}", str(reference_after_text))
                       .replace("{framework_analysis}", str(framework_analysis)))
    system_template = special_chars_parse(system_template)
    # 用户提示词
    user_template = (user_template
                     .replace("{relation_analysis}", str(relation_analysis))
                     .replace("{reference_before_text}", str(reference_before_text))
                     .replace("{original_text}", str(original_text))
                     .replace("{reference_after_text}", str(reference_after_text))
                     .replace("{framework_analysis}", str(framework_analysis)))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_polish_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = str(inputs['polish_prompt_system'])
    user_template = str(inputs['polish_prompt_user'])
    user_template = user_template + """
            【输出内容】: 只输出润色后的内容，禁止携带无关内容。
            "润色完成后的内容"
    """
    original_framework_text = (inputs['original_framework_text'])
    original_text = (inputs['original_text'])
    # 系统提示词
    system_template = (system_template
                       .replace("{original_text}", str(original_text))
                       .replace("{original_framework_text}", str(original_framework_text)))
    system_template = special_chars_parse(system_template)
    # 用户提示词
    user_template = (user_template
                     .replace("{original_text}", str(original_text))
                     .replace("{original_framework_text}", str(original_framework_text)))
    user_template = special_chars_parse(user_template)
    template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("user", user_template)
    ])
    return template

def get_extra_scene_prompt_template(inputs) -> ChatPromptTemplate:
    """获取关系分析提示词模版"""
    system_template = str(inputs['extra_scene_prompt_system'])
    user_template = str(inputs['extra_scene_prompt_user'])
    user_template = user_template + """
            【输出格式】：严格按照下述格式输出数组数据，禁止携带无关内容,根据匹配度排序选出最匹配的3个场景。
             ["场景名称","场景名称"]
    """
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    relation_analysis = (inputs['relation_analysis'])
    process_analysis = (inputs['process_analysis'])
    scene_list = (inputs['scene_list'])
    # 系统提示词
    system_template = (system_template
                       .replace("{reference_before_text}", reference_before_text)
                       .replace("{original_text}", str(original_text))
                       .replace("{reference_after_text}", reference_after_text)
                       .replace("{relation_analysis}", relation_analysis)
                       .replace("{process_analysis}", process_analysis)
                       .replace("{scene_list}", scene_list))
    system_template = special_chars_parse(system_template)
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
    system_template = str(inputs['extra_framework_prompt_system'])
    user_template = str(inputs['extra_framework_prompt_user'])
    user_template = user_template + """
            【输出内容】: 只输出脉络内容，禁止携带与内容无关输出
            [脉络生成的内容]
    """
    framework_analysis = (inputs['framework_analysis'])
    reference_before_text = (inputs['reference_before_text'])
    original_text = (inputs['original_text'])
    reference_after_text = (inputs['reference_after_text'])
    relation_analysis = (inputs['relation_analysis'])
    create_framework_text = (inputs['create_framework_text'])
    # 系统提示词
    system_template = (system_template
                       .replace("{reference_before_text}", str(reference_before_text))
                       .replace("{original_text}", str(original_text))
                       .replace("{reference_after_text}", str(reference_after_text))
                       .replace("{relation_analysis}", str(relation_analysis))
                       .replace("{create_framework_text}", str(create_framework_text))
                       .replace("{framework_analysis}", str(framework_analysis)))
    system_template = special_chars_parse(system_template)
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