from pojo.relation import RelationPromptResult
from sqlite.RoleRelationDB import query_family_role, query_family_relation_name_a, query_family_relation_name_b

relation_data = RelationPromptResult.RelationPromptResult(角色关系=[], 角色数组=[])
# 获取主角女性亲友信息
family_list = query_family_role(3)
if family_list:
    ## 循环处理
    role_names = []
    for family in family_list:
        role_names.append(family['role_name'])
        relation_data.角色数组.append(RelationPromptResult.CharacterResult.model_validate_json(family['role_json']))
    ## 关系补充
    if role_names and len(role_names) > 0:
        names_a = query_family_relation_name_a(3, role_names)
        if names_a:
            for item in names_a:
                relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(item['relation']))
        names_b = query_family_relation_name_b(3, role_names)
        if names_b:
            for item in names_b:
                relation_data.角色关系.append(RelationPromptResult.RelationResult.model_validate_json(item['relation']))
print(relation_data.model_dump_json())