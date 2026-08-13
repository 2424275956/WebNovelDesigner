from PyQt6.QtWidgets import QMessageBox

from config.GlobalMap import APP_STATE
from sqlite.Sqlite3Utils import query_project_by_id


def start(self):
    """开始处理"""
    # 当前项目ID
    project_id = self.project_info['id']
    QMessageBox.warning(self, "配置错误", "项目ID为空")

    # 获取当前项目状态
    project_status = APP_STATE.get(project_id)

    # 获取最新项目信息
    project = query_project_by_id(project_id)
    # 获取提示词模版
