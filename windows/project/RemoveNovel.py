from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from sqlite.Sqlite3Utils import remove_novel_info


class RemoveNovel(QDialog):
    def __init__(self, project_id, parent=None):
        super().__init__(parent)
        """生成弹窗"""
        self.setWindowTitle("确认操作")
        self.setFixedSize(300, 150)

        # 1. 布局
        layout = QVBoxLayout(self)

        # 2. 提示文本
        label = QLabel("你确定要执行此操作吗？")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # 3. 按钮区域
        btn_layout = QHBoxLayout()

        self.btn_cancel = QPushButton("取消")
        self.btn_ok = QPushButton("确定")

        # 设置按钮样式（可选）
        self.btn_ok.setStyleSheet("""
            QPushButton { background-color: #1890ff; color: white; padding: 6px 20px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #40a9ff; }
        """)
        self.btn_cancel.setStyleSheet("""
            QPushButton { background-color: #1890ff; color: white; padding: 6px 20px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #40a9ff; }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)

        # 4. 绑定信号
        self.btn_ok.clicked.connect(lambda: self.remove_novel_parse(project_id))
        self.btn_cancel.clicked.connect(self.reject)

    def remove_novel_parse(self, project_id):
        """删除novel数据"""
        remove_novel_info(project_id)
        self.accept()