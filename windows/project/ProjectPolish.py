from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QFrame, QListWidget, QPushButton, QPlainTextEdit, \
    QComboBox, QListWidgetItem

from sqlite.Sqlite3Utils import query_project_by_id, query_all_model, query_all_prompt, query_prompt_template, \
    edit_project_prompt_id, edit_project_role_model_id, edit_project_relation_model_id, edit_project_scene_model_id, \
    edit_project_framework_model_id, edit_project_polish_model_id
from style.StyleSheet import title_style_sheet, line_edit_style_sheet, button_style_sheet, label_style_sheet, \
    list_widget_style_sheet
from config.GlobalMap import APP_STATE
from utils.ClearLayoutRecursive import clear_layout
from utils.StatusDot import StatusDot
from . import NovelChapterList

def on_prompt_item_clicked(self, point_type, prompt_type):
    choose_project_id = self.prompt_combo.currentData()
    if choose_project_id is None:
        return
    prompt_list = query_prompt_template(choose_project_id, point_type, prompt_type)

    """文本处理"""
    prompt_text = ""
    if 3 == prompt_type:
        if prompt_list:
            for prompt in prompt_list:
                prompt_text = prompt_text + f"{prompt['scene_name']}\n"
                prompt_text = prompt_text + f"{prompt['scene_identify']}\n"
                prompt_text = prompt_text + f"{prompt['context']}\n\n"
    else:
        if prompt_list:
            prompt = prompt_list[0]
            if prompt:
                prompt_text = prompt['context']

    self.text_content.setPlainText(prompt_text)


def on_item_clicked(self, item: QListWidgetItem):
    """触发事件"""
    chapter = item.data(Qt.ItemDataRole.UserRole)
    self.chapter_info = chapter

def polish_btn_clicked(self):
    """润色内容按钮触发"""
    if self.chapter_info is None:
        return
    self.text_content.setPlainText(self.chapter_info['new_content'])

def framework_btn_clicked(self):
    """脉络内容按钮触发"""
    if self.chapter_info is None:
        return
    self.text_content.setPlainText(self.chapter_info['framework_content'])

def scene_btn_clicked(self):
    """场景规则按钮触发"""
    if self.chapter_info is None:
        return
    self.text_content.setPlainText(self.chapter_info['scene_content'])

def relation_btn_clicked(self):
    """关系分析按钮触发"""
    if self.chapter_info is None:
        return
    self.text_content.setPlainText(self.chapter_info['relation_content'])

def role_btn_clicked(self):
    """角色分析按钮触发"""
    if self.chapter_info is None:
        return
    self.text_content.setPlainText(self.chapter_info['role_content'])

def original_btn_clicked(self):
    """原文按钮触发"""
    if self.chapter_info is None:
        return
    self.text_content.setPlainText("")
    for line in self.chapter_info['old_content'].split('\\n'):
        self.text_content.appendPlainText(line)

def update_project_prompt_id(self, text):
    """更新索引"""
    prompt_id = self.prompt_combo.currentData()
    if prompt_id:
        edit_project_prompt_id(prompt_id, self.project_info['id'])

def update_project_role_id(self, combo, text):
    """更新索引"""
    role_model_id = combo.currentData()
    if role_model_id:
        edit_project_role_model_id(role_model_id, self.project_info['id'])

def update_project_relation_id(self, combo, text):
    """更新索引"""
    relation_model_id = combo.currentData()
    if relation_model_id:
        edit_project_relation_model_id(relation_model_id, self.project_info['id'])

def update_project_scene_id(self, combo, text):
    """更新索引"""
    scene_model_id = combo.currentData()
    if scene_model_id:
        edit_project_scene_model_id(scene_model_id, self.project_info['id'])

def update_project_framework_id(self, combo, text):
    """更新索引"""
    framework_model_id = combo.currentData()
    if framework_model_id:
        edit_project_framework_model_id(framework_model_id, self.project_info['id'])

def update_project_polish_id(self, combo, text):
    """更新索引"""
    polish_model_id = combo.currentData()
    if polish_model_id:
        edit_project_polish_model_id(polish_model_id, self.project_info['id'])


