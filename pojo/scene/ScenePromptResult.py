from typing import List

from pydantic import BaseModel, Field


class ScenePromptResult(BaseModel):
    is_polish: bool = Field(default=True, description="是否需要改写润色")
    scene_list: List[str] = Field(description="匹配的场景")