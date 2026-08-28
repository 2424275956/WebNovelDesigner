from dataclasses import dataclass


@dataclass
class StreamChunk:
    """流式片段包装"""
    text: str
    is_valid: bool = True  # False 表示该 chunk 因重复被过滤