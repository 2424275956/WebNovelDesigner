from typing import List

from pydantic import BaseModel, Field


class ScenePromptResult(BaseModel):
    scene_list: List[str] = Field(description="匹配的场景")