import os
import sys
import json
import inspect
import datetime
import importlib
import subprocess

class Requirements:
    def __init__(self, txt_file="requirements.txt"):
        if os.path.exists('/.dockerenv'):
            return

        requirements_path = txt_file

        if os.path.exists(requirements_path):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
            except subprocess.CalledProcessError:
                print("Error: Failed to install requirements from requirements.txt")
        else:
            print("Warning: requirements.txt not found")

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

    def get_supabase_url(self):
        return self.config_data.get("supabase", {}).get("url", "")

    def get_supabase_key(self):
        return self.config_data.get("supabase", {}).get("key", "")

class Loader:
    def __init__(self, payload: dict[str, any], folder="cogs"):
        self.payload = payload
        self.client = payload.get("client")
        self.folder = folder

        for filename in os.listdir(self.folder):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"{self.folder}.{filename[:-3]}"

                base_name = filename[:-3]
                pascal_case_name = "".join(word.capitalize() for word in base_name.split("_"))

                cog_class_name = f"{pascal_case_name}Cog"
                standard_class_name = pascal_case_name

                try:
                    module = importlib.import_module(module_name)

                    if hasattr(module, cog_class_name):
                        class_name = cog_class_name
                        cog_class = getattr(module, cog_class_name)
                    elif hasattr(module, standard_class_name):
                        class_name = standard_class_name
                        cog_class = getattr(module, standard_class_name)
                    else:
                        print(
                            f"\n > Failed to load: {module_name}: Class {cog_class_name} or {standard_class_name} not found.\n")
                        continue

                    sig = inspect.signature(cog_class.__init__)
                    params = list(sig.parameters)[1:]

                    args_map = {
                        "client": self.payload.get('client'),
                        "config": self.payload.get('config'),
                        "database": self.payload.get('database')
                    }

                    args = [args_map[p] for p in params if p in args_map]

                    cog_instance = cog_class(*args)
                    self.client.add_cog(cog_instance)

                    print(f"Loaded: {class_name}")

                except (ImportError, TypeError) as e:
                    print(f"\n > Failed to load: {module_name}.{class_name}: {e}\n")
                except Exception as e:
                    print(f"\n > Unexpected error loading {module_name}: {e}\n")

class TimeTools:
    HOURS_MAP = {
        1: ["8:00", "8:45"],
        2: ["8:50", "9:35"],
        3: ["9:45", "10:30"],
        4: ["10:40", "11:25"],
        5: ["11:45", "12:30"],
        6: ["12:40", "13:25"],
        7: ["13:35", "14:20"],
        8: ["14:30", "15:15"],
        9: ["15:30", "16:15"],
        10: ["16:25", "17:10"],
        11: ["17:20", "18:05"],
        12: ["18:15", "19:00"],
        13: ["19:05", "19:50"],
        14: ["19:55", "20:40"]
    }

    @staticmethod
    def get_hours(number: int):
        return TimeTools.HOURS_MAP.get(number, [])

    @staticmethod
    def short_year(year):
        year_str = str(year)
        base = str(datetime.date.today().year)
        prefix_len = len(base) - len(year_str)
        if prefix_len < 0:
            return year_str
        return base[:prefix_len] + year_str

class FormatTools:
    @staticmethod
    def zero_num(number: int, _len: int = 2):
        return str(number).zfill(_len)

class ListTools:
    @staticmethod
    def list_common(data: list[list]):
        if not data:
            return []

        first_list = data[0]
        other_sets = [set(sublist) for sublist in data[1:]]

        return [
            item for item in first_list
            if all(item in s for s in other_sets)
        ]