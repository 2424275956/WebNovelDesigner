import json
import os

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QFrame, QListWidget, QPushButton, QPlainTextEdit, \
    QComboBox, QListWidgetItem, QLineEdit, QMessageBox, QFileDialog

from resources.style.StyleSheet import title_style_sheet, line_edit_style_sheet, button_style_sheet, label_style_sheet, \
    list_widget_style_sheet
from config.GlobalMap import APP_STATE
from sqlite.ChapterDB import count_all_chapter_num, count_success_chapter_num, count_fail_chapter_num, \
    count_extra_chapter_num, query_all_polish_chapter, query_chapter_by_id
from sqlite.ModelDB import query_all_model
from sqlite.ProjectDB import edit_project_prompt_id, edit_project_role_model_id, edit_polish_before_num, \
    edit_polish_after_num, edit_project_relation_model_id, edit_project_process_model_id, edit_project_scene_model_id, \
    edit_project_extra_scene_model_id, edit_project_framework_model_id, edit_project_extra_framework_model_id, \
    edit_project_polish_model_id, query_project_by_id, edit_project_status
from sqlite.PromptDB import query_prompt_template, query_all_prompt
from utils.ClearLayoutRecursive import clear_layout
from utils.StatusDot import StatusDot
from windows.project import NovelChapterList
from windows.project import ProjectStartPolish

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
                prompt_text = prompt_text + f"场景名称：{prompt['scene_name']}\n"
                prompt_text = prompt_text + f"识别规则：{prompt['scene_identify']}\n"
                prompt_text = prompt_text + f"执行规则：{prompt['context']}\n\n"
    else:
        if prompt_list:
            prompt = prompt_list[0]
            if prompt:
                prompt_text = prompt['context']

    self.text_content.setPlainText(prompt_text)
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))


def on_item_clicked(self, item: QListWidgetItem):
    """触发事件"""
    chapter = item.data(Qt.ItemDataRole.UserRole)
    self.chapter_info = chapter

def polish_btn_clicked(self):
    """润色内容按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText(chapter['new_content'])
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

def framework_btn_clicked(self):
    """脉络内容按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText(chapter['framework_content'])
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

def scene_btn_clicked(self):
    """场景规则按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText(chapter['scene_content'])
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

def relation_btn_clicked(self):
    """关系分析按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText(chapter['relation_content'])
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

def process_btn_clicked(self):
    """流程控制按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText(chapter['process_content'])
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

def role_btn_clicked(self):
    """角色分析按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText(chapter['role_content'])
    QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

def original_btn_clicked(self):
    """原文按钮触发"""
    if self.chapter_info is None:
        return
    chapter = query_chapter_by_id(self.chapter_info['id'])
    self.text_content.setPlainText("")
    if chapter['old_content']:
        for line in chapter['old_content'].split('\\n'):
            self.text_content.appendPlainText(line)
        QTimer.singleShot(0, lambda: self.text_content.verticalScrollBar().setValue(0))

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

def update_polish_before_num(self, chapter_before_num):
    """更新附带章节"""
    num = 0
    if len(chapter_before_num.text()) > 0:
        num = int(chapter_before_num.text())
    edit_polish_before_num(num, self.project_info['id'])

def update_polish_after_num(self, chapter_after_num):
    """更新附带章节"""
    num = 0
    if len(chapter_after_num.text()) > 0:
        num = int(chapter_after_num.text())
    edit_polish_after_num(num, self.project_info['id'])

def update_project_relation_id(self, combo, text):
    """更新索引"""
    relation_model_id = combo.currentData()
    if relation_model_id:
        edit_project_relation_model_id(relation_model_id, self.project_info['id'])

def update_project_process_id(self, combo, text):
    """更新索引"""
    process_id = combo.currentData()
    if process_id:
        edit_project_process_model_id(process_id, self.project_info['id'])

def update_project_scene_id(self, combo, text):
    """更新索引"""
    scene_model_id = combo.currentData()
    if scene_model_id:
        edit_project_scene_model_id(scene_model_id, self.project_info['id'])

def update_project_extra_scene_id(self, combo, text):
    """更新索引"""
    extra_scene_id = combo.currentData()
    if extra_scene_id:
        edit_project_extra_scene_model_id(extra_scene_id, self.project_info['id'])

def update_project_framework_id(self, combo, text):
    """更新索引"""
    framework_model_id = combo.currentData()
    if framework_model_id:
        edit_project_framework_model_id(framework_model_id, self.project_info['id'])

