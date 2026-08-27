from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame


class ClickableFrame(QFrame):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置鼠标悬停时变为小手 (PySide6 需要写全枚举路径)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        # 仅响应鼠标左键
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        # 调用父类方法，确保子控件（如按钮）的事件正常处理
        super().mousePressEvent(event)