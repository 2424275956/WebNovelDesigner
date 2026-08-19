import threading
import time

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
from openai import OpenAI

from config.GlobalMap import APP_STATE, APP_FUTURE, APP_STOP_EVENT
from sqlite.Sqlite3Utils import query_project_by_id, query_prompt_info_by_id, query_prompt_template, query_model_by_id
from windows.polish.NovelPolish import polish
from windows.project.NovelChapterList import novel_chapter, update_chapter_num


def prompt_rules_parse(self, transmit, transmit_key, prompt_id, point_type, prompt_type, title):
    """提示词规则处理"""
    prompt_list = query_prompt_template(prompt_id, point_type, prompt_type)
    if prompt_list is None or len(prompt_list) < 1:
        QMessageBox.warning(self, "", f"项目{title}提示词配置信息为空")
        return False
    prompt = prompt_list[0]
    if prompt is None or len(prompt['context']) < 1:
        QMessageBox.warning(self, "", f"项目{title}提示词配置规则为空")
        return False
    transmit[transmit_key] = prompt['context']
    return True

def model_connection_check(self, model_id, title, model_map):
    """模型校验处理"""
    # 模型ID判断
    if model_id is None:
        QMessageBox.warning(self, "", f"项目{title}模型ID为空")
        return False
    # 判断模型map中是否存在, 存在直接返回
    model = model_map.get(model_id)
    if model:
        return True
    # 校验信息
    model = query_model_by_id(model_id)
    if model is None:
        QMessageBox.warning(self, "", f"项目{title}模型信息为空")
        return False
    if len(model['url']) < 1:
        QMessageBox.warning(self, "", f"项目{title}模型BaseURL地址为空")
        return False
    if len(model['model_id']) < 1:
        QMessageBox.warning(self, "", f"项目{title}模型ID为空")
        return False
    if model['type'] is None:
        QMessageBox.warning(self, "", f"项目{title}模型类型为空")
        return False
    if 1 == model['type'] or 3 == model['type']:
        if len(model['api_key']) < 1:
            QMessageBox.warning(self, "", f"项目{title}模型ApiKey为空")
            return False
    if model['temperature'] is None:
        QMessageBox.warning(self, "", f"项目{title}模型温度(Temperature)为空")
        return False
    if model['temperature'] < 0 or model['temperature'] > 2.0:
        QMessageBox.warning(self, "", f"项目{title}模型温度(Temperature)范围应0.1~2.0")
        return False
    if model['top_p'] is None:
        QMessageBox.warning(self, "", f"项目{title}模型Top-P为空")
        return False
    if model['top_p'] <= 0 or model['top_p']  > 1.0:
        QMessageBox.warning(self, "", f"项目{title}模型Top-P范围应0.01~1.00")
        return False
    if model['max_token'] is None:
        QMessageBox.warning(self, "", f"项目{title}模型最大Token(Max Tokens)为空")
        return False
    if model['time_out'] is None:
        QMessageBox.warning(self, "", f"项目{title}模型超时时间为空")
        return False
    model_map[model_id] = model
    # 测试连接通畅度
    try:
        client = OpenAI(
            base_url = model['url'],
            api_key= model['api_key']
        )
        # 发送一个极短的请求来测试连通性
        models = client.models.list()
        # next是防止提前返回
        next(iter(models))
        return True
    except Exception as e:
        print(e)
        QMessageBox.warning(self, "错误", f"项目{title}模型连接失败")
        return False

