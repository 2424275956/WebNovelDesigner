from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QListWidget, \
    QListWidgetItem, QDialog, QPlainTextEdit, QScrollArea, QLineEdit, QStatusBar

from sqlite.Sqlite3Utils import query_all_prompt, query_all_scene_prompt, save_prompt_info
from style.StyleSheet import button_style_sheet, title_style_sheet, line_edit_style_sheet
from windows.prompt.InsertPrompt import InsertModel


"""触发事件"""
def on_item_clicked(self, item: QListWidgetItem):
    model = item.data(Qt.ItemDataRole.UserRole)
    # 设置配置ID
    self.prompt_id = model['id']
    prompt_page_info(self, model)

"""页面信息"""
def prompt_page_info(self, model):
    123

"""保存模版"""
def save_prompt_conf(self):
    # 系统提示词
    if self.system_prompt is None:
        self.prompt_status_bar.showMessage("❌ 未获取到系统提示词模版")
        return False
    else:
        if len(self.system_prompt.toPlainText()) <= 0:
            self.prompt_status_bar.showMessage("❌ 系统提示词规则为空")
            return False
    # 用户提示词
    if self.user_prompt.toPlainText() is None:
        self.prompt_status_bar.showMessage("❌ 未获取到用户提示词模版")
        return False
    else:
        if len(self.user_prompt.toPlainText()) <= 0:
            self.prompt_status_bar.showMessage("❌ 用户提示词规则为空")
            return False
    # 模版ID
    if self.prompt_id is None:
        self.prompt_status_bar.showMessage("❌ 未选择提示词模版")
        return False
    # 场景规则 循环获取
    scene = []
    for index in range(self.scene_prompt_list.count()):
        # 获取到item并循环处理
        item = self.scene_prompt_list.item(index)

        # item不可以为空
        if item:
            # 通过 QListWidget 的 itemWidget() 方法，取出绑定到该 item 上的真实 QWidget
            custom_widget = self.scene_prompt_list.itemWidget(item)

            # 容器不为空
            if custom_widget:
                # 场景名称
                scene_name = custom_widget.findChild(QLineEdit, "scene_name")
                if scene_name is None:
                    self.prompt_status_bar.showMessage(f"❌ 第{index + 1}行场景规则，场景名称对象获取失败")
                    return False
                else:
                    if len(scene_name.text()) <= 0:
                        self.prompt_status_bar.showMessage("❌ 第{index + 1}行场景规则，场景名称为空")
                        return False
                # 识别点
                identify_text = custom_widget.findChild(QPlainTextEdit, "identify_text")
                if identify_text is None:
                    self.prompt_status_bar.showMessage(f"❌ 第{index + 1}行场景规则，场景识别规则对象获取失败")
                    return False
                else:
                    if len(identify_text.toPlainText()) <= 0:
                        self.prompt_status_bar.showMessage("❌ 第{index + 1}行场景规则，场景识别规则为空")
                        return False

                # 改写规则
                rules_text = custom_widget.findChild(QPlainTextEdit, "rules_text")
                if rules_text is None:
                    self.prompt_status_bar.showMessage(f"❌ 第{index + 1}行场景规则，场景改写规则对象获取失败")
                    return False
                else:
                    if len(rules_text.toPlainText()) <= 0:
                        self.prompt_status_bar.showMessage("❌ 第{index + 1}行场景规则，场景改写规则为空")
                        return False
                # json组装
                scene.append({
                    "name": scene_name.text(),
                    "identify_text": identify_text.toPlainText(),
                    "rules_text": rules_text.toPlainText()
                })

    # 请求组装
    req_json = {
        "id": self.prompt_id,
        "system": self.system_prompt.toPlainText(),
        "user": self.user_prompt.toPlainText(),
        "scene":scene
    }
    # 新增
    save_prompt_info(req_json)
    return True


"""提示词窗口"""
def prompt_open_windows(self):
    # 中心部件
    central_widget = QWidget()

    # 垂直布局
    self.model_win_layout = QVBoxLayout(central_widget)
    self.model_win_layout.setContentsMargins(20, 20, 20, 20)
    self.model_win_layout.setSpacing(5)
    # 默认值定义
    self.prompt_id = None

    # 页面渲染
    review_page(self)

    return central_widget

def show_insert_dialog(self):
    dialog = InsertModel(self)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        review_prompt_list(self.model_list)

