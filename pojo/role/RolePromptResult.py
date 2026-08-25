from typing import Optional, List

from pydantic import BaseModel, Field

class CharacterResult(BaseModel):
    """
    角色标准信息
    """
    character_name: str = Field(description="角色的标准名称")
    temp_alias_name: Optional[List[str]] = Field(default=[], description="多数人对其的代称，如：李律师、王城主、云公主等")

class RoleResult(BaseModel):
    """
    角色分析
    """
    character_list: List[CharacterResult] = Field(description="角色的基础信息")