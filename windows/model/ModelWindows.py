from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, QDialog

from sqlite.Sqlite3Utils import query_all_model
from style.StyleSheet import button_style_sheet
from . import InsertModel

"""模型窗口"""
def model_open_windows(self):
    # 中心部件
    central_widget = QWidget()

    # 垂直布局
    self.model_win_layout = QVBoxLayout(central_widget)
    self.model_win_layout.setContentsMargins(20, 20, 20, 20)
    self.model_win_layout.setSpacing(5)

    # 页面渲染
    review_page(self)

    return central_widget

"""页面渲染"""
def review_page(self):
    # 顶部标题栏
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 文案
    title_label = QLabel("模型配置")
    title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
    header_layout.addWidget(title_label)

    # 弹到另一端
    header_layout.addStretch()

    # 新模型按钮
    insert_model_btn = QPushButton("+ 新增模型配置")
    # 按钮大小
    insert_model_btn.setFixedSize(120, 40)
    # 按钮样式
    insert_model_btn.setStyleSheet(button_style_sheet())
    # 按钮触发函数
    insert_model_btn.clicked.connect(lambda: insert_model(self))
    header_layout.addWidget(insert_model_btn)

    # 加入主架构
    self.model_win_layout.addLayout(header_layout)

    # 插入水平分割线
    hqf = QFrame()
    hqf.setFrameShape(QFrame.Shape.HLine)
    hqf.setFrameShadow(QFrame.Shadow.Sunken)
    self.model_win_layout.addWidget(hqf)

    # 下部分内容
    self.model_lower_layout = QHBoxLayout()
    self.model_lower_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    # 左侧列表创建
    model_list = QListWidget()
    # 设置大小
    model_list.setFixedWidth(200)
    # 模型配置查询
    all_model = query_all_model()
    # 模型配置非空
    if all_model is not None:
        for model in enumerate(all_model):
            model_list.addItem(model['name'])
    self.model_lower_layout.addWidget(model_list)

    # 垂直分割线
    vqf = QFrame()
    vqf.setFrameShape(QFrame.Shape.VLine)
    vqf.setFrameShadow(QFrame.Shadow.Sunken)
    self.model_lower_layout.addWidget(vqf)

    # 配置


    # 尾部插入
    self.model_win_layout.addLayout(self.model_lower_layout)




"""新增模型"""
def insert_model(self):
    dialog = InsertModel.InsertModel(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 对话框成功保存并关闭同时刷新页面
        print(123)

"""模型配置"""
