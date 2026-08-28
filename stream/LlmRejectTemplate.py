import re

REFUSAL_PATTERNS = [
    # 英文常见拒绝
    r"(?i)i\s+(cannot|can't|am\s+unable|will\s+not)\s+(assist|help|provide|generate|create)",
    r"(?i)i'm\s+sorry.{0,30}(cannot|can't|inappropriate|harmful|illegal|ethical)",
    r"(?i)as\s+an\s+ai\s+(language\s+)?model",
    r"(?i)i\s+don't\s+feel\s+comfortable",

    # 中文常见拒绝
    r"(?i)(抱歉|对不起|不好意思).{0,20}(无法|不能|不会|不适合|违反|不合规)",
    r"(?i)(涉及|包含).{0,10}(色情|暴力|违法|犯罪|政治敏感|不当内容)",
    r"(?i)(作为|我是).{0,10}(AI|人工智能|语言模型|助手)",
    r"(?i)(拒绝|不能|无法).{0,10}(回答|生成|提供|协助)",
]

def is_refusal(text: str) -> tuple[bool, str]:
    """返回: (是否被拒绝, 匹配到的模式)"""
    if not text or len(text.strip()) < 5:
        return True, "empty_or_too_short"

    for pattern in REFUSAL_PATTERNS:
        if re.search(pattern, text):
            return True, pattern
    return False, ""