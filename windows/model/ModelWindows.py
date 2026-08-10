from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, QDialog, \
    QListWidgetItem

from sqlite.Sqlite3Utils import query_all_model
from style.StyleSheet import button_style_sheet, title_style_sheet
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
    self.model_list = QListWidget()
    self.model_list.setContentsMargins(10, 10, 10, 10)
    # 设置大小
    self.model_list.setFixedWidth(200)
    self.model_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.model_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # 渲染列表
    review_model_list(self.model_list)
    self.model_lower_layout.addWidget(self.model_list)

    # 垂直分割线
    vqf = QFrame()
    vqf.setFrameShape(QFrame.Shape.VLine)
    vqf.setFrameShadow(QFrame.Shadow.Sunken)
    self.model_lower_layout.addWidget(vqf)

    # 配置


    # 尾部插入
    self.model_win_layout.addLayout(self.model_lower_layout)

"""更新模型列表"""
def review_model_list(model_list):
    # 清空item
    model_list.clear()

    # 模型配置查询
    all_model = query_all_model()
    # 模型配置非空
    if all_model is not None:
        for index, model in enumerate(all_model):
            # 创建item占位
            model_item = QListWidgetItem()
            # 设置高度（宽度由列表控制）
            model_item.setSizeHint(QSize(200, 80))  # 高度比卡片稍高
            model_list.addItem(model_item)

            # ===== 关键：创建一个居中容器 =====
            container = QWidget()
            container.setFixedWidth(200)  # 与列表宽度一致

            # 容器内部使用水平布局，让卡片居中
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 10, 0, 10)  # 上下各10px边距
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 创建卡片
            model_frame = QFrame()
            model_frame.setFixedSize(180, 100)
            model_frame.setStyleSheet("""
                QFrame {
                    background-color: #2D3436;
                    border-radius: 12px;
                    border: 1px solid #3D4447;
                }
                QFrame:hover {
                    border: 1px solid #4A90D9;
                    background-color: #353D3F;
                }
            """)

            # 卡片内部布局
            frame_layout = QVBoxLayout(model_frame)
            frame_layout.setContentsMargins(10, 5, 10, 5)
            frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            # 模型名称
            label = QLabel(model['name'])
            label.setStyleSheet("color: white;border: none; padding: 0; margin: 0; background: transparent;")
            frame_layout.addWidget(label)

            # 模型类型
            model_type = "Custom"
            if "2" == model['type']:
                model_type = "Ollama"
            if "3" == model['type']:
                model_type = "oMLX"
            type_label = QLabel(model_type)
            type_label.setStyleSheet("color: white;border: none; padding: 0; margin: 0; background: transparent;")
            frame_layout.addWidget(type_label)


            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 将容器设置为列表项
            model_list.setItemWidget(model_item, container)



"""新增模型"""
def insert_model(self):
    dialog = InsertModel.InsertModel(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 对话框成功保存并关闭同时刷新页面
        review_model_list(self.model_list)

"""模型配置"""
