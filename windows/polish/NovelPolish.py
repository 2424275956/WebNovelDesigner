from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableSequence
from langchain_openai import ChatOpenAI

from sqlite.Sqlite3Utils import query_wait_polish_chapter, query_chapter_by_id, query_before_chapter, \
    query_after_chapter
from windows.polish.DynamicPromptTemplate import get_role_prompt_template, get_relation_prompt_template, \
    get_process_prompt_template


def polish(params):
    """润色小说"""
    self, transmit = params
    # 获取项目ID
    project_id = transmit['project_id']
    # 获取全部待完成章节
    chapter_list = query_wait_polish_chapter(project_id)
    # 没有待处理章节
    if chapter_list is None or len(chapter_list) <= 0:
        return

    # 模型数组
    model_map = {}
    # 循环初始化模型
    for model_id, model in transmit['model_map'].items():
        llm = ChatOpenAI(model=model['model_id'],
                         api_key=model['api_key'],
                         base_url=model['url'],
                         temperature=model['temperature'],
                         max_tokens=model['max_token'],
                         top_p=model['top_p'],
                         timeout=model['time_out'])
        model_map[model_id] = llm

    # 定义提示词
    ## 角色分析提示词模版
    # role_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['role_system']),
    #     ("user", transmit['role_user'])
    # ])
    # ## 关系分析提示词模版
    # relation_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['relation_system']),
    #     ("user", transmit['relation_user'])
    # ])
    # ## 流程控制提示词模版
    # process_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['process_system']),
    #     ("user", transmit['process_user'])
    # ])
    # ## 原文改写
    # ### 原文改写-场景分析
    # original_scene_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['scene_system']),
    #     ("user", transmit['scene_user'])
    # ])
    # ### 原文改写-脉络改写
    # original_framework_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['framework_system']),
    #     ("user", transmit['framework_user'])
    # ])
    # ## 番外撰写
    # ### 番外撰写-场景分析
    # extra_scene_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['extra_scene_system']),
    #     ("user", transmit['extra_scene_user'])
    # ])
    # ### 番外撰写-脉络生成
    # extra_framework_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['extra_framework_system']),
    #     ("user", transmit['extra_framework_user'])
    # ])
    # ## 结果润色
    # polish_prompt_template = ChatPromptTemplate.from_messages([
    #     ("system", transmit['polish_system']),
    #     ("user", transmit['polish_user'])
    # ])

    # 测试
    # 取一个章节
    chapter = chapter_list[0]
    # 获取最新章节信息
    chapter = query_chapter_by_id(chapter['id'])
    # 获取前几章内容
    reference_text = ""
    chapter_before_list = query_before_chapter(chapter['project_id'], chapter['sort'], transmit['polish_before_num'])
    if chapter_before_list:
        for chapter_before in chapter_before_list:
            if chapter_before['new_content'] is None or len(chapter_before['new_content']) <= 0:
                reference_text = reference_text + chapter_before['old_content']
            else:
                reference_text = reference_text + chapter_before['new_content']
    else:
        reference_text = "-"

    print(1.01)
    # 角色分析
    # role_chain = (
    #         RunnableLambda(get_role_prompt_template) |
    #         model_map.get(transmit['role_model_id']) |
    #         StrOutputParser()
    # )
    print(1.02)
    # role = role_chain.invoke({
    #     "reference_text": reference_text,
    #     "original_text": chapter['old_content'],
    #     "role_prompt_system": transmit['role_system'],
    #     "role_prompt_user": transmit['role_user']
    # })
    # print(f"role {role}")
    role = """{
  "character_list": [
    {
      "character_name": "宁擒水",
      "alias_name": "宁老先生",
      "identify": "老道士 / 师父",
      "sex": "男性",
      "type": "人类",
      "size": "约1米7（推测）",
      "colour": "面色削瘦苍白（推测）",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "蘑菇头型",
      "core_traits": [
        {
          "trait_label": "深谋远虑",
          "evidence": "宁擒水一到宫院便通过铜币试探出凶宅的秘密，并识破了宋侧的试探。",
          "motivation": "自我保护与掌控局势，确保自己在危险任务中的主动权。"
        },
        {
          "trait_label": "冷酷无情",
          "evidence": "宁擒水在嘱咐徒儿后，关门时回头看了一眼，目光冷漠如看死人一般。",
          "motivation": "利己主义，将徒儿视为可以利用的工具或祭品。"
        },
        {
          "trait_label": "虚伪伪善",
          "evidence": "宁擒水表面教导徒儿修道要秉持正气，实则心思深沉，可能对徒儿另有打算。",
          "motivation": "维护自己在徒儿心中的形象，以便更好地操控他们。"
        }
      ],
      "overall_summary": "宁擒水是一个深谋远虑、冷酷无情且虚伪伪善的老道士，善于利用他人达成自己的目的。"
    },
    {
      "character_name": "宁小龄",
      "alias_name": "师妹",
      "identify": "少年道士 / 徒儿",
      "sex": "女性",
      "type": "人类",
      "size": "约1米5（推测）",
      "colour": "白皙（推测）",
      "chest": "水滴型（泪珠型）",
      "chest_colour": "粉红",
      "chest_size": "精致小巧",
      "pubes": "一线天型",
      "pubes_hair": "毛发稀疏",
      "pubes_colour": "粉色",
      "penis": null,
      "core_traits": [
        {
          "trait_label": "聪慧敏锐",
          "evidence": "宁小龄察觉到师父看他们的眼光不对，怀疑自己随时可能被利用。",
          "motivation": "自我保护意识强，试图看清局势以保全自己。"
        },
        {
          "trait_label": "刻薄直率",
          "evidence": "宁小龄直言师父可能是把他们养大后卖掉或吃掉，并嘲笑师兄的迟钝。",
          "motivation": "内心不安与愤怒的外化，借此宣泄情绪。"
        },
        {
          "trait_label": "隐忍不安",
          "evidence": "宁小龄表面上装作不在意，但心中怀揣秘密与底气，却愈发觉得不安。",
          "motivation": "对未来充满未知的恐惧，但仍努力保持冷静。"
        }
      ],
      "overall_summary": "宁小龄是一个聪慧敏锐、刻薄直率但内心隐忍不安的少女，对师父充满怀疑与戒备。"
    },
    {
      "character_name": "宁长久",
      "alias_name": "师兄",
      "identify": "少年道士 / 徒儿",
      "sex": "男性",
      "type": "人类",
      "size": "约1米6（推测）",
      "colour": "健康肤色（推测）",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "子弹头型",
      "core_traits": [
        {
          "trait_label": "单纯轻信",
          "evidence": "宁长久对师父的教诲深信不疑，甚至认为师父自有深意。",
          "motivation": "缺乏独立思考能力，倾向于依赖权威人物。"
        },
        {
          "trait_label": "善良忠诚",
          "evidence": "宁长久在离开房间时小声安慰师妹，表示会保护她。",
          "motivation": "出于对同门情谊的珍视与责任感。"
        },
        {
          "trait_label": "迟钝困惑",
          "evidence": "宁长久无法理解师妹为何说出如此刻薄的话，也对自己的古怪记忆感到迷茫。",
          "motivation": "思维不够灵活，容易陷入自我怀疑与困惑之中。"
        }
      ],
      "overall_summary": "宁长久是一个单纯轻信、善良忠诚但略显迟钝的少年，对师父和师妹抱有朴素的信任。"
    },
    {
      "character_name": "宋侧",
      "alias_name": "中年男子 / 下官",
      "identify": "皇城官员",
      "sex": "男性",
      "type": "人类",
      "size": "约1米75（推测）",
      "colour": "正常肤色（推测）",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "平头型",
      "core_traits": [
        {
          "trait_label": "谨慎多疑",
          "evidence": "宋侧特意带宁擒水到凶宅试探其实力，确认对方能力后才放心。",
          "motivation": "确保任务顺利进行，避免因用人不当而承担风险。"
        },
        {
          "trait_label": "圆滑世故",
          "evidence": "宋侧在试探过程中始终保持礼貌与微笑，事后还主动提出安排别院。",
          "motivation": "维护自身形象与关系，避免因试探引发冲突。"
        }
      ],
      "overall_summary": "宋侧是一个谨慎多疑、圆滑世故的皇城官员，善于权衡利弊以达成目标。"
    }
  ] 
}"""
    # 关系分析
    # relation_chain = (
    #     RunnableLambda(get_relation_prompt_template) |
    #     model_map.get(transmit['relation_model_id']) |
    #     StrOutputParser()
    # )
    print(1.03)
    # relation = relation_chain.invoke({
    #     "role_analysis": str(role),
    #     "relation_prompt_system": transmit['relation_system'],
    #     "relation_prompt_user": transmit['relation_user'],
    #     "reference_text": reference_text,
    #     "original_text": chapter['old_content'],
    #     "db_role_json": "-"
    # })
    # print(f"relation {relation}")
    relation = """
    {
  "character_list": [
    {
      "character_name": "宁擒水",
      "alias_name": "宁老先生",
      "identify": "老道士 / 师父",
      "sex": "男性",
      "type": "人类",
      "size": "约1米7（推测）",
      "colour": "面色削瘦苍白（推测）",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "蘑菇头型",
      "core_traits": [
        {
          "trait_label": "深谋远虑",
          "evidence": "宁擒水一到宫院便通过铜币试探出凶宅的秘密，并识破了宋侧的试探。",
          "motivation": "自我保护与掌控局势，确保自己在危险任务中的主动权。"
        },
        {
          "trait_label": "冷酷无情",
          "evidence": "宁擒水在嘱咐徒儿后，关门时回头看了一眼，目光冷漠如看死人一般。",
          "motivation": "利己主义，将徒儿视为可以利用的工具或祭品。"
        },
        {
          "trait_label": "虚伪伪善",
          "evidence": "宁擒水表面教导徒儿修道要秉持正气，实则心思深沉，可能对徒儿另有打算。",
          "motivation": "维护自己在徒儿心中的形象，以便更好地操控他们。"
        }
      ],
      "overall_summary": "宁擒水是一个深谋远虑、冷酷无情且虚伪伪善的老道士，善于利用他人达成自己的目的。"
    },
    {
      "character_name": "宁小龄",
      "alias_name": "师妹",
      "identify": "少年道士 / 徒儿",
      "sex": "女性",
      "type": "人类",
      "size": "约1米5（推测）",
      "colour": "白皙（推测）",
      "chest": "水滴型（泪珠型）",
      "chest_colour": "粉红",
      "chest_size": "精致小巧",
      "pubes": "一线天型",
      "pubes_hair": "毛发稀疏",
      "pubes_colour": "粉色",
      "penis": null,
      "core_traits": [
        {
          "trait_label": "聪慧敏锐",
          "evidence": "宁小龄察觉到师父看他们的眼光不对，怀疑自己随时可能被利用。",
          "motivation": "自我保护意识强，试图看清局势以保全自己。"
        },
        {
          "trait_label": "刻薄直率",
          "evidence": "宁小龄直言师父可能是把他们养大后卖掉或吃掉，并嘲笑师兄的迟钝。",
          "motivation": "内心不安与愤怒的外化，借此宣泄情绪。"
        },
        {
          "trait_label": "隐忍不安",
          "evidence": "宁小龄表面上装作不在意，但心中怀揣秘密与底气，却愈发觉得不安。",
          "motivation": "对未来充满未知的恐惧，但仍努力保持冷静。"
        }
      ],
      "overall_summary": "宁小龄是一个聪慧敏锐、刻薄直率但内心隐忍不安的少女，对师父充满怀疑与戒备。"
    },
    {
      "character_name": "宁长久",
      "alias_name": "师兄",
      "identify": "少年道士 / 徒儿",
      "sex": "男性",
      "type": "人类",
      "size": "约1米6（推测）",
      "colour": "健康肤色（推测）",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "子弹头型",
      "core_traits": [
        {
          "trait_label": "单纯轻信",
          "evidence": "宁长久对师父的教诲深信不疑，甚至认为师父自有深意。",
          "motivation": "缺乏独立思考能力，倾向于依赖权威人物。"
        },
        {
          "trait_label": "善良忠诚",
          "evidence": "宁长久在离开房间时小声安慰师妹，表示会保护她。",
          "motivation": "出于对同门情谊的珍视与责任感。"
        },
        {
          "trait_label": "迟钝困惑",
          "evidence": "宁长久无法理解师妹为何说出如此刻薄的话，也对自己的古怪记忆感到迷茫。",
          "motivation": "思维不够灵活，容易陷入自我怀疑与困惑之中。"
        }
      ],
      "overall_summary": "宁长久是一个单纯轻信、善良忠诚但略显迟钝的少年，对师父和师妹抱有朴素的信任。"
    },
    {
      "character_name": "宋侧",
      "alias_name": "中年男子 / 下官",
      "identify": "皇城官员",
      "sex": "男性",
      "type": "人类",
      "size": "约1米75（推测）",
      "colour": "正常肤色（推测）",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "平头型",
      "core_traits": [
        {
          "trait_label": "谨慎多疑",
          "evidence": "宋侧特意带宁擒水到凶宅试探其实力，确认对方能力后才放心。",
          "motivation": "确保任务顺利进行，避免因用人不当而承担风险。"
        },
        {
          "trait_label": "圆滑世故",
          "evidence": "宋侧在试探过程中始终保持礼貌与微笑，事后还主动提出安排别院。",
          "motivation": "维护自身形象与关系，避免因试探引发冲突。"
        }
      ],
      "overall_summary": "宋侧是一个谨慎多疑、圆滑世故的皇城官员，善于权衡利弊以达成目标。"
    }
  ],
  "relationships": [
    {
      "character_a": "宁擒水",
      "character_b": "宋侧",
      "relation_label": "利益同盟 / 试探与认可",
      "interaction_analysis": "宋侧因任务凶险而多疑，试图试探宁擒水的真实能力；宁擒水凭借高超道术识破试探并反向揭示凶宅真相，赢得了宋侧的钦佩与信任。两人基于共同利益（驱邪任务）达成默契合作。",
      "evidence": "宋侧带宁擒水至凶宅试探，宁擒水以铜币之术揭穿真相后，宋侧表示‘传闻果然不假’并安排其住别院。",
      "overall_relation_summary": "宋侧与宁擒水是建立在相互试探、认可基础上的利益合作关系，彼此心照不宣地维持着表面客气。"
    },
    {
      "character_a": "宁擒水",
      "character_b": "宁长久",
      "relation_label": "操控者与被操控者 / 伪师徒",
      "interaction_analysis": "宁长久单纯轻信、渴望认同，容易被权威引导；宁擒水利用其忠诚与迟钝，用‘修道正气’等说辞进行精神控制，实则将其视为可利用的棋子。宁长久的信任反而加深了宁擒水的冷酷算计。",
      "evidence": "宁长久对师父教诲深信不疑，而宁擒水关门时‘如看死人一般’地注视他。",
      "overall_relation_summary": "宁擒水以伪善的师父形象操控单纯忠诚的宁长久，形成一种不对等的、充满利用意味的‘师徒’关系。"
    },
    {
      "character_a": "宁擒水",
      "character_b": "宁小龄",
      "relation_label": "猎人与猎物 / 怀疑与戒备",
      "interaction_analysis": "宁小龄聪慧敏锐，能察觉师父眼中的异样与潜在危险，因此对其保持高度警惕；宁擒水则因其清醒而可能更加忌惮或厌恶，但仍试图用话术稳住她。两人处于一种表面顺从、内心博弈的紧张关系中。",
      "evidence": "宁小龄直言师父可能‘卖掉或吃掉’他们，并怀疑其眼光不对；宁擒水虽未正面回应，但关门时的冷漠目光暗示其真实态度。",
      "overall_relation_summary": "宁小龄对宁擒水充满怀疑与戒备，而宁擒水则视她为潜在威胁或可利用工具，双方处于一种暗流涌动的对峙状态。"
    },
    {
      "character_a": "宁长久",
      "character_b": "宁小龄",
      "relation_label": "师兄妹 / 信任与疏离",
      "interaction_analysis": "宁长久善良迟钝，试图保护师妹并维护师父形象；宁小龄则因看透现实而显得刻薄疏离，对师兄的‘天真’感到无奈甚至轻视。两人虽为同门，但因认知差异与性格反差，关系并不亲密，更多是形式上的陪伴。",
      "evidence": "宁长久安慰师妹‘我会保护你’，而宁小龄内心冷哼‘呆子’却仍点头回应；她嘲笑师兄中邪，也叹其笨拙。",
      "overall_relation_summary": "宁长久与宁小龄是名义上的师兄妹，实则因性格与认知差异而彼此疏离，宁长久试图维系温情，宁小龄则清醒地保持距离。"
    }
  ]
}
"""
    print(1.04)
    process_chain = (
        RunnableLambda(get_process_prompt_template) |
        model_map.get(transmit['process_model_id']) |
        StrOutputParser()
    )
    print(1.05)
    # 获取后几章内容
    reference_after_text = ""
    chapter_after_list = query_after_chapter(chapter['project_id'], chapter['sort'], transmit['polish_after_num'])
    if chapter_after_list:
        for chapter_after in chapter_after_list:
            if chapter_after['new_content'] is None or len(chapter_after['new_content']) <= 0:
                reference_after_text = reference_after_text + chapter_after['old_content']
            else:
                reference_after_text = reference_after_text + chapter_after['new_content']
    else:
        reference_after_text = "-"
    print(1.06)
    process = process_chain.invoke({
        "relation_analysis": str(relation),
        "process_prompt_system": transmit['process_system'],
        "process_prompt_user": transmit['process_user'],
        "reference_before_text": reference_text,
        "original_text": chapter['old_content'],
        "reference_after_text": reference_after_text
    })
    print(process)
    print(1.07)
    return

    # 定义LangChain流程
    ## 公共前置LangChain链
    common_chain = (
        {"role_analysis": role_prompt_template | model_map.get(transmit['role_model_id']) | StrOutputParser() | RunnableLambda()} |
        {"relation_analysis": relation_prompt_template | model_map.get(transmit['relation_model_id']) | StrOutputParser()} |
        {"process_analysis": process_prompt_template | model_map.get(transmit['process_model_id']) | StrOutputParser()}
    )
    ## 原文改写LangChain链
    original_chain = (
        {"original_scene_analysis": original_scene_prompt_template | model_map.get(transmit['scene_model_id']) | StrOutputParser()} |
        {"original_framework_analysis": original_framework_prompt_template | model_map.get(transmit['framework_model_id']) | StrOutputParser()} |
        {"polish_analysis": polish_prompt_template | model_map.get(transmit['polish_model_id']) | StrOutputParser()}
    )
    ## 番外撰写LangChain链
    extra_chain = (
        {"extra_scene_analysis": extra_scene_prompt_template | model_map.get(transmit['extra_scene_model_id']) | StrOutputParser()} |
        {"extra_framework_analysis": extra_framework_prompt_template | model_map.get(transmit['extra_framework_model_id']) | StrOutputParser()} |
        {"polish_analysis": polish_prompt_template | model_map.get(transmit['polish_model_id']) | StrOutputParser()}
    )

    # 循环处理
    for chapter in chapter_list:
        # 从开头开始
        if 400 > chapter['point']:
            # 判断是否需要切割
            if 100 == chapter['point']:
                # todo 首次进入正常执行
                123
            elif 200 == chapter['point']:
                # todo 截取执行
                123
            else:
                # todo 流程控制执行
                321

        # 如果进入说明，上次失败导致进度卡住了
        if 2 == chapter['type']:
            # 说明刚到就退出了
            if 410 == chapter['point']:
                # todo 正常执行番外撰写
                123
            elif 411 == chapter['point']:
                # todo 截取并执行
                123
            else:
                # todo 润色
                123
        else:
            # 先判断节点
            if 400 == chapter['point']:
                # 判断是否需要扩写内容
                is_extra = False
                if is_extra:
                    """需要进行番外扩写"""
                    # todo 新增番外章节
                    # todo 改写当前章节
                else:
                    """不需要扩写，正常执行"""
            elif 401 == chapter['point']:
                # todo 截取执行
                123
            else:
                # todo 润色
                123

def chapter_polish(self, chapter, transmit):
    123