import re
from itertools import permutations
from typing import List, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import Field, BaseModel, ConfigDict

from pojo.table.Chapter import ChapterBO, ChapterPoint, ChapterStatus, ChapterType
from sqlite.ChapterDB import update_chapter_role, update_chapter_status, update_chapter_relation, \
    update_chapter_process, update_chapter_scene, update_chapter_framework, update_chapter_polish
from sqlite.Sqlite3Utils import query_role_model, \
    query_role_relation, remove_old_role_model, insert_role_model, remove_old_role_relation, insert_role_relation
from windows.polish.DynamicPromptTemplate import get_role_prompt_template, get_relation_prompt_template, \
    get_process_prompt_template, get_original_scene_prompt_template, get_original_framework_prompt_template, \
    get_polish_prompt_template, get_extra_scene_prompt_template, get_extra_framework_prompt_template, \
    get_novel_resume_template
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

class CharacterCoreTraitLabel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True,
                              extra='ignore' )
    trait_label: str = Field(description="性格标签（如：温柔）")
    evidence: str = Field(description="对该性格的综合一句话总结")

class CharacterInfoResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True,
                              extra='ignore' )
    character_name: str = Field(description="角色的标准名称")
    alias_name: Optional[str] = Field(default=None, description="角色的别称，多数人对其的称呼")
    identify: str = Field(description="角色的身份，如皇帝、公主、大侠、圣女等")
    sex: str = Field(description="角色的性别，如男性、女性、男女同体等")
    type: str = Field(description="角色的类别，如人类、妖兽、精灵等")
    size: str = Field(description="角色的大概身高，如1米5、2米等")
    colour: str = Field(description="角色的肤色，如苍白、咖啡色、白色等")
    chest: Optional[str] = Field(default=None, description="女性角色的胸部特征,如：半球型（圆型）、水滴型（泪珠型）、圆盘型、圆锥型（鸟嘴型）、下垂型（松弛型/钟型）、扁平型（苗条型/平胸型）、外扩型（东西型）")
    chest_colour: Optional[str] = Field(default=None, description="女性角色的乳晕颜色（粉红、褐红、深红发黑）")
    chest_size: Optional[str] = Field(default=None, description="女性角色的胸部大小（精致小巧、馒头大小、硕大丰盈等）")
    pubes: Optional[str] = Field(default=None, description="女性角色的阴部特征（馒头型、一线天型、蝴蝶型等）")
    pubes_hair: Optional[str] = Field(default=None, description="女性角色的阴部毛发特征（毛发稀疏、毛发浓密、白虎等）")
    pubes_colour: Optional[str] = Field(default=None, description="女性角色的阴部颜色（粉色、褐色、深褐色、黑色）")
    penis: Optional[str] = Field(default=None, description="男性角色的阴茎特征（如蘑菇头型、子弹头型、平头型）")
    overall_summary: str = Field(description="对该角色性格的综合一句话总结")
    core_traits: List[CharacterCoreTraitLabel] = Field(description="角色性格特征")

class RolePromptResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    character_list: List[CharacterInfoResult] = Field(description="每个角色的建模信息")

def role_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    """角色分析处理"""
    # 角色分析
    try:
        print("角色分析-LangChain链构建")
        role_chain = (
                RunnableLambda(get_role_prompt_template) |
                model_map.get(ChapterPoint.ROLE_ANALYSIS.value).with_structured_output(RolePromptResult)
        )
        print(f"角色分析-LangChain链Invoke数据填充")
        role = role_chain.invoke({
            "reference_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "role_prompt_system": transmit['role_system'],
            "role_prompt_user": transmit['role_user']
        })
        print(101)
        role_data = RolePromptResult.model_validate(role)
        print(str(role_data))
        # 章节数据更新
        update_chapter_role(role_data.model_dump_json(), chapter_model.id)
        chapter_model.role_content = role_data.model_dump_json()
        chapter_model.point = ChapterPoint.RELATION_ANALYSIS.value
        print(f"角色分析-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
        else:
            role_chapter_polish(chapter_model, transmit, model_map, for_num + 1)


class RelationshipsResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True,
                              extra='ignore' )
    character_a: str = Field(description="角色A的标准名称")
    character_b: str = Field(description="角色B的标准名称")
    relation_label: str = Field(description="关系标签（如：宿敌、好友、伴侣、师徒、父女等）")
    interaction_analysis: str = Field(description="基于性格和动机的互动分析（简述为什么他们会形成这种关系）")
    evidence: str = Field(description="原文中的关键情节支撑")
    overall_relation_summary: str = Field(description="对角色关系综合一句话总结")

