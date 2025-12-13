from typing import List, Optional
from pydantic import BaseModel
import yaml
from pathlib import Path

class SystemConfig(BaseModel):
    packages: List[str] = []

class GitRepo(BaseModel):
    url: str
    path: str
    branch: Optional[str] = "main"

class Dotfile(BaseModel):
    source: str
    target: str

class GitConfig(BaseModel):
    repositories: List[GitRepo] = []

class RigConfig(BaseModel):
    name: str
    system: Optional[SystemConfig] = None
    git: Optional[GitConfig] = None
    dotfiles: List[Dotfile] = []

    @classmethod
    def load(cls, path: str) -> "RigConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)
