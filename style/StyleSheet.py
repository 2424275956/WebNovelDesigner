
"""按钮样式"""
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

def list_widget_style_sheet():
    return """
            /* 1. 【关键】去除 QListWidget 自身的边框和内边距 */
            /* 如果不加这个，控件外围会有一圈默认的灰/黑线，导致红线无法贴合 */
            QListWidget {
                border: none; 
                background-color: #2B2B2B; /* 与你的黑色背景保持一致 */
                outline: 0px;              /* 去除点击时的外层焦点框 */
                padding: 0px;              /* 确保内容填满容器 */
            }
        
            /* 2. 默认状态：列表项样式 */
            QListWidget::item {
                padding: 8px 10px;         /* 增加上下内边距，让文字不拥挤 */
                border-bottom: 1px solid #444; /* 分隔线颜色调暗，适应深色背景 */
                color: #FFFFFF;            /* 默认文字颜色 */
                border: none;              /* 确保项本身没有边框 */
            }
        
            /* 3. 鼠标悬停状态（可选） */
            QListWidget::item:hover {
                background-color: #3A3A3A; /* 悬停时稍微变亮 */
            }
        
            /* 4. 【关键】选中且获得焦点时（艳红背景） */
            /* active 表示窗口当前是激活状态 */
            QListWidget::item:selected:active {
                background-color: #FF0000; 
                color: white;
                border: none;              /* 再次强调去除边框 */
            }
        
            /* 5. 【关键】选中但失去焦点时（深红色背景） */
            /* !active 表示用户点击了窗口外部，窗口变灰时的状态 */
            QListWidget::item:selected:!active {
                background-color: #CC0000; 
                color: white;
                border: none;
            }
        
            /* 6. 【关键】去除选中项周围的虚线框 */
            /* 这行代码对于深色 UI 非常重要，否则会有个难看的点状框 */
            QListWidget::item:focus {
                outline: 0px;
                border: 0px;
            }
        """