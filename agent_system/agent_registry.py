import os
import yaml
import importlib


class AgentRegistry:
    """
    Loads agent class mappings from a YAML config and instantiates agents by name.
    """
    def __init__(self, config_path: str = None, plugins_path: str = None):
        # Load core agents
        self.config_path = config_path or os.getenv(
            'AGENTS_CONFIG_PATH', 'config/agents.yaml'
        )
        with open(self.config_path, 'r') as f:
            self.registry = yaml.safe_load(f) or {}
        # Load plugin agents
        from agent_system.plugin_manager import PluginManager

        pm = PluginManager(config_path=plugins_path)
        for name in pm.list_plugins():
            self.registry[name] = pm.plugins[name]

    def get_agent(self, name: str, **kwargs):
        """
        Instantiate and return the agent with the given name.
        Additional kwargs are passed to the agent constructor.
        """
        if name not in self.registry:
            raise KeyError(f"Agent '{name}' not found in registry")
        entry = self.registry[name]
        module_name = entry['module']
        class_name = entry['class']
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls(**kwargs)
