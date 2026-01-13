"""
JSON Schema for AutoRig configuration validation.
"""

from typing import Any, Dict


def get_config_schema() -> Dict[str, Any]:
    """
    Returns the JSON schema for AutoRig configuration files.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["name"],
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the configuration",
                "minLength": 1,
                "maxLength": 200,
            },
            "variables": {
                "type": "object",
                "description": "Variables available for template rendering",
                "additionalProperties": True,
                "default": {},
            },
            "system": {
                "type": "object",
                "description": "System package configuration",
                "properties": {
                    "packages": {
                        "type": "array",
                        "items": {"type": "string", "minLength": 1},
                        "default": [],
                    }
                },
                "additionalProperties": False,
                "default": {},
            },
            "git": {
                "type": "object",
                "description": "Git repository configuration",
                "properties": {
                    "repositories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["url", "path"],
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "description": "Git repository URL",
                                },
                                "path": {
                                    "type": "string",
                                    "description": "Local path to clone repository",
                                },
                                "branch": {"type": "string", "default": "main"},
                            },
                            "additionalProperties": False,
                        },
                        "default": [],
                    }
                },
                "additionalProperties": False,
                "default": {},
            },
            "dotfiles": {
                "type": "array",
                "description": "Dotfile configuration",
                "items": {
                    "type": "object",
                    "required": ["source", "target"],
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source file path (relative to config)",
                        },
                        "target": {
                            "type": "string",
                            "description": "Target file path (absolute on system)",
                        },
                    },
                    "additionalProperties": False,
                },
                "default": [],
            },
            "scripts": {
                "type": "array",
                "description": "Custom script configuration",
                "items": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the script",
                        },
                        "cwd": {
                            "type": "string",
                            "description": "Working directory for the script",
                        },
                        "when": {
                            "type": "string",
                            "enum": ["pre", "post", "both"],
                            "description": "When to run the script",
                            "default": "post",
                        },
                    },
                    "additionalProperties": False,
                },
                "default": [],
            },
            "hooks": {
                "type": "object",
                "description": "Pre/post hooks for different operations",
                "properties": {
                    "pre_system": {"$ref": "#/definitions/scripts"},
                    "post_system": {"$ref": "#/definitions/scripts"},
                    "pre_git": {"$ref": "#/definitions/scripts"},
                    "post_git": {"$ref": "#/definitions/scripts"},
                    "pre_dotfiles": {"$ref": "#/definitions/scripts"},
                    "post_dotfiles": {"$ref": "#/definitions/scripts"},
                    "pre_scripts": {"$ref": "#/definitions/scripts"},
                    "post_scripts": {"$ref": "#/definitions/scripts"},
                },
                "additionalProperties": False,
                "default": {},
            },
            "profiles": {
                "type": "object",
                "description": "Profile-specific configurations",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "system": {"$ref": "#/properties/system"},
                        "git": {"$ref": "#/properties/git"},
                        "dotfiles": {"$ref": "#/properties/dotfiles"},
                        "scripts": {"$ref": "#/properties/scripts"},
                        "hooks": {"$ref": "#/properties/hooks"},
                    },
                    "additionalProperties": False,
                },
                "default": {},
            },
        },
        "additionalProperties": False,
        "definitions": {
            "scripts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the script",
                        },
                        "cwd": {
                            "type": "string",
                            "description": "Working directory for the script",
                        },
                        "when": {
                            "type": "string",
                            "enum": ["pre", "post", "both"],
                            "description": "When to run the script",
                            "default": "post",
                        },
                    },
                    "additionalProperties": False,
                },
            }
        },
    }
