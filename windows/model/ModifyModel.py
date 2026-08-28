import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QFrame, \
    QPushButton, QMessageBox
from openai import OpenAI

from resources.style.StyleSheet import title_style_sheet, line_edit_style_sheet, button_style_sheet
from sqlite.ModelDB import modify_model_conf
from utils.DoubleLineEdit import DoubleLineEdit


class ModifyModel(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle("模型配置")

        # 主体窗口
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        self.id = model.conf_page_id

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
        self.name_edit = QLineEdit()
        self.name_edit.setText(model.conf_page_right_model_name.text())
        self.name_edit.setFixedSize(220, 40)
        self.name_edit.setStyleSheet(line_edit_style_sheet())
        self.name_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_row1_col1.addWidget(self.name_edit)
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
        self.type_combo = QComboBox()
        self.type_combo.addItem("Custom(网络模型)", 1)
        self.type_combo.addItem("Local(本地Ollama)", 2)
        self.type_combo.addItem("Local(本地oMLX)", 3)
        self.type_combo.setFixedSize(220, 40)
        self.type_combo.setStyleSheet(line_edit_style_sheet())
        self.type_combo.setCurrentIndex(0)
        self.type_combo.currentTextChanged.connect(lambda : self.update_ui_visibility(self.type_combo.currentText()))
        layout_row1_col2.addWidget(self.type_combo)
        layout_row1.addLayout(layout_row1_col2)
        main_layout.addLayout(layout_row1)

        # 第二行
        self.layout_row2 = QLabel("API Key")
        self.layout_row2.setStyleSheet(title_style_sheet())
        self.layout_row2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.layout_row2)

        # 第三行
        self.api_key = QLineEdit()
        self.api_key.setText(model.conf_page_api_key)
        self.api_key.setFixedSize(460, 40)
        self.api_key.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.api_key.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(self.api_key)

        # 第四行
        layout_row4 = QLabel("Base URL")
        layout_row4.setStyleSheet(title_style_sheet())
        layout_row4.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(layout_row4)

        # 第五行
        self.base_url = QLineEdit()
        self.base_url.setText(model.conf_page_base_url.text())
        self.base_url.setFixedSize(460, 40)
        self.base_url.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.base_url.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(self.base_url)

        # 第六行
        layout_row6 = QLabel("模型ID（示例：Qwen3.6-35B...）")
        layout_row6.setStyleSheet(title_style_sheet())
        layout_row6.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(layout_row6)

        # 第七行
        self.model_id = QLineEdit()
        self.model_id.setText(model.conf_page_model_id.text())
        self.model_id.setFixedSize(460, 40)
        self.model_id.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.model_id.setStyleSheet(line_edit_style_sheet())
        main_layout.addWidget(self.model_id)

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
        self.temperature_edit = DoubleLineEdit(0.1, 2.0, 1)
        self.temperature_edit.setText(model.conf_page_temperature.text())
        self.temperature_edit.setFixedSize(220, 40)
        self.temperature_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.temperature_edit.setStyleSheet(line_edit_style_sheet())
        layout_row9_col1.addWidget(self.temperature_edit)
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
        self.top_p_edit = DoubleLineEdit(0.10, 1.00, 2)
        self.top_p_edit.setFixedSize(220, 40)
        self.top_p_edit.setText(model.conf_page_top_p.text())
        self.top_p_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.top_p_edit.setStyleSheet(line_edit_style_sheet())
        layout_row9_col2.addWidget(self.top_p_edit)
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
        self.token_edit = DoubleLineEdit(8000, 256000, 0)
        self.token_edit.setFixedSize(220, 40)
        self.token_edit.setText(model.conf_page_max_token.text())
        self.token_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.token_edit.setStyleSheet(line_edit_style_sheet())
        layout_row10_col1.addWidget(self.token_edit)
        layout_row10.addLayout(layout_row10_col1)

        # 第10行第2列
        # layout_row10_col2 = QVBoxLayout()
        # layout_row10_col2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # # timeOut
        # time_out_title = QLabel("Timeout（s）")
        # time_out_title.setStyleSheet(title_style_sheet())
        # time_out_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # layout_row10_col2.addWidget(time_out_title)
        # # timeOut输入
        # self.time_out_edit = DoubleLineEdit(300, 3600, 0)
        # self.time_out_edit.setFixedSize(220, 40)
        # self.time_out_edit.setText(model.conf_page_time_out.text())
        # self.time_out_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.time_out_edit.setStyleSheet(line_edit_style_sheet())
        # layout_row10_col2.addWidget(self.time_out_edit)
        # layout_row10.addLayout(layout_row10_col2)
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

    """测试模型连接"""
    def test_connection(self):
        try:
            start_time = time.time()
            if len(self.base_url.text()) < 1:
                QMessageBox.warning(self, "错误", f"❌ Base URL连接地址为空")
                return False

            # 是否 ollama
            is_ollama = "ollama" in self.type_combo.currentText().lower()
            if is_ollama:
                self.api_key.setText("Ollama")
            if not is_ollama and len(self.api_key.text()) < 1:
                QMessageBox.warning(self, "错误", f"❌ API Key密匙为空")
                return False

            client = OpenAI(
                base_url = self.base_url.text(),
                api_key= self.api_key.text()
            )

            # 发送一个极短的请求来测试连通性
            client.models.list()

            end_time = time.time()
            elapsed = (end_time - start_time) * 1000
            QMessageBox.warning(self, "错误", f"✅ 连接成功！耗时:{elapsed:.2f}ms")
            return True
        except Exception as e:
            print(e)
            QMessageBox.warning(self, "错误", f"❌ 连接失败")
            return False

    "确认模型配置"
    def confirm_model(self):
        # 模型名称
        name = self.name_edit.text()
        if len(name) < 1:
            QMessageBox.warning(self, "错误", f"❌ 模型名称为空")
            return

        # 配置类型
        model_type = self.type_combo.currentData()
        if model_type is None:
            QMessageBox.warning(self, "错误", f"❌ 模型类型为空")
            return

        # baseUrl
        url = self.base_url.text()
        if url is None:
            QMessageBox.warning(self, "错误", f"❌ BaseURL地址为空")
            return

        # api_key
        api_key = self.api_key.text()
        if api_key is None:
            QMessageBox.warning(self, "错误", f"❌ API Key密匙为空")
            return

        # model_id
        model_id = self.model_id.text()
        if model_id is None:
            QMessageBox.warning(self, "错误", f"❌ 模型ID为空")
            return

        # 保存配置信息
        req_json = {
            "id": self.id,
            "name": name,
            "type": model_type,
            "url": url,
            "api_key": api_key,
            "model_id": model_id,
            "temperature": self.temperature_edit.text(),
            "top_p": self.top_p_edit.text(),
            "max_token": self.token_edit.text()
        }
        modify_model_conf(req_json)
        self.accept()

    """根据选择的提供商动态显示或隐藏控件"""
    def update_ui_visibility(self, text:str):
        # 判断是否选择了 Ollama (忽略大小写)
        is_ollama = "ollama" in text.lower()
        is_o_mlx = "oMLX" in text.lower()

        # 2. 设置可见性
        # 如果是 Ollama，则隐藏（False），否则显示（True）
        self.layout_row2.setVisible(not is_ollama)
        self.api_key.setVisible(not is_ollama)

        # 窗口大小
        if is_ollama:
            self.setFixedSize(500, 500)
        else:
            self.setFixedSize(500, 560)

        # 可选：如果是 Ollama，自动填入默认地址
        if is_ollama:
            self.base_url.setText("http://localhost:11434/v1")

        if is_o_mlx:
            self.base_url.setText("http://localhost:8080/v1")
