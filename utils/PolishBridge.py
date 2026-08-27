from PySide6.QtCore import QObject, Signal


class PolishBridge(QObject):
    """
    所有信号都携带 project_id，支持多任务并发。
    用 QObject 封装是为了能被 QThread/Executor 安全引用。
    """
    # (项目ID, 进度百分比, 状态文本)
    progress = Signal(int)
