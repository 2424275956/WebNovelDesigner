from typing import List

from pydantic import BaseModel, Field


class RoleOptionalResult(BaseModel):
    role_name: str = Field(description="角色的标准名称")
    role_action: str = Field(description="角色的事件，可以进行番外扩写的点,一句话总结。如出差、前往目的地过程中、在房间的一段时间")

class ProcessPromptResult(BaseModel):
    extra: bool = Field(description="是否可以插入番外(True/False)")
    optional_roles: List[RoleOptionalResult] | None = Field(description="可以选择的角色")