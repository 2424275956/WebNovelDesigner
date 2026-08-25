
"""定义全局http客户端"""
import httpx

GLOBAL_HTTP_CLIENT: dict = {}

"""关闭客户端数组"""
def close_all_clients():
    for name, client in GLOBAL_HTTP_CLIENT.items():
        if hasattr(client, 'close'):
            try:
                client.close()
            except Exception as e:
                print(f"Error closing {name}: {e}")
    GLOBAL_HTTP_CLIENT.clear()

"""获取或创建Http"""
def get_or_create_http_client(project_id):
    key = f"project_{project_id}"
    if key not in GLOBAL_HTTP_CLIENT:
        GLOBAL_HTTP_CLIENT[key] = httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0)
        )
    return GLOBAL_HTTP_CLIENT[key]

# 取消时关闭所有连接（会抛出异常，子线程捕获后退出）
def emergency_stop(project_id):
    key = f"project_{project_id}"
    if key not in GLOBAL_HTTP_CLIENT:
        return
    http = GLOBAL_HTTP_CLIENT[key]
    if http:
        http.close()
        del GLOBAL_HTTP_CLIENT[key]