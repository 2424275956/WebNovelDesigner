from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QLineEdit
from utils import CustomDoubleValidator

class DoubleLineEdit(QLineEdit):
    """增强的 QLineEdit，自动修正范围"""

    def __init__(self, edit_min, edit_max, decimals=1, parent=None):
        super().__init__(parent)

        self.edit_min = edit_min
        self.edit_max = edit_max

        # 设置自定义验证器
        self.validator = CustomDoubleValidator.CustomDoubleValidator(edit_min, edit_max, decimals, self)
        self.setValidator(self.validator)

        # 设置占位文本
        self.setPlaceholderText(f"请输入 {edit_min} ~ {edit_max}")

        # 连接信号
        self.editingFinished.connect(self.fix_value)  # 编辑完成时修正
        self.textChanged.connect(self.on_text_changed)  # 实时处理

    def on_text_changed(self, text):
        """实时更新状态显示"""
        if not text:
            self.setStyleSheet("QLineEdit { border: 1px solid gray; }")
            return

        # 检查当前输入是否有效
        state = self.validator.validate(text, 0)[0]
        if state == QValidator.State.Acceptable:
            self.setStyleSheet("QLineEdit { border: 2px solid green; }")
        elif state == QValidator.State.Intermediate:
            self.setStyleSheet("QLineEdit { border: 2px solid orange; }")
        else:
            self.setStyleSheet("QLineEdit { border: 2px solid red; }")

    def fix_value(self):
        """当编辑完成时，自动修正数值到合法范围"""
        text = self.text()
        if not text or text == "." or text == "0.":
            # 如果为空或不完整，设置为最小值
            self.setText(str(min))
            return

        try:
            value = float(text)
            # 修正范围
            if value < self.edit_min:
                self.setText(str(self.edit_min))
            elif value > self.edit_max:
                self.setText(str(self.edit_max))
            # 否则保持原值
        except ValueError:
            # 如果转换失败，设置为最小值
            self.setText(str(self.edit_min))

    def focusOutEvent(self, event):
        """重写焦点离开事件，确保修正生效（额外保险）"""
        # 在失去焦点时也调用修正
        self.fix_value()
        # 调用父类方法继续处理事件
        super().focusOutEvent(event)

    def get_value(self, edit_min, edit_max):
        """获取当前数值，如果无效则返回 None"""
        text = self.text()
        if not text:
            return None
        try:
            value = float(text)
            # 确保在有效范围内
            return max(edit_min, min(edit_max, value))
        except ValueError:
            return None