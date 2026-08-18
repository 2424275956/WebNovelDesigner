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
            【输出内容】：严格按照下述JSON格式输出，JSON必须是有效的格式。
            {
                "character_list": [
                    {
                        "character_name": "角色的标准名称",
                        "alias_name": "角色的别称，多数人对其的称呼",
                        "identify": "角色的身份，如皇帝、公主、大侠、圣女等",
                        "sex": "角色的性别，如男性、女性、男女同体等",
                        "type": "角色的类别，如人类、妖兽、精灵等",
                        "size": "角色的大概身高，如1米5、2米等",
                        "colour": "角色的肤色，如苍白、咖啡色、白色等",
                        "chest": "女性角色的胸部特征（半球型（圆型）、水滴型（泪珠型）、圆盘型、圆锥型（鸟嘴型）、下垂型（松弛型/钟型）、扁平型（苗条型/平胸型）、外扩型（东西型））",
                        "chest_colour": "女性角色的乳晕颜色（粉红、褐红、深红发黑）",
                        "chest_size": "女性角色的胸部大小（精致小巧、馒头大小、硕大丰盈等）",
                        "pubes": "女性角色的阴部特征（馒头型、一线天型、蝴蝶型等）",
                        "pubes_hair": "女性角色的阴部毛发特征（毛发稀疏、毛发浓密、白虎等）",
                        "pubes_colour": "女性角色的阴部颜色（粉色、褐色、深褐色、黑色）",
                        "penis": "男性角色的阴茎特征（如蘑菇头型、子弹头型、平头型）",
                        "core_traits": [
                            {
                                "trait_label": "性格标签（如：温柔）",
                                "evidence": "原文中的具体支撑证据（简述关键情节）",
                                "motivation": "该行为背后的动机分析"
                            }
                        ],
                        "overall_summary": "对该角色性格的综合一句话总结"
                    }
                ]
            }
            【输出内容规则】：
            - ‘chest’未提及时随机选择，男性角色为NULL。
            - ‘chest_colour’未提及按角色年龄匹配，男性角色为NULL。
            - ‘chest_size’未提及时模糊描述，男性角色为NULL。
            - ‘pubes’随机进行选择，男性角色为NULL。
            - ‘pubes_hair’以‘pubes’为基础进行推测，男性角色为NULL。
            - ‘pubes_colour’按年龄与身体状态匹配，男性角色为NULL。
            - ‘penis’随机进行选择，女性角色为NULL。
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
            【输出内容】：严格按照下述JSON格式输出，JSON必须是有效的格式，为每个识别出的角色与角色关系创建一份档案。
            {
                "character_list": [
                    {
                        "character_name": "角色的标准名称",
                        "alias_name": "角色的别称，多数人对其的称呼",
                        "identify": "角色的身份，如皇帝、公主、大侠、圣女等",
                        "sex": "角色的性别，如男性、女性、男女同体等",
                        "type": "角色的类别，如人类、妖兽、精灵等",
                        "size": "角色的大概身高，如1米5、2米等",
                        "colour": "角色的肤色，如苍白、咖啡色、白色等",
                        "chest": "女性角色的胸部特征",
                        "chest_colour": "女性角色的乳晕颜色",
                        "chest_size": "女性角色的胸部大小",
                        "pubes": "女性角色的阴部特征",
                        "pubes_hair": "女性角色的阴部毛发特征",
                        "pubes_colour": "女性角色的阴部颜色",
                        "penis": "男性角色的阴茎特征",
                        "core_traits": [
                            {
                                "trait_label": "性格标签（如：温柔）",
                                "evidence": "原文中的具体支撑证据（简述关键情节）",
                                "motivation": "该行为背后的动机分析"
                            }
                        ],
                        "overall_summary": "对该角色性格的综合一句话总结"
                    }
                ],
                "relationships": [
                    {
                        "character_a": "角色A的标准名称",
                            "character_b": "角色B的标准名称",
                            "relation_label": "关系标签（如：宿敌、好友、伴侣、师徒、父女等）",
                            "interaction_analysis": "基于性格和动机的互动分析（简述为什么他们会形成这种关系）",
                            "evidence": "原文中的关键情节支撑",
                        "overall_relation_summary": "对角色关系综合一句话总结"
                    }
                ]
            }
            【输出内容规则】：
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
            【输出格式要求】：请使用清晰的Json排版，JSON必须是有效的格式，语言风格保持专业、客观、犀利且富有洞察力。多使用文学评论和心理学的专业术语进行支撑，但解释要通俗易懂。
            {
                "extra": "是否可以插入番外(True/False)",
                "optional_roles": [
                    {
                        "role_name": "角色的标准名称",
                        "role_action": "角色的动作行为，如前往某个地点、会到房间等"
                    }
                ]
            }
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
            【输出格式】：严格按照JSON格式生成,根据匹配度排序选出最匹配的3个场景。
             ["场景名称"]
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
            【输出内容】:
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
            【输出内容】:
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
            【输出格式】：严格按照JSON格式生成,根据匹配度排序选出最匹配的3个场景。
             ["场景名称"]
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
            【输出内容】:
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