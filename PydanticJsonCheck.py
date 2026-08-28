from pojo.relation.RelationPromptResult import RelationPromptResult
from json_repair import repair_json

from stream.LlmRejectTemplate import is_refusal

json_str = """皇城里的大钟敲过三响，雨丝裹着寒意坠了下来，打在青石板上溅
"""
print(len(json_str))
print(is_refusal(json_str))