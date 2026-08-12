import re
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QTableWidget, QHeaderView, QTableWidgetItem
from sqlite.Sqlite3Utils import insert_project_info, insert_project_chapter
from style.StyleSheet import title_style_sheet, line_edit_style_sheet


def split_list_generator(lst, chunk_size):
    """使用生成器分割（内存友好）"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


class ImportDialog(QDialog):
    """自定义导入对话框（可操作）"""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = Path(file_path).name
        self.setWindowTitle("项目编辑")
        # 窗口大小
        self.resize(1000, 800)
        # 小说名称
        self.title = QLineEdit(f"{self.file_name}")
        # 作者名称
        self.author = QLineEdit("-")
        # 字数
        self.word_count = 0
        # 章节数据
        self.chapters_data = []
        # 章节table
        self.chapter_table = QTableWidget()
        # 章节统计与记数
        self.chapter_review_size = QLabel("暂无章节文本信息")
        # 章节正则
        self.chapter_regex = QLineEdit("^\\s*(序言|序卷|序\\d*|序曲|楔子|前言|后记|尾声|番外|最终章|第([一二三四五六七八九十百千万亿\\d]+)[章回卷节集部])")
        # ui处理
        self.setup_ui()


    # 导入文件窗口
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 文件名称
        # 创建网格布局
        grid_layout = QGridLayout()
        # 标题
        label = QLabel("文件名:")
        label.setStyleSheet(title_style_sheet())
        grid_layout.addWidget(label, 0, 0)
        self.title.setStyleSheet(line_edit_style_sheet())
        grid_layout.addWidget(self.title, 0, 1)

        # 作者
        author_label = QLabel("作 者：")
        author_label.setStyleSheet(title_style_sheet())
        grid_layout.addWidget(author_label, 1, 0)
        self.author.setStyleSheet(line_edit_style_sheet())
        grid_layout.addWidget(self.author, 1, 1)
        layout.addLayout(grid_layout)

        # 文件信息
        info = QLabel(f"路径: {self.file_path}")
        info.setStyleSheet("color: green;")
        layout.addWidget(info)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # 章节拆分
        chapter_layout = QGridLayout()
        # 正则规则
        chapter_repex_label = QLabel("章节正则规则：")
        chapter_repex_label.setStyleSheet(title_style_sheet())
        chapter_layout.addWidget(chapter_repex_label, 0, 0)
        self.chapter_regex.setStyleSheet("""
            QLineEdit {
                font-size: 12px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        chapter_layout.addWidget(self.chapter_regex, 0, 1)
        layout.addLayout(chapter_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # 章节预览
        chapter_review_layout = QGridLayout()
        chapter_review_txt = QLabel("章节预览：")
        chapter_review_txt.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: black;
            }
        """)
        chapter_review_txt.setAlignment(Qt.AlignmentFlag.AlignLeft)
        chapter_review_layout.addWidget(chapter_review_txt, 0, 0)
        # 章节数量
        self.chapter_review_size.setStyleSheet("font-size: 16px; font-weight: bold; color: #87CEEB;")
        chapter_review_layout.addWidget(self.chapter_review_size, 0, 1, Qt.AlignmentFlag.AlignHCenter)
        # 预览按钮
        chapter_review_button = QPushButton("▶️预览")
        chapter_review_button.setFixedSize(100, 30)
        chapter_review_button.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        chapter_review_button.clicked.connect(self.review_chapter)
        chapter_review_layout.addWidget(chapter_review_button, 0, 2, alignment=Qt.AlignmentFlag.AlignRight)

        # 拉伸控制
        layout.addLayout(chapter_review_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(line)

        # 章节预览
        self.chapter_table.setColumnCount(3)
        self.chapter_table.setHorizontalHeaderLabels(["#", "章节标题", "行号"])

        # 第0列：固定宽度
        header = self.chapter_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.chapter_table.setColumnWidth(0, 120)

        # 第1列：拉伸占满剩余空间
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # 第2列：固定宽度
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.chapter_table.setColumnWidth(2, 120)

        # 禁用水平滚动条
        self.chapter_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.chapter_table)

        # 底部按钮
        button_style = """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """

        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(button_style)
        close_btn.clicked.connect(self.close)
        close_btn.setFixedSize(200, 30)
        button_layout.addWidget(close_btn, Qt.AlignmentFlag.AlignLeft)

        # 添加弹性空间。
        button_layout.addStretch(5)

        process_btn = QPushButton("Next")
        process_btn.setStyleSheet(button_style)
        process_btn.clicked.connect(self.process_file)
        process_btn.setFixedSize(200, 30)
        button_layout.addWidget(process_btn, Qt.AlignmentFlag.AlignRight)
        layout.addLayout(button_layout)

    # 预览章节
    def review_chapter(self):
        # 读取文件内容
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # 正则对象
                regex_obj = re.compile(self.chapter_regex.text())
                # 行数
                row = 1
                # 字数
                for line_num, line in enumerate(f, start=1):
                    if regex_obj.search(line):
                        self.chapters_data.append({"title":line.strip(),"row":row})

                    row = row + 1
                    self.word_count = self.word_count + len(line.strip())

                # 更新table
                self.update_chapter_table()

                # 更新章节数与字数
                self.chapter_review_size.setText(f"识别到{len(self.chapters_data)}章节、{round(self.word_count / 10000, 1)}万文字")

        except:
            self.chapter_table.setText("预览章节失败")

    def update_chapter_table(self):
        # 设置table行数
        self.chapter_table.setRowCount(len(self.chapters_data))

        # 循环设置内容
        for i, chapter in enumerate(self.chapters_data):
            # 序号
            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chapter_table.setItem(i, 0, num_item)

            # 章节标题
            title_item = QTableWidgetItem(chapter['title'])
            title_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.chapter_table.setItem(i, 1, title_item)

            # 行号
            line_item = QTableWidgetItem(str(chapter['row']))
            line_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.chapter_table.setItem(i, 2, line_item)

    # 保存文本信息
    def process_file(self):
        chapter_context_data = []
        word_count = 0
        # 章节分割
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # 正则对象
                regex_obj = re.compile(self.chapter_regex.text())
                # 章节内容
                context = ""
                # 排序
                sort = 1
                # 章节名称
                chapter_title = ""
                # 字数
                for line_num, line in enumerate(f, start=1):
                    if regex_obj.search(line):
                        # 当前存在内容
                        if len(context) > 0:
                            # 清理结尾 \\n
                            context = context[:-3]
                            # 是正文章节
                            if len(chapter_title) > 0:
                                chapter_context_data.append({"title": chapter_title,
                                                             "old_len": len(context),
                                                             "old_content": context,
                                                             "sort": sort})
                            # 开头序言
                            else:
                                chapter_context_data.append({"title": "序言",
                                                             "old_len": len(context),
                                                             "old_content": context,
                                                             "sort": sort})
                        # 记录章节名称
                        chapter_title = line.strip()
                        # 排序累加
                        sort = sort + 1
                        # 正文内容置空
                        context = ""
                    else:
                        line = line.strip()
                        if len(line) > 0:
                            context = context + line + "\\n"

                    # 总字数
                    word_count = word_count + len(line.strip())

                # 循环完后还有最后一个章节内容需要保存
                chapter_context_data.append({"title": chapter_title,
                                             "old_len": len(context),
                                             "old_content": context,
                                             "sort": sort})
        except:
            self.chapter_table.setText("分析章节失败")

        # 项目创建
        project_id = insert_project_info({"title": self.title.text(),
                             "author": self.author.text(),
                             "chapter_num": len(chapter_context_data),
                             "word_count": word_count})

        # 章节信息创建
        for chunk in split_list_generator(chapter_context_data, 10):
            insert_project_chapter(project_id, chunk)

        self.accept()