def update_project_extra_framework_id(self, combo, text):
    """更新索引"""
    extra_framework_id = combo.currentData()
    if extra_framework_id:
        edit_project_extra_framework_model_id(extra_framework_id, self.project_info['id'])

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
        # 获取章节判断
        all_num = count_all_chapter_num(project_id)
        success_num = count_success_chapter_num(project_id)
        if success_num[0] >= all_num[0]:
            project_status = 3
            APP_STATE[project_id] = project_status
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
    """章节提示"""
    chapter_title = QLabel("章节导航")
    chapter_title.setFixedWidth(100)
    chapter_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_title.setStyleSheet(title_style_sheet())
    center_left_layout.addWidget(chapter_title)

    """章节列表筛选框"""


    """章节列表"""
    self.chapter_list = QListWidget()
    self.chapter_list.setContentsMargins(10, 10, 10, 10)
    self.chapter_list.setFixedSize(250, 800)
    self.chapter_list.setStyleSheet(list_widget_style_sheet())
    self.chapter_list.setItemAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.chapter_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    # 渲染列表
    self.all_chapter = NovelChapterList.novel_chapter(self, project_id)
    self.chapter_list.itemClicked.connect(lambda item: on_item_clicked(self, item))
    center_left_layout.addWidget(self.chapter_list)

    """垂直分割线"""
    frame6 = QFrame()
    frame6.setFrameShape(QFrame.Shape.VLine)
    frame6.setFrameShadow(QFrame.Shadow.Sunken)
    center_layout.addWidget(frame6)

    """文本框区域"""
    text_layout = QVBoxLayout()
    text_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_layout.addLayout(text_layout)
    # 文本框标题
    text_title = QLabel("文本区域（提示词配置 与 阶段内容）")
    text_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    text_title.setStyleSheet(label_style_sheet(font_size=20))
    text_layout.addWidget(text_title)

    """按钮区域"""
    text_btn_layout = QHBoxLayout()
    text_btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    text_layout.addLayout(text_btn_layout)
    """原文按钮"""
    original_btn = QPushButton("原        文")
    original_btn.setFixedSize(80, 30)
    original_btn.setStyleSheet(button_style_sheet())
    original_btn.setToolTip("原文内容")
    original_btn.clicked.connect(lambda : original_btn_clicked(self))
    text_btn_layout.addWidget(original_btn)
    """角色分析按钮"""
    role_btn = QPushButton("角色分析")
    role_btn.setFixedSize(80, 30)
    role_btn.setStyleSheet(button_style_sheet())
    role_btn.setToolTip("原文中出场角色信息内容")
    role_btn.clicked.connect(lambda : role_btn_clicked(self))
    text_btn_layout.addWidget(role_btn)
    """关系分析按钮"""
    relation_btn = QPushButton("关系分析")
    relation_btn.setFixedSize(80, 30)
    relation_btn.setStyleSheet(button_style_sheet())
    relation_btn.setToolTip("原文角色之间的关系内容")
    relation_btn.clicked.connect(lambda : relation_btn_clicked(self))
    text_btn_layout.addWidget(relation_btn)
    """流程控制按钮"""
    process_btn = QPushButton("流程控制")
    process_btn.setFixedSize(80, 30)
    process_btn.setStyleSheet(button_style_sheet())
    process_btn.setToolTip("流程判断结果内容")
    process_btn.clicked.connect(lambda : process_btn_clicked(self))
    text_btn_layout.addWidget(process_btn)
    """场景规则按钮"""
    scene_btn = QPushButton("场景规则")
    scene_btn.setFixedSize(80, 30)
    scene_btn.setStyleSheet(button_style_sheet())
    scene_btn.setToolTip("原文匹配的全部场景规则进行融合内容")
    scene_btn.clicked.connect(lambda : scene_btn_clicked(self))
    text_btn_layout.addWidget(scene_btn)
    """脉络内容按钮"""
    framework_btn = QPushButton("脉络内容")
    framework_btn.setFixedSize(80, 30)
    framework_btn.setStyleSheet(button_style_sheet())
    framework_btn.setToolTip("原文润色主体脉络发展内容")
    framework_btn.clicked.connect(lambda : framework_btn_clicked(self))
    text_btn_layout.addWidget(framework_btn)
    """润色内容按钮"""
    polish_btn = QPushButton("润色内容")
    polish_btn.setFixedSize(80, 30)
    polish_btn.setStyleSheet(button_style_sheet())
    polish_btn.setToolTip("原文最终润色内容")
    polish_btn.clicked.connect(lambda : polish_btn_clicked(self))
    text_btn_layout.addWidget(polish_btn)

    """文本框"""
    self.text_content = QPlainTextEdit()
    self.text_content.setFixedSize(590, 780)
    self.text_content.setStyleSheet(line_edit_style_sheet())
    self.text_content.setReadOnly(True)
    text_layout.addWidget(self.text_content)


    """垂直分割线"""
    frame3 = QFrame()
    frame3.setFrameShape(QFrame.Shape.VLine)
    frame3.setFrameShadow(QFrame.Shadow.Sunken)
    center_layout.addWidget(frame3)

    """右侧区域"""
    center_right_layout = QVBoxLayout()
    center_right_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_layout.addLayout(center_right_layout)

    """顶部章节统计"""
    center_right_top_layout = QHBoxLayout()
    center_right_top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(center_right_top_layout)
    # 顶部左侧统计
    """章节信息"""
    center_right_top_left_layout = QVBoxLayout()
    center_right_top_left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_top_layout.addLayout(center_right_top_left_layout)
    """章节统计1"""
    all_chapter = (count_all_chapter_num(project_id))[0]
    self.chapter_count1 = QLabel(f"项目共有 {all_chapter} 章节")
    self.chapter_count1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.chapter_count1.setStyleSheet(label_style_sheet(font_size=20))
    center_right_top_left_layout.addWidget(self.chapter_count1)
    """章节统计2"""
    success_chapter = (count_success_chapter_num(project_id))[0]
    self.chapter_count2 = QLabel(f"项目已完成 {success_chapter} 章节")
    self.chapter_count2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.chapter_count2.setStyleSheet(label_style_sheet(font_size=20))
    center_right_top_left_layout.addWidget(self.chapter_count2)
    """章节统计3"""
    fail_chapter = (count_fail_chapter_num(project_id))[0]
    self.chapter_count3 = QLabel(f"项目已失败 {fail_chapter} 章节")
    self.chapter_count3.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.chapter_count3.setStyleSheet(label_style_sheet(font_size=20))
    center_right_top_left_layout.addWidget(self.chapter_count3)
    """章节统计4"""
    wait_chapter = all_chapter - success_chapter
    self.chapter_count4 = QLabel(f"项目待完成 {wait_chapter} 章节")
    self.chapter_count4.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.chapter_count4.setStyleSheet(label_style_sheet(font_size=20))
    center_right_top_left_layout.addWidget(self.chapter_count4)
    """章节统计5"""
    expansion_num = (count_extra_chapter_num(project_id))[0]
    self.chapter_count5 = QLabel(f"项目已新增 {expansion_num} 章节")
    self.chapter_count5.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    self.chapter_count5.setStyleSheet(label_style_sheet(font_size=20))
    center_right_top_left_layout.addWidget(self.chapter_count5)

    # 弹开
    center_right_top_layout.addStretch()

    # 分割线
    frame11 = QFrame()
    frame11.setFrameShape(QFrame.Shape.VLine)
    frame11.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_top_layout.addWidget(frame11)

    """章节配置"""
    center_right_top_col2 = QVBoxLayout()
    center_right_top_col2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_top_layout.addLayout(center_right_top_col2)

    """提示词布局"""
    prompt_low_layout = QHBoxLayout()
    prompt_low_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_top_col2.addLayout(prompt_low_layout)
    """提示词标题"""
    prompt_title = QLabel("项目提示词模版：")
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
        self.prompt_combo.setCurrentIndex(-1)
        self.prompt_combo.setPlaceholderText("请选择...")
    self.prompt_combo.textActivated.connect(lambda text : update_project_prompt_id(self, text))
    prompt_low_layout.addWidget(self.prompt_combo)

    """分割线"""
    frame7 = QFrame()
    frame7.setFrameShape(QFrame.Shape.HLine)
    frame7.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_top_col2.addWidget(frame7)

    """章节滑动窗口数"""
    # 附带当前章节前数量
    chapter_before_num_layout = QHBoxLayout()
    chapter_before_num_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_top_col2.addLayout(chapter_before_num_layout)
    ## 标题
    chapter_before_num_title = QLabel("改写（撰写）附带前n章节数：")
    chapter_before_num_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_before_num_title.setStyleSheet(label_style_sheet())
    chapter_before_num_layout.addWidget(chapter_before_num_title)
    ## 编辑框
    chapter_before_num = QLineEdit()
    chapter_before_num.setText("5")
    if self.project_info['polish_before_num']:
        chapter_before_num.setText(str(self.project_info['polish_before_num']))
    chapter_before_num.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_before_num.setStyleSheet(line_edit_style_sheet())
    int_validator = QIntValidator(0, 9999, self)
    chapter_before_num.setValidator(int_validator)
    chapter_before_num.textChanged.connect(lambda : update_polish_before_num(self, chapter_before_num))
    chapter_before_num_layout.addWidget(chapter_before_num)

    # 附带当前章节后数量
    chapter_after_num_layout = QHBoxLayout()
    chapter_after_num_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_top_col2.addLayout(chapter_after_num_layout)
    ## 标题
    chapter_after_num_title = QLabel("改写（撰写）附带后n章节数：")
    chapter_after_num_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_after_num_title.setStyleSheet(label_style_sheet())
    chapter_after_num_layout.addWidget(chapter_after_num_title)
    ## 编辑框
    chapter_after_num = QLineEdit()
    chapter_after_num.setText("1")
    if self.project_info['polish_after_num']:
        chapter_after_num.setText(str(self.project_info['polish_after_num']))
    chapter_after_num.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    chapter_after_num.setStyleSheet(line_edit_style_sheet())
    chapter_after_num.setValidator(int_validator)
    chapter_after_num.textChanged.connect(lambda : update_polish_after_num(self, chapter_after_num))
    chapter_after_num_layout.addWidget(chapter_after_num)

    """分割线"""
    frame12 = QFrame()
    frame12.setFrameShape(QFrame.Shape.HLine)
    frame12.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_top_col2.addWidget(frame12)

    """插入分割线"""
    frame5 = QFrame()
    frame5.setFrameShape(QFrame.Shape.HLine)
    frame5.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_layout.addWidget(frame5)

    """查询全部模型配置"""
    all_model = query_all_model()

    # 角色分析提示词-配置
    ## 角色分析提示词-配置-布局
    role_prompt_conf_layout = QHBoxLayout()
    role_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(role_prompt_conf_layout)
    ## 角色分析提示词-配置-布局-标题
    role_prompt_conf_title = QLabel("1.角色分析提示词/模型配置")
    role_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    role_prompt_conf_title.setStyleSheet(label_style_sheet())
    role_prompt_conf_layout.addWidget(role_prompt_conf_title)
    ### 角色分析提示词-配置-布局-模型选择
    role_prompt_conf_model = QComboBox()
    for model in all_model:
        role_prompt_conf_model.addItem(model['name'], model['id'])
    role_prompt_conf_model.setFixedSize(200, 30)
    role_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['role_model_id']:
        tool1_model_index = role_prompt_conf_model.findData(self.project_info['role_model_id'])
        role_prompt_conf_model.setCurrentIndex(tool1_model_index)
    else:
        role_prompt_conf_model.setCurrentIndex(-1)
        role_prompt_conf_model.setPlaceholderText("请选择...")
    role_prompt_conf_model.textActivated.connect(lambda text : update_project_role_id(self, role_prompt_conf_model, text))
    role_prompt_conf_layout.addWidget(role_prompt_conf_model)
    ### 角色分析提示词-配置-布局-系统提示词
    role_prompt_btn_system = QPushButton("系统提示词")
    role_prompt_btn_system.setStyleSheet(button_style_sheet())
    role_prompt_btn_system.setFixedSize(80, 30)
    role_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 1, 1))
    role_prompt_conf_layout.addWidget(role_prompt_btn_system)
    ### 角色分析提示词-配置-布局-用户提示词
    role_prompt_btn_user = QPushButton("用户提示词")
    role_prompt_btn_user.setStyleSheet(button_style_sheet())
    role_prompt_btn_user.setFixedSize(80, 30)
    role_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 1, 2))
    role_prompt_conf_layout.addWidget(role_prompt_btn_user)

    # 流程控制提示词-配置
    ## 流程控制提示词-配置-布局
    process_prompt_conf_layout = QHBoxLayout()
    process_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(process_prompt_conf_layout)
    ## 流程控制提示词-配置-布局-标题
    process_prompt_conf_title = QLabel("2.流程控制提示词/模型配置")
    process_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    process_prompt_conf_title.setStyleSheet(label_style_sheet())
    process_prompt_conf_layout.addWidget(process_prompt_conf_title)
    ### 流程控制提示词-配置-布局-模型选择
    process_prompt_conf_model = QComboBox()
    for model in all_model:
        process_prompt_conf_model.addItem(model['name'], model['id'])
    process_prompt_conf_model.setFixedSize(200, 30)
    process_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['scene_model_id']:
        tool3_model_index = process_prompt_conf_model.findData(self.project_info['scene_model_id'])
        process_prompt_conf_model.setCurrentIndex(tool3_model_index)
    else:
        process_prompt_conf_model.setCurrentIndex(-1)
        process_prompt_conf_model.setPlaceholderText("请选择...")
    process_prompt_conf_model.textActivated.connect(lambda text : update_project_process_id(self, process_prompt_conf_model, text))
    process_prompt_conf_layout.addWidget(process_prompt_conf_model)
    ### 流程控制提示词-配置-布局-系统提示词
    process_prompt_btn_system = QPushButton("系统提示词")
    process_prompt_btn_system.setStyleSheet(button_style_sheet())
    process_prompt_btn_system.setFixedSize(80, 30)
    process_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 6, 1))
    process_prompt_conf_layout.addWidget(process_prompt_btn_system)
    ### 流程控制提示词-配置-布局-用户提示词
    process_prompt_btn_user = QPushButton("用户提示词")
    process_prompt_btn_user.setStyleSheet(button_style_sheet())
    process_prompt_btn_user.setFixedSize(80, 30)
    process_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 6, 2))
    process_prompt_conf_layout.addWidget(process_prompt_btn_user)
    
    # 分割线
    frame8 = QFrame()
    frame8.setFrameShape(QFrame.Shape.HLine)
    frame8.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_layout.addWidget(frame8)
    
    # 原文改写内容
    original_polish_title = QLabel("原文章节改写提示词/模型配置")
    original_polish_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    original_polish_title.setStyleSheet(label_style_sheet(font_size=20))
    center_right_layout.addWidget(original_polish_title)

    # 场景分析提示词-配置
    ## 场景分析提示词-配置-布局
    original_scene_prompt_conf_layout = QHBoxLayout()
    original_scene_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(original_scene_prompt_conf_layout)
    ## 场景分析提示词-配置-布局-标题
    original_scene_prompt_conf_title = QLabel("3.场景分析")
    original_scene_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    original_scene_prompt_conf_title.setStyleSheet(label_style_sheet())
    original_scene_prompt_conf_layout.addWidget(original_scene_prompt_conf_title)
    ### 场景分析提示词-配置-布局-模型选择
    original_scene_prompt_conf_model = QComboBox()
    for model in all_model:
        original_scene_prompt_conf_model.addItem(model['name'], model['id'])
    original_scene_prompt_conf_model.setFixedSize(200, 30)
    original_scene_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['scene_model_id']:
        tool3_model_index = original_scene_prompt_conf_model.findData(self.project_info['scene_model_id'])
        original_scene_prompt_conf_model.setCurrentIndex(tool3_model_index)
    else:
        original_scene_prompt_conf_model.setCurrentIndex(-1)
        original_scene_prompt_conf_model.setPlaceholderText("请选择...")
    original_scene_prompt_conf_model.textActivated.connect(lambda text : update_project_scene_id(self, original_scene_prompt_conf_model, text))
    original_scene_prompt_conf_layout.addWidget(original_scene_prompt_conf_model)
    ### 场景分析提示词-配置-布局-系统提示词
    original_scene_prompt_btn_system = QPushButton("系统提示词")
    original_scene_prompt_btn_system.setStyleSheet(button_style_sheet())
    original_scene_prompt_btn_system.setFixedSize(80, 30)
    original_scene_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 3, 1))
    original_scene_prompt_conf_layout.addWidget(original_scene_prompt_btn_system)
    ### 场景分析提示词-配置-布局-用户提示词
    original_scene_prompt_btn_user = QPushButton("用户提示词")
    original_scene_prompt_btn_user.setStyleSheet(button_style_sheet())
    original_scene_prompt_btn_user.setFixedSize(80, 30)
    original_scene_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 3, 2))
    original_scene_prompt_conf_layout.addWidget(original_scene_prompt_btn_user)
    ### 场景分析提示词-配置-布局-场景提示词
    original_scene_prompt_btn_scene = QPushButton("场景提示词")
    original_scene_prompt_btn_scene.setStyleSheet(button_style_sheet())
    original_scene_prompt_btn_scene.setFixedSize(80, 30)
    original_scene_prompt_btn_scene.clicked.connect(lambda : on_prompt_item_clicked(self, 3, 3))
    original_scene_prompt_conf_layout.addWidget(original_scene_prompt_btn_scene)

    # 脉络改写提示词-配置
    ## 脉络改写提示词-配置-布局
    original_framework_prompt_conf_layout = QHBoxLayout()
    original_framework_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(original_framework_prompt_conf_layout)
    ## 脉络改写提示词-配置-布局-标题
    original_framework_prompt_conf_title = QLabel("4.脉络改写提示词/模型配置")
    original_framework_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    original_framework_prompt_conf_title.setStyleSheet(label_style_sheet())
    original_framework_prompt_conf_layout.addWidget(original_framework_prompt_conf_title)
    ### 脉络改写提示词-配置-布局-模型选择
    original_framework_prompt_conf_model = QComboBox()
    for model in all_model:
        original_framework_prompt_conf_model.addItem(model['name'], model['id'])
    original_framework_prompt_conf_model.setFixedSize(200, 30)
    original_framework_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['framework_model_id']:
        tool4_col1_row1_model_index = original_framework_prompt_conf_model.findData(self.project_info['framework_model_id'])
        original_framework_prompt_conf_model.setCurrentIndex(tool4_col1_row1_model_index)
    else:
        original_framework_prompt_conf_model.setCurrentIndex(-1)
        original_framework_prompt_conf_model.setPlaceholderText("请选择...")
    original_framework_prompt_conf_model.textActivated.connect(lambda text : update_project_framework_id(self, original_framework_prompt_conf_model, text))
    original_framework_prompt_conf_layout.addWidget(original_framework_prompt_conf_model)
    ### 脉络改写提示词-配置-布局-系统提示词
    original_framework_prompt_btn_system = QPushButton("系统提示词")
    original_framework_prompt_btn_system.setStyleSheet(button_style_sheet())
    original_framework_prompt_btn_system.setFixedSize(80, 30)
    original_framework_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 4, 1))
    original_framework_prompt_conf_layout.addWidget(original_framework_prompt_btn_system)
    ### 脉络改写提示词-配置-布局-用户提示词
    original_framework_prompt_btn_user = QPushButton("用户提示词")
    original_framework_prompt_btn_user.setStyleSheet(button_style_sheet())
    original_framework_prompt_btn_user.setFixedSize(80, 30)
    original_framework_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 4, 2))
    original_framework_prompt_conf_layout.addWidget(original_framework_prompt_btn_user)

    # 分割线
    frame9 = QFrame()
    frame9.setFrameShape(QFrame.Shape.HLine)
    frame9.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_layout.addWidget(frame9)

    # 番外章节撰写
    extra_write_title = QLabel("番外章节撰写提示词/模型配置")
    extra_write_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    extra_write_title.setStyleSheet(label_style_sheet(font_size=20))
    center_right_layout.addWidget(extra_write_title)

    # 场景分析提示词-配置
    ## 场景分析提示词-配置-布局
    extra_scene_prompt_conf_layout = QHBoxLayout()
    extra_scene_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(extra_scene_prompt_conf_layout)
    ## 场景分析提示词-配置-布局-标题
    extra_scene_prompt_conf_title = QLabel("3.场景分析")
    extra_scene_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    extra_scene_prompt_conf_title.setStyleSheet(label_style_sheet())
    extra_scene_prompt_conf_layout.addWidget(extra_scene_prompt_conf_title)
    ### 场景分析提示词-配置-布局-模型选择
    extra_scene_prompt_conf_model = QComboBox()
    for model in all_model:
        extra_scene_prompt_conf_model.addItem(model['name'], model['id'])
    extra_scene_prompt_conf_model.setFixedSize(200, 30)
    extra_scene_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['scene_model_id']:
        tool3_model_index = extra_scene_prompt_conf_model.findData(self.project_info['scene_model_id'])
        extra_scene_prompt_conf_model.setCurrentIndex(tool3_model_index)
    else:
        extra_scene_prompt_conf_model.setCurrentIndex(-1)
        extra_scene_prompt_conf_model.setPlaceholderText("请选择...")
    extra_scene_prompt_conf_model.textActivated.connect(lambda text : update_project_extra_scene_id(self, extra_scene_prompt_conf_model, text))
    extra_scene_prompt_conf_layout.addWidget(extra_scene_prompt_conf_model)
    ### 场景分析提示词-配置-布局-系统提示词
    extra_scene_prompt_btn_system = QPushButton("系统提示词")
    extra_scene_prompt_btn_system.setStyleSheet(button_style_sheet())
    extra_scene_prompt_btn_system.setFixedSize(80, 30)
    extra_scene_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 7, 1))
    extra_scene_prompt_conf_layout.addWidget(extra_scene_prompt_btn_system)
    ### 场景分析提示词-配置-布局-用户提示词
    extra_scene_prompt_btn_user = QPushButton("用户提示词")
    extra_scene_prompt_btn_user.setStyleSheet(button_style_sheet())
    extra_scene_prompt_btn_user.setFixedSize(80, 30)
    extra_scene_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 7, 2))
    extra_scene_prompt_conf_layout.addWidget(extra_scene_prompt_btn_user)
    ### 场景分析提示词-配置-布局-场景提示词
    extra_scene_prompt_btn_scene = QPushButton("场景提示词")
    extra_scene_prompt_btn_scene.setStyleSheet(button_style_sheet())
    extra_scene_prompt_btn_scene.setFixedSize(80, 30)
    extra_scene_prompt_btn_scene.clicked.connect(lambda : on_prompt_item_clicked(self, 7, 3))
    extra_scene_prompt_conf_layout.addWidget(extra_scene_prompt_btn_scene)

    # 脉络生成提示词-配置
    ## 脉络生成提示词-配置-布局
    extra_framework_prompt_conf_layout = QHBoxLayout()
    extra_framework_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(extra_framework_prompt_conf_layout)
    ## 脉络生成提示词-配置-布局-标题
    extra_framework_prompt_conf_title = QLabel("4.脉络生成提示词/模型配置")
    extra_framework_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    extra_framework_prompt_conf_title.setStyleSheet(label_style_sheet())
    extra_framework_prompt_conf_layout.addWidget(extra_framework_prompt_conf_title)
    ### 脉络生成提示词-配置-布局-模型选择
    extra_framework_prompt_conf_model = QComboBox()
    for model in all_model:
        extra_framework_prompt_conf_model.addItem(model['name'], model['id'])
    extra_framework_prompt_conf_model.setFixedSize(200, 30)
    extra_framework_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['framework_model_id']:
        tool4_col1_row1_model_index = extra_framework_prompt_conf_model.findData(self.project_info['framework_model_id'])
        extra_framework_prompt_conf_model.setCurrentIndex(tool4_col1_row1_model_index)
    else:
        extra_framework_prompt_conf_model.setCurrentIndex(-1)
        extra_framework_prompt_conf_model.setPlaceholderText("请选择...")
    extra_framework_prompt_conf_model.textActivated.connect(lambda text : update_project_extra_framework_id(self, extra_framework_prompt_conf_model, text))
    extra_framework_prompt_conf_layout.addWidget(extra_framework_prompt_conf_model)
    ### 脉络生成提示词-配置-布局-系统提示词
    extra_framework_prompt_btn_system = QPushButton("系统提示词")
    extra_framework_prompt_btn_system.setStyleSheet(button_style_sheet())
    extra_framework_prompt_btn_system.setFixedSize(80, 30)
    extra_framework_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 8, 1))
    extra_framework_prompt_conf_layout.addWidget(extra_framework_prompt_btn_system)
    ### 脉络生成提示词-配置-布局-用户提示词
    extra_framework_prompt_btn_user = QPushButton("用户提示词")
    extra_framework_prompt_btn_user.setStyleSheet(button_style_sheet())
    extra_framework_prompt_btn_user.setFixedSize(80, 30)
    extra_framework_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 8, 2))
    extra_framework_prompt_conf_layout.addWidget(extra_framework_prompt_btn_user)

    # 分割线
    frame10 = QFrame()
    frame10.setFrameShape(QFrame.Shape.HLine)
    frame10.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_layout.addWidget(frame10)
    
    # 结果润色提示词-配置
    ## 结果润色提示词-配置-布局
    polish_prompt_conf_layout = QHBoxLayout()
    polish_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(polish_prompt_conf_layout)
    ## 结果润色提示词-配置-布局-标题
    polish_prompt_conf_title = QLabel("5.结果润色提示词/模型配置")
    polish_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    polish_prompt_conf_title.setStyleSheet(label_style_sheet())
    polish_prompt_conf_layout.addWidget(polish_prompt_conf_title)
    ### 结果润色提示词-配置-布局-模型选择
    polish_prompt_conf_model = QComboBox()
    for model in all_model:
        polish_prompt_conf_model.addItem(model['name'], model['id'])
    polish_prompt_conf_model.setFixedSize(200, 30)
    polish_prompt_conf_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['polish_model_id']:
        tool4_col1_row2_model_index = polish_prompt_conf_model.findData(self.project_info['polish_model_id'])
        polish_prompt_conf_model.setCurrentIndex(tool4_col1_row2_model_index)
    else:
        polish_prompt_conf_model.setCurrentIndex(-1)
        polish_prompt_conf_model.setPlaceholderText("请选择...")
    polish_prompt_conf_model.textActivated.connect(lambda text : update_project_polish_id(self, polish_prompt_conf_model, text))
    polish_prompt_conf_layout.addWidget(polish_prompt_conf_model)
    ### 结果润色提示词-配置-布局-系统提示词
    polish_prompt_btn_system = QPushButton("系统提示词")
    polish_prompt_btn_system.setStyleSheet(button_style_sheet())
    polish_prompt_btn_system.setFixedSize(80, 30)
    polish_prompt_btn_system.clicked.connect(lambda : on_prompt_item_clicked(self, 5, 1))
    polish_prompt_conf_layout.addWidget(polish_prompt_btn_system)
    ### 结果润色提示词-配置-布局-用户提示词
    polish_prompt_btn_user = QPushButton("用户提示词")
    polish_prompt_btn_user.setStyleSheet(button_style_sheet())
    polish_prompt_btn_user.setFixedSize(80, 30)
    polish_prompt_btn_user.clicked.connect(lambda : on_prompt_item_clicked(self, 5, 2))
    polish_prompt_conf_layout.addWidget(polish_prompt_btn_user)

    # 分割线
    frame11 = QFrame()
    frame11.setFrameShape(QFrame.Shape.HLine)
    frame11.setFrameShadow(QFrame.Shadow.Sunken)
    center_right_layout.addWidget(frame11)

    # 关系分析提示词-配置
    ## 关系分析提示词-配置-布局
    relation_prompt_conf_layout = QHBoxLayout()
    relation_prompt_conf_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(relation_prompt_conf_layout)
    ## 关系分析提示词-配置-布局-标题
    relation_prompt_conf_title = QLabel("6.关系分析提示词/模型配置")
    relation_prompt_conf_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    relation_prompt_conf_title.setStyleSheet(label_style_sheet())
    relation_prompt_conf_layout.addWidget(relation_prompt_conf_title)
    ### 关系分析提示词-配置-布局-模型选择
    relation_prompt_btn_model = QComboBox()
    for model in all_model:
        relation_prompt_btn_model.addItem(model['name'], model['id'])
    relation_prompt_btn_model.setFixedSize(200, 30)
    relation_prompt_btn_model.setStyleSheet(line_edit_style_sheet())
    if self.project_info['relation_model_id']:
        tool2_model_index = relation_prompt_btn_model.findData(self.project_info['relation_model_id'])
        relation_prompt_btn_model.setCurrentIndex(tool2_model_index)
    else:
        relation_prompt_btn_model.setCurrentIndex(-1)
        relation_prompt_btn_model.setPlaceholderText("请选择...")
    relation_prompt_btn_model.textActivated.connect(lambda text : update_project_relation_id(self, relation_prompt_btn_model, text))
    relation_prompt_conf_layout.addWidget(relation_prompt_btn_model)
    ### 关系分析提示词-配置-布局-系统提示词
    tool2_system = QPushButton("系统提示词")
    tool2_system.setStyleSheet(button_style_sheet())
    tool2_system.setFixedSize(80, 30)
    tool2_system.clicked.connect(lambda : on_prompt_item_clicked(self, 2, 1))
    relation_prompt_conf_layout.addWidget(tool2_system)
    ### 关系分析提示词-配置-布局-用户提示词
    tool2_user = QPushButton("用户提示词")
    tool2_user.setStyleSheet(button_style_sheet())
    tool2_user.setFixedSize(80, 30)
    tool2_user.clicked.connect(lambda : on_prompt_item_clicked(self, 2, 2))
    relation_prompt_conf_layout.addWidget(tool2_user)

    """弹开"""
    center_right_layout.addStretch()

    """开始按钮"""
    start_stop_layout = QHBoxLayout()
    start_stop_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    center_right_layout.addLayout(start_stop_layout)
    # 弹开
    start_stop_layout.addStretch()
    # 按钮
    self.start_stop_btn = QPushButton()
    self.start_stop_btn.setFixedSize(80, 80)
    self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#00C853'))
    self.start_stop_btn.clicked.connect(lambda : start_stop_clicked(self,
                                                                    role_prompt_conf_model,
                                                                    relation_prompt_btn_model,
                                                                    process_prompt_conf_model,
                                                                    original_scene_prompt_conf_model,
                                                                    original_framework_prompt_conf_model,
                                                                    extra_scene_prompt_conf_model,
                                                                    extra_framework_prompt_conf_model,
                                                                    polish_prompt_conf_model,
                                                                    chapter_before_num,
                                                                    chapter_after_num))
    start_stop_layout.addWidget(self.start_stop_btn)
    """开始按钮控制"""
    if 1 == project_status:
        self.start_stop_btn.setText("开始")
        self.start_stop_btn.setEnabled(True)
    elif 2 == project_status:
        self.start_stop_btn.setText("停止")
        self.start_stop_btn.setEnabled(True)
        self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#FF0000'))
    else:
        self.start_stop_btn.setText("导出")
        self.start_stop_btn.setEnabled(True)

    """可选框初始化"""
    disable_enable_prompt_model_conf(self.project_info['id'],
                                     self.prompt_combo,
                                     role_prompt_conf_model,
                                     relation_prompt_btn_model,
                                     process_prompt_conf_model,
                                     original_scene_prompt_conf_model,
                                     original_framework_prompt_conf_model,
                                     extra_scene_prompt_conf_model,
                                     extra_framework_prompt_conf_model,
                                     polish_prompt_conf_model,
                                     chapter_before_num,
                                     chapter_after_num)

