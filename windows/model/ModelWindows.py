import time

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, QDialog, \
    QListWidgetItem, QMessageBox
from openai import OpenAI

from resources.style.StyleSheet import button_style_sheet, title_style_sheet
from sqlite.ModelDB import remove_model_conf, query_all_model, query_model_by_id
from windows.model import InsertModel
from windows.model import ModifyModel

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
    self.all_models = review_model_list(self.model_list)
    self.model_list.itemClicked.connect(lambda item: on_item_clicked(self, item))
    # 按钮触发函数
    insert_model_btn.clicked.connect(lambda: insert_model(self))
    # 配置不为空
    if self.model_list.count() > 0:
        self.model_list.setCurrentRow(0)
    self.model_lower_layout.addWidget(self.model_list)

    # 垂直分割线
    vqf = QFrame()
    vqf.setFrameShape(QFrame.Shape.VLine)
    vqf.setFrameShadow(QFrame.Shadow.Sunken)
    self.model_lower_layout.addWidget(vqf)

    # 配置页面
    self.conf_page = QVBoxLayout()
    self.conf_page.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

    # 菜单栏
    conf_page_row1 = QHBoxLayout()
    conf_page_row1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 第一列
    self.conf_page_right_model_name = QLabel("-")
    self.conf_page_right_model_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.conf_page_right_model_name.setStyleSheet(title_style_sheet())
    conf_page_row1.addWidget(self.conf_page_right_model_name)
    # 弹开
    conf_page_row1.addStretch()
    # 按钮
    conf_page_row1_col2 = QPushButton("⚡️测试连接")
    conf_page_row1_col2.setStyleSheet(button_style_sheet())
    conf_page_row1_col2.setFixedSize(100, 30)
    conf_page_row1_col2.clicked.connect(lambda : test_connection(self))
    conf_page_row1.addWidget(conf_page_row1_col2)
    # 编辑
    conf_page_row1_col3 = QPushButton("🖊️编辑")
    conf_page_row1_col3.setStyleSheet(button_style_sheet())
    conf_page_row1_col3.setFixedSize(80, 30)
    conf_page_row1_col3.clicked.connect(lambda : modify_model_conf(self))
    conf_page_row1.addWidget(conf_page_row1_col3)
    # 删除
    conf_page_row1_col4 = QPushButton("🗑️删除")
    conf_page_row1_col4.setStyleSheet(button_style_sheet())
    conf_page_row1_col4.setFixedSize(80, 30)
    conf_page_row1_col4.clicked.connect(lambda : delete_model_conf(self))
    conf_page_row1.addWidget(conf_page_row1_col4)
    self.conf_page.addLayout(conf_page_row1)

    # 插入分割线
    conf_page_fream1 = QFrame()
    conf_page_fream1.setFrameShape(QFrame.Shape.HLine)
    conf_page_fream1.setFrameShadow(QFrame.Shadow.Sunken)
    self.conf_page.addWidget(conf_page_fream1)

    # title
    conf_page_model_type_title = QLabel("模型类型")
    conf_page_model_type_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    conf_page_model_type_title.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(conf_page_model_type_title)
    # 类型
    self.conf_page_model_type = QLabel("-")
    self.conf_page_model_type.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.conf_page_model_type.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(self.conf_page_model_type)

    # 模型ID title
    conf_page_model_id_title = QLabel("模型 ID")
    conf_page_model_id_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    conf_page_model_id_title.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(conf_page_model_id_title)
    # 模型ID
    self.conf_page_model_id = QLabel("-")
    self.conf_page_model_id.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.conf_page_model_id.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(self.conf_page_model_id)

    # API端点
    conf_page_base_url_title = QLabel("API端点")
    conf_page_base_url_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    conf_page_base_url_title.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(conf_page_base_url_title)
    # 端点
    self.conf_page_base_url = QLabel("-")
    self.conf_page_base_url.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.conf_page_base_url.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(self.conf_page_base_url)

    # 插入分割线
    conf_page_fream2 = QFrame()
    conf_page_fream2.setFrameShape(QFrame.Shape.HLine)
    conf_page_fream2.setFrameShadow(QFrame.Shadow.Sunken)
    self.conf_page.addWidget(conf_page_fream2)

    # 温度
    conf_page_temperature_title = QLabel("温度（Temperature）")
    conf_page_temperature_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    conf_page_temperature_title.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(conf_page_temperature_title)
    # 温度类型
    self.conf_page_temperature = QLabel("-")
    self.conf_page_temperature.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.conf_page_temperature.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(self.conf_page_temperature)

    # Top-P
    conf_page_top_p_title = QLabel("Top-P")
    conf_page_top_p_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    conf_page_top_p_title.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(conf_page_top_p_title)
    # top-p
    self.conf_page_top_p = QLabel("-")
    self.conf_page_top_p.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.conf_page_top_p.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(self.conf_page_top_p)

    # Max Token
    conf_page_max_token_title = QLabel("Max Tokens")
    conf_page_max_token_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    conf_page_max_token_title.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(conf_page_max_token_title)
    # max
    self.conf_page_max_token = QLabel("-")
    self.conf_page_max_token.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.conf_page_max_token.setStyleSheet(title_style_sheet())
    self.conf_page.addWidget(self.conf_page_max_token)

    # # timeOut
    # conf_page_time_out_title = QLabel("TimeOut(单位秒：s)")
    # conf_page_time_out_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # conf_page_time_out_title.setStyleSheet(title_style_sheet())
    # self.conf_page.addWidget(conf_page_time_out_title)
    # # time
    # self.conf_page_time_out = QLabel("-")
    # self.conf_page_time_out.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # self.conf_page_time_out.setStyleSheet(title_style_sheet())
    # self.conf_page.addWidget(self.conf_page_time_out)

    # 数据填充
    if len(self.all_models) > 0:
        model_conf_info(self, self.all_models[0])

    # 尾部插入配置页面
    self.model_lower_layout.addLayout(self.conf_page)
    # 尾部插入
    self.model_win_layout.addLayout(self.model_lower_layout)

