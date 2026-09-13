import os

import shiboken6
from PySide6.QtGui import QTextCursor


def open_file(file_path):
    """打开最新文件"""
    # 确保父目录存在
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    # 用 rb 打开，seek 定位更准确；稍后 decode
    with open(file_path, 'a', encoding="utf-8") as f:
        """打开文件，存在无妨，不存在创建"""
    log_file = open(file_path, "rb")
    log_file.seek(0, os.SEEK_END)  # 从末尾开始（只看新内容）
    return log_file

def read_new(self, log_file, log_path):
    if not shiboken6.isValid(self.polish_log_content):
        return
    if log_file is None:
        return
    try:
        # 文件被轮转/删除后重建的情况
        if not os.path.exists(log_path):
            return

        log_file.seek(self.log_pos)
        data = log_file.read()
        if not data:
            return

        self.log_pos = log_file.tell()
        text = data.decode("utf-8", errors="replace")

        # 追加到控件
        self.polish_log_content.moveCursor(QTextCursor.MoveOperation.End)
        self.polish_log_content.insertPlainText(text)

        # 自动滚到底
        if self._auto_scroll:
            sb = self.polish_log_content.verticalScrollBar()
            sb.setValue(sb.maximum())
    except Exception as e:
        # 出错时不要在 UI 里疯狂报错
        print("read log error:", e)

def on_scroll(self, value: int):
    sb = self.polish_log_content.verticalScrollBar()
    # 是否贴底（容差 4px）
    self._auto_scroll = value >= sb.maximum() - 4