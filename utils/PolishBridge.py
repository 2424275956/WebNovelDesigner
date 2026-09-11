from PySide6.QtCore import QObject, Signal


class PolishBridge(QObject):
    """
    所有信号都携带 project_id，支持多任务并发。
    用 QObject 封装是为了能被 QThread/Executor 安全引用。
    """
    # (项目ID, 进度百分比, 状态文本)
    progress = Signal(int)
    # 流式输出内容(项目ID，输出内容，是否首次输出)
    stream_out = Signal(int, str, bool)
    # 状态文本日志(项目ID，日志内容)
    running_log = Signal(int, str)