"""页面渲染"""
def review_page(self):
    # 顶部标题栏
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 文案
    title_label = QLabel("提示词配置")
    title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
    header_layout.addWidget(title_label)

    header_layout.addStretch()

    # 状态栏标题
    status_bar_title = QLabel("状态提示：")
    status_bar_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
    status_bar_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
    header_layout.addWidget(status_bar_title)
    # 状态栏
    self.prompt_status_bar = QStatusBar()
    header_layout.addWidget(self.prompt_status_bar)

    # 弹到另一端
    header_layout.addStretch()

    # 新模型按钮
    insert_model_btn = QPushButton("+ 新建模版")
    # 按钮大小
    insert_model_btn.setFixedSize(120, 40)
    # 按钮样式
    insert_model_btn.setStyleSheet(button_style_sheet())
    # 按钮触发函数
    insert_model_btn.clicked.connect(lambda: show_insert_dialog(self))
    header_layout.addWidget(insert_model_btn)

    # 新增导入按钮
    import_model_btn = QPushButton("⏫导入模版")
    # 按钮大小
    import_model_btn.setFixedSize(120, 40)
    # 按钮样式
    import_model_btn.setStyleSheet(button_style_sheet())
    # 按钮触发函数
    import_model_btn.clicked.connect(lambda: 123)
    header_layout.addWidget(import_model_btn)

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
    self.all_models = review_prompt_list(self.model_list)
    self.model_list.itemClicked.connect(lambda item: on_item_clicked(self, item))
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
    self.conf_page_model_name = QLabel("-")
    self.conf_page_model_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
    self.conf_page_model_name.setStyleSheet(title_style_sheet())
    conf_page_row1.addWidget(self.conf_page_model_name)
    # 弹开
    conf_page_row1.addStretch()
    # 导出模版
    conf_page_row1_col2 = QPushButton("⏬导出模版")
    conf_page_row1_col2.setStyleSheet(button_style_sheet())
    conf_page_row1_col2.setFixedSize(100, 30)
    conf_page_row1_col2.clicked.connect(lambda : 123)
    conf_page_row1.addWidget(conf_page_row1_col2)
    # 编辑
    conf_page_row1_col3 = QPushButton("🖊保存")
    conf_page_row1_col3.setStyleSheet(button_style_sheet())
    conf_page_row1_col3.setFixedSize(80, 30)
    conf_page_row1_col3.clicked.connect(lambda : save_prompt_conf(self))
    conf_page_row1.addWidget(conf_page_row1_col3)
    # 删除
    conf_page_row1_col4 = QPushButton("🗑️删除")
    conf_page_row1_col4.setStyleSheet(button_style_sheet())
    conf_page_row1_col4.setFixedSize(80, 30)
    conf_page_row1_col4.clicked.connect(lambda : 123)
    conf_page_row1.addWidget(conf_page_row1_col4)
    self.conf_page.addLayout(conf_page_row1)

    # 插入分割线
    conf_page_fream1 = QFrame()
    conf_page_fream1.setFrameShape(QFrame.Shape.HLine)
    conf_page_fream1.setFrameShadow(QFrame.Shadow.Sunken)
    self.conf_page.addWidget(conf_page_fream1)

    # 创建滚动区域
    scroll_area = QScrollArea(self)
    # 【关键】允许内容自适应宽度
    scroll_area.setWidgetResizable(True)
    # 隐藏水平滚动条
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    # 创建内容容器
    prompt_widget = QWidget()
    scroll_area.setWidget(prompt_widget)

    # 创建水平内部布局
    prompt_inner_layout = QVBoxLayout(prompt_widget)
    prompt_inner_layout.setSpacing(10)

    # 系统提示词
    system_prompt_title = QLabel("系统提示词（最好1000字以内，过长会导致遗忘设定）")
    system_prompt_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    system_prompt_title.setStyleSheet(title_style_sheet())
    prompt_inner_layout.addWidget(system_prompt_title)
    # 系统提示词框
    self.system_prompt = QPlainTextEdit()
    self.system_prompt.setStyleSheet(line_edit_style_sheet())
    self.system_prompt.setFixedHeight(200)
    prompt_inner_layout.addWidget(self.system_prompt)

    # 分割线
    fream_row1 = QFrame()
    fream_row1.setFrameShape(QFrame.Shape.HLine)
    fream_row1.setFrameShadow(QFrame.Shadow.Sunken)
    prompt_inner_layout.addWidget(fream_row1)

    # 用户提示词
    user_prompt_title = QLabel("用户提示词（主要为改写规则）")
    user_prompt_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    user_prompt_title.setStyleSheet(title_style_sheet())
    prompt_inner_layout.addWidget(user_prompt_title)
    # 用户提示词框

    self.user_prompt = QPlainTextEdit()
    self.user_prompt.setStyleSheet(line_edit_style_sheet())
    self.user_prompt.setFixedHeight(350)
    prompt_inner_layout.addWidget(self.user_prompt)

    # 分割线
    fream_row2 = QFrame()
    fream_row2.setFrameShape(QFrame.Shape.HLine)
    fream_row2.setFrameShadow(QFrame.Shadow.Sunken)
    prompt_inner_layout.addWidget(fream_row2)


    # 场景提示词顶部
    scene_prompt_top = QHBoxLayout()
    scene_prompt_top.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 场景提示词内容
    scene_prompt_title = QLabel("场景提示词")
    scene_prompt_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    scene_prompt_title.setStyleSheet(title_style_sheet())
    scene_prompt_top.addWidget(scene_prompt_title)
    # 弹开
    scene_prompt_top.addStretch()
    # 增加场景规则
    insert_scene_prompt_btn = QPushButton("+ 新增场景规则")
    insert_scene_prompt_btn.setFixedSize(120, 30)
    insert_scene_prompt_btn.setStyleSheet(button_style_sheet())
    insert_scene_prompt_btn.clicked.connect(lambda : create_scene_prompt_text(self))
    scene_prompt_top.addWidget(insert_scene_prompt_btn)
    prompt_inner_layout.addLayout(scene_prompt_top)

    # 场景提示词列表
    self.scene_prompt_list = QListWidget()
    self.scene_prompt_list.setContentsMargins(10, 10, 10, 10)
    # 设置大小
    self.scene_prompt_list.setFixedHeight(500)
    self.scene_prompt_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.scene_prompt_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # 渲染列表
    review_scene_prompt_list(self.scene_prompt_list)
    prompt_inner_layout.addWidget(self.scene_prompt_list)

    self.conf_page.addWidget(scroll_area)

    # 尾部插入配置页面
    self.model_lower_layout.addLayout(self.conf_page)
    # 尾部插入
    self.model_win_layout.addLayout(self.model_lower_layout)

