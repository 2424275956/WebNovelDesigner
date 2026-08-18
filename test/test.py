import json
import re


def json_parse(raw_text):
    cleaned_json = re.sub(r'^\s*```(?:json)?\s*', '', raw_text, flags=re.IGNORECASE)
    cleaned_json = re.sub(r'\s*```\s*$', '', cleaned_json)
    return cleaned_json

def is_valid_json(json_str):
    """
    校验字符串是否为有效的 JSON 格式
    """
    # 直接尝试解析，用解析结果来判断是否合法
    try:
        parsed_data = json.loads(json_str)

        # 3. 【可选】进一步校验解析出来的是不是字典
        if not isinstance(parsed_data, dict):
            raise ValueError(f"期望返回字典，但实际返回了 {type(parsed_data)}")

        return True
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"角色分析-json格式校验失败，原因: {e}")
        return False

text =  """
{
  "character_list": [
    {
      "character_name": "宁长久",
      "alias_name": ["师兄", "呆子", "大人"],
      "identify": "道门弟子/混沌灵脉觉醒者",
      "sex": "男性",
      "type": "人类（天生灵根）",
      "size": "1米7左右",
      "colour": "白皙",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "巨大粗长型（龟头轮廓清晰，青筋暴起）",
      "core_traits": [
        {
          "trait_label": "隐忍沉稳",
          "evidence": "原文片段中，面对师妹的试探与追问，他言简意赅地回答“死了”“兴许是运气好”，独自坐在檐下看雨“一动不动”，不轻易表露内心波澜。",
          "motivation": "自我保护与消化创伤；觉醒后深知自身变化，选择以沉默掩盖真实意图，避免引起他人警觉。"
        },
        {
          "trait_label": "忠诚护短",
          "evidence": "参考片段中，符箓夺命时他“艰难地踏出了一步，拦在了少女的身前”；原文片段中主动提出“我会保护好你的”，并将师父私藏的钱财全数让给师妹，细心为其敷药。",
          "motivation": "利他与情感羁绊；尽管师妹常出言不逊，但他视其为唯一同伴，出于本能的守护欲与责任感。"
        },
        {
          "trait_label": "霸道占有",
          "evidence": "参考片段中灵脉觉醒后，他宣称“在这大殿里，只有我的规矩”，以混沌气息压制他人，强行宣告师妹为“专属容器”。",
          "motivation": "利己与本能宣泄；先天混沌灵脉苏醒带来原始欲望与力量膨胀，需通过绝对掌控来确认自身存在与安全感。"
        }
      ],
      "overall_summary": "表面木讷温顺、实则隐忍深沉的道门少年，觉醒混沌灵脉后展现出极端的霸道与占有欲，对师妹有着本能的护短与掌控欲。"
    },
    {
      "character_name": "宁小龄",
      "alias_name": ["师妹", "贼丫头"],
      "identify": "道门弟子/雪狐灵根修士",
      "sex": "女性",
      "type": "人类（天生灵根）",
      "size": "1米55左右",
      "colour": "白皙",
      "chest": "水滴型（泪珠型）",
      "chest_colour": "粉红",
      "chest_size": "硕大丰盈",
      "pubes": "蝴蝶型",
      "pubes_hair": "毛发浓密",
      "pubes_colour": "粉色",
      "penis": null,
      "core_traits": [
        {
          "trait_label": "敏锐警惕",
          "evidence": "原文片段中她直言师父看他们的眼光像“待宰的羔羊”，察觉护身符诡异；结尾处警觉发问“你到底是谁呢？”。",
          "motivation": "自我保护；作为被买来的孩童，对环境与人心保持高度戒备，依靠直觉规避潜在杀机。"
        },
        {
          "trait_label": "口是心非",
          "evidence": "原文片段中常骂师兄“呆子”，言语刻薄，却在危机时点头回应他的保护承诺，事后轻声说“谢谢你”。",
          "motivation": "情感防御；用尖锐言辞掩饰内心的不安与依赖，实则极度珍视这段相依为命的师徒/同门关系。"
        },
        {
          "trait_label": "坚韧求生",
          "evidence": "参考片段中遭受极端折磨与侵入后理智崩溃却未死亡；原文片段中经脉胀裂、紫府受损，仍强撑身体恢复并追查真相。",
          "motivation": "纯粹求生意志；拒绝成为他人修仙路上的祭品，以顽强的生命力对抗命运与外力摧残。"
        }
      ],
      "overall_summary": "外表娇小口齿锋利、实则心思细腻警觉的道门少女，身负雪狐灵根，在绝境中展现出顽强的求生欲与对师兄复杂而依赖的情感。"
    },
    {
      "character_name": "宁擒水",
      "alias_name": ["宁老先生", "师父"],
      "identify": "游方道人/修仙者",
      "sex": "男性",
      "type": "人类（修士）",
      "size": "1米7左右",
      "colour": "枯黄",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "干瘪萎缩型",
      "core_traits": [
        {
          "trait_label": "冷酷功利",
          "evidence": "参考片段中视徒弟为“法宝，该砸的时候任你心里滴血，也是要砸出去的”，毫不犹豫将其作为镇魔容器。",
          "motivation": "极端利己；为追求飞升长生，将他人生命视作可消耗的工具，毫无怜悯与师徒情分。"
        },
        {
          "trait_label": "伪善道貌岸然",
          "evidence": "原文片段中教导徒弟“秉持的是一身正气”，转头却目光灼热打量师妹身体，暗中准备用护符夺命。",
          "motivation": "维持控制与体面；以道德说教麻痹徒弟，掩盖内心的算计与欲望，以便顺利达成目的。"
        },
        {
          "trait_label": "贪婪执念",
          "evidence": "参考片段中明知“活不了几年了”，仍不惜动用珍贵紫金神符，只为换取“长生的一线生机”。",
          "motivation": "恐惧死亡与权力欲；对生命的贪恋和对长生的执念使其丧失人性底线，行事孤注一掷。"
        }
      ],
      "overall_summary": "道貌岸然、极度利己的修仙老者，为求长生不惜将徒弟视作消耗品，冷酷算计之下掩藏着压抑的欲望与对死亡的恐惧。"
    },
    {
      "character_name": "宋侧",
      "alias_name": ["宋侧大人"],
      "identify": "皇室官员/接引人",
      "sex": "男性",
      "type": "人类",
      "size": "1米75左右",
      "colour": "健康肤色",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "常态型",
      "core_traits": [
        {
          "trait_label": "圆滑试探",
          "evidence": "原文片段中故意带宁擒水前往凶宅，直言“本欲试探，如今看来果然瞒不住”，以验证其道法深浅。",
          "motivation": "职责与自保；代表皇室或“那位大人”筛选可用且可牺牲的修士，确保任务执行者具备相应能力。"
        },
        {
          "trait_label": "懦弱易控",
          "evidence": "参考片段中面对王殃渔尸身时“喉结上下滚动”“声音颤抖”，后在宁长久混沌气息笼罩下理智崩塌，跪地舔舐淫水。",
          "motivation": "力量缺失与欲望驱使；缺乏实权与修为，在绝对强权或淫靡法则面前极易丧失尊严，沦为顺从者。"
        }
      ],
      "overall_summary": "表面沉稳圆滑的皇室官员，实则外强中干，在绝对的力量与淫靡气息面前极易丧失理智，沦为顺从的见证者。"
    },
    {
      "character_name": "王殃渔",
      "alias_name": ["王将军", "走尸"],
      "identify": "已故将军/怨灵",
      "sex": "男性",
      "type": "怨灵（尸傀）",
      "size": "1米85左右",
      "colour": "青灰腐烂",
      "chest": null,
      "chest_colour": null,
      "chest_size": null,
      "pubes": null,
      "pubes_hair": null,
      "pubes_colour": null,
      "penis": "萎缩溃烂型",
      "core_traits": [
        {
          "trait_label": "怨毒凶戾",
          "evidence": "参考片段中尸身“自燃”，阴气压迫呼吸道，夺舍宁擒水后将其撕碎，惨叫凄厉。",
          "motivation": "复仇与不甘；死状凄惨（自燃、被腐蚀），死后怨气不散，本能地攻击一切靠近者以宣泄痛苦。"
        },
        {
          "trait_label": "贪婪淫邪",
          "evidence": "参考片段中夺舍后盯着宁小龄“似望见了人间至味”，笑容贪婪，残暴撕扯其衣物。",
          "motivation": "欲望释放与侵蚀；怨灵与宁擒水压抑的恶念融合，借尸还魂后彻底抛弃约束，沉溺于肉体掠夺与掌控。"
        }
      ],
      "overall_summary": "死状凄惨、怨气极重的将军厉鬼，凶戾嗜杀，夺舍老道后释放出积压的恶念与淫邪欲望。"
    }
  ]
}
"""
if not is_valid_json(text):
    print(1)
print(is_valid_json(text))