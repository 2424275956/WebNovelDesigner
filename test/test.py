import json
import re


def json_parse(chain):
    cleaned_json = re.sub(r'^\s*```(?:json)?\s*', '', chain, flags=re.IGNORECASE)
    cleaned_json = re.sub(r'\s*```\s*$', '', cleaned_json)
    return cleaned_json
relation_content = json.loads("""

{
    "character_list": [
        {
            "character_name": "宁长久",
            "alias_name": ["师兄"],
            "identify": "道士/修道者（混沌灵脉觉醒体）",
            "sex": "男性",
            "type": "人类（半妖化/混沌灵体）",
            "size": "约1米75（精壮少年体型，文中描述为‘魁梧’、'高大身影笼罩下来')",
            "colour": "肤色正常，但觉醒后带有金红色灵光气息",
            "chest": null,
            "chest_colour": null,
            "chest_size": null,
            "pubes": null,
            "pubes_hair": null,
            "pubes_colour": null,
            "penis", 
        },
""")

print(relation_content)