def start_stop_clicked(self,
                       role_prompt_conf_model,
                       relation_prompt_btn_model,
                       process_prompt_conf_model,
                       original_scene_prompt_conf_model,
                       original_framework_prompt_conf_model,
                       extra_scene_prompt_conf_model,
                       extra_framework_prompt_conf_model,
                       polish_prompt_conf_model,
                       chapter_before_num,
                       chapter_after_num):
    # 获取状态
    old_project_status = APP_STATE.get(self.project_info['id'])
    if 1 == old_project_status:
        APP_STATE[self.project_info['id']] = 2
    elif 2 == old_project_status:
        APP_STATE[self.project_info['id']] = 1
    else:
        # 导出文件
        all_num = count_all_chapter_num(self.project_info['id'])
        success_num = count_success_chapter_num(self.project_info['id'])
        if success_num[0] >= all_num[0]:
            project_txt = ""
            all_chapter = query_all_polish_chapter(self.project_info['id'])
            for chapter in all_chapter:
                project_txt += f"\n\n\n\n{str(chapter['title']).strip()}\n\n\n"
                new_content = chapter['new_content']
                if new_content is None or len(chapter['new_content']) < 100:
                    QMessageBox.warning(self, "", f"章节：{chapter['title']} 字数小于100！！！")
                    return False
                for line in str(new_content).splitlines():
                    if len(line.strip()) < 1:
                        continue
                    project_txt += f" {line.strip()}\n\n"
            # 弹出文件夹选择对话框，让用户选择保存位置
            folder_path = QFileDialog.getExistingDirectory(self, "请选择导出文件夹")
            # 检查用户是否选择了文件夹（防止用户直接点击取消）
            if folder_path:
                # 拼接完整的文件路径
                file_path = os.path.join(folder_path, f"{self.project_info['title']}_{self.project_info['author']}.txt")
                # 将数据写入txt文件
                try:
                    with open(file_path, "w", encoding="utf-8") as file:
                        # indent=4 用于格式化输出，ensure_ascii=False 用于正确保存中文
                        json.dump(project_txt, file, indent=4, ensure_ascii=False)
                    QMessageBox.warning(self, "错误", f"✅ 文件导出成功")
                    return True
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"❌ 导出失败")
                    print(f"导出失败: {e}")
                    return False
        else:
            edit_project_status(self.project_info['id'], 2)
            APP_STATE[self.project_info['id']] = 2

    # 处理操作
    if not ProjectStartPolish.start(self):
        APP_STATE[self.project_info['id']] = old_project_status
        return False

    # 获取状态
    if 1 == old_project_status:
        self.start_stop_btn.setText("停止")
        self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#FF0000'))
    elif 2 == old_project_status:
        self.start_stop_btn.setText("开始")
        self.start_stop_btn.setStyleSheet(button_style_sheet(back_color='#00C853'))

    # 更新按钮状态
    disable_enable_prompt_model_conf(self.project_info['id'],
                                     self.prompt_combo,
                                     role_prompt_conf_model,
                                     relation_prompt_btn_model,
                                     process_prompt_conf_model,
                                     original_scene_prompt_conf_model,
                                     original_framework_prompt_conf_model,
                                     extra_scene_prompt_conf_model,
                                     extra_framework_prompt_conf_model,
                                     polish_prompt_conf_model,
                                     chapter_before_num,
                                     chapter_after_num)
    return True



