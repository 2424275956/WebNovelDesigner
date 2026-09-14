from PySide6.QtWidgets import QLabel


class StatusDot(QLabel):
    def __init__(self, color: str, size: int = 16):
        super().__init__()
        self._color = color
        self._size = size
        # 设置固定大小
        self.setFixedSize(size, size)
        # 关键：用样式表画圆，背景色决定颜色
        self._apply_style()

    def _apply_style(self):
        """根据当前颜色和尺寸重建样式表"""
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {self._color};
                border-radius: {self._size // 2}px;
                border: 1px solid rgba(0,0,0,0.1);
            }}
        """)

    def set_color(self, color: str):
        """更新圆点颜色"""
        if color == self._color:
            return              # 颜色没变就不重刷，省性能
        self._color = color
        self._apply_style()