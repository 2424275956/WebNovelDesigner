import sys
import os
from pathlib import Path

def is_frozen() -> bool:
    """判断是否处于 PyInstaller 打包环境"""
    return getattr(sys, 'frozen', False)

def get_app_name() -> str:
    return "WebNovelDesigner"

# ═══════════════════════════════════════
# 1. 静态资源路径（打包后从 .app 内读取，只读）
# ═══════════════════════════════════════
def resource_path(relative_path: str) -> str:
    """
    获取静态资源绝对路径。
    开发环境：项目根目录 / resources/xxx
    打包后：YourApp.app/Contents/MacOS/resources/xxx
    """
    if is_frozen():
        # PyInstaller 打包后，sys._MEIPASS 指向 .app/Contents/MacOS/
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境：以当前文件向上追溯，或直接用项目根目录
        base_path = Path(__file__).parent.parent  # 根据你的目录结构调整

    return str(base_path / relative_path)

# ═══════════════════════════════════════
# 2. 用户数据路径（可写：数据库、日志、缓存）
# ═══════════════════════════════════════
def user_data_path(relative_path: str = "") -> Path:
    """
    获取用户数据目录。
    macOS: ~/Library/Application Support/WebNovelDesigner/
    Windows: %APPDATA%/WebNovelDesigner/
    Linux: ~/.local/share/WebNovelDesigner/
    """
    if sys.platform == 'darwin':
        base = Path.home() / "Library" / "Application Support" / get_app_name()
    elif sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming')) / get_app_name()
    else:
        base = Path.home() / ".local" / "share" / get_app_name()

    if relative_path:
        target = base / relative_path
    else:
        target = base

    # 自动创建目录
    target.parent.mkdir(parents=True, exist_ok=True)
    return target