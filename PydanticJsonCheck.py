import json
import re

from windows.polish.ChapterPolish import RelationPromptResult, ProcessPromptResult


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
  "extra": true,
  "optional_roles": [
    {
      "role_name": "宁小龄",
      "role_action": "此处存在由幻境收束到天未破晓的叙事延宕与身体预热的结构缝隙，宁小龄可在恐惧唤起、情动溢出和破境仪式三重心理机制中展开与男主的性交互，形成独立情绪闭环而保留山妖扑击的悬念。"
    }
  ]
}
"""
relation_data = ProcessPromptResult.model_validate_json(text)