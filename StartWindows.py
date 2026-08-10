import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QApplication, QLabel, \
    QButtonGroup

from windows.model.ModelWindows import model_open_windows
from windows.project.ProjectWindows import project_open_windows, review_page


def create_button(text, icon_path):
    """创建按钮"""
    """创建按钮"""
    btn = QPushButton()
    """设置悬浮Tip"""
    btn.setToolTip(text)
    """设置为可选中状态"""
    btn.setCheckable(True)
    """尝试加载图标，如果失败则不显示图标以免报错"""
    try:
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(30, 30))
    except:
        pass
    """悬浮图标时指针变化"""
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    """按钮样式：选中时保持状态"""
    btn.setCheckable(True)
    """按钮样式"""
    btn.setStyleSheet("""
        QPushButton {
            border: none;
            background-color: transparent;
            font-size: 14px;
            color: #666;
            font-weight: bold;
            padding: 10px;
        }
        QPushButton:checked {
            color: #3498db;
            background-color: #f0f8ff;
            border-top: 3px solid #3498db;
        }
        QPushButton:hover {
            background-color: #f9f9f9;
            border-radius: 10px;
        }
    """)
    return btn


class MainWindows(QMainWindow):
    def __init__(self):
        super().__init__()
        """标题名称"""
        self.setWindowTitle("WebNovel大师")
        """宽度1080，高度800"""
        self.resize(1080, 800)

        """窗口渲染"""
        """创建主容器"""
        self.central_widget = QWidget()
        """水平布局"""
        self.main_layout = QHBoxLayout(self.central_widget)

        """创建左侧导航栏容器"""
        self.left_widget = QFrame()
        """固定导航栏宽度"""
        self.left_widget.setFixedWidth(60)
        """导航栏样式"""
        self.left_widget.setStyleSheet("background-color: #f0f0f0; border-right: 1px solid #ccc;")

        """设置导航栏图片水平排列"""
        self.left_layout = QVBoxLayout(self.left_widget)

        """创建左侧按钮"""
        """项目管理按钮"""
        self.project_btn = create_button("项目管理", "pics/项目管理.jpeg")
        self.left_layout.addWidget(self.project_btn)

        """模型管理按钮"""
        self.chat_btn = create_button("模型管理", "pics/AI图标.png")
        self.left_layout.addWidget(self.chat_btn)

        """提示词管理按钮"""
        self.prompt_btn = create_button("提示词管理", "pics/提示词图标.png")
        self.left_layout.addWidget(self.prompt_btn)

        """把按钮顶上去"""
        self.left_layout.addStretch()

        """创建按钮逻辑分组"""
        self.icon_group = QButtonGroup(self)
        self.icon_group.addButton(self.project_btn, 0)
        self.icon_group.addButton(self.chat_btn, 1)
        self.icon_group.addButton(self.prompt_btn, 2)


        """创建右侧页面"""
        """项目管理页面"""
        self.right_project_windows = project_open_windows(self)
        """模型管理页面"""
        self.right_model_windows = model_open_windows(self)
        """提示词管理页面"""
        self.right_prompt_windows = QLabel("这是 页面3 的内容")



        """绑定页面与按钮（必须两者创建后）"""
        self.project_btn.clicked.connect(self.project_to_confirm)
        self.chat_btn.clicked.connect(self.chat_to_confirm)
        self.prompt_btn.clicked.connect(self.prompt_to_confirm)

        """导航栏放入布局"""
        self.main_layout.addWidget(self.left_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        """项目管理页面放入布局"""
        self.main_layout.addWidget(self.right_project_windows)
        """模型管理页面放入布局"""
        self.main_layout.addWidget(self.right_model_windows)
        """提示词管理页面放入布局"""
        self.main_layout.addWidget(self.right_prompt_windows)

        """设置默认展示页面"""
        self.right_project_windows.show()
        self.right_model_windows.hide()
        self.right_prompt_windows.hide()

        """设置布局完成"""
        self.setCentralWidget(self.central_widget)

    def project_to_confirm(self):
        """项目管理按钮"""
        """按钮状态管理"""
        self.button_group_parse(0)
        """内容展示"""
        review_page(self)
        self.right_project_windows.show()
        self.right_prompt_windows.hide()
        self.right_model_windows.hide()

    def prompt_to_confirm(self):
        """提示词管理按钮"""
        """按钮状态管理"""
        self.button_group_parse(2)
        """内容展示"""
        self.right_project_windows.hide()
        self.right_prompt_windows.show()
        self.right_model_windows.hide()

    def chat_to_confirm(self):
        """模型管理按钮"""
        """按钮状态管理"""
        self.button_group_parse(1)
        """内容展示"""
        self.right_project_windows.hide()
        self.right_prompt_windows.hide()
        self.right_model_windows.show()

    def button_group_parse(self, button_id):
        """遍历组内所有按钮，取消非当前按钮的选中状态"""
        for btn in self.icon_group.buttons():
            if self.icon_group.id(btn) != button_id:
                btn.setChecked(False)

        # 设置当前按钮为选中状态
        current_btn = self.icon_group.button(button_id)
        current_btn.setChecked(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #ffffff;
            color: #333333;
        }
        QLineEdit, QTextEdit {
            border: 1px solid #cccccc;
            padding: 4px;
        }
    """)
    window = MainWindows()
    window.show()
    sys.exit(app.exec())