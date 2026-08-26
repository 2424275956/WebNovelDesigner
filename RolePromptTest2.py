from itertools import combinations

from pojo.relation import RelationPromptResult
from pojo.role import RolePromptResult
from sqlite.RoleRelationDB import query_role_model, query_role_relation

rele_str = """
{"character_list":[{"character_name":"宁长久","temp_alias_name":["张久","师兄"]},{"character_name":"宁小龄","temp_alias_name":["师妹"]},{"character_name":"少女","temp_alias_name":["殿下","襄儿"]},{"character_name":"宁擒水","temp_alias_name":["师父"]},{"character_name":"宋侧","temp_alias_name":["宋大人"]}]}
"""
relation_data = RelationPromptResult.RelationPromptResult(角色数组=[], 角色关系=[])
## 角色信息与关系补充
role_data = RolePromptResult.RoleResult.model_validate_json(rele_str)
if role_data and role_data.character_list:
    role_names = []
    ### 抽取全部角色
    for character in role_data.character_list:
        if character:
            character_name = character.character_name
            if character_name:
                role_names.append(character_name)
    ### 循环查询
    if role_names:
        role_list = query_role_model(3, role_names)
        if role_list:
            for role in role_list:
                print(str(role))
                if role and role['role_json']:
                    print(321.13)
                    relation_data.角色数组.append(RelationPromptResult.CharacterResult.model_validate_json(role['role_json']))
                    print(321.14)
    ### 关联关系补充
    print(321.15)
    if role_names and len(role_names) > 1:
        print(321.16)
        pairs = list(combinations(role_names, 2))
        print(321.17)
        for a, b in pairs:
            print(321.18)
            relation_json = query_role_relation(3, a, b)
            print(321.19)
            if relation_json:
                print(321.2)
                relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(relation_json['relation']))
                print(321.21)

print(relation_data.model_dump_json())