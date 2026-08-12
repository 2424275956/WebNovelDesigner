
"""按钮样式"""
from shutil import which


def button_style_sheet(color='white', back_color='#3498db'):
    return f"""
                QPushButton {{
                    background-color: {back_color}; 
                    color: {color}; 
                    border-radius: 6px; 
                    border: none; 
                    font-weight: bold;
                }}
                QPushButton:hover {{ 
                    background-color: #2980b9; 
                }}
            """

"""标题样式"""
def title_style_sheet(color='black', font_size = 16):
    return f"font-size: {font_size}px; font-weight: bold; color: {color};"

"""QLabel样式"""
def label_style_sheet(color="black", font_size=16):
    return f"""
        QLabel {{
            padding: 2px;              /* 增加内边距让效果更明显 */
            font-size: {font_size}px;
            color: {color};
        }}
        QLabel:hover {{
            border: none;               /* 悬停状态：去掉边框 */
        }}
    """

"""输入框样式"""
def line_edit_style_sheet(font_size= 18, color = '#2c3e50', back_color='white'):
    return f"""
                QLineEdit {{
                        font-size: {font_size}px;
                        font-weight: bold;
                        color: {color};
                        border: 2px solid #bdc3c7;
                        border-radius: 5px;
                        padding: 5px;
                        background-color: {back_color};
                    }}
                QLineEdit:focus {{
                    border: 2px solid #3498db;
                }}
                QPlainTextEdit {{
                    color: {color};                /* 文字颜色 */
                    background-color: {back_color};     /* 深色背景，避免纯黑刺眼 */
                    border: 1px solid #444;        /* 边框可选 */
                    padding: 8px;                  /* 内边距提升可读性 */
                    font-size: 14px;               /* 字体大小 */
                }}
                QPlainTextEdit:focus {{
                    border-color: #007acc;         /* 聚焦时边框高亮 */
                }}
            """