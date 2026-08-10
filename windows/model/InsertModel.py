from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QComboBox, QFrame, QPushButton

from style.StyleSheet import title_style_sheet, line_edit_style_sheet, button_style_sheet
from utils.DoubleLineEdit import DoubleLineEdit

"""新增模型"""
class InsertModel(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("模型配置")
        # 窗口大小
        self.resize(500, 350)

        # 主体窗口
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        # 第一行信息
        layout_row1 = QHBoxLayout()
        layout_row1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # 第一行第一列
        layout_row1_col1 = QVBoxLayout()
        layout_row1_col1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # 模型名称
        name_title = QLabel("模型名称")
        name_title.setStyleSheet(title_style_sheet())
        name_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row1_col1.addWidget(name_title)
        # 模型名称输入框
        name_edit = QLineEdit()
        name_edit.setFixedSize(220, 40)
        name_edit.setStyleSheet(line_edit_style_sheet())
        name_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row1_col1.addWidget(name_edit)
        layout_row1.addLayout(layout_row1_col1)

        # 第一行第二列
        layout_row1_col2 = QVBoxLayout()
        layout_row1_col2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # 模型类型
        type_title = QLabel("模型类型")
        type_title.setStyleSheet(title_style_sheet())
        type_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row1_col2.addWidget(type_title)
        # 模型类型下拉框
        type_combo = QComboBox()
        type_combo.addItem("Custom(网络模型)", 1)
        type_combo.addItem("Local(本地Ollama)", 2)
        type_combo.addItem("Local(本地oMLX)", 3)
        type_combo.setFixedSize(220, 40)
        type_combo.setStyleSheet(line_edit_style_sheet())
        type_combo.setCurrentIndex(0)
        type_combo.currentTextChanged.connect(lambda : self.update_ui_visibility(type_combo.currentText()))
        layout_row1_col2.addWidget(type_combo)
        layout_row1.addLayout(layout_row1_col2)
        main_layout.addLayout(layout_row1)

        # 第二行
        self.layout_row2 = QLabel("API Key")
        self.layout_row2.setStyleSheet(title_style_sheet())
        self.layout_row2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.layout_row2)

        # 第三行
        self.layout_row3 = QLineEdit()
        self.layout_row3.setFixedSize(460, 40)
        self.layout_row3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout_row3.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(self.layout_row3)

        # 第四行
        layout_row4 = QLabel("Base URL")
        layout_row4.setStyleSheet(title_style_sheet())
        layout_row4.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(layout_row4)

        # 第五行
        self.layout_row5 = QLineEdit()
        self.layout_row5.setFixedSize(460, 40)
        self.layout_row5.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout_row5.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(self.layout_row5)

        # 第六行
        layout_row6 = QLabel("模型ID（示例：Qwen3.6-35B...）")
        layout_row6.setStyleSheet(title_style_sheet())
        layout_row6.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(layout_row6)

        # 第七行
        layout_row7 = QLineEdit()
        layout_row7.setFixedSize(460, 40)
        layout_row7.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row7.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(layout_row7)

        # 第八行
        layout_row8 = QFrame()
        layout_row8.setFrameShape(QFrame.Shape.HLine)
        layout_row8.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(layout_row8)

        # 第九行
        layout_row9 = QHBoxLayout()
        layout_row9.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # 第九行第1列
        layout_row9_col1 = QVBoxLayout()
        layout_row9_col1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # 温度标题
        temperature_title = QLabel("温度（Temperature）")
        temperature_title.setStyleSheet(title_style_sheet())
        temperature_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row9_col1.addWidget(temperature_title)
        # 温度输入
        temperature_edit = DoubleLineEdit(0.1, 2.0, 1)
        temperature_edit.setFixedSize(220, 40)
        temperature_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        temperature_edit.setStyleSheet(line_edit_style_sheet())
        layout_row9_col1.addWidget(temperature_edit)
        layout_row9.addLayout(layout_row9_col1)

        # 第九行第2列
        layout_row9_col2 = QVBoxLayout()
        layout_row9_col2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # Top-P
        top_p_title = QLabel("选择范围(Top-P)")
        top_p_title.setStyleSheet(title_style_sheet())
        top_p_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row9_col2.addWidget(top_p_title)
        # Top-P输入
        top_p_edit = DoubleLineEdit(0.10, 1.00, 2)
        top_p_edit.setFixedSize(220, 40)
        top_p_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        top_p_edit.setStyleSheet(line_edit_style_sheet())
        layout_row9_col2.addWidget(top_p_edit)
        layout_row9.addLayout(layout_row9_col2)
        main_layout.addLayout(layout_row9)

        # 第10行
        layout_row10 = QHBoxLayout()
        layout_row10.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # 第10行第1列
        layout_row10_col1 = QVBoxLayout()
        layout_row10_col1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # token
        token_title = QLabel("Max Tokens")
        token_title.setStyleSheet(title_style_sheet())
        token_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row10_col1.addWidget(token_title)
        # token输入
        token_edit = DoubleLineEdit(8000, 256000, 0)
        token_edit.setFixedSize(220, 40)
        token_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        token_edit.setStyleSheet(line_edit_style_sheet())
        layout_row10_col1.addWidget(token_edit)
        layout_row10.addLayout(layout_row10_col1)

        # 第10行第2列
        layout_row10_col2 = QVBoxLayout()
        layout_row10_col2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # timeOut
        time_out_title = QLabel("Timeout（s）")
        time_out_title.setStyleSheet(title_style_sheet())
        time_out_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row10_col2.addWidget(time_out_title)
        # timeOut输入
        time_out_edit = DoubleLineEdit(300, 3600, 0)
        time_out_edit.setFixedSize(220, 40)
        time_out_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        time_out_edit.setStyleSheet(line_edit_style_sheet())
        layout_row10_col2.addWidget(time_out_edit)
        layout_row10.addLayout(layout_row10_col2)
        main_layout.addLayout(layout_row10)

        # 第十一行分割线
        layout_row11 = QFrame()
        layout_row11.setFrameShape(QFrame.Shape.HLine)
        layout_row11.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(layout_row11)

        # 第十二行
        layout_row12 = QHBoxLayout()
        layout_row12.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # 测试链接按钮
        test_connection_btn = QPushButton("⚡️测试连接")
        test_connection_btn.setFixedSize(120, 30)
        test_connection_btn.setStyleSheet(button_style_sheet())
        test_connection_btn.clicked.connect(lambda : self.test_connection())
        layout_row12.addWidget(test_connection_btn)
        # 弹向右侧
        layout_row12.addStretch()
        # 取消按钮
        close_btn = QPushButton("取消")
        close_btn.setFixedSize(80, 30)
        close_btn.setStyleSheet(button_style_sheet())
        close_btn.clicked.connect(lambda : self.close())
        layout_row12.addWidget(close_btn)
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setFixedSize(120, 30)
        confirm_btn.setStyleSheet(button_style_sheet())
        confirm_btn.clicked.connect(lambda : self.confirm_model())
        layout_row12.addWidget(confirm_btn)

        main_layout.addLayout(layout_row12)
        self.accept()

    """测试模型连接"""
    def test_connection(self):
        123

    "确认模型配置"
    def confirm_model(self):
        123

    """根据选择的提供商动态显示或隐藏控件"""
    def update_ui_visibility(self, text:str):
        # 判断是否选择了 Ollama (忽略大小写)
        is_ollama = "ollama" in text.lower()

        # 2. 设置可见性
        # 如果是 Ollama，则隐藏（False），否则显示（True）
        self.layout_row2.setVisible(not is_ollama)
        self.layout_row3.setVisible(not is_ollama)

        # 可选：如果是 Ollama，自动填入默认地址
        if is_ollama:
            self.layout_row5.setText("http://localhost:11434/v1")

        is_o_mlx = "oMLX" in text.lower()
        if is_o_mlx:
            self.layout_row5.setText("http://localhost:8080/v1")
