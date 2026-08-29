from typing import Optional


class StreamingValidator:
    """
    流式输出实时重复校验器。
    维护滑动窗口，检测块状循环与行级重复。
    """

    def __init__(
            self,
            window_size: int = 10,           # 检测最近 N 行
            similarity_threshold: float = 0.75,
            max_repeat_streak: int = 2       # 连续重复 N 次触发截断
    ):
        self.lines: list[str] = []
        self.buffer: str = ""
        self.window_size = window_size
        self.threshold = similarity_threshold
        self.max_streak = max_repeat_streak
        self.repeat_streak = 0
        self.total_valid_text = ""       # 已确认的有效累积文本

    def _fingerprint(self, text: str) -> str:
        """简化指纹"""
        return text.strip().replace(" ", "").replace("　", "")[:30]

    def _is_duplicate_line(self, line: str) -> bool:
        """检查单行是否在最近历史中重复"""
        fp = self._fingerprint(line)
        if len(fp) < 6:
            return False

        recent = self.lines[-self.window_size:] if self.lines else []
        for hist in recent:
            hist_fp = self._fingerprint(hist)
            # 完全包含或高度相似
            if fp == hist_fp or fp in hist_fp or hist_fp in fp:
                return True
            # 相似度检查（针对变体重述）
            from difflib import SequenceMatcher
            if SequenceMatcher(None, fp, hist_fp).quick_ratio() > self.threshold:
                return True
        return False

    def _detect_cycle_pattern(self) -> bool:
        """检测循环模式 A-B-C-A-B-C"""
        if len(self.lines) < 6:
            return False

        tail = self.lines[-6:]
        fps = [self._fingerprint(l) for l in tail]

        # 周期 3: A-B-C-A-B-C
        if len(fps) >= 6 and fps[0] == fps[3] and fps[1] == fps[4] and fps[2] == fps[5]:
            return True

        # 退化循环
        if len(set(fps)) <= 3 and len(fps) >= 4:
            return True

        return False

    def feed(self, chunk: str) -> Optional[str]:
        """
        消费一个 chunk。
        返回: 有效文本（str）/ 空字符串（跳过）/ None（触发截断，需重试）
        """
        self.buffer += chunk

        if "\n" not in self.buffer:
            return chunk

        parts = self.buffer.split("\n")
        self.buffer = parts.pop()  # 最后一行不完整，留到下次

        output_parts = []

        for line in parts:
            line = line.strip()
            if not line:
                continue

            # 🔴 重复检测
            if self._is_duplicate_line(line):
                self.repeat_streak += 1
                if self.repeat_streak >= self.max_streak:
                    return None  # 触发重试
                continue  # 跳过本次重复

            # 🔴 循环模式检测
            self.lines.append(line)
            if self._detect_cycle_pattern():
                return None

            self.repeat_streak = 0
            output_parts.append(line + "\n")
            self.total_valid_text += line + "\n"

        return "".join(output_parts) if output_parts else ""

    def flush(self) -> str:
        """流结束，输出缓冲区剩余"""
        remaining = self.buffer.strip()
        self.buffer = ""
        if remaining and not self._is_duplicate_line(remaining):
            self.total_valid_text += remaining
            return remaining
        return ""

    def get_valid_text(self) -> str:
        """获取截至目前所有有效文本"""
        return self.total_valid_text