"""增加场景规则"""
def create_scene_prompt_text(self):
    # 新创卡片
    model_item = QListWidgetItem()
    # 设置高度（宽度由列表控制）
    model_item.setSizeHint(QSize(680, 200))
    self.scene_prompt_list.insertItem(0, model_item)

    # ===== 关键：创建一个居中容器 =====
    container = QWidget()
    container.setFixedSize(680, 200)

    # 容器内部使用水平布局，让卡片居中
    container_layout = QHBoxLayout(container)
    container_layout.setContentsMargins(10, 10, 10, 10)
    container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # 创建卡片
    model_frame = QFrame()
    model_frame.setFixedSize(670, 200)
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

    # 顶部
    top_layout = QHBoxLayout()
    top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 场景名称
    scene_name_title = QLabel("场景名称：")
    scene_name_title.setFixedSize(80, 30)
    scene_name_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    scene_name_title.setStyleSheet(title_style_sheet(color='white'))
    top_layout.addWidget(scene_name_title)
    # 场景名称修改
    scene_name = QLineEdit()
    scene_name.setObjectName("scene_name")
    scene_name.setFixedSize(300, 30)
    scene_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
    scene_name.setStyleSheet(line_edit_style_sheet(15))
    top_layout.addWidget(scene_name)
    # 弹开按钮
    top_layout.addStretch()
    # 按钮
    scene_delete = QPushButton("🗑️删除")
    scene_delete.setFixedSize(80, 30)
    scene_delete.setStyleSheet(button_style_sheet())
    scene_delete.clicked.connect(lambda : remove_scene_prompt(self.scene_prompt_list, model_item))
    top_layout.addWidget(scene_delete)
    frame_layout.addLayout(top_layout)

    # 底部框
    low_layout = QHBoxLayout()
    low_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 左侧布局
    low_col1 = QVBoxLayout()
    low_col1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 识别框标题
    identify_title = QLabel("场景识别匹配规则")
    identify_title.setFixedHeight(30)
    identify_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    identify_title.setStyleSheet(title_style_sheet(color='white'))
    low_col1.addWidget(identify_title)
    # 识别框
    identify_text = QPlainTextEdit()
    identify_text.setObjectName("identify_text")
    identify_text.setFixedSize(200, 100)
    identify_text.setStyleSheet(line_edit_style_sheet())
    low_col1.addWidget(identify_text)
    low_layout.addLayout(low_col1)

    # 弹开距离
    low_layout.addStretch()

    # 右侧布局
    low_col2 = QVBoxLayout()
    low_col2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    # 规则框标题
    rules_title = QLabel("场景改写规则")
    rules_title.setFixedHeight(30)
    rules_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    rules_title.setStyleSheet(title_style_sheet(color='white'))
    low_col2.addWidget(rules_title)
    # 规则框
    rules_text = QPlainTextEdit()
    rules_text.setObjectName("rules_text")
    rules_text.setFixedSize(440, 100)
    rules_text.setStyleSheet(line_edit_style_sheet())
    low_col2.addWidget(rules_text)
    low_layout.addLayout(low_col2)

    frame_layout.addLayout(low_layout)

    # 将卡片添加到容器（居中）
    container_layout.addWidget(model_frame)

    # 将容器设置为列表项
    self.scene_prompt_list.setItemWidget(model_item, container)

