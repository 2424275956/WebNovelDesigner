from typing import List

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class Transmit(BaseModel):
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

