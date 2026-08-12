from PyQt6.QtWidgets import QApplication


def clear_layout(layout):
    """递归清除布局中的所有控件"""
    if layout is None:
        return

    """先清除子布局"""
    while True:
        item = layout.takeAt(0)

        if item is None:
            break

        """如果是子布局，递归清除"""
        sub_layout = item.layout()
        if sub_layout:
            clear_layout(sub_layout)
            """销毁子布局本身"""
            sub_layout.deleteLater()
        elif item.widget():
            widget = item.widget()
            """解除父子关系，防止隐藏残留"""
            widget.setParent(None)
            """安排异步销毁，释放内存"""
            widget.deleteLater()
        else:
            del item

    """立即生效"""
    QApplication.processEvents()