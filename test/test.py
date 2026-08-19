import json
import re

from windows.polish.ChapterPolish import RelationPromptResult


def json_parse(raw_text: str):
    if not isinstance(raw_text, str):
        return None

    # 1. 剥离首尾的 Markdown 标记
    cleaned = re.sub(r'^\s*```(?:json)?\s*', '', raw_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```\s*$', '', cleaned)

    # 2. 【终极修复】处理字符串内部未转义的双引号
    # 逻辑：利用 JSON 的键值对结构 `": "` 作为锚点，将两个锚点之间所有残留的英文双引号
    # 强制替换为中文双引号，从而避免破坏 JSON 的解析结构
    def fix_inner_quotes(match):
        content = match.group(1)
        # 将字符串内容中残留的英文双引号替换为中文引号
        content = content.replace('"', '“').replace('"', '”')
        return f': "{content}"'

    # 匹配 JSON 中 ": "..." 的结构，对中间的内容进行替换
    cleaned = re.sub(r':\s*"((?:[^"\\]|\\.)*)"', fix_inner_quotes, cleaned)

    # 3. 剔除尾部多余的逗号和非法符号
    cleaned = re.sub(r',+\s*$', '', cleaned)
    cleaned = re.sub(r',+\s*([}\]])', r'\1', cleaned)

    # 4. 智能补全缺失的括号
    open_braces = cleaned.count('{') - cleaned.count('}')
    open_brackets = cleaned.count('[') - cleaned.count(']')
    if open_braces > 0: cleaned += '}' * open_braces
    if open_brackets > 0: cleaned += ']' * open_brackets

    # 5. 尝试解析
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[警告] JSON 修复后仍解析失败: {e}")
        return None

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

"""
relation_data = RelationPromptResult.model_validate_json(text)