def polist_page(self, project_id):
    """
    项目润色页面
    """

    """章节信息"""
    self.chapter_info = None

    # 存在数据则销毁
    if self.project_win_layout:
        clear_layout(self.project_win_layout)

    # 项目查询
    self.project_info = query_project_by_id(project_id)
    if self.project_info is None:
        # 查询为空
        project_none = QLabel("无项目信息")
        self.project_win_layout.addWidget(project_none)
        return

    # 存在项目
    """顶部标题栏"""
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    """顶部状态栏加入主分区"""
    self.project_win_layout.addLayout(header_layout)
    """项目润色文案"""
    title_label = QLabel("📒 项目润色")
    title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
    header_layout.addWidget(title_label)
    """弹开到两边"""
    header_layout.addStretch()
    """右侧布局"""
    header_right = QVBoxLayout()
    header_right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
    header_layout.addLayout(header_right)
    """项目名称"""
    project_name = QLabel(self.project_info['title'])
    project_name.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
    project_name.setStyleSheet(title_style_sheet())
    header_right.addWidget(project_name)
    """项目状态"""
    project_status_box = QHBoxLayout()
    project_status_box.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
    """状态"""
    project_status = APP_STATE.get(project_id)
    if project_status is None:
        project_status = 1
        APP_STATE.setdefault(project_id, project_status)
    """状态渲染"""
    if 1 == project_status:
        self.project_status_color = StatusDot("#9E9E9E")
        project_status_box.addWidget(self.project_status_color)
        self.project_status_title = QLabel("待开始")
        project_status_box.addWidget(self.project_status_title)
    elif 2 == project_status:
        self.project_status_color = StatusDot("#00FF00")
        project_status_box.addWidget(self.project_status_color)
        self.project_status_title = QLabel("进行中")
        project_status_box.addWidget(self.project_status_title)
    elif 3 == project_status:
        self.project_status_color = StatusDot("#00FF00")
        project_status_box.addWidget(self.project_status_color)
        self.project_status_title = QLabel("已完成")
        project_status_box.addWidget(self.project_status_title)
    header_right.addLayout(project_status_box)


    """分割线"""
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.HLine)
    frame.setFrameShadow(QFrame.Shadow.Sunken)
    self.project_win_layout.addWidget(frame)

    """中间项目"""
    center_layout = QHBoxLayout()
    center_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.project_win_layout.addLayout(center_layout)
    """左侧章节栏"""
    center_left_layout = QVBoxLayout()
    center_left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_layout.addLayout(center_left_layout)
    """"顶部"""
    chapter_top_layout = QHBoxLayout()
    chapter_top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_left_layout.addLayout(chapter_top_layout)
    """章节提示"""
    chapter_title = QLabel("章节导航")
    chapter_title.setFixedWidth(100)
    chapter_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_title.setStyleSheet(title_style_sheet())
    chapter_top_layout.addWidget(chapter_title)
    """章节统计1"""
    all_chapter = self.project_info['chapter_num']
    self.chapter_count1 = QLabel(f"共 {all_chapter} 章节")
    self.chapter_count1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_top_layout.addWidget(self.chapter_count1)
    """章节统计2"""
    success_chapter = self.project_info['success_num']
    fail_chapter = self.project_info['fail_num']
    self.chapter_count2 = QLabel(f"已完成 {success_chapter} 章节 · 已失败 {fail_chapter} 章节")
    self.chapter_count2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_left_layout.addWidget(self.chapter_count2)
    """章节统计3"""
    wait_chapter = all_chapter - success_chapter
    self.chapter_count3 = QLabel(f"待完成 {wait_chapter} 章节 · 新增 {self.project_info['expansion_num']} 章节")
    self.chapter_count3.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_left_layout.addWidget(self.chapter_count3)
    """提示词布局"""
    prompt_low_layout = QHBoxLayout()
    prompt_low_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_left_layout.addLayout(prompt_low_layout)
    """提示词标题"""
    prompt_title = QLabel("Prompt：")
    prompt_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    prompt_low_layout.addWidget(prompt_title)
    """查询全部提示词模版"""
    all_prompt = query_all_prompt()
    """提示词选择列表"""
    self.prompt_combo = QComboBox()
    for prompt in all_prompt:
        self.prompt_combo.addItem(prompt['name'], prompt['id'])
    self.prompt_combo.setFixedSize(180, 25)
    self.prompt_combo.setStyleSheet(line_edit_style_sheet())
    if self.project_info['prompt_id']:
        prompt_combo_index = self.prompt_combo.findData(self.project_info['prompt_id'])
        self.prompt_combo.setCurrentIndex(prompt_combo_index)
    else:
        self.prompt_combo.setCurrentIndex(0)
    self.prompt_combo.textActivated.connect(lambda text : update_project_prompt_id(self, text))
    prompt_low_layout.addWidget(self.prompt_combo)

    """分割线"""
    frame2 = QFrame()
    frame2.setFrameShape(QFrame.Shape.HLine)
    frame2.setFrameShadow(QFrame.Shadow.Sunken)
    center_left_layout.addWidget(frame2)

    """章节列表"""
    self.chapter_list = QListWidget()
    self.chapter_list.setContentsMargins(10, 10, 10, 10)
    self.chapter_list.setFixedSize(250, 565)
    self.chapter_list.setStyleSheet(list_widget_style_sheet())
    self.chapter_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.chapter_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # 渲染列表
    self.all_chapter = NovelChapterList.novel_chapter(self, project_id)
    self.chapter_list.itemClicked.connect(lambda item: on_item_clicked(self, item))
    center_left_layout.addWidget(self.chapter_list)

    """垂直分割线"""
    frame3 = QFrame()
    frame3.setFrameShape(QFrame.Shape.VLine)
    frame3.setFrameShadow(QFrame.Shadow.Sunken)
    center_layout.addWidget(frame3)

    """右侧区域"""
    center_right_layout = QVBoxLayout()
    center_right_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_layout.addLayout(center_right_layout)

    """章节内容"""
    center_right_row1 = QHBoxLayout()
    center_right_row1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(center_right_row1)

    """按钮区域"""
    center_right_row1_col1 = QVBoxLayout()
    center_right_row1_col1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_row1.addLayout(center_right_row1_col1)
    """原文按钮"""
    original_btn = QPushButton("原        文")
    original_btn.setFixedSize(100, 30)
    original_btn.setStyleSheet(button_style_sheet())
    original_btn.setToolTip("原文内容")
    original_btn.clicked.connect(lambda : original_btn_clicked(self))
    center_right_row1_col1.addWidget(original_btn)
    """角色分析按钮"""
    role_btn = QPushButton("角色分析")
    role_btn.setFixedSize(100, 30)
    role_btn.setStyleSheet(button_style_sheet())
    role_btn.setToolTip("原文中出场角色信息内容")
    role_btn.clicked.connect(lambda : role_btn_clicked(self))
    center_right_row1_col1.addWidget(role_btn)
    """关系分析按钮"""
    relation_btn = QPushButton("关系分析")
    relation_btn.setFixedSize(100, 30)
    relation_btn.setStyleSheet(button_style_sheet())
    relation_btn.setToolTip("原文角色之间的关系内容")
    relation_btn.clicked.connect(lambda : relation_btn_clicked(self))
    center_right_row1_col1.addWidget(relation_btn)
    """场景规则按钮"""
    scene_btn = QPushButton("场景规则")
    scene_btn.setFixedSize(100, 30)
    scene_btn.setStyleSheet(button_style_sheet())
    scene_btn.setToolTip("原文匹配的全部场景规则进行融合内容")
    scene_btn.clicked.connect(lambda : scene_btn_clicked(self))
    center_right_row1_col1.addWidget(scene_btn)
    """脉络内容按钮"""
    framework_btn = QPushButton("脉络内容")
    framework_btn.setFixedSize(100, 30)
    framework_btn.setStyleSheet(button_style_sheet())
    framework_btn.setToolTip("原文润色主体脉络发展内容")
    framework_btn.clicked.connect(lambda : framework_btn_clicked(self))
    center_right_row1_col1.addWidget(framework_btn)
    """润色内容按钮"""
    polish_btn = QPushButton("润色内容")
    polish_btn.setFixedSize(100, 30)
    polish_btn.setStyleSheet(button_style_sheet())
    polish_btn.setToolTip("原文最终润色内容")
    polish_btn.clicked.connect(lambda : polish_btn_clicked(self))
    center_right_row1_col1.addWidget(polish_btn)

    """分割线"""
    frame4 = QFrame()
    frame4.setFrameShape(QFrame.Shape.VLine)
    frame4.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_row1.addWidget(frame4)

    """文本框"""
    center_right_row1_col2 = QVBoxLayout()
    center_right_row1_col2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_row1.addLayout(center_right_row1_col2)

    """文本框"""
    self.text_content = QPlainTextEdit()
    self.text_content.setFixedSize(550, 420)
    self.text_content.setStyleSheet(line_edit_style_sheet())
    self.text_content.setReadOnly(True)
    center_right_row1_col2.addWidget(self.text_content)

    """插入分割线"""
    frame5 = QFrame()
    frame5.setFrameShape(QFrame.Shape.HLine)
    frame5.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_layout.addWidget(frame5)

    """工具栏1"""
    tool1_layout = QHBoxLayout()
    tool1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(tool1_layout)

    """查询全部模型配置"""
    all_model = query_all_model()

    """工具栏第一行"""
    tool1 = QHBoxLayout()
    tool1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(tool1)
    """角色分析提示词-标题"""
    tool1_title = QLabel("1.角色分析配置：")
    tool1_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool1_title.setStyleSheet(label_style_sheet())
    tool1.addWidget(tool1_title)
    """角色分析提示词-模型选择"""
    tool1_model = QComboBox()
    for model in all_model:
        tool1_model.addItem(model['name'], model['id'])
    tool1_model.setFixedSize(200, 30)
    tool1_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['role_model_id']:
        tool1_model_index = tool1_model.findData(self.project_info['role_model_id'])
        tool1_model.setCurrentIndex(tool1_model_index)
    else:
        tool1_model.setCurrentIndex(0)
    tool1_model.textActivated.connect(lambda text : update_project_role_id(self, tool1_model, text))
    tool1.addWidget(tool1_model)
    """角色分析系统提示词"""
    tool1_system = QPushButton("系统提示词")
    tool1_system.setStyleSheet(button_style_sheet())
    tool1_system.setFixedSize(80, 30)
    tool1_system.clicked.connect(lambda : on_prompt_item_clicked(self, 1, 1))
    tool1.addWidget(tool1_system)
    """角色分析用户提示词"""
    tool1_user = QPushButton("用户提示词")
    tool1_user.setStyleSheet(button_style_sheet())
    tool1_user.setFixedSize(80, 30)
    tool1_user.clicked.connect(lambda : on_prompt_item_clicked(self, 1, 2))
    tool1.addWidget(tool1_user)

    """工具栏第二行"""
    tool2 = QHBoxLayout()
    tool2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(tool2)
    """关系分析提示词-标题"""
    tool2_title = QLabel("2.关系分析配置：")
    tool2_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool2_title.setStyleSheet(label_style_sheet())
    tool2.addWidget(tool2_title)
    """关系分析提示词-模型选择"""
    tool2_model = QComboBox()
    for model in all_model:
        tool2_model.addItem(model['name'], model['id'])
    tool2_model.setFixedSize(200, 30)
    tool2_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['relation_model_id']:
        tool2_model_index = tool2_model.findData(self.project_info['relation_model_id'])
        tool2_model.setCurrentIndex(tool2_model_index)
    else:
        tool2_model.setCurrentIndex(0)
    tool2_model.textActivated.connect(lambda text : update_project_relation_id(self, tool2_model, text))
    tool2.addWidget(tool2_model)
    """关系分析系统提示词"""
    tool2_system = QPushButton("系统提示词")
    tool2_system.setStyleSheet(button_style_sheet())
    tool2_system.setFixedSize(80, 30)
    tool2_system.clicked.connect(lambda : on_prompt_item_clicked(self, 2, 1))
    tool2.addWidget(tool2_system)
    """关系分析用户提示词"""
    tool2_user = QPushButton("用户提示词")
    tool2_user.setStyleSheet(button_style_sheet())
    tool2_user.setFixedSize(80, 30)
    tool2_user.clicked.connect(lambda : on_prompt_item_clicked(self, 2, 2))
    tool2.addWidget(tool2_user)

    """工具栏第三行"""
    tool3 = QHBoxLayout()
    tool3.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(tool3)
    """场景分析提示词-标题"""
    tool3_title = QLabel("3.场景分析配置：")
    tool3_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool3_title.setStyleSheet(label_style_sheet())
    tool3.addWidget(tool3_title)
    """场景分析提示词-模型选择"""
    tool3_model = QComboBox()
    for model in all_model:
        tool3_model.addItem(model['name'], model['id'])
    tool3_model.setFixedSize(200, 30)
    tool3_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['scene_model_id']:
        tool3_model_index = tool3_model.findData(self.project_info['scene_model_id'])
        tool3_model.setCurrentIndex(tool3_model_index)
    else:
        tool3_model.setCurrentIndex(0)
    tool3_model.textActivated.connect(lambda text : update_project_scene_id(self, tool3_model, text))
    tool3.addWidget(tool3_model)
    """场景分析提示词-系统提示词"""
    tool3_system = QPushButton("系统提示词")
    tool3_system.setStyleSheet(button_style_sheet())
    tool3_system.setFixedSize(80, 30)
    tool3_system.clicked.connect(lambda : on_prompt_item_clicked(self, 3, 1))
    tool3.addWidget(tool3_system)
    """场景分析提示词-用户提示词"""
    tool3_user = QPushButton("用户提示词")
    tool3_user.setStyleSheet(button_style_sheet())
    tool3_user.setFixedSize(80, 30)
    tool3_user.clicked.connect(lambda : on_prompt_item_clicked(self, 3, 2))
    tool3.addWidget(tool3_user)
    """场景分析提示词-场景提示词"""
    tool3_scene = QPushButton("场景提示词")
    tool3_scene.setStyleSheet(button_style_sheet())
    tool3_scene.setFixedSize(80, 30)
    tool3_scene.clicked.connect(lambda : on_prompt_item_clicked(self, 3, 3))
    tool3.addWidget(tool3_scene)


    """工具栏第四行"""
    tool4 = QHBoxLayout()
    tool4.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(tool4)

    """工具栏第四行第一列"""
    tool4_col1 = QVBoxLayout()
    tool4_col1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool4.addLayout(tool4_col1)

    """工具栏第四行第一列第一行"""
    tool4_col1_row1 = QHBoxLayout()
    tool4_col1_row1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool4_col1.addLayout(tool4_col1_row1)
    """脉络改写提示词-标题"""
    tool4_col1_row1_title = QLabel("4.脉络改写配置：")
    tool4_col1_row1_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool4_col1_row1_title.setStyleSheet(label_style_sheet())
    tool4_col1_row1.addWidget(tool4_col1_row1_title)
    """脉络改写提示词-模型选择"""
    tool4_col1_row1_model = QComboBox()
    for model in all_model:
        tool4_col1_row1_model.addItem(model['name'], model['id'])
    tool4_col1_row1_model.setFixedSize(200, 30)
    tool4_col1_row1_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['framework_model_id']:
        tool4_col1_row1_model_index = tool4_col1_row1_model.findData(self.project_info['framework_model_id'])
        tool4_col1_row1_model.setCurrentIndex(tool4_col1_row1_model_index)
    else:
        tool4_col1_row1_model.setCurrentIndex(0)
    tool4_col1_row1_model.textActivated.connect(lambda text : update_project_framework_id(self, tool4_col1_row1_model, text))
    tool4_col1_row1.addWidget(tool4_col1_row1_model)
    """脉络改写提示词-系统提示词"""
    tool4_col1_row1_system = QPushButton("系统提示词")
    tool4_col1_row1_system.setStyleSheet(button_style_sheet())
    tool4_col1_row1_system.setFixedSize(80, 30)
    tool4_col1_row1_system.clicked.connect(lambda : on_prompt_item_clicked(self, 4, 1))
    tool4_col1_row1.addWidget(tool4_col1_row1_system)
    """脉络改写提示词-用户提示词"""
    tool4_col1_row1_user = QPushButton("用户提示词")
    tool4_col1_row1_user.setStyleSheet(button_style_sheet())
    tool4_col1_row1_user.setFixedSize(80, 30)
    tool4_col1_row1_user.clicked.connect(lambda : on_prompt_item_clicked(self, 4, 2))
    tool4_col1_row1.addWidget(tool4_col1_row1_user)

    """工具栏第四行第一列第二行"""
    tool4_col1_row2 = QHBoxLayout()
    tool4_col1_row2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool4_col1.addLayout(tool4_col1_row2)
    """结果润色提示词-标题"""
    tool4_col1_row2_title = QLabel("5.结果润色配置：")
    tool4_col1_row2_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    tool4_col1_row2_title.setStyleSheet(label_style_sheet())
    tool4_col1_row2.addWidget(tool4_col1_row2_title)
    """结果润色提示词-模型选择"""
    tool4_col1_row2_model = QComboBox()
    for model in all_model:
        tool4_col1_row2_model.addItem(model['name'], model['id'])
    tool4_col1_row2_model.setFixedSize(200, 30)
    tool4_col1_row2_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['polish_model_id']:
        tool4_col1_row2_model_index = tool4_col1_row2_model.findData(self.project_info['polish_model_id'])
        tool4_col1_row2_model.setCurrentIndex(tool4_col1_row2_model_index)
    else:
        tool4_col1_row2_model.setCurrentIndex(0)
    tool4_col1_row2_model.textActivated.connect(lambda text : update_project_polish_id(self, tool4_col1_row2_model, text))
    tool4_col1_row2.addWidget(tool4_col1_row2_model)
    """结果润色提示词-系统提示词"""
    tool4_col1_row2_system = QPushButton("系统提示词")
    tool4_col1_row2_system.setStyleSheet(button_style_sheet())
    tool4_col1_row2_system.setFixedSize(80, 30)
    tool4_col1_row2_system.clicked.connect(lambda : on_prompt_item_clicked(self, 5, 1))
    tool4_col1_row2.addWidget(tool4_col1_row2_system)
    """结果润色提示词-用户提示词"""
    tool4_col1_row2_user = QPushButton("用户提示词")
    tool4_col1_row2_user.setStyleSheet(button_style_sheet())
    tool4_col1_row2_user.setFixedSize(80, 30)
    tool4_col1_row2_user.clicked.connect(lambda : on_prompt_item_clicked(self, 5, 2))
    tool4_col1_row2.addWidget(tool4_col1_row2_user)

    """弹开"""
    tool4.addStretch()

    """开始按钮"""
    self.start_stop_btn = QPushButton()
    self.start_stop_btn.setFixedSize(80, 80)
    self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#00C853'))
    self.start_stop_btn.clicked.connect(lambda : start_stop_clicked(self, tool1_model, tool2_model, tool3_model, tool4_col1_row1_model, tool4_col1_row2_model))
    tool4.addWidget(self.start_stop_btn)
    """开始按钮控制"""
    if 1 == project_status:
        self.start_stop_btn.setText("开始")
        self.start_stop_btn.setEnabled(True)
    elif 2 == project_status:
        self.start_stop_btn.setText("停止")
        self.start_stop_btn.setEnabled(True)
        self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#FF0000'))
    else:
        self.start_stop_btn.setText("开始")
        self.start_stop_btn.setEnabled(False)

    """可选框初始化"""
    disable_enable_prompt_model_conf(self.project_info['id'], self.prompt_combo, tool1_model, tool2_model, tool3_model, tool4_col1_row1_model, tool4_col1_row2_model)

