from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QListWidgetItem, QWidget, QHBoxLayout, QFrame, QVBoxLayout, QLabel

from sqlite.Sqlite3Utils import query_project_chapter_by_id
from style.StyleSheet import label_style_sheet
from utils.StatusDot import StatusDot


def novel_chapter(self, project_id):
    """
    章节列表
    """
    """清空列表"""
    self.chapter_list.clear()

    """查询章节列表"""
    chapter_list = query_project_chapter_by_id(project_id)

    """循环处理"""
    if chapter_list:
        for index, chapter in enumerate(chapter_list):
            # 创建item占位
            chapter_item = QListWidgetItem()
            # 设置高度（宽度由列表控制）
            chapter_item.setSizeHint(QSize(240, 80))  # 高度比卡片稍高
            chapter_item.setData(Qt.ItemDataRole.UserRole, chapter)
            self.chapter_list.addItem(chapter_item)

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
            if 6 == chapter['point']:
                word_label = QLabel(f"{word_count}字 -> {new_word_count}字")
            else:
                word_label = QLabel(f"{word_count}字")
            word_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            word_label.setStyleSheet(label_style_sheet("white", font_size=12))
            chapter_layout.addWidget(word_label)

            # 将容器设置为列表项
            self.chapter_list.setItemWidget(chapter_item, container)

    return chapter_list