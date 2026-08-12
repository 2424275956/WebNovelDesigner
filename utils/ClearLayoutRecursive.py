from PyQt6.QtWidgets import QApplication


def clear_layout(layout):
    """递归清除布局中的所有控件"""
    if layout is None:
        return

    """先清除子布局"""
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item:
            """如果是子布局，递归清除"""
            sub_layout = item.layout()
            if sub_layout:
                clear_layout(sub_layout)

            """如果是控件，直接删除"""
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    """清除当前布局"""
    while layout.count():
        item = layout.takeAt(0)
        if item:
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    sub_layout.setParent(None)
                    sub_layout.deleteLater()

    """立即生效"""
    QApplication.processEvents()