def disable_enable_prompt_model_conf(project_id,
                                     prompt_combo,
                                     role_prompt_conf_model,
                                     relation_prompt_btn_model,
                                     process_prompt_conf_model,
                                     original_scene_prompt_conf_model,
                                     original_framework_prompt_conf_model,
                                     extra_scene_prompt_conf_model,
                                     extra_framework_prompt_conf_model,
                                     polish_prompt_conf_model,
                                     chapter_before_num,
                                     chapter_after_num):
    # 获取状态
    project_status = APP_STATE.get(project_id)
    if 1 == project_status:
        # 可选
        prompt_combo.setEnabled(True)
        role_prompt_conf_model.setEnabled(True)
        relation_prompt_btn_model.setEnabled(True)
        process_prompt_conf_model.setEnabled(True)
        original_scene_prompt_conf_model.setEnabled(True)
        original_framework_prompt_conf_model.setEnabled(True)
        extra_scene_prompt_conf_model.setEnabled(True)
        extra_framework_prompt_conf_model.setEnabled(True)
        polish_prompt_conf_model.setEnabled(True)
        chapter_before_num.setEnabled(True)
        chapter_after_num.setEnabled(True)
    else:
        # 不可选
        prompt_combo.setEnabled(False)
        role_prompt_conf_model.setEnabled(False)
        relation_prompt_btn_model.setEnabled(False)
        process_prompt_conf_model.setEnabled(False)
        original_scene_prompt_conf_model.setEnabled(False)
        original_framework_prompt_conf_model.setEnabled(False)
        extra_scene_prompt_conf_model.setEnabled(False)
        extra_framework_prompt_conf_model.setEnabled(False)
        polish_prompt_conf_model.setEnabled(False)
        chapter_before_num.setEnabled(False)
        chapter_after_num.setEnabled(False)
