from PySide6.QtWidgets import QLabel


class StatusDot(QLabel):
    def __init__(self, color: str, size: int = 16):
        super().__init__()
        # 设置固定大小
        self.setFixedSize(size, size)
        # 关键：用样式表画圆，背景色决定颜色
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: {size // 2}px;  /* 半径 = 边长一半，形成正圆 */
                border: 1px solid rgba(0,0,0,0.1);
            }}
        """)