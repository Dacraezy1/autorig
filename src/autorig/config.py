from typing import List, Optional, Dict, Any
import os
import re
from pydantic import BaseModel, field_validator
import yaml


class SystemConfig(BaseModel):
    packages: List[str] = []


class GitRepo(BaseModel):
    url: str
    path: str
    branch: Optional[str] = "main"

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        # Basic URL validation
        if not re.match(r'^https?://', v) and not re.match(r'^git@', v):
            raise ValueError('Invalid git URL format')
        return v


class GitConfig(BaseModel):
    repositories: List[GitRepo] = []


class Dotfile(BaseModel):
    source: str
    target: str

    @field_validator('source', 'target')
    @classmethod
    def validate_path(cls, v):
        # Basic security validation to prevent path traversal
        if '../' in v or '..\\' in v:
            raise ValueError('Relative path traversal detected in dotfile paths')
        return v


class Script(BaseModel):
    command: str
    description: Optional[str] = None
    cwd: Optional[str] = None

    @field_validator('command')
    @classmethod
    def validate_command(cls, v):
        # Basic command validation to prevent dangerous operations
        dangerous_patterns = [
            r'\|\|',  # command chaining
            r'&&',    # command chaining
            r';',     # command separation
            r'\$\(\(', # arithmetic expansion
            r'`',     # command substitution
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v):
                raise ValueError(f'Dangerous command pattern detected: {pattern}')
        return v


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