import json
from itertools import permutations

from sqlite.Sqlite3Utils import remove_old_role_model, insert_role_model, remove_old_role_relation, insert_role_relation

project_id = 1
text = """
{
  "character_list": [
    {
      "character_name": "宁长久",
      "alias_name": ["张久"],
      "identify": "道士弟子 / 混沌灵脉觉醒者",
      "sex": "男性",
      "type": "人类(修真)",
      "size": "1米75左右",
      "colour": "苍白至健康小麦色(觉醒后肌肉紧绷)",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "龙鳞状巨物型(远超常理尺寸)",
      "core_traits": [
        {
          "trait_label": "隐忍伪装",
          "evidence": "前期表现得木讷痴傻(被宁小龄称为呆子师兄)，对师父的试探和阴谋不置可否，暗中保护师妹并默默打坐掩饰内心波动。",
          "motivation": "因记忆碎片化与身份认知混乱，出于生存本能隐藏真实状态；同时受修道规矩束缚，习惯性压抑自我。"
        },
        {
          "trait_label": "霸道掌控欲强",
          "evidence": "觉醒混沌灵脉后，对宁小龄实施绝对支配(强行压制、羞辱并宣告主权)，称其为专属容器，对宋侧等旁观者展现不容置疑的威严。",
          "motivation": "混沌法则自带的原始雄性荷尔蒙与占有欲觉醒；曾作为容器被利用的创伤转化为对控制权与被支配者的极致渴望。"
        },
        {
          "trait_label": "冷静理智/敏锐洞察",
          "evidence": "在九灵台面对师父腐烂尸身时情绪稳定，通过观察尸体胸口的怪鸟血印与红点痕迹冷静推演死亡原因并追问宋侧二十天前事件。",
          "motivation": "务实的生存策略；不迷信传统驱邪手段，倾向于寻找事物根源与逻辑症结以高效解决威胁。"
        }
      ],
      "overall_summary": "表面温顺隐忍实则心思缜密，觉醒后受混沌法则驱使展现出极度霸道、冷酷且充满掌控欲的绝对支配者形象。"
    },
    {
      "character_name": "宁小龄",
      "alias_name": ["师妹"],
      "identify": "道士弟子 / 雪狐灵根持有者",
      "sex": "女性",
      "type": "人类(修真)",
      "size": "1米58左右",
      "colour": "白皙泛着细腻釉色",
      "chest": "水滴型(泪珠型)",
      "chest_colour": "粉红",
      "chest_size": "饱满(初具规模至硕大丰盈)",
      "pubes": "蝴蝶型",
      "pubes_hair": "毛发浓密且湿润泛油亮光泽(被淫水浸透)",
      "pubes_colour": "粉色至深粉充血",
      "penis": null,
      "core_traits": [
        {
          "trait_label": "敏锐多疑",
          "evidence": "较早察觉师父宁擒水目光不对(看他们像私藏金银或待宰羔羊)，直言其可能随时卖了自己，后期也警惕质问宁长久身份。",
          "motivation": "自我保护机制；深知自己是被买来的命，缺乏安全感导致对权威和亲近之人抱有本能的不信任与警惕。"
        },
        {
          "trait_label": "矛盾挣扎",
          "evidence": "恐惧宁长久的视线与触碰，却在阴符灵力侵蚀下身体不受控地分泌爱液并产生隐秘渴望；理智抗拒但生理本能迎合。",
          "motivation": "修道者的道德底线与理性认知同体内雪狐灵根被混沌能量点燃后的原始欲望发生剧烈冲突。"
        },
        {
          "trait_label": "顺从臣服(后期)",
          "evidence": "在混沌气息彻底掌控下放弃抵抗，跪地爬行侍奉并哀求被灌满精液称其为容器之主。",
          "motivation": "精神防线在绝对力量与灵力改造下彻底崩塌；生存本能适应新秩序，将臣服视为唯一的存活方式。"
        }
      ],
      "overall_summary": "聪慧敏锐且对人性抱有警惕，但在绝对的力量压制与混沌灵力侵蚀下，从挣扎反抗彻底异化为渴望被支配、甘愿臣服的专属容器。"
    },
    {
      "character_name": "宁擒水",
      "alias_name": ["师父"],
      "identify": "资深道士 / 容器实验者",
      "sex": "男性",
      "type": "人类(修真)",
      "size": "1米70左右",
      "colour": "削瘦如刀刻至死灰腐烂(后期)",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "普通萎缩型",
      "core_traits": [
        {
          "trait_label": "阴险狡诈",
          "evidence": "将黄符称为护身宝符实则作为夺命钩索，暗中耗费数年寻找合适徒儿作为容器以吸收阴邪之气。",
          "motivation": "为实现飞升觅长生的目的不择手段；将他人完全物化为修行的工具与耗材。"
        },
        {
          "trait_label": "冷酷自私",
          "evidence": "在法事危急时刻毫不犹豫将徒儿推向死路，认为该砸的时候任你心里滴血也要砸出去。",
          "motivation": "极端的利己主义；在自身性命与长生面前，师徒伦理毫无价值。"
        },
        {
          "trait_label": "贪婪好色",
          "evidence": "言语中暗示徒儿心思纯净莫生歪念，视线却刻意停留在宁小龄胸口；被夺舍后尸体借机撕扯少女衣物释放积压恶念。",
          "motivation": "道貌岸然下的压抑欲望；视年幼徒儿为私有物与发泄对象，受肉体腐朽影响恶念彻底失控。"
        }
      ],
      "overall_summary": "道貌岸然却心狠手辣的功利主义者，为求长生视人命如草芥，其冷酷算计与隐秘欲望最终导致自身沦为怨灵躯壳。"
    },
    {
      "character_name": "宋侧",
      "alias_name": ["宋大人"],
      "identify": "皇城官员 / 皇室联络人",
      "sex": "男性",
      "type": "人类(凡人)",
      "size": "1米72左右",
      "colour": "正常肤色(后期憔悴)",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "子弹头型",
      "core_traits": [
        {
          "trait_label": "谨慎务实",
          "evidence": "初次接触宁擒水时先试探其道法深浅，事后只想尽快将徒儿送出皇城以平息事态。",
          "motivation": "维护皇室利益与朝局稳定；倾向于用可控手段处理超自然事件，避免不可预测的风险。"
        },
        {
          "trait_label": "畏惧权势/易动摇",
          "evidence": "面对宁长久觉醒后的混沌威压瞬间双腿发软跪地臣服；听闻血羽君出世时神色癫狂颤抖。",
          "motivation": "凡人面对未知与绝对力量时的生存本能；尊严在强权压迫下迅速让位于自我保全。"
        },
        {
          "trait_label": "圆滑世故",
          "evidence": "周旋于道士、皇帝与宫人之间，应对得体并迅速处理王殃渔将军府变故的现场秩序。",
          "motivation": "在复杂的政治生态中保全自身官位与仕途；善于平衡各方势力以避免成为牺牲品。"
        }
      ],
      "overall_summary": "善于周旋于朝堂与诡异之间的务实官僚，表面镇定自持实则极度畏惧未知力量，在绝对威压面前迅速放弃尊严以求苟全。"
    }
  ],
  "relationships": [
    {
      "character_a": "宁长久",
      "character_b": "宁小龄",
      "relation_label": "支配与臣服 / 掠夺者与容器",
      "interaction_analysis": "宁长久觉醒后的“霸道掌控欲”结合混沌灵脉的原始法则，彻底碾压了宁小龄基于修道道德与个人意志构建的心理防线。而宁小龄“雪狐灵根”的生理特性使其在灵力侵蚀下产生无法抗拒的欲望反馈，其“矛盾挣扎”迅速转化为生存本能驱动的“顺从臣服”，最终形成以肉体与精神完全占有为核心的绝对支配关系。",
      "evidence": "宁长久强行宣告“专属容器”主权、实施羞辱性性行为并灌注精液；宁小龄从恐惧抗拒到主动哀求“变成你的容器”、“是……主人”。",
      "overall_relation_summary": "由师兄妹情谊彻底异化为主仆与掠夺关系，以混沌灵力为锁链将女性完全物化为满足支配欲的活体容器。"
    },
    {
      "character_a": "宁长久",
      "character_b": "宁擒水",
      "relation_label": "伪师徒 / 猎食者与反噬猎物",
      "interaction_analysis": "宁擒水出于“阴险狡诈”与飞升私欲，将徒弟视为可牺牲的修行耗材（容器），其“冷酷自私”直接导致他尝试吞噬宁长久。然而此举意外唤醒了潜伏的混沌灵脉，使原本“隐忍伪装”、处于食物链底端的宁长久瞬间进化为拥有绝对力量的上位者，完成猎杀与身份的反转。",
      "evidence": "宁擒水一掌拍开天灵盖灌入恶灵、视徒儿为“该砸就砸”的法宝；宁长久苏醒后一指化腐朽、冷漠评价“真弱”，并继承其冷酷特质用于支配他人。",
      "overall_relation_summary": "一场以长生为饵的残酷献祭反噬，被剥削者通过力量觉醒彻底碾碎伪善导师的物理与精神存在。"
    },
    {
      "character_a": "宁长久",
      "character_b": "宋侧",
      "relation_label": "威权碾压与卑微附庸 / 绝对支配者与被臣服官僚",
      "interaction_analysis": "宋侧作为凡人官僚，其“谨慎务实”建立在世俗权力秩序之上。当面对宁长久觉醒后散发出的超自然混沌威压与原始兽性时，其“畏惧权势/易动摇”的本能被瞬间激发。世俗官威在绝对力量面前毫无意义，促使他迅速抛弃尊严与理性认知，转而寻求依附以求自保甚至获得恩赐。",
      "evidence": "宋侧初见其威压时双腿发软跪地、目睹淫靡场景后理智崩塌；卑微哀求“赐奴”并虔诚舔舐精液混合物。",
      "overall_relation_summary": "世俗官僚体系对不可名状之混沌力量的本能臣服，权力关系从试探利用瞬间跌落为彻底的敬畏与奴性依附。"
    },
    {
      "character_a": "宁擒水",
      "character_b": "宁小龄",
      "relation_label": "物化利用与潜在猎物 / 伪善导师与被剥削容器",
      "interaction_analysis": "宁擒水的“贪婪好色”与其将徒儿视为工具的动机，使他对宁小龄始终抱有隐秘的物化视线与性剥削意图。尽管表面上维持师徒伦理，但其“阴险狡诈”的本质注定她只是待宰羔羊。宁小龄的“敏锐多疑”虽让她提前察觉危机，但在绝对的力量与算计差距下仍无力反抗。",
      "evidence": "宁擒水借贴符之名揉捏其胸口与私密处、法事时毫不犹豫将其推向死路；夺舍尸体后撕扯其衣物释放积压欲望。",
      "overall_relation_summary": "披着修道外衣的残酷剥削关系，女性弟子在导师绝对的利益权衡与隐秘欲望中被彻底物化为可消耗的资源。"
    }
  ]
}
"""
relation_content = json.loads(text)
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
            remove_old_role_model(project_id, role_name)
        for cha in character_list:
            name = cha.get("character_name")
            if name:
                insert_role_model(project_id, name, cha)
        # 关系
        if len(role_name) > 1:
            relation_list = list(permutations(role_name, 2))
            # 清除关系信息
            if relation_list:
                for a, b in relation_list:
                    remove_old_role_relation(project_id, a, b)
    # 新增关系
    relationships = relation_content.get("relationships")
    if relationships:
        for relation in relationships:
            role_a = relation.get("character_a")
            role_b = relation.get("character_b")
            if role_a and role_b:
                insert_role_relation(project_id, role_a, role_b, relation)
    print("处理完成")