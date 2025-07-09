import os
import yaml
import importlib


class PluginManager:
    """
    Loads plugin definitions from a YAML config and provides access to plugin classes.
    """
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.getenv(
            'PLUGINS_CONFIG_PATH', 'config/plugins.yaml'
        )
        with open(self.config_path, 'r') as f:
            self.plugins = yaml.safe_load(f) or {}

    def list_plugins(self):
        """Return available plugin names."""
        return list(self.plugins.keys())

    def get_plugin(self, name: str, **kwargs):
        """
        Instantiate and return the plugin class for the given name.
        """
        if name not in self.plugins:
            raise KeyError(f"Plugin '{name}' not found in registry")
        entry = self.plugins[name]
        module = importlib.import_module(entry['module'])
        cls = getattr(module, entry['class'])
        return cls(**kwargs)
