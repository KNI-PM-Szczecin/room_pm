import os
import sys
import json
import inspect
import datetime
import importlib
import subprocess

class Requirements:
    def __init__(self, txt_file="requirements.txt"):
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

class HoursConverter:
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

    def __init__(self, number: int):
        self.number = number

    def __getitem__(self, index: int):
        time_list = self.HOURS_MAP.get(self.number, [])
        return time_list[index]

    def __str__(self):
        time = self.HOURS_MAP.get(self.number, "Incorrect value")
        return str(time)

class ZeroNum:
    def __init__(self, number: int, _len: int = 2):
        self.len = _len
        self.number = str(number)

    def __str__(self):
        return self.number.zfill(self.len)

class ShortYear:
    def __init__(self, year):
        self.year = str(year)
        self.base = str(datetime.date.today().year)

    def __str__(self):
        prefix_len = len(self.base) - len(self.year)
        if prefix_len < 0:
            return self.year
        return self.base[:prefix_len] + self.year

class ListCommon:
    def __init__(self, data: list[list]):
        if not data:
            self.result = []
            return

        first_list = data[0]
        other_sets = [set(sublist) for sublist in data[1:]]

        self.result = [
            item for item in first_list
            if all(item in s for s in other_sets)
        ]

    def __str__(self):
        return str(self.result)

    def __repr__(self):
        return f"ListCommon({self.result})"

    def __iter__(self):
        return iter(self.result)

    def __getitem__(self, index):
        return self.result[index]

    def __len__(self):
        return len(self.result)