from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel

from config.GlobalMap import APP_STATE
from pojo.table.Chapter import ChapterPoint
from sqlite.ChapterDB import query_project_chapter_by_id, count_all_chapter_num, count_success_chapter_num, \
    count_fail_chapter_num, count_extra_chapter_num
from resources.style.StyleSheet import label_style_sheet
from utils.StatusDot import StatusDot


def novel_chapter(self, project_id):
    """
    章节列表
    """
    """清空列表"""
    self.chapter_list.clear()

    """查询章节列表"""
    chapter_list = query_project_chapter_by_id(project_id)
    is_current_running = False
    project_status = APP_STATE.get(project_id)
    if 2 == project_status:
        is_current_running = True

    """循环处理"""
    if chapter_list:
        for index, chapter in enumerate(chapter_list):
            # 创建item占位
            chapter_item = QListWidgetItem()
            # 设置高度（宽度由列表控制）
            chapter_item.setSizeHint(QSize(240, 80))  # 高度比卡片稍高
            chapter_item.setData(Qt.ItemDataRole.UserRole, chapter)
            self.chapter_list.addItem(chapter_item)

            # 判断是否当前选择的章节
            if self.chapter_list_choose_id:
                if self.chapter_list_choose_id == chapter['id']:
                    self.chapter_list.setCurrentItem(chapter_item)

            # ===== 关键：创建一个居中容器 =====
            container = QWidget()
            container.setFixedWidth(240)  # 与列表宽度一致

            # 容器内部使用水平布局，让卡片居中
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)  # 上下各10px边距
            container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # 创建卡片
            model_frame = QFrame()
            model_frame.setFixedSize(230, 100)
            model_frame.setStyleSheet("""
                QFrame {
                    background-color: #000000; /* 背景改为纯黑 */
                    color: #FFFFFF;            /* 字体颜色改为白色 */
                    border: 1px solid #333333; /* 边框改为深灰，避免在黑色背景下太突兀 */
                }
                
                QFrame:hover {
                    background-color: #1A1A1A; /* 悬停时变为深灰色，提供视觉反馈 */
                    border: 1px solid #4A90D9; /* 保持悬停时的蓝色高亮边框 */
                }
            """)

            # 卡片内部布局
            frame_layout = QHBoxLayout(model_frame)
            frame_layout.setContentsMargins(10, 5, 10, 5)
            frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

            # 将卡片添加到容器（居中）
            container_layout.addWidget(model_frame)

            # 是否处理中章节
            is_polish_chapter = is_current_running and 2 == chapter['status']
            # 状态提示
            chapter_status = StatusDot("#9E9E9E", size=8)
            chapter_status.setFixedSize(10, 10)
            chapter_status.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            if 2 == chapter['status']:
                chapter_status = StatusDot("white", size=8)
            elif 3 == chapter['status']:
                chapter_status = StatusDot("#00FF00", size=8)
            elif 4 == chapter['status']:
                chapter_status = StatusDot("#FF0000", size=8)
            if is_polish_chapter:
                chapter_status = StatusDot("#FFA500", size=8)
                is_current_running = False
            frame_layout.addWidget(chapter_status)

            # 章节名称
            chapter_layout = QVBoxLayout()
            chapter_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            frame_layout.addLayout(chapter_layout)
            # 章节名称1
            chapter_title = QLabel(chapter['title'])
            chapter_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
            chapter_title.setStyleSheet(label_style_sheet("white", font_size=16))
            chapter_title.setToolTip(chapter['title'])
            chapter_layout.addWidget(chapter_title)
            # 章节字数
            word_count = chapter['old_len']
            new_word_count = chapter['new_len']
            word_label = QLabel(f"{word_count}字")
            if is_polish_chapter:
                is_current_running = False
                if ChapterPoint.ROLE_ANALYSIS.value == chapter['point']:
                    word_label.setText(f"场景角色分析中···")
                elif ChapterPoint.PROCESS_CHOOSES.value == chapter['point']:
                    word_label.setText(f"流程控制判断中···")
                elif ChapterPoint.ORIGINAL_SCENE.value ==  chapter['point']:
                    word_label.setText(f"原文场景匹配中···")
                elif ChapterPoint.ORIGINAL_FRAMEWORK.value == chapter['point']:
                    word_label = QLabel(f"原文脉络改写中···")
                elif ChapterPoint.EXTRA_SCENE.value == chapter['point']:
                    word_label = QLabel(f"番外场景筛选中···")
                elif ChapterPoint.EXTRA_FRAMEWORK.value == chapter['point']:
                    word_label = QLabel(f"番外脉络撰写中···")
                elif ChapterPoint.POLISH_CONTENT.value == chapter['point']:
                    word_label = QLabel(f"脉络内容润色中···")
                elif ChapterPoint.RELATION_ANALYSIS.value == chapter['point']:
                    word_label = QLabel(f"更新角色档案中···")
                else:
                    word_label = QLabel(f"{word_count}字 -> {new_word_count}字")
            else:
                if chapter['point'] in [ChapterPoint.SUCCESS.value, ChapterPoint.RELATION_ANALYSIS.value]:
                    word_label.setText(f"{word_count}字 -> {new_word_count}字")
            word_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            word_label.setStyleSheet(label_style_sheet("white", font_size=12))
            chapter_layout.addWidget(word_label)

            # 将容器设置为列表项
            self.chapter_list.setItemWidget(chapter_item, container)

    return chapter_list


def update_chapter_num(self, project_id):
    """章节统计1"""
    all_chapter = (count_all_chapter_num(project_id))[0]
    self.chapter_count1.setText(f"项目共有 {all_chapter} 章节")
    """章节统计2"""
    success_chapter = (count_success_chapter_num(project_id))[0]
    self.chapter_count2.setText(f"项目已完成 {success_chapter} 章节")
    """章节统计3"""
    fail_chapter = (count_fail_chapter_num(project_id))[0]
    self.chapter_count3.setText(f"项目已失败 {fail_chapter} 章节")
    """章节统计4"""
    wait_chapter = all_chapter - success_chapter
    self.chapter_count4.setText(f"项目待完成 {wait_chapter} 章节")
    """章节统计5"""
    expansion_num = (count_extra_chapter_num(project_id))[0]
    self.chapter_count5.setText(f"项目已新增 {expansion_num} 章节")

def update_chapter_title(self, project_id):
    project_status = APP_STATE.get(project_id)
    color = ""
    size = 16
    status_str = ""
    if 1 == project_status:
        color += "#9E9E9E"
        status_str += "待开始"
    elif 2 == project_status:
        color += "#FFA500"
        status_str += "进行中"
    elif 3 == project_status:
        color += "#00FF00"
        status_str += "已完成"

    if len(color) > 0:
        self.project_status_color.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: {size // 2}px;  /* 半径 = 边长一半，形成正圆 */
                border: 1px solid rgba(0,0,0,0.1);
            }}
        """)
        self.project_status_title.setText(status_str)