
"""按钮样式"""
def button_style_sheet():
    return """
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
            """

"""标题样式"""
def title_style_sheet():
    return "font-size: 16px; font-weight: bold; color: black;"

"""输入框样式"""
def line_edit_style_sheet():
    return """
                QLineEdit {
                    font-size: 18px;
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
        """