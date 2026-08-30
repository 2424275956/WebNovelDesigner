import threading
import time

import shiboken6
from PySide6.QtWidgets import QMessageBox
from langchain_openai import ChatOpenAI
from openai import OpenAI

from config import GlobalHttpClient
from config.GlobalMap import APP_STATE, APP_FUTURE, APP_STOP_EVENT
from pojo.polish import PolishTransmit
from sqlite.ModelDB import query_model_by_id
from sqlite.ProjectDB import query_project_by_id
from sqlite.PromptDB import query_prompt_template, query_prompt_info_by_id
from utils.PolishBridge import PolishBridge
from windows.polish.NovelPolish import polish
from windows.project.NovelChapterList import novel_chapter, update_chapter_num, update_chapter_title


def prompt_rules_parse(self, prompt_id, point_type, prompt_type, title):
    """提示词规则处理"""
    prompt_list = query_prompt_template(prompt_id, point_type, prompt_type)
    if prompt_list is None or len(prompt_list) < 1:
        QMessageBox.warning(self, "", f"项目{title}提示词配置信息为空")
        return None
    prompt = prompt_list[0]
    if prompt is None or len(prompt['context']) < 1:
        QMessageBox.warning(self, "", f"项目{title}提示词配置规则为空")
        return None
    return prompt['context']

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
    api_key = model['api_key']
    if 1 == model['type'] or 3 == model['type']:
        if len(model['api_key']) < 1:
            QMessageBox.warning(self, "", f"项目{title}模型ApiKey为空")
            return False
    else:
        api_key = "Ollama"
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
            api_key= api_key
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
    transmit = PolishTransmit.Transmit()
    transmit.project_id = self.project_info['id']
    # 当前项目ID
    if transmit.project_id is None:
        QMessageBox.warning(self, "配置错误", "项目ID为空")
        return False

    # 获取当前项目状态
    project_status = APP_STATE.get(transmit.project_id)
    if project_status is None:
        QMessageBox.warning(self, "", "当前项目状态为空")
        return False

    # 待开始状态 或 完成状态直接退出
    if 1 == project_status or 3 == project_status:
        # 停止线程
        stop_event = APP_STOP_EVENT.get(transmit.project_id)
        if stop_event:
            stop_event.set()
        # 停止client
        GlobalHttpClient.emergency_stop(transmit.project_id)
        # 更新ui
        update_progress(self, transmit.project_id)
        return True

    # 获取最新项目信息
    self.project_info = query_project_by_id(transmit.project_id)
    if self.project_info is None:
        QMessageBox.warning(self, "", "项目信息为空")
        return False

    """提示词模版信息"""
    # 获取提示词模版
    prompt_id = self.project_info['prompt_id']
    if prompt_id is None:
        QMessageBox.warning(self, "", "项目提示词模版ID为空")
        return False

    # 获取提示词模版信息
    prompt_info = query_prompt_info_by_id(prompt_id)
    if prompt_info is None:
        QMessageBox.warning(self, "", "项目提示词配置信息为空")
        return False

    """角色分析"""
    # 获取角色分析系统提示词规则
    transmit.role_system = prompt_rules_parse(self, prompt_id, 1, 1, "角色分析系统")
    if transmit.role_system is None:
        return False
    # 获取角色分析用户提示词规则
    transmit.role_user = prompt_rules_parse(self, prompt_id, 1, 2, "角色分析用户")
    if transmit.role_user is None:
        return False
    """关系分析"""
    # 获取关系分析系统提示词规则
    transmit.relation_system = prompt_rules_parse(self, prompt_id, 2, 1, "关系分析系统")
    if transmit.relation_system is None:
        return False
    # 获取关系分析用户提示词规则
    transmit.relation_user = prompt_rules_parse(self, prompt_id, 2, 2, "关系分析用户")
    if transmit.relation_user is None:
        return False
    """流程控制"""
    # 获取流程控制系统提示词规则
    transmit.process_system = prompt_rules_parse(self, prompt_id, 6, 1, "流程控制系统")
    if transmit.process_system is None:
        return False
    # 获取流程控制用户提示词规则
    transmit.process_user = prompt_rules_parse(self, prompt_id, 6, 2, "流程控制用户")
    if transmit.process_user is None:
        return False
    """原文改写场景分析"""
    # 获取场景规则系统提示词规则
    transmit.original_scene_system = prompt_rules_parse(self, prompt_id, 3, 1, "原文改写场景分析系统")
    if transmit.original_scene_system is None:
        return False
    # 获取场景规则用户提示词规则
    transmit.original_scene_user = prompt_rules_parse(self, prompt_id, 3, 2, "原文改写场景分析用户")
    if transmit.original_scene_user is None:
        return False
    # 获取场景规则场景提示词规则
    # 1. 获取全部场景规则
    scene_prompt_list = query_prompt_template(prompt_id, 3, 3)
    if scene_prompt_list is None or len(scene_prompt_list) < 1:
        QMessageBox.warning(self, "", "项目原文改写场景分析场景提示词配置信息为空")
        return False
    # 2. 定义存储配置信息
    transmit.original_scene_identity = {}
    transmit.original_scene_polish = {}
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
        transmit.original_scene_identity[scene_prompt['scene_name']] = scene_prompt['scene_identify']
        transmit.original_scene_polish[scene_prompt['scene_name']] = scene_prompt['context']
    """原文改写脉络改写"""
    # 获取脉络改写系统提示词规则
    transmit.original_framework_system = prompt_rules_parse(self, prompt_id, 4, 1, "原文改写脉络改写系统")
    if transmit.original_framework_system is None:
        return False
    # 获取脉络改写用户提示词规则
    transmit.original_framework_user = prompt_rules_parse(self, prompt_id, 4, 2, "原文改写脉络改写用户")
    if transmit.original_framework_user is None:
        return False
    """番外撰写场景分析"""
    # 获取场景规则系统提示词规则
    transmit.extra_scene_system = prompt_rules_parse(self, prompt_id, 7, 1, "番外撰写场景分析系统")
    if transmit.extra_scene_system is None:
        return False
    # 获取场景规则用户提示词规则
    transmit.extra_scene_user = prompt_rules_parse(self, prompt_id, 7, 2, "番外撰写场景分析用户")
    if transmit.extra_scene_user is None:
        return False
    # 获取场景规则场景提示词规则
    # 1. 获取全部场景规则
    extra_scene_prompt_list = query_prompt_template(prompt_id, 7, 3)
    if extra_scene_prompt_list is None or len(extra_scene_prompt_list) < 1:
        QMessageBox.warning(self, "", "项目番外撰写场景分析场景提示词配置信息为空")
        return False
    # 2. 定义存储配置信息
    transmit.extra_scene_identify = {}
    transmit.extra_scene_polish = {}
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
        transmit.extra_scene_identify[scene_prompt['scene_name']] = scene_prompt['scene_identify']
        transmit.extra_scene_polish[scene_prompt['scene_name']] = scene_prompt['context']
    """番外撰写脉络改写"""
    # 获取脉络改写系统提示词规则
    transmit.extra_framework_system = prompt_rules_parse(self, prompt_id, 8, 1, "番外撰写脉络改写系统")
    if transmit.extra_framework_system is None:
        return False
    # 获取脉络改写用户提示词规则
    transmit.extra_framework_user = prompt_rules_parse(self, prompt_id, 8, 2, "番外撰写脉络改写用户")
    if transmit.extra_framework_user is None:
        return False
    """结果润色"""
    # 获取结果润色系统提示词规则
    transmit.polish_system = prompt_rules_parse(self, prompt_id, 5, 1, "结果润色系统")
    if transmit.polish_system is None:
        return False
    # 获取结果润色用户提示词规则
    transmit.polish_user = prompt_rules_parse(self, prompt_id, 5, 2, "结果润色用户")
    if transmit.polish_user is None:
        return False

    """章节附带数"""
    transmit.polish_before_num = self.project_info['polish_before_num']
    if transmit.polish_before_num is None:
        QMessageBox.warning(self, "", "改写（撰写）附带前述章节数量为空")
        return False
    transmit.polish_after_num = self.project_info['polish_after_num']
    if transmit.polish_after_num is None:
        QMessageBox.warning(self, "", "改写（撰写）附带后续章节数量为空")
        return False
    transmit.extra_start_num = self.project_info['extra_start_num']
    if transmit.extra_start_num is None:
        QMessageBox.warning(self, "", "番外剧情插入章节数为空")
        return False

    """主角团队"""
    # 男主角
    transmit.male_lead = self.project_info['male_lead']
    if transmit.male_lead is None:
        QMessageBox.warning(self, "", "男主角团队信息为空")
        return False
    # 女主角
    transmit.heroine = self.project_info['heroine']
    if transmit.heroine is None:
        QMessageBox.warning(self, "", "女主角团队信息为空")
        return False

    """模型配置"""
    model_map = {}
    # 获取角色分析模型配置信息
    if not model_connection_check(self, self.project_info['role_model_id'], "角色分析", model_map):
        return False
    # 获取关系分析模型配置信息
    if not model_connection_check(self, self.project_info['relation_model_id'], "关系分析", model_map):
        return False
    # 获取流程控制模型配置信息
    if not model_connection_check(self, self.project_info['process_model_id'], "流程控制", model_map):
        return False
    # 原文改写
    ## 获取场景规则模型配置信息
    if not model_connection_check(self, self.project_info['scene_model_id'], "原文改写场景规则", model_map):
        return False
    ## 获取脉络改写模型配置信息
    if not model_connection_check(self, self.project_info['framework_model_id'], "原文改写脉络改写", model_map):
        return False
    # 番外撰写
    ## 获取场景规则模型配置信息
    if not model_connection_check(self, self.project_info['extra_scene_model_id'], "番外撰写场景规则", model_map):
        return False
    ## 获取脉络改写模型配置信息
    if not model_connection_check(self, self.project_info['extra_framework_model_id'], "番外撰写脉络改写", model_map):
        return False
    # 获取结果润色模型配置信息
    if not model_connection_check(self, self.project_info['polish_model_id'], "结果润色", model_map):
        return False

    """模型llm创建"""
    # 终止符
    stop_list = [
        # 格式终止符
        "\n\n\n",                    # 三个换行

        # 防止过度标点
        "！！！！",          # 三个感叹号
        "!!!!",
        "？？？？",          # 三个问号
        "????",
        "，，，，",
        ",,,,",
    ]
    # 角色分析
    role_model = model_map[self.project_info['role_model_id']]
    transmit.role_llm = ChatOpenAI(
        model=role_model['model_id'],
        api_key=role_model['api_key'] if role_model['api_key'] else "Ollama",
        base_url=role_model['url'],
        temperature=role_model['temperature'],
        max_tokens=role_model['max_token'],
        top_p=role_model['top_p'],
        streaming=True,
        stop=stop_list,
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 流程控制
    process_model = model_map[self.project_info['process_model_id']]
    transmit.process_llm = ChatOpenAI(
        model=process_model['model_id'],
        api_key=process_model['api_key'] if process_model['api_key'] else "Ollama",
        base_url=process_model['url'],
        temperature=process_model['temperature'],
        max_tokens=process_model['max_token'],
        top_p=process_model['top_p'],
        streaming=True,
        stop=stop_list,
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 原文改写-场景分析
    original_scene_model = model_map[self.project_info['scene_model_id']]
    transmit.original_scene_llm = ChatOpenAI(
        model=original_scene_model['model_id'],
        api_key=original_scene_model['api_key'] if original_scene_model['api_key'] else "Ollama",
        base_url=original_scene_model['url'],
        temperature=original_scene_model['temperature'],
        max_tokens=original_scene_model['max_token'],
        top_p=original_scene_model['top_p'],
        streaming=True,
        stop=stop_list,
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 原文改写-脉络改写
    original_framework_model = model_map[self.project_info['framework_model_id']]
    transmit.original_framework_llm = ChatOpenAI(
        model=original_framework_model['model_id'],
        api_key=original_framework_model['api_key'] if original_framework_model['api_key'] else "Ollama",
        base_url=original_framework_model['url'],
        temperature=original_framework_model['temperature'],
        max_tokens=original_framework_model['max_token'],
        top_p=original_framework_model['top_p'],
        streaming=True,
        presence_penalty=-0.1,      # 全局重复惩罚，防止车轱辘话
        frequency_penalty=0.25,     # 频率惩罚，抑制高频词
        stop=stop_list,
        extra_body={
            "repetition_penalty": 0.99  #
        },
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 番外生成-场景分析
    extra_scene_model = model_map[self.project_info['extra_scene_model_id']]
    transmit.extra_scene_llm = ChatOpenAI(
        model=extra_scene_model['model_id'],
        api_key=extra_scene_model['api_key'] if extra_scene_model['api_key'] else "Ollama",
        base_url=extra_scene_model['url'],
        temperature=extra_scene_model['temperature'],
        max_tokens=extra_scene_model['max_token'],
        top_p=extra_scene_model['top_p'],
        streaming=True,
        stop=stop_list,
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 番外生成-脉络生成
    extra_framework_model = model_map[self.project_info['extra_framework_model_id']]
    transmit.extra_framework_llm = ChatOpenAI(
        model=extra_framework_model['model_id'],
        api_key=extra_framework_model['api_key'] if extra_framework_model['api_key'] else "Ollama",
        base_url=extra_framework_model['url'],
        temperature=extra_framework_model['temperature'],
        max_tokens=extra_framework_model['max_token'],
        top_p=extra_framework_model['top_p'],
        streaming=True,
        presence_penalty=0.1,      # 全局重复惩罚，防止车轱辘话
        frequency_penalty=0.0,     # 频率惩罚，抑制高频词
        stop=stop_list,
        extra_body={
            "repetition_penalty": 1.01
        },
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 结果润色
    polish_model = model_map[self.project_info['polish_model_id']]
    transmit.polish_llm = ChatOpenAI(
        model=polish_model['model_id'],
        api_key=polish_model['api_key'] if polish_model['api_key'] else "Ollama",
        base_url=polish_model['url'],
        temperature=polish_model['temperature'],
        max_tokens=polish_model['max_token'],
        top_p=polish_model['top_p'],
        streaming=True,
        presence_penalty=0.0,      # 全局重复惩罚，防止车轱辘话
        frequency_penalty=0.0,     # 频率惩罚，抑制高频词
        stop=stop_list,
        extra_body={
            "repetition_penalty": 1.00
        },
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )
    # 关系分析
    relation_model = model_map[self.project_info['relation_model_id']]
    transmit.relation_llm = ChatOpenAI(
        model=relation_model['model_id'],
        api_key=relation_model['api_key'],
        base_url=relation_model['url'],
        temperature=relation_model['temperature'],
        max_tokens=relation_model['max_token'],
        top_p=relation_model['top_p'],
        streaming=True,
        stop=stop_list,
        http_client=GlobalHttpClient.get_or_create_http_client(transmit.project_id)
    )

    # 处理模型任务
    future = APP_FUTURE.get(transmit.project_id)
    if future:
        # 任务还在执行
        if not future.done():
            # 发送停止事件
            stop_event = APP_STOP_EVENT.get(transmit.project_id)
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
    APP_STOP_EVENT[transmit.project_id] = threading.Event()
    # 创建新的任务
    self.pending_updates = []  # 存储待处理的更新
    bridge = PolishBridge()
    bridge.progress.connect(lambda project_id: update_progress(self, project_id))
    future = self.executor.submit(polish, transmit, bridge)
    # 放入全局
    APP_FUTURE[transmit.project_id] = future
    return True


def update_progress(self, project_id):
    """在主线程中执行"""
    if self.project_info['id'] == project_id:
        # 判断对象是否销毁
        if not hasattr(self, 'chapter_list') or not shiboken6.isValid(self.chapter_list):
            return
        if not hasattr(self, 'chapter_count1') or not shiboken6.isValid(self.chapter_count1):
            return
        if not hasattr(self, 'chapter_count2') or not shiboken6.isValid(self.chapter_count2):
            return
        if not hasattr(self, 'chapter_count3') or not shiboken6.isValid(self.chapter_count3):
            return
        if not hasattr(self, 'chapter_count4') or not shiboken6.isValid(self.chapter_count4):
            return
        if not hasattr(self, 'chapter_count5') or not shiboken6.isValid(self.chapter_count5):
            return
        if not hasattr(self, 'project_status_color') or not shiboken6.isValid(self.project_status_color):
            return
        if not hasattr(self, 'project_status_title') or not shiboken6.isValid(self.project_status_title):
            return
        # 更新信息
        novel_chapter(self, self.project_info['id'])
        update_chapter_num(self, self.project_info['id'])
        update_chapter_title(self, self.project_info['id'])