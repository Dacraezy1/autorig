"""
Example plugin for Python development environment setup.
"""
from .plugins import Plugin
from .config import RigConfig
from pathlib import Path
import subprocess
import os


class PythonDevPlugin(Plugin):
    """
    Plugin for setting up Python development environment.
    """
    
    @property
    def name(self) -> str:
        return "python-dev"
    
    def apply(self, config: RigConfig, dry_run: bool = False, verbose: bool = False) -> bool:
        if verbose:
            print(f"Applying Python development environment setup...")
        
        # Look for Python-specific configuration in the variables
        python_version = config.variables.get('python_version', '3.9')
        venv_name = config.variables.get('python_venv', '.venv')
        
        if dry_run:
            print(f"DRY RUN: Would setup Python {python_version} with venv {venv_name}")
            return True
        
        try:
            # Create a virtual environment if it doesn't exist
            if not hasattr(config, 'python') or not config.variables.get('skip_venv', False):
                current_dir = Path.cwd()
                venv_path = current_dir / venv_name
                
                if not venv_path.exists():
                    subprocess.run(['python3', '-m', 'venv', str(venv_path)], check=True)
                    if verbose:
                        print(f"Created virtual environment at {venv_path}")
                else:
                    if verbose:
                        print(f"Virtual environment already exists at {venv_path}")
            
            # Install packages if specified
            python_packages = config.variables.get('python_packages', [])
            if python_packages:
                venv_python = str(Path(venv_name) / 'bin' / 'python') if os.name != 'nt' else str(Path(venv_name) / 'Scripts' / 'python.exe')
                
                if Path(venv_python).exists():
                    cmd = [venv_python, '-m', 'pip', 'install'] + python_packages
                    subprocess.run(cmd, check=True)
                    if verbose:
                        print(f"Installed Python packages: {', '.join(python_packages)}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting up Python environment: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error in PythonDevPlugin: {e}")
            return False