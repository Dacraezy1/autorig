from typing import List, Optional
from pydantic import BaseModel
import yaml

class SystemConfig(BaseModel):
    packages: List[str] = []

class GitRepo(BaseModel):
    url: str
    path: str
    branch: Optional[str] = "main"

class GitConfig(BaseModel):
    repositories: List[GitRepo] = []

class Dotfile(BaseModel):
    source: str
    target: str

class RigConfig(BaseModel):
    name: str
    system: SystemConfig = SystemConfig()
    git: GitConfig = GitConfig()
    dotfiles: List[Dotfile] = []

    @classmethod
    def from_yaml(cls, path: str) -> "RigConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)