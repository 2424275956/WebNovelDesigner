import json
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChapterBO(BaseModel):
    id: int = Field(description="章节ID")
    project_id: int = Field(description="项目ID")
    title: str = Field(description="章节名称")
    before_content: Optional[str] = Field(default=None, description="前述剧情简述")
    after_content: Optional[str] = Field(default=None, description="后续剧情简述")
    original_resume: Optional[str] = Field(default=None, description="原文剧情简述")
    polish_resume: Optional[str] = Field(default=None, description="润色内容简述")
    old_content: Optional[str] = Field(default=None, description="原文内容")
    role_content: Optional[str] = Field(default=None, description="角色分析")
    relation_content: Optional[str] = Field(default=None, description="关系分析")
    process_content: Optional[str] = Field(default=None, description="流程控制")
    scene_content: Optional[str] = Field(default=None, description="场景分析")
    framework_content: Optional[str] = Field(default=None, description="脉络内容")
    new_content: Optional[str] = Field(default=None, description="润色内容")
    type: int = Field(description="章节类型")
    status: int = Field(description="章节状态")
    point: int = Field(description="章节节点")
    sort: int = Field(description="章节序号")


class ChapterType(Enum):
    """
    章节类型
    """
    # 原文改写
    ORIGINAL_POLISH = 1
    # 番外生成
    EXTRA_GENERATE = 2

class ChapterStatus(Enum):
    """
    章节状态
    """
    # 待开始
    WAIT = 1
    # 进行中
    RUNNING = 2
    # 已完成
    SUCCESS = 3
    # 已失败
    FAIL = 4

class ChapterPoint(Enum):
    """
    章节节点
    """
    # 分析角色模型
    ROLE_ANALYSIS = 100
    # 流程控制判断
    PROCESS_CHOOSES = 200
    # 原文改写-匹配场景规则
    ORIGINAL_SCENE = 300
    # 原文改写-脉络发展改写
    ORIGINAL_FRAMEWORK = 310
    # 番外生成-匹配场景规则
    EXTRA_SCENE = 400
    # 番外生成-脉络发展生成
    EXTRA_FRAMEWORK = 410
    # 润色输出内容
    POLISH_CONTENT = 500
    # 去重整理
    REPETITION_ORGANIZE = 550
    # 分析角色关系
    RELATION_ANALYSIS = 600
    # 已完成
    SUCCESS = 700

def sqliteToChapter(row) -> ChapterBO:
    """
    SQLite查询对象转Chapter对象
    """
    row_dict = dict(row)
    row_json = json.dumps(row_dict)
    return ChapterBO.model_validate_json(row_json)
