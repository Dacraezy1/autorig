__version__ = "1.0.0"

# Import and register plugins
from .plugins import plugin_manager

try:
    from .python_plugin import PythonDevPlugin

    plugin_manager.register(PythonDevPlugin())
except ImportError:
    # Python plugin not available if dependencies are missing
    pass
