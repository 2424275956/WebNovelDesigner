import re

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ConfigDict

from config.GlobalMap import APP_STOP_EVENT
from pojo.table.Chapter import ChapterBO, ChapterStatus
from utils.PolishBridge import PolishBridge


class Transmit(BaseModel):
    # 允许任意类型，跳过对 PolishBridge 的 schema 生成和字段验证
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # 字段处理
    project_id : int = Field(default=None, description="项目ID")

    role_system : str = Field(default=None, description="角色分析系统提示词")
    role_user : str = Field(default=None, description="角色分析用户提示词")

    relation_system : str = Field(default=None, description="角色关系系统提示词")
    relation_user : str = Field(default=None, description="角色关系用户提示词")

    process_system : str = Field(default=None, description="流程控制系统提示词")
    process_user : str = Field(default=None, description="流程控制用户提示词")

    original_scene_system : str = Field(default=None, description="原文场景分析系统提示词")
    original_scene_user : str = Field(default=None, description="原文场景分析用户提示词")
    original_scene_identity : dict[str, str] = Field(default=None, description="原文场景分析识别数组")
    original_scene_polish : dict[str, str] = Field(default=None, description="原文场景分析规则数组")

    original_framework_system : str = Field(default=None, description="原文脉络改写系统提示词")
    original_framework_user : str = Field(default=None, description="原文脉络改写用户提示词")

    extra_scene_system : str = Field(default=None, description="番外场景分析系统提示词")
    extra_scene_user : str = Field(default=None, description="番外场景分析用户提示词")
    extra_scene_identify : dict[str, str] = Field(default=None, description="番外场景分析识别规则")
    extra_scene_polish : dict[str, str] = Field(default=None, description="番外场景分析改写规则")

    extra_framework_system : str = Field(default=None, description="番外脉络生成系统提示词")
    extra_framework_user : str = Field(default=None, description="番外脉络生成用户提示词")

    polish_system : str = Field(default=None, description="结果润色系统提示词")
    polish_user : str = Field(default=None, description="结果润色用户提示词")

    polish_before_num : int = Field(default=None, description="附带前n章片段")
    polish_after_num : int = Field(default=None, description="附带后n章片段")
    extra_start_num : int = Field(default=None, description="番外插入开始章节")

    male_lead : str = Field(default=None, description="男主角团队")
    heroine : str = Field(default=None, description="女主角团队")

    role_llm : ChatOpenAI = Field(default=None, description="角色分析llm")
    relation_llm : ChatOpenAI = Field(default=None, description="角色关系llm")
    process_llm : ChatOpenAI = Field(default=None, description="流程控制llm")
    original_scene_llm : ChatOpenAI = Field(default=None, description="原文场景分析llm")
    original_framework_llm : ChatOpenAI = Field(default=None, description="原文脉络改写llm")
    extra_scene_llm : ChatOpenAI = Field(default=None, description="番外场景分析llm")
    extra_framework_llm : ChatOpenAI = Field(default=None, description="番外脉络生成llm")
    polish_llm : ChatOpenAI = Field(default=None, description="结果润色llm")

    # 信号量通知
    project_bridge : PolishBridge = Field(default=None, description="项目线程信号传输对象")

    # 章节数据对象
    ## 当前章节数据
    chapter_model : ChapterBO = Field(default=None, description="当前章节内容")
    temp_model : ChapterBO = Field(default=None, description="临时章节内容（简述使用）")

    # 封装函数方法
    def runningLog(self, log):
        self.project_bridge.running_log.emit(self.project_id, log)

    # 刷新润色项目页面
    def reflushPolishPage(self):
        self.project_bridge.progress.emit(self.project_id)

    # 定义当前章节处理失败
    def chapterParseFail(self):
        self.chapter_model.status = ChapterStatus.FAIL.value

    # 当前章节是否处理失败
    def isChapterPolishFail(self):
        return self.chapter_model.status == ChapterStatus.FAIL.value

    # 是否结束当前线程
    def isStopThread(self):
        stop_event = APP_STOP_EVENT.get(self.project_id)
        if stop_event and stop_event.is_set():
            return True
        return False
