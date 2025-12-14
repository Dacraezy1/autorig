"""
Environment detection and profiles functionality for AutoRig.
"""
import os
import platform
import socket
from pathlib import Path
from typing import Dict, Optional, Any


class EnvironmentDetector:
    """
    Detects the current environment and system characteristics.
    """
    
    def __init__(self):
        self.env_info = self._collect_environment_info()
    
    def _collect_environment_info(self) -> Dict[str, Any]:
        """Collect information about the current environment."""
        return {
            'os': platform.system().lower(),
            'platform': platform.platform(),
            'machine': platform.machine(),
            'node': socket.gethostname(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'shell': os.environ.get('SHELL', ''),
            'user': os.environ.get('USER', os.environ.get('USERNAME', '')),
            'home': os.path.expanduser('~'),
            'is_wsl': self._is_wsl(),
            'is_docker': self._is_docker(),
            'desktop_environment': os.environ.get('XDG_CURRENT_DESKTOP', ''),
            'display_server': os.environ.get('XDG_SESSION_TYPE', ''),
        }
    
    def _is_wsl(self) -> bool:
        """Check if running under Windows Subsystem for Linux."""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except FileNotFoundError:
            return False
    
    def _is_docker(self) -> bool:
        """Check if running inside a Docker container."""
        # Check for .dockerenv file
        if Path('/.dockerenv').exists():
            return True
        
        # Check for docker cgroup
        try:
            with open('/proc/1/cgroup', 'r') as f:
                return 'docker' in f.read()
        except FileNotFoundError:
            return False
    
    def get_profile_name(self) -> str:
        """Generate a profile name based on environment characteristics."""
        os_name = self.env_info['os']
        machine = self.env_info['machine']
        node = self.env_info['node']
        
        # Create a profile name like "linux-x86_64-workstation"
        profile_parts = [os_name, machine]
        
        # Add more specific identifiers if available
        if 'laptop' in node.lower() or 'thinkpad' in node.lower():
            profile_parts.append('laptop')
        elif 'desktop' in node.lower() or 'tower' in node.lower():
            profile_parts.append('desktop')
        elif self.env_info.get('is_wsl'):
            profile_parts.append('wsl')
        elif self.env_info.get('is_docker'):
            profile_parts.append('docker')
        
        return '-'.join(profile_parts)
    
    def matches_profile(self, profile_spec: Dict[str, Any]) -> bool:
        """
        Check if the current environment matches a profile specification.
        
        Profile spec can contain:
        - 'os': 'linux', 'darwin', 'windows'
        - 'platform': partial match for platform string
        - 'machine': architecture (x86_64, arm64, etc.)
        - 'hostname': match for hostname
        - 'shell': match for shell
        - 'conditions': custom conditions
        """
        if 'os' in profile_spec and profile_spec['os'] != self.env_info['os']:
            return False
            
        if 'platform' in profile_spec and profile_spec['platform'] not in self.env_info['platform']:
            return False
            
        if 'machine' in profile_spec and profile_spec['machine'] != self.env_info['machine']:
            return False
            
        if 'hostname' in profile_spec and profile_spec['hostname'] != self.env_info['node']:
            return False
            
        if 'shell' in profile_spec and profile_spec['shell'] not in self.env_info['shell']:
            return False
        
        # Check custom conditions
        if 'conditions' in profile_spec:
            for condition in profile_spec['conditions']:
                if not self._evaluate_condition(condition):
                    return False
        
        return True
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a custom condition."""
        # Simple condition evaluation
        if condition == 'is_wsl':
            return self.env_info.get('is_wsl', False)
        elif condition == 'is_docker':
            return self.env_info.get('is_docker', False)
        elif condition.startswith('env:'):
            # Check environment variable
            env_var = condition[4:]  # Remove 'env:' prefix
            key, expected = env_var.split('=', 1) if '=' in env_var else (env_var, '1')
            return os.environ.get(key, '') == expected
        return False


def load_profile_config(config_path: str, profile: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a configuration file with profile-specific overrides.

    If a profile is specified or auto-detected, it will try to load:
    - rig.yaml (base config)
    - rig-{profile}.yaml (profile-specific config)
    - rig.local.yaml (local overrides, not committed)

    Profile-specific config overrides base config.
    """
    detector = EnvironmentDetector()

    # Determine profile to use
    if not profile:
        profile = detector.get_profile_name()

    # List of config files to try, in order of precedence (last wins)
    config_files = [
        config_path,  # Base config
        config_path.replace('.yaml', f'-{profile}.yaml'),  # Profile-specific
        config_path.replace('.yaml', '.local.yaml'),  # Local overrides
    ]

    final_config = {}

    for config_file in config_files:
        config_path_obj = Path(config_file)
        if config_path_obj.exists():
            with open(config_path_obj, 'r') as f:
                content = f.read()

            # Expand environment variables in the content
            try:
                content = os.path.expandvars(content)
            except Exception as e:
                raise ValueError(f"Error expanding environment variables in config: {e}")

            import yaml
            try:
                config_data = yaml.safe_load(content) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in configuration file: {e}")

            # Apply profile-specific sections if they exist
            if profile and 'profiles' in config_data and profile in config_data['profiles']:
                profile_config = config_data['profiles'][profile]
                # Merge profile config with base config
                final_config = _deep_merge(final_config, profile_config)
            else:
                # Regular config merge
                final_config = _deep_merge(final_config, config_data)

    return final_config


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries.
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result