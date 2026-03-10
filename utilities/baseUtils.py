import os
import json
import importlib
import inspect

class ConfigReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config_data = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Config file not found: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_bot_token(self):
        return self.config_data.get("bot", {}).get("token", "")

    def get_bot_id(self):
        return self.config_data.get("bot", {}).get("id", "")

class Loader:
    def __init__(self, payload: dict[str, any], folder="cogs"):
        self.payload = payload
        self.client = payload.get("client")
        self.folder = folder

        for filename in os.listdir(self.folder):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"{self.folder}.{filename[:-3]}"
                class_name = filename[:-3][0].upper() + filename[:-3][1:] + "Cog"

                try:
                    module = importlib.import_module(module_name)
                    cog_class = getattr(module, class_name)

                    sig = inspect.signature(cog_class.__init__)
                    params = list(sig.parameters)[1:]

                    args_map = {
                        "client": self.payload['client'],
                        "config": self.payload['config']
                    }

                    args = [args_map[p] for p in params if p in args_map]

                    cog_instance = cog_class(*args)
                    self.client.add_cog(cog_instance)

                    print(f"Loaded: {class_name}")
                except (ImportError, AttributeError, TypeError) as e:
                    print(f"\n > Failed to load: {module_name}.{class_name}: {e}\n")