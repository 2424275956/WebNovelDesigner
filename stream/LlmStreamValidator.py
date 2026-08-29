from difflib import SequenceMatcher
from typing import Optional, List


class StreamingValidator:
    """
    流式输出实时重复校验器。
    按语句结尾（。！？.!?；…）分割，仅当片段长度≥30字符或出现句尾时才处理。
    """

    SENTENCE_ENDINGS = set('。！？.!?；…~')

    def __init__(
            self,
            similarity_threshold: float = 0.75,
            max_repeat_streak: int = 2,
            min_segment_len: int = 30,      # 新增：最小分割长度
            cycle_window: int = 6
    ):
        self.similarity_threshold = similarity_threshold
        self.max_repeat_streak = max_repeat_streak
        self.min_segment_len = min_segment_len
        self.cycle_window = cycle_window

        self.buffer: str = ""                      # 未处理完的缓冲区
        self.confirmed_segments: List[str] = []    # 已确认的历史句
        self.repeat_streak: int = 0
        self.total_valid_text: str = ""            # 累积有效正文

    # ───────────── 工具方法 ─────────────

    def _fingerprint(self, text: str) -> str:
        """简化指纹，用于比对"""
        return text.strip().replace(" ", "").replace("　", "")[:30]

    def _split_sentences(self, text: str) -> List[str]:
        """
        按句尾标点分割，保留标点在所属句中。
        例如："abc。def" -> ["abc。", "def"]
        """
        sentences: List[str] = []
        current = ""
        for char in text:
            current += char
            if char in self.SENTENCE_ENDINGS:
                sentences.append(current)
                current = ""
        if current:
            sentences.append(current)
        return sentences

    def _ends_with_sentence_end(self, text: str) -> bool:
        return bool(text and text[-1] in self.SENTENCE_ENDINGS)

    def _is_duplicate_segment(self, segment: str) -> bool:
        """与最近历史比对，检测单行/单句重复"""
        fp = self._fingerprint(segment)
        if len(fp) < 6:
            return False

        recent = self.confirmed_segments[-10:] if self.confirmed_segments else []
        for hist in recent:
            hist_fp = self._fingerprint(hist)
            # 完全相等
            if fp == hist_fp:
                return True
            # 互相包含
            if fp in hist_fp or hist_fp in fp:
                return True
            # 相似度
            if len(fp) > 10 and len(hist_fp) > 10:
                if SequenceMatcher(None, fp, hist_fp).quick_ratio() > self.similarity_threshold:
                    return True
        return False

    def _detect_cycle_pattern(self) -> bool:
        """检测块状循环 A-B-C-A-B-C"""
        if len(self.confirmed_segments) < self.cycle_window:
            return False

        tail = self.confirmed_segments[-self.cycle_window:]
        fps = [self._fingerprint(s) for s in tail]

        # 周期 3
        if (len(fps) >= 6 and
                fps[0] == fps[3] and fps[1] == fps[4] and fps[2] == fps[5]):
            return True

        # 退化循环（元素极少反复出现）
        if len(set(fps)) <= 3 and len(fps) >= 4:
            return True

        return False

    # ───────────── 核心 feed ─────────────

    def feed(self, chunk: str) -> Optional[str]:
        """
        消费 chunk。
        返回：
            str  -> 有效文本（可能为空字符串，表示已接收但暂不可输出）
            None -> 检测到循环/严重重复，触发截断
        """
        self.buffer += chunk

        # 🔴 长度保护：不足 min_segment_len 且没有句尾标点 → 继续累积
        if len(self.buffer) < self.min_segment_len:
            if not any(c in self.buffer for c in self.SENTENCE_ENDINGS):
                return ""  # 已接收，等待更多内容

        # 按句尾分割
        segments = self._split_sentences(self.buffer)
        if not segments:
            return ""

        # 判断最后一段是否完整（以句尾结束）
        if not self._ends_with_sentence_end(segments[-1]):
            self.buffer = segments.pop()
        else:
            self.buffer = ""

        output_parts: List[str] = []

        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue

            # 极短句（<5字）直接放行，不做重复检测
            if len(seg) < 5:
                output_parts.append(seg)
                self.confirmed_segments.append(seg)
                self.total_valid_text += seg
                continue

            # 🔴 单行重复检测
            if self._is_duplicate_segment(seg):
                self.repeat_streak += 1
                if self.repeat_streak >= self.max_repeat_streak:
                    return None  # 触发截断，外部应停止或续写
                continue  # 跳过本次重复

            # 🔴 循环模式检测（先临时加入，检测后决定）
            self.confirmed_segments.append(seg)
            if self._detect_cycle_pattern():
                self.confirmed_segments.pop()  # 回退，不污染历史
                return None

            # 确认有效
            self.repeat_streak = 0
            output_parts.append(seg)
            self.total_valid_text += seg

        return "".join(output_parts)

    # ───────────── 结束处理 ─────────────

    def flush(self) -> str:
        """
        流结束时，输出缓冲区剩余内容。
        此时跳过长度检查，但保留重复检测。
        """
        remaining = self.buffer.strip()
        self.buffer = ""

        if not remaining or len(remaining) < 3:
            return ""

        # 重复检测（宽松）
        if self._is_duplicate_segment(remaining):
            return ""

        self.confirmed_segments.append(remaining)
        self.total_valid_text += remaining
        return remaining

    def get_valid_text(self) -> str:
        return self.total_valid_text