def start(self):
    """开始处理"""
    transmit = {'project_id': self.project_info['id']}
    # 当前项目ID
    if transmit['project_id'] is None:
        QMessageBox.warning(self, "配置错误", "项目ID为空")
        return False

    # 获取当前项目状态
    project_status = APP_STATE.get(transmit['project_id'])
    if project_status is None:
        QMessageBox.warning(self, "", "当前项目状态为空")
        return False

    # 待开始状态 或 完成状态直接退出
    if 1 == project_status or 3 == project_status:
        # 停止线程
        stop_event = APP_STOP_EVENT.get(transmit['project_id'])
        if stop_event:
            stop_event.set()
        return True

    # 获取最新项目信息
    transmit['project_info'] = query_project_by_id(transmit['project_id'])
    if transmit['project_info'] is None:
        QMessageBox.warning(self, "", "项目信息为空")
        return False

    """提示词模版信息"""
    # 获取提示词模版
    prompt_id = transmit['project_info']['prompt_id']
    if prompt_id is None:
        QMessageBox.warning(self, "", "项目提示词模版ID为空")
        return False

    # 获取提示词模版信息
    transmit['prompt_info'] = query_prompt_info_by_id(prompt_id)
    if transmit['prompt_info'] is None:
        QMessageBox.warning(self, "", "项目提示词配置信息为空")
        return False

    """角色分析"""
    # 获取角色分析系统提示词规则
    if not prompt_rules_parse(self, transmit, 'role_system', prompt_id, 1, 1, "角色分析系统"):
        return False
    # 获取角色分析用户提示词规则
    if not prompt_rules_parse(self, transmit, 'role_user', prompt_id, 1, 2, "角色分析用户"):
        return False
    """关系分析"""
    # 获取关系分析系统提示词规则
    if not prompt_rules_parse(self, transmit, 'relation_system', prompt_id, 2, 1, "关系分析系统"):
        return False
    # 获取关系分析用户提示词规则
    if not prompt_rules_parse(self, transmit, 'relation_user', prompt_id, 2, 2, "关系分析用户"):
        return False
    """流程控制"""
    # 获取流程控制系统提示词规则
    if not prompt_rules_parse(self, transmit, 'process_system', prompt_id, 6, 1, "流程控制系统"):
        return False
    # 获取流程控制用户提示词规则
    if not prompt_rules_parse(self, transmit, 'process_user', prompt_id, 6, 2, "流程控制用户"):
        return False
    """原文改写场景分析"""
    # 获取场景规则系统提示词规则
    if not prompt_rules_parse(self, transmit, 'scene_system', prompt_id, 3, 1, "原文改写场景分析系统"):
        return False
    # 获取场景规则用户提示词规则
    if not prompt_rules_parse(self, transmit, 'scene_user', prompt_id, 3, 2, "原文改写场景分析用户"):
        return False
    # 获取场景规则场景提示词规则
    # 1. 获取全部场景规则
    scene_prompt_list = query_prompt_template(prompt_id, 3, 3)
    if scene_prompt_list is None or len(scene_prompt_list) < 1:
        QMessageBox.warning(self, "", "项目原文改写场景分析场景提示词配置信息为空")
        return False
    # 2. 定义存储配置信息
    ## 1. 场景识别kv
    scene_identify = {}
    transmit['scene_identify'] = scene_identify
    ## 2. 场景改写kv
    scene_polish = {}
    transmit['scene_polish'] = scene_polish
    for scene_prompt in scene_prompt_list:
        if len(scene_prompt['scene_name']) < 1:
            QMessageBox.warning(self, "", f"项目原文改写场景分析场景提示词，序号：{scene_prompt['sort']} 场景名称为空")
            return False
        if len(scene_prompt['scene_identify']) < 1:
            QMessageBox.warning(self, "", f"项目原文改写场景分析场景提示词，序号：{scene_prompt['sort']} 场景识别规则为空")
            return False
        if len(scene_prompt['context']) < 1:
            QMessageBox.warning(self, "", f"项目原文改写场景分析场景提示词，序号：{scene_prompt['sort']} 场景改写规则为空")
            return False
        scene_identify[scene_prompt['scene_name']] = scene_prompt['scene_identify']
        scene_polish[scene_prompt['scene_name']] = scene_prompt['context']
    """原文改写脉络改写"""
    # 获取脉络改写系统提示词规则
    if not prompt_rules_parse(self, transmit, 'framework_system', prompt_id, 4, 1, "原文改写脉络改写系统"):
        return False
    # 获取脉络改写用户提示词规则
    if not prompt_rules_parse(self, transmit, 'framework_user', prompt_id, 4, 2, "原文改写脉络改写用户"):
        return False
    """番外撰写场景分析"""
    # 获取场景规则系统提示词规则
    if not prompt_rules_parse(self, transmit, 'extra_scene_system', prompt_id, 7, 1, "番外撰写场景分析系统"):
        return False
    # 获取场景规则用户提示词规则
    if not prompt_rules_parse(self, transmit, 'extra_scene_user', prompt_id, 7, 2, "番外撰写场景分析用户"):
        return False
    # 获取场景规则场景提示词规则
    # 1. 获取全部场景规则
    extra_scene_prompt_list = query_prompt_template(prompt_id, 7, 3)
    if extra_scene_prompt_list is None or len(extra_scene_prompt_list) < 1:
        QMessageBox.warning(self, "", "项目番外撰写场景分析场景提示词配置信息为空")
        return False
    # 2. 定义存储配置信息
    ## 1. 场景识别kv
    extra_scene_identify = {}
    transmit['extra_scene_identify'] = extra_scene_identify
    ## 2. 场景改写kv
    extra_scene_polish = {}
    transmit['extra_scene_polish'] = extra_scene_polish
    for scene_prompt in extra_scene_prompt_list:
        if len(scene_prompt['scene_name']) < 1:
            QMessageBox.warning(self, "", f"项目番外撰写场景分析场景提示词，序号：{scene_prompt['sort']} 场景名称为空")
            return False
        if len(scene_prompt['scene_identify']) < 1:
            QMessageBox.warning(self, "", f"项目番外撰写场景分析场景提示词，序号：{scene_prompt['sort']} 场景识别规则为空")
            return False
        if len(scene_prompt['context']) < 1:
            QMessageBox.warning(self, "", f"项目番外撰写场景分析场景提示词，序号：{scene_prompt['sort']} 场景改写规则为空")
            return False
        extra_scene_identify[scene_prompt['scene_name']] = scene_prompt['scene_identify']
        extra_scene_polish[scene_prompt['scene_name']] = scene_prompt['context']
    """番外撰写脉络改写"""
    # 获取脉络改写系统提示词规则
    if not prompt_rules_parse(self, transmit, 'extra_framework_system', prompt_id, 8, 1, "番外撰写脉络改写系统"):
        return False
    # 获取脉络改写用户提示词规则
    if not prompt_rules_parse(self, transmit, 'extra_framework_user', prompt_id, 8, 2, "番外撰写脉络改写用户"):
        return False
    """结果润色"""
    # 获取结果润色系统提示词规则
    if not prompt_rules_parse(self, transmit, 'polish_system', prompt_id, 5, 1, "结果润色系统"):
        return False
    # 获取结果润色用户提示词规则
    if not prompt_rules_parse(self, transmit, 'polish_user', prompt_id, 5, 2, "结果润色用户"):
        return False

    """章节附带数"""
    transmit['polish_before_num'] = transmit['project_info']['polish_before_num']
    if transmit['polish_before_num'] is None:
        QMessageBox.warning(self, "", "改写（撰写）附带前n篇数量为空")
        return False
    transmit['polish_after_num'] = transmit['project_info']['polish_after_num']
    if transmit['polish_after_num'] is None:
        QMessageBox.warning(self, "", "改写（撰写）附带后n篇数量为空")
        return False

    """模型配置"""
    # 1. 定义模型数组
    model_map = {}
    transmit['model_map'] = model_map
    # 获取角色分析模型配置信息
    transmit['role_model_id'] = transmit['project_info']['role_model_id']
    if not model_connection_check(self, transmit['role_model_id'], "角色分析", model_map):
        return False
    # 获取关系分析模型配置信息
    transmit['relation_model_id'] = transmit['project_info']['relation_model_id']
    if not model_connection_check(self, transmit['relation_model_id'], "关系分析", model_map):
        return False
    # 获取流程控制模型配置信息
    transmit['process_model_id'] = transmit['project_info']['process_model_id']
    if not model_connection_check(self, transmit['process_model_id'], "流程控制", model_map):
        return False
    # 原文改写
    ## 获取场景规则模型配置信息
    transmit['scene_model_id'] = transmit['project_info']['scene_model_id']
    if not model_connection_check(self, transmit['scene_model_id'], "原文改写场景规则", model_map):
        return False
    ## 获取脉络改写模型配置信息
    transmit['framework_model_id'] = transmit['project_info']['framework_model_id']
    if not model_connection_check(self, transmit['framework_model_id'], "原文改写脉络改写", model_map):
        return False
    # 番外撰写
    ## 获取场景规则模型配置信息
    transmit['extra_scene_model_id'] = transmit['project_info']['extra_scene_model_id']
    if not model_connection_check(self, transmit['extra_scene_model_id'], "番外撰写场景规则", model_map):
        return False
    ## 获取脉络改写模型配置信息
    transmit['extra_framework_model_id'] = transmit['project_info']['extra_framework_model_id']
    if not model_connection_check(self, transmit['extra_framework_model_id'], "番外撰写脉络改写", model_map):
        return False
    # 获取结果润色模型配置信息
    transmit['polish_model_id'] = transmit['project_info']['polish_model_id']
    if not model_connection_check(self, transmit['polish_model_id'], "结果润色", model_map):
        return False

    # 处理模型任务
    future = APP_FUTURE.get(transmit['project_id'])
    if future:
        # 任务还在执行
        if not future.done():
            # 发送停止事件
            stop_event = APP_STOP_EVENT.get(transmit['project_id'])
            if stop_event:
                stop_event.set()
            else:
                QMessageBox.warning(self, "", "项目存在旧任务线程但未获取到停止事件信息")
                return False
            # 循环3次，每次5秒钟
            for i in range(3):
                # 睡眠5秒钟
                time.sleep(5)
                # 判断任务状态, 结束退出循环
                if future.done():
                    break
            # 判断3次循环后，是否依旧未结束
            if not future.done():
                QMessageBox.warning(self, "", "项目存在旧任务线程且尝试结束失败，请等待一段时间后重试")
                return False

    # 生成新的停止事件
    APP_STOP_EVENT[transmit['project_id']] = threading.Event()
    # 创建新的任务
    params = (self, transmit)
    self.pending_updates = []  # 存储待处理的更新
    future = self.executor.submit(polish, params, lambda project_id, chapter_id: _safe_progress_callback(self, project_id, chapter_id))
    # 放入全局
    APP_FUTURE[transmit['project_id']] = future
    return True

def _safe_progress_callback(self, project_id, chapter_id):
    # 不直接操作 UI，而是将数据存入队列
    self.pending_updates.append({project_id: chapter_id})
    # 触发主线程的更新
    QTimer.singleShot(0, _process_updates)

def _process_updates(self):
    """在主线程中处理所有待处理的更新"""
    while self.pending_updates:
        time.sleep(10)
        value = self.pending_updates.pop(0)
        # ✅ 安全：在主线程中操作 UI
        update_progress(self, value)

def update_progress(self, value):
    """在主线程中执行"""
    for k, v in value.items():
        novel_chapter(self, k)
        update_chapter_num(self, k)