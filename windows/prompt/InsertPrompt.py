from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from resources.style.StyleSheet import title_style_sheet, line_edit_style_sheet, button_style_sheet
from sqlite.PromptDB import insert_prompt_conf


class InsertModel(QDialog):
    """新增提示词对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提示词配置")
        self.setFixedSize(280, 180)  # 设置固定大小

        self.setup_ui()

    def setup_ui(self):
        """初始化UI"""
        # 主体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        # ---- 提示词名称 ----
        name_title = QLabel("提示词名称")
        name_title.setStyleSheet(title_style_sheet())
        name_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(name_title)

        # 输入框
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入提示词模版名称")  # 使用占位符更好
        self.name_edit.setFixedSize(220, 40)
        self.name_edit.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(self.name_edit)

        # 添加间距
        main_layout.addSpacing(20)

        # ---- 底部按钮行 ----
        layout_row12 = QHBoxLayout()
        layout_row12.setAlignment(Qt.AlignmentFlag.AlignRight)  # 按钮靠右

        # 取消按钮
        close_btn = QPushButton("取消")
        close_btn.setFixedSize(80, 30)
        close_btn.setStyleSheet(button_style_sheet())
        close_btn.clicked.connect(self.close)  # 不需要 lambda
        layout_row12.addWidget(close_btn)

        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setFixedSize(80, 30)
        confirm_btn.setStyleSheet(button_style_sheet())
        confirm_btn.clicked.connect(self.confirm_model)
        layout_row12.addWidget(confirm_btn)

        main_layout.addLayout(layout_row12)

        # 自动选中输入框文本
        self.name_edit.selectAll()

    def confirm_model(self):
        """确认模型配置"""
        # 1. 获取输入内容
        name = self.name_edit.text().strip()

        # 2. 验证是否为空
        if not name:
            QMessageBox.warning(self, "提示", "请输入提示词名称")
            self.name_edit.setFocus()
            return

        # 3. 插入数据库
        try:
            result = insert_prompt_conf(name)
            if result:
                QMessageBox.information(self, "成功", "提示词添加成功！")
                self.accept()  # 关闭对话框并返回 QDialog.Accepted
            else:
                QMessageBox.warning(self, "错误", "添加失败，请重试")
        except Exception as e:
            QMessageBox.critical(self, "异常", f"添加时发生错误：{str(e)}")