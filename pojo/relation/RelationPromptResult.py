from typing import List, Optional

from pydantic import BaseModel, Field


class CharacterResult(BaseModel):
    """
    角色基础信息
    """
    名称: str = Field(description="角色标准名称")
    代称: Optional[List[str]] = Field(default=[], description="角色日常代称")
    性别: str | None = Field(description="角色性别")
    身份: Optional[List[str]] = Field(default=[], description="角色身份")
    种族: str | None = Field(description="角色种族")
    身高: str | None = Field(description="角色身高")
    身材: str | None = Field(description="角色身材")
    肤色: str | None = Field(description="角色肤色")
    主角女性亲友: bool | None = Field(description="女性角色是否是主角的亲友")
    面对敌人性格: Optional[List[str]] = Field(default=[], description="面对敌人的性格特征，如：冷酷、卑鄙、残忍等")
    面对陌生人性格: Optional[List[str]] = Field(default=[], description="面对陌生人的性格特征，如：虚假、冷淡、温柔、妩媚等")
    面对亲友性格: Optional[List[str]] = Field(default=[], description="面对亲友的性格特征，如：温柔、冷淡等")
    胸部形状: str | None = Field(description="女性胸部形状")
    胸部大小: str | None = Field(description="女性胸部大小")
    乳头特征: str | None = Field(description="女性乳头特征")
    乳头乳晕颜色: str | None = Field(description="女性乳头颜色")
    阴部外观: str | None = Field(description="女性阴部外观")
    阴部毛发: str | None = Field(description="女性阴部毛发")
    阴部颜色: str | None = Field(description="女性阴部颜色")
    阴茎特征: str | None = Field(description="男性阴茎特征")
    阴茎长短: str | None = Field(description="男性阴茎长短")
    阴茎粗细: str | None = Field(description="男性阴茎粗细")
    最近动作: str | None = Field(description="角色最近的动作")

class RoleOptionalResult(BaseModel):
    """
    角色态度信息
    """
    态度: str = Field(description="态度如何，如：冷淡、关系、仇恨等")
    简述: str = Field(description="一句话总结关系")


class RelationResult(BaseModel):
    """
    角色关联关系信息
    """
    角色A: str = Field(description="角色A的标准名称")
    角色B: str = Field(description="角色B的标准名称")
    关系: List[str] = Field(default=[], description="角色关系，如：父女、母子、师徒、仇敌、陌生人等")
    A对B的日常称呼: Optional[List[str]] = Field(default=[], description="角色A日常如何称呼角色B，如：师傅、二师兄、城主等")
    A对B的私下称呼: Optional[List[str]] = Field(default=[], description="角色A私下如何称呼角色B，如：老东西、老不死、宝贝等")
    A对B的态度: Optional[List[str]] = Field(default=[], description="角色A对角色B的态度如何")
    B对A的日常称呼: Optional[List[str]] = Field(default=[], description="角色B日常如何称呼角色A，如：师傅、二师兄、城主等")
    B对A的私下称呼: Optional[List[str]] = Field(default=[], description="角色B私下如何称呼角色A，如：老东西、老不死、宝贝等")
    B对A的态度: Optional[List[str]] = Field(default=[], description="角色B对角色A的态度如何")

class RelationPromptResult(BaseModel):
    """
    角色信息补充与关联关系
    """
    角色数组: List[CharacterResult] = Field(description="角色的基础信息")
    角色关系: Optional[List[RelationResult]] = Field(default=[], description="角色之间的关联关系")