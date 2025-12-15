import abc
from typing import List
from .config import RigConfig


class Plugin(abc.ABC):
    """
    Abstract base class for AutoRig plugins.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The name of the plugin."""
        pass

    @abc.abstractmethod
    def apply(
        self, config: RigConfig, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """
        Apply the plugin's functionality based on the configuration.

        Returns True if successful, False otherwise.
        """
        pass


class PluginManager:
    """
    Manages loading and executing plugins.
    """

    def __init__(self) -> None:
        self.plugins: List[Plugin] = []

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        self.plugins.append(plugin)

    def register_from_module(self, module_name: str) -> None:
        """Dynamically load and register plugins from a module."""
        try:
            module = __import__(module_name, fromlist=[""])
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Plugin)
                    and attr != Plugin
                ):
                    try:
                        plugin_instance = attr()
                        self.register(plugin_instance)
                    except Exception:
                        # Skip plugins that can't be instantiated
                        continue
        except ImportError:
            pass  # Module not available

    def get_available_plugins(self) -> List[str]:
        """Return list of available plugin names."""
        return [plugin.name for plugin in self.plugins]

    def run_plugin(
        self, name: str, config: RigConfig, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Run a specific plugin by name."""
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin.apply(config, dry_run, verbose)

        raise ValueError(f"Plugin '{name}' not found")

    def run_all_plugins(
        self, config: RigConfig, dry_run: bool = False, verbose: bool = False
    ) -> None:
        """Run all registered plugins."""
        for plugin in self.plugins:
            try:
                plugin.apply(config, dry_run, verbose)
            except Exception as e:
                print(f"Plugin {plugin.name} failed: {e}")


class DotfilePlugin(Plugin):
    """
    Built-in plugin for managing dotfiles - a more advanced version of the core functionality.
    """

    @property
    def name(self) -> str:
        return "dotfiles"

    def apply(
        self, config: RigConfig, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        # This would be the enhanced dotfile management logic
        return True


# Global plugin manager instance
plugin_manager = PluginManager()