class RelationPromptResult(BaseModel):
    character_list: List[CharacterInfoResult] = Field(description="每个角色的建模信息")
    relationships: Optional[List[RelationshipsResult]] = Field(default=None, description="角色与角色之间的关系信息")

def relation_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    """关系分析处理"""
    try:
        # 关系分析
        print("关系分析-LangChain链构建")
        relation_chain = (
            RunnableLambda(get_relation_prompt_template) |
            model_map.get(ChapterPoint.RELATION_ANALYSIS.value).with_structured_output(RelationPromptResult)
        )
        # 查询角色信息
        db_role = {}
        print(2.01)
        role_data = RolePromptResult.model_validate_json(chapter_model.role_content)
        print(f"关系分析-角色信息查询: {role_data}")
        if role_data:
            print(2.02)
            character_list = role_data.character_list
            character_list_db = []
            relation_list_db = []
            if character_list:
                print(2.03)
                role_names = []
                for chapter_role in character_list:
                    print(2.04)
                    if chapter_role:
                        print(2.05)
                        character_name = chapter_role.character_name
                        print(2.06)
                        if character_name:
                            print(2.07)
                            role_names.append(character_name)
                # 查询角色信息
                print(2.08)
                if chapter_model.project_id and role_names:
                    print(2.09)
                    role_list = query_role_model(chapter_model.project_id, role_names)
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
                if chapter_model.project_id and role_names and len(role_names) > 1:
                    print(2.16)
                    pairs = list(permutations(role_names, 2))
                    print(2.17)
                    for a, b in pairs:
                        print(2.18)
                        relation_json = query_role_relation(chapter_model.project_id, a, b)
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
            "role_analysis": chapter_model.role_content,
            "relation_prompt_system": transmit['relation_system'],
            "relation_prompt_user": transmit['relation_user'],
            "reference_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "db_role_json": str(db_role)
        })
        print(2.22)
        relation_data = RelationPromptResult.model_validate(relation)
        print(relation_data)
        # 更新
        update_chapter_relation(relation_data.model_dump_json(), chapter_model.id)
        chapter_model.point = ChapterPoint.PROCESS_CHOOSES.value
        chapter_model.relation_content = relation_data.model_dump_json()
        print(f"关系分析-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(4, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            relation_chapter_polish(chapter_model, transmit, model_map, for_num + 1)

class RoleOptionalResult(BaseModel):
    role_name: str = Field(description="角色的标准名称")
    role_action: str = Field(description="角色的事件，可以进行番外扩写的点,一句话总结。如出差、前往目的地过程中、在房间的一段时间")

class ProcessPromptResult(BaseModel):
    extra: bool = Field(description="是否可以插入番外(True/False)")
    optional_roles: List[RoleOptionalResult] = Field(description="可以选择的角色")

def process_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    try:
        """流程控制处理"""
        print("流程控制-LangChain链构建")
        process_chain = (
            RunnableLambda(get_process_prompt_template) |
            model_map.get(ChapterPoint.PROCESS_CHOOSES.value) |
            StrOutputParser()
        )
        print(f"流程控制-LangChain链Invoke数据填充")
        process = process_chain.invoke({
            "relation_analysis": chapter_model.relation_content,
            "process_prompt_system": transmit['process_system'],
            "process_prompt_user": transmit['process_user'],
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
        if 3 == for_num:
            update_chapter_status(4, chapter_model.id)
            return False
        else:
            return process_chapter_polish(chapter_model, transmit, model_map, for_num + 1)

def original_scene_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    try:
        """原文改写-场景分析"""
        print("原文改写-场景分析-LangChain链构建")
        original_chain = (
            RunnableLambda(get_original_scene_prompt_template) |
            model_map.get(ChapterPoint.ORIGINAL_SCENE.value) |
            StrOutputParser()
        )
        print(4.01)
        scene_identify_list = transmit['scene_identify']
        print(f"原文改写-场景分析-LangChain链Invoke数据填充")
        original_scene = original_chain.invoke({
            "relation_analysis": chapter_model.relation_content,
            "original_scene_prompt_system": transmit['scene_system'],
            "original_scene_prompt_user": transmit['scene_user'],
            "reference_before_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "reference_after_text": chapter_model.after_content,
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
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
                return False
            else:
                return original_scene_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
        print(f"原文改写-场景分析-推理结果完成：{scene_str}")
        # 更新状态
        update_chapter_scene(scene_str, ChapterPoint.ORIGINAL_FRAMEWORK.value, chapter_model.id)
        chapter_model.point = ChapterPoint.ORIGINAL_FRAMEWORK.value
        chapter_model.scene_content = scene_str
        print(f"原文改写-场景分析-章节信息更新完成")
        return True
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
            return False
        else:
            return original_scene_chapter_polish(chapter_model, transmit, model_map, for_num + 1)

def original_framework_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    try:
        """原文改写-脉络改写"""
        print(5.01)
        original_analysis_json = json.loads(chapter_model.scene_content)
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
            model_map.get(ChapterPoint.ORIGINAL_FRAMEWORK.value) |
            StrOutputParser()
        )
        print(f"原文改写-脉络改写-LangChain链Invoke数据填充")
        original_framework = original_framework_chain.invoke({
                "relation_analysis": chapter_model.relation_content,
                "framework_analysis": str(original_analysis_text),
                "original_framework_prompt_system": transmit['framework_system'],
                "original_framework_prompt_user": transmit['framework_user'],
                "reference_before_text": chapter_model.before_content,
                "original_text": chapter_model.old_content,
                "reference_after_text": chapter_model.after_content
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
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                original_framework_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
            return
        print(f"原文改写-脉络改写-推理结果完成：{framework_str}")
        # 长度判断
        if len(framework_str) < 3500:
            print(f"原文改写-脉络改写-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                original_framework_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
            return
        # 更新状态
        update_chapter_framework(framework_str, ChapterPoint.POLISH_CONTENT.value, chapter_model.id)
        chapter_model.point = ChapterPoint.POLISH_CONTENT.value
        chapter_model.framework_content = framework_str
        print(f"原文改写-脉络改写-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            original_framework_chapter_polish(chapter_model, transmit, model_map, for_num + 1)

def extra_scene_chapter_plish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    try:
        """番外章节-场景分析"""
        print("番外章节-场景分析-LangChain链构建")
        extra_scene_chain = (
            RunnableLambda(get_extra_scene_prompt_template) |
            model_map.get(ChapterPoint.EXTRA_SCENE.value) |
            StrOutputParser()
        )
        print(f"番外章节-场景分析-LangChain链Invoke数据填充")
        extra_scene = extra_scene_chain.invoke({
                "extra_scene_prompt_system": transmit['extra_scene_system'],
                "extra_scene_prompt_user": transmit['extra_scene_user'],
                "reference_before_text": chapter_model.before_content,
                "original_text": chapter_model.old_content,
                "reference_after_text": chapter_model.after_content,
                "relation_analysis": chapter_model.relation_content,
                "process_analysis": chapter_model.process_content,
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
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                extra_scene_chapter_plish(chapter_model, transmit, model_map, for_num + 1)
            return
        print(f"番外章节-场景分析-推理结果完成：{scene_str}")
        # 更新信息
        update_chapter_scene(scene_str, ChapterPoint.EXTRA_FRAMEWORK.value, chapter_model.id)
        chapter_model.scene_content = scene_str
        chapter_model.point = ChapterPoint.EXTRA_FRAMEWORK.value
        print(f"番外章节-场景分析-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            extra_scene_chapter_plish(chapter_model, transmit, model_map, for_num + 1)

def extra_framework_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    try:
        """番外章节-脉络生成"""
        extra_scene_list = json.loads(chapter_model.scene_content)
        # 获取场景map
        extra_scene_polish_list = transmit['extra_scene_polish']
        extra_analysis_text = {}
        for extra_scene in extra_scene_list:
            scene = extra_scene_polish_list.get(extra_scene)
            extra_analysis_text[extra_scene] = scene

        print("番外章节-脉络生成-LangChain链构建")
        extra_framework_chain = (
                RunnableLambda(get_extra_framework_prompt_template) |
                model_map.get(ChapterPoint.EXTRA_FRAMEWORK.value) |
                StrOutputParser()
        )
        print(f"番外章节-脉络生成-LangChain链Invoke数据填充")
        extra_framework = extra_framework_chain.invoke({
            "extra_framework_prompt_system": transmit['extra_framework_system'],
            "extra_framework_prompt_user": transmit['extra_framework_user'],
            "framework_analysis": str(extra_analysis_text),
            "reference_before_text": chapter_model.before_content,
            "original_text": chapter_model.old_content,
            "reference_after_text": chapter_model.after_content,
            "relation_analysis": chapter_model.relation_content,
            "create_framework_text": chapter_model.process_content
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
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                extra_framework_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
            return
        print(f"番外章节-脉络生成-推理结果完成：{framework_str}")
        # 长度判断
        if len(framework_str) < 3500:
            print(f"番外章节-脉络生成-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                extra_framework_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
            return
        # 更新状态
        update_chapter_framework(framework_str, ChapterPoint.POLISH_CONTENT.value, chapter_model.id)
        chapter_model.framework_content = framework_str
        chapter_model.point = ChapterPoint.POLISH_CONTENT.value
        print(f"番外章节-脉络生成-章节信息更新完成")
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            extra_framework_chapter_polish(chapter_model, transmit, model_map, for_num + 1)

def polish_chapter_polish(chapter_model: ChapterBO, transmit, model_map, for_num=1):
    try:
        print("结果润色-LangChain链构建")
        polish_chain = (
            RunnableLambda(get_polish_prompt_template) |
            model_map.get(ChapterPoint.POLISH_CONTENT.value) |
            StrOutputParser()
        )
        print(f"结果润色-LangChain链Invoke数据填充")
        polish = polish_chain.invoke({
                    "polish_prompt_system": transmit['polish_system'],
                    "polish_prompt_user": transmit['polish_user'],
                    "original_text": chapter_model.old_content,
                    "original_framework_text": chapter_model.framework_content
        })
        # 英文含量校验
        raw_text = polish.content if hasattr(polish, 'content') else str(polish)
        is_valid, english_ratio = is_valid_chinese_text(raw_text)
        if not is_valid:
            print(f"结果润色-英文占比校验失败：{for_num}, 英文占比：{english_ratio * 100}%")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
            return
        print(f"结果润色-推理结果完成：{raw_text}")
        # 长度判断
        if len(raw_text) < 3500:
            print(f"结果润色-长度低于阈值")
            if 3 == for_num:
                update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
                chapter_model.status = ChapterStatus.FAIL.value
            else:
                polish_chapter_polish(chapter_model, transmit, model_map, for_num + 1)
            return
        # 更新状态
        update_chapter_polish(raw_text, chapter_model.id)
        chapter_model.point = ChapterPoint.SUCCESS.value
        chapter_model.new_content = raw_text
        chapter_model.status = ChapterStatus.SUCCESS.value
        print(f"结果润色-章节信息更新完成")

        # 更新角色信息
        relation_data = RelationPromptResult.model_validate_json(chapter_model.relation_content)
        print(f"结果润色-角色信息：{relation_data}")
        if relation_data:
            character_list = relation_data.character_list
            if character_list:
                role_name = []
                for cha in character_list:
                    name = cha.character_name
                    if name:
                        role_name.append(name)
                if role_name and len(role_name) > 0:
                    remove_old_role_model(chapter_model.project_id, role_name)
                for cha in character_list:
                    name = cha.character_name
                    if name:
                        insert_role_model(chapter_model.project_id, name, cha)
                # 关系
                if len(role_name) > 1:
                    relation_list = list(permutations(role_name, 2))
                    # 清除关系信息
                    if relation_list:
                        for a, b in relation_list:
                            remove_old_role_relation(chapter_model.project_id, a, b)
            # 新增关系
            relationships = relation_data.relationships
            if relationships:
                for relation in relationships:
                    role_a = relation.character_a
                    role_b = relation.character_b
                    if role_a and role_b:
                        insert_role_relation(chapter_model.project_id, role_a, role_b, relation)
    except Exception as e:
        print(e)
        if 3 == for_num:
            update_chapter_status(ChapterStatus.FAIL.value, chapter_model.id)
            chapter_model.status = ChapterStatus.FAIL.value
        else:
            polish_chapter_polish(chapter_model, transmit, model_map, for_num + 1)


def chapter_novel_resume(chapter_model: ChapterBO, novel_content, transmit, model_map, for_num=1):
    """
    文本简述
    """
    try:
        print(22.01)
        novel_resume_chain = (
                RunnableLambda(get_novel_resume_template) |
                model_map.get(ChapterPoint.POLISH_CONTENT.value) |
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
                return chapter_novel_resume(chapter_model, novel_content, transmit, model_map, for_num + 1)
        print(f"剧情简述-推理结果完成：{raw_text}")
        return raw_text
    except Exception as e:
        print(f"剧情简述-文本压缩失败：{e}")
        if 3 == for_num:
            chapter_model.status = ChapterStatus.FAIL.value
            return novel_content
        else:
            return chapter_novel_resume(chapter_model, novel_content, transmit, model_map, for_num + 1)