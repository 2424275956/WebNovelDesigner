from PySide6.QtWidgets import QPlainTextEdit


class CustomPlainTextEdit(QPlainTextEdit):
    def wheelEvent(self, event):
        # 先让 QPlainTextEdit 自己处理
        super().wheelEvent(event)
        # 然后阻止事件冒泡到父级
        event.accept()