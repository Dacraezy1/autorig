from typing import List, Optional, Dict, Any
import os
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

class Script(BaseModel):
    command: str
    description: Optional[str] = None
    cwd: Optional[str] = None

class RigConfig(BaseModel):
    name: str
    system: SystemConfig = SystemConfig()
    git: GitConfig = GitConfig()
    dotfiles: List[Dotfile] = []
    scripts: List[Script] = []
    variables: Dict[str, Any] = {}

    @classmethod
    def from_yaml(cls, path: str) -> "RigConfig":
        with open(path, "r") as f:
            content = f.read()
        
        content = os.path.expandvars(content)
        data = yaml.safe_load(content)
        return cls(**data)