"""Lazy import optimization for faster startup."""

from typing import Any, Callable, Optional


class LazyLoader:
    """Lazy loader for modules to improve startup time."""

    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: Optional[Any] = None

    def __call__(self) -> Any:
        """Load and return the module."""
        if self._module is None:
            import importlib

            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the loaded module."""
        if self._module is None:
            self()
        return getattr(self._module, name)


class LazyDict(dict):
    """Dictionary with lazy loading support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loaders: dict[str, Callable] = {}

    def add_lazy_loader(self, key: str, loader: Callable[[], Any]) -> None:
        """Add a lazy loader for a key."""
        self._loaders[key] = loader

    def __getitem__(self, key: str) -> Any:
        """Get item with lazy loading."""
        if key in self._loaders:
            if key not in self:
                self[key] = self._loaders[key]()
            del self._loaders[key]
        return super().__getitem__(key)


def lazy_import(module_path: str) -> Callable[[], Any]:
    """Decorator for lazy importing a module."""

    def wrapper() -> Any:
        import importlib

        return importlib.import_module(module_path)

    return wrapper
