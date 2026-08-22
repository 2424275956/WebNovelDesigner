from sqlite.SqliteDB import SqliteDB

# 删除模型配置
def remove_model_conf(conf_id):
    SqliteDB.execute("DELETE FROM model_info WHERE id = ?", (conf_id,))


# 查询全部模型配置信息
def query_all_model():
    return SqliteDB.query_execute_batch("SELECT * FROM model_info")

# 根据ID获取模型配置信息
def query_model_by_id(model_id):
    return SqliteDB.query_execute("SELECT * FROM model_info WHERE id = ?", (model_id,))

# 保存模型配置信息
def insert_model_conf(req_json):
    SqliteDB.execute("INSERT INTO model_info (name, type, api_key, url, model_id, temperature, top_p, max_token, time_out) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (req_json['name'], req_json['type'], req_json['api_key'], req_json['url'], req_json['model_id'],
                            req_json['temperature'] if req_json['temperature'] is not None else 0.7,
                            req_json['top_p'] if req_json['top_p'] is not None else 0.9,
                            req_json['max_token'] if req_json['max_token'] is not None else 32768,
                            req_json['time_out'] if req_json['time_out'] is not None else 300))

# 更新模型配置信息
def modify_model_conf(req_json):
    SqliteDB.execute("UPDATE model_info SET name = ?, type = ?, api_key = ?, url = ?, model_id = ?, temperature = ?, top_p = ?, max_token = ?, time_out = ? WHERE id = ?",
                           (req_json['name'], req_json['type'], req_json['api_key'], req_json['url'], req_json['model_id'],
                            req_json['temperature'] if req_json['temperature'] is not None else 0.7,
                            req_json['top_p'] if req_json['top_p'] is not None else 0.9,
                            req_json['max_token'] if req_json['max_token'] is not None else 32768,
                            req_json['time_out'] if req_json['time_out'] is not None else 300,
                            req_json['id']))