"""触发事件"""
def on_item_clicked(self, item: QListWidgetItem):
    model = item.data(Qt.ItemDataRole.UserRole)
    model_conf_info(self, model)

"""删除模型"""
def delete_model_conf(self):
    remove_model_conf(self.conf_page_id)
    review_model_list(self.model_list)
    # 配置不为空
    if self.model_list.count() > 0:
        self.model_list.setCurrentRow(0)
    # 数据填充
    if len(self.all_models) > 0:
        model_conf_info(self, self.all_models[0])


"""编辑模型"""
def modify_model_conf(self):
    dialog = ModifyModel.ModifyModel(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 对话框成功保存并关闭同时刷新页面
        review_model_list(self.model_list)
        # 获取最新模型信息
        model_conf_info(self, query_model_by_id(self.conf_page_id))


"""模型详情"""
def model_conf_info(self, model_conf):
    if model_conf:
        self.conf_page_right_model_name.setText(model_conf['name'])
        self.conf_page_model_type_int = model_conf['type']
        if model_conf['type'] == 1:
            self.conf_page_model_type.setText("Custom")
        if model_conf['type'] == 2:
            self.conf_page_model_type.setText("Ollama")
        if model_conf['type'] == 3:
            self.conf_page_model_type.setText("oMLX")
        self.conf_page_model_id.setText(model_conf['model_id'])
        self.conf_page_base_url.setText(model_conf['url'])
        self.conf_page_temperature.setText(str(model_conf['temperature']))
        self.conf_page_top_p.setText(str(model_conf['top_p']))
        self.conf_page_max_token.setText(str(model_conf['max_token']))
        # self.conf_page_time_out.setText(str(model_conf['time_out']))
        self.conf_page_api_key = model_conf['api_key']
        self.conf_page_id = model_conf['id']


"""测试模型连接"""
def test_connection(self):
    try:
        start_time = time.time()
        if len(self.conf_page_base_url.text()) < 1 or self.conf_page_base_url.text() == "-":
            QMessageBox.warning(self, "错误", f"❌ Base URL连接地址为空")
            return False

        # 是否 ollama
        is_ollama = "ollama" in self.conf_page_api_key.lower()
        if not is_ollama and len(self.conf_page_api_key) < 1:
            QMessageBox.warning(self, "错误", f"❌ API Key密匙为空")
            return False

        client = OpenAI(
            base_url = self.conf_page_base_url.text(),
            api_key= self.conf_page_api_key
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
            model_item.setData(Qt.ItemDataRole.UserRole, model)
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
            if 2 == model['type']:
                model_type = "Ollama"
            if 3 == model['type']:
                model_type = "oMLX"
            type_label = QLabel(model_type)
            type_label.setStyleSheet("color: white;border: none; padding: 0; margin: 0; background: transparent;")
            frame_layout.addWidget(type_label)


            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 将容器设置为列表项
            model_list.setItemWidget(model_item, container)

    return all_model



"""新增模型"""
def insert_model(self):
    dialog = InsertModel.InsertModel(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 对话框成功保存并关闭同时刷新页面
        review_model_list(self.model_list)

"""模型配置"""