def start_stop_clicked(self, tool1_model, tool2_model, tool3_model, tool4_col1_row1_model, tool4_col1_row2_model):
    # 获取状态
    project_status = APP_STATE.get(self.project_info['id'])
    if 1 == project_status:
        APP_STATE[self.project_info['id']] = 2
        self.start_stop_btn.setText("停止")
        self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#FF0000'))
    elif 2 == project_status:
        APP_STATE[self.project_info['id']] = 1
        self.start_stop_btn.setText("开始")
        self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#00C853'))

    disable_enable_prompt_model_conf(self.project_info['id'], self.prompt_combo, tool1_model, tool2_model, tool3_model, tool4_col1_row1_model, tool4_col1_row2_model)


def disable_enable_prompt_model_conf(project_id, prompt_combo, tool1_model, tool2_model, tool3_model, tool4_col1_row1_model, tool4_col1_row2_model):
    # 获取状态
    project_status = APP_STATE.get(project_id)
    if 1 == project_status:
        # 可选
        prompt_combo.setEnabled(True)
        tool1_model.setEnabled(True)
        tool2_model.setEnabled(True)
        tool3_model.setEnabled(True)
        tool4_col1_row1_model.setEnabled(True)
        tool4_col1_row2_model.setEnabled(True)
    else:
        # 不可选
        prompt_combo.setEnabled(False)
        tool1_model.setEnabled(False)
        tool2_model.setEnabled(False)
        tool3_model.setEnabled(False)
        tool4_col1_row1_model.setEnabled(False)
        tool4_col1_row2_model.setEnabled(False)

