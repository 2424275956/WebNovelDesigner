import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QFrame, \
    QFileDialog, QDialog
from . import ImportNovel
from . import RemoveNovel
from . import ClickableFrame


"""添加项目根目录到路径"""
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from sqlite.Sqlite3Utils import query_all_project

def project_open_windows(self):
    """项目窗口"""
    """中心部件"""
    central_widget = QWidget()

    """垂直布局"""
    self.project_win_layout = QVBoxLayout(central_widget)
    self.project_win_layout.setContentsMargins(20, 20, 20, 20)
    self.project_win_layout.setSpacing(10)



    review_page(self)

    return central_widget

def review_page(self):
    """存在数据则销毁"""
    if self.project_win_layout is not None:
        while self.project_win_layout.count():
            item = self.project_win_layout.takeAt(0)
            widget = item.widget()
            if widget:
                """安全销毁旧控件"""
                widget.deleteLater()

    """获取数据来判断下部分界面渲染"""
    projects = query_all_project()
    """顶部标题栏"""
    header_layout = QHBoxLayout()
    """我的项目文案"""
    title_label = QLabel("📚 我的项目")
    title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
    header_layout.addWidget(title_label)
    """弹开到两边"""
    header_layout.addStretch()

    """导入按钮放在右上角"""
    import_btn = QPushButton("+ 导入文件")
    """导入按钮大小"""
    import_btn.setFixedSize(120, 40)
    """导入按钮样式"""
    import_btn.setStyleSheet("""
                QPushButton { 
                    background-color: #3498db; 
                    color: white; 
                    border-radius: 6px; 
                    border: none; 
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background-color: #2980b9; 
                }
            """)
    """导入按钮触发函数"""
    import_btn.clicked.connect(lambda: import_file(self))
    """加入顶部状态栏"""
    header_layout.addWidget(import_btn)
    """顶部状态栏加入主分区"""
    self.project_win_layout.addLayout(header_layout)

    """数据不为空"""
    if not projects:
        # 如果没有项目，显示空状态
        empty_label = QLabel("暂无项目，请导入文件或拖拽文件到此处")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        empty_label.setStyleSheet("font-size: 18px; color: #888; margin-top: 100px;")
        self.project_win_layout.addWidget(empty_label)
    else:
        # 如果有项目，显示网格列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # 简单的网格填充逻辑
        for i, proj in enumerate(projects):
            card = create_project_card(self, proj['title'], proj['id'])
            # 每行放3个 (列, 行)
            grid_layout.addWidget(card, i // 3, i % 3)

        scroll_area.setWidget(grid_widget)
        self.project_win_layout.addWidget(scroll_area)

def import_file(self):
    """使用文件对话框选择文件"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "选择文件",
        "",
        "文本文件 (*.txt)"
    )
    if file_path:
        # 弹出可操作窗口
        dialog = ImportNovel.ImportDialog(file_path, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 对话框成功保存并关闭同时刷新页面
            review_page(self)

def create_project_card(self, name, project_id):
    card = ClickableFrame.ClickableFrame()
    card.setObjectName("projectCard")
    card.setFixedSize(180, 260)
    card.setStyleSheet("QFrame#projectCard { background-color: #ffffff; border-radius: 12px; border: 1px solid #f0f0f0; }")
    # 连接自定义的点击信号
    card.clicked.connect(lambda: open_project(self, project_id))


    # 1. 将 QVBoxLayout 替换为 QGridLayout
    grid_layout = QGridLayout(card)
    grid_layout.setContentsMargins(0, 0, 0, 0)
    grid_layout.setSpacing(0)

    # --- 上半部分：封面/图标区 ---
    cover_area = QLabel()
    cover_area.setObjectName("coverLabel")
    cover_area.setFixedHeight(180)
    cover_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
    # 加载图标
    pixmap = QPixmap("pics/书籍图标.png")
    # 如果图标很大，可以限制它的大小，防止撑破布局
    pixmap = pixmap.scaled(80, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    cover_area.setPixmap(pixmap)
    cover_area.setStyleSheet("""
        QLabel#coverLabel {
            background-color: #f8f9fa;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            border-bottom: 1px solid #eeeeee;
        }
    """)
    cover_area.setContentsMargins(0, 20, 0, 20)

    # --- 下半部分：标题区 ---
    title_label = QLabel(name)
    title_label.setObjectName("titleLabel")
    title_label.setWordWrap(True)
    title_label.setStyleSheet("""
        QLabel#titleLabel {
            background-color: transparent;
            color: #333333;
            font-size: 14px;
            font-weight: 500; 
            padding: 10px 12px;
            qproperty-alignment: AlignTop | AlignHCenter; 
        }
    """)

    # --- 创建右上角删除按钮 ---
    close_btn = QPushButton("×", card)
    close_btn.setObjectName("closeBtn")
    close_btn.setFixedSize(24, 24)
    close_btn.setStyleSheet("""
        QPushButton#closeBtn {
            background-color: rgba(0, 0, 0, 0.4);
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            border: none;
        }
        QPushButton#closeBtn:hover {
            background-color: #ff4d4f;
        }
    """)
    close_btn.clicked.connect(lambda: remove_novel(self, project_id))

    # 2. 关键修改：用 addWidget 精确指定行列
    # 参数 1：控件, 行号, 列号, 行跨度, 列跨度, 对齐方式
    # 按钮放在 0行, 1列 (因为 grid 是 2 列的，1列代表最右边)
    grid_layout.addWidget(close_btn, 0, 1)
    # 封面图占据 1行, 跨 0~1 两列
    grid_layout.addWidget(cover_area, 1, 0, 1, 2)
    # 标题占据 2行, 跨 0~1 两列
    grid_layout.addWidget(title_label, 2, 0, 1, 2)

    return card

def remove_novel(self, project_id):
    """删除项目触发"""
    dialog = RemoveNovel.RemoveNovel(project_id)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # 对话框成功保存并关闭同时刷新页面
        review_page(self)

def open_project(self, project_id):
    123