"""删除卡片"""
def remove_scene_prompt(scene_prompt_list, item):
    if item is None:
        return

    # 1. 获取该 item 在列表中的行号
    row = scene_prompt_list.row(item)

    # 2. 从列表中移除该 item（takeItem 会解除它与列表的绑定）
    taken_item = scene_prompt_list.takeItem(row)

    # 3. 【关键】手动删除 item 释放内存（takeItem 不会自动释放内存）
    if taken_item:
        del taken_item

"""场景规则渲染列表"""
def review_scene_prompt_list(model_list):
    # 场景规则查询
    all_scene_prompt = query_all_scene_prompt()
    # 内容不为空
    if all_scene_prompt:
        for prompt in all_scene_prompt:
            # 创建item占位
            model_item = QListWidgetItem()
            # 设置高度（宽度由列表控制）
            model_item.setSizeHint(QSize(680, 200))
            model_list.addItem(model_item)

            # ===== 关键：创建一个居中容器 =====
            container = QWidget()
            container.setFixedSize(680, 200)

            # 容器内部使用水平布局，让卡片居中
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(10, 10, 10, 10)  # 上下各10px边距
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # 创建卡片
            model_frame = QFrame()
            model_frame.setFixedSize(670, 200)
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

            # 顶部
            top_layout = QHBoxLayout()
            top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            # 场景名称
            scene_name_title = QLabel("场景名称：")
            scene_name_title.setFixedSize(80, 30)
            scene_name_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            scene_name_title.setStyleSheet(title_style_sheet(color='white'))
            top_layout.addWidget(scene_name_title)
            # 场景名称修改
            scene_name = QLineEdit()
            scene_name.setText(prompt['scene_name'])
            scene_name.setObjectName("scene_name")
            scene_name.setFixedSize(300, 30)
            scene_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
            scene_name.setStyleSheet(line_edit_style_sheet(15))
            top_layout.addWidget(scene_name)
            # 弹开按钮
            top_layout.addStretch()
            # 按钮
            scene_delete = QPushButton("🗑️删除")
            scene_delete.setFixedSize(80, 30)
            scene_delete.setStyleSheet(button_style_sheet())
            scene_delete.clicked.connect(lambda : remove_scene_prompt(model_list, model_item))
            top_layout.addWidget(scene_delete)
            frame_layout.addLayout(top_layout)

            # 底部框
            low_layout = QHBoxLayout()
            low_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            # 左侧布局
            low_col1 = QVBoxLayout()
            low_col1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            # 识别框标题
            identify_title = QLabel("场景识别匹配规则")
            identify_title.setFixedHeight(30)
            identify_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            identify_title.setStyleSheet(title_style_sheet(color='white'))
            low_col1.addWidget(identify_title)
            # 识别框
            identify_text = QPlainTextEdit()
            identify_text.setObjectName("identify_text")
            identify_text.setPlainText(prompt['scene_identify'])
            identify_text.setFixedSize(200, 100)
            identify_text.setStyleSheet(line_edit_style_sheet())
            low_col1.addWidget(identify_text)
            low_layout.addLayout(low_col1)

            # 弹开距离
            low_layout.addStretch()

            # 右侧布局
            low_col2 = QVBoxLayout()
            low_col2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            # 规则框标题
            rules_title = QLabel("场景改写规则")
            rules_title.setFixedHeight(30)
            rules_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            rules_title.setStyleSheet(title_style_sheet(color='white'))
            low_col2.addWidget(rules_title)
            # 规则框
            rules_text = QPlainTextEdit()
            rules_text.setObjectName("rules_text")
            rules_text.setPlainText(prompt['context'])
            rules_text.setFixedSize(440, 100)
            rules_text.setStyleSheet(line_edit_style_sheet())
            low_col2.addWidget(rules_text)
            low_layout.addLayout(low_col2)

            frame_layout.addLayout(low_layout)

            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 将容器设置为列表项
            model_list.setItemWidget(model_item, container)


"""更新模型列表"""
def review_prompt_list(model_list):
    # 清空item
    model_list.clear()

    # 模型配置查询
    all_model = query_all_prompt()
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

            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 将容器设置为列表项
            model_list.setItemWidget(model_item, container)

    return all_model
