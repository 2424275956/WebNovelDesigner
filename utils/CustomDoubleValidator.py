from PyQt6.QtGui import QDoubleValidator, QValidator


class CustomDoubleValidator(QDoubleValidator):
    """自定义双精度验证器"""

    def __init__(self, min_val, max_val, decimals=1, parent=None):
        super().__init__(min_val, max_val, decimals, parent)
        self.edit_min = min_val
        self.edit_max = max_val
        self.setNotation(QDoubleValidator.Notation.StandardNotation)

    def validate(self, input_str, pos):
        """重写验证方法，加入空值和边界检查"""
        # 允许空输入（方便删除所有内容后重新输入）
        if input_str == "":
            return QValidator.State.Intermediate, input_str, pos

        # 允许单独的"0"（输入中状态）
        if input_str == "0":
            return QValidator.State.Intermediate, input_str, pos

        # 允许"0."（输入中状态，方便输入小数）
        if input_str == "0.":
            return QValidator.State.Intermediate, input_str, pos

        # 使用父类的验证逻辑
        state, _, _ = super().validate(input_str, pos)

        # 如果验证通过，还需要检查是否在范围内
        if state == QValidator.State.Acceptable:
            try:
                value = float(input_str)
                # 检查是否在范围内
                if self.edit_min <= value <= self.edit_max:
                    return QValidator.State.Acceptable, input_str, pos
                else:
                    # 在范围外但格式正确，标记为中间状态
                    return QValidator.State.Intermediate, input_str, pos
            except ValueError:
                return QValidator.State.Invalid, input_str, pos

        return state, input_str, pos