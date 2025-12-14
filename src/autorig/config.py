from typing import List, Optional, Dict, Any
import os
import re
from pydantic import BaseModel, field_validator, model_validator
from .profiles import load_profile_config


class SystemConfig(BaseModel):
    packages: List[str] = []

    @field_validator('packages')
    @classmethod
    def validate_packages(cls, v):
        if not isinstance(v, list):
            raise ValueError('packages must be a list')
        for pkg in v:
            if not isinstance(pkg, str):
                raise ValueError(f'package names must be strings: {pkg}')
            if not pkg.strip():
                raise ValueError('package names cannot be empty')
        return v


class GitRepo(BaseModel):
    url: str
    path: str
    branch: Optional[str] = "main"

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        # Basic URL validation
        if not re.match(r'^https?://', v) and not re.match(r'^(git@|ssh://)', v):
            raise ValueError(f'Invalid git URL format: {v}')
        return v

    @field_validator('path')
    @classmethod
    def validate_path(cls, v):
        # Validate path does not contain dangerous patterns
        if '../' in v or '..\\' in v:
            raise ValueError(f'Path traversal detected in repository path: {v}')
        # Additional validation: path should be expandable
        expanded_path = os.path.expanduser(v)
        if not expanded_path.startswith(('/', '~', os.path.expanduser('~'), '.')):
            raise ValueError(f'Invalid repository path: {v}')
        return v


class GitConfig(BaseModel):
    repositories: List[GitRepo] = []

    @field_validator('repositories')
    @classmethod
    def validate_repositories(cls, v):
        if not isinstance(v, list):
            raise ValueError('repositories must be a list')
        return v


class Dotfile(BaseModel):
    source: str
    target: str

    @field_validator('source', 'target')
    @classmethod
    def validate_path(cls, v):
        # Validate path does not contain dangerous patterns
        if '../' in v or '..\\' in v:
            raise ValueError(f'Path traversal detected in dotfile path: {v}')
        return v


class Script(BaseModel):
    command: str
    description: Optional[str] = None
    cwd: Optional[str] = None

    @field_validator('command')
    @classmethod
    def validate_command(cls, v):
        # Enhanced command validation to prevent dangerous operations
        dangerous_patterns = [
            r'\|\|',  # command chaining
            r'&&',    # command chaining
            r';',     # command separation
            r'\$\(\(', # arithmetic expansion
            r'`',     # command substitution
            r'\$\{.*\}', # environment variable injection
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v):
                raise ValueError(f'Dangerous command pattern detected: {pattern}')
        return v

    @field_validator('cwd')
    @classmethod
    def validate_cwd(cls, v):
        if v is not None:
            if '../' in v or '..\\' in v:
                raise ValueError(f'Path traversal detected in script cwd: {v}')
        return v


class RigConfig(BaseModel):
    name: str
    system: SystemConfig = SystemConfig()
    git: GitConfig = GitConfig()
    dotfiles: List[Dotfile] = []
    scripts: List[Script] = []
    variables: Dict[str, Any] = {}

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Configuration name cannot be empty')
        return v.strip()

    @model_validator(mode='after')
    def validate_config_consistency(self):
        # Check for duplicate dotfile targets
        targets = [df.target for df in self.dotfiles]
        if len(targets) != len(set(targets)):
            duplicates = [x for x in targets if targets.count(x) > 1]
            raise ValueError(f'Duplicate dotfile targets found: {list(set(duplicates))}')

        # Check for potentially conflicting operations
        # For example, if a script tries to install a package that's also in system.packages
        return self

    @classmethod
    def from_yaml(cls, path: str, profile: Optional[str] = None) -> "RigConfig":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file does not exist: {path}")

        # Load configuration with profile support
        data = load_profile_config(path, profile)

        # Check for required fields in the raw data
        if 'name' not in data or not data['name']:
            raise ValueError("Configuration must have a 'name' field")

        return cls(**data)