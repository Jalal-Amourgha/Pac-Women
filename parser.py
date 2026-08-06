from typing import Dict
from pathlib import Path
import json, sys



class Parser():
    def __init__(self, file_path: str):
        self.data: Dict = {
            'highscore_filename': 'highscore.json',
            'level': [],
            'lives': 42,
            'pacgum': 10,
            'points_per_pacgum': 50,
            'points_per_super_pacgum': 50,
            'points_per_ghost': 200,
            'seed': 42,
            'level_max_time': 90
        }
        self.file_data = ""
        self._read_data(file_path)


    def _read_data(self, file_path: str) -> None:
        try:
            suffix: str = Path(file_path).suffix
            if (suffix != '.json'):
                sys.exit("[ERROR]: Config must be in '.json' format!")

            with open(file_path, 'r') as file:
                self.file_data = json.load(file)
            
        except Exception:
            sys.exit("[ERROR]: File Not found!")

        self._parse_data()

    def _parse_data(self) -> None:
        """
        Hada old logic kaml ghalet 7it makanch 3ndi config.json file
        """
        pass
        # int_attributes: set = {
        #     'level',
        #     'lives',
        #     'pacgum',
        #     'points_per_pacgum',
        #     'points_per_super_pacgum',
        #     'points_per_ghos',
        #     'seed',
        #     'level_max_time'
        #     }
        # pos_att: set = {
        #     'lives',
        #     'pacgum',
        #     'points_per_pacgum',
        #     'points_per_super_pacgum',
        #     'points_per_ghos',
        #     'seed',
        #     'level_max_time'
        #     }

        # for (key, val) in self.file_data.items():
        #     if (key in self.data):
        #         if (key == 'highscore_filename'):
        #             if (Path(val).suffix == '.json'):
        #                 self.data[key] = val

        #         if (key in int_attributes):
        #             try:
        #                 self.data[key] = int(val)

        #                 if (key in pos_att and self.data[key] <= 0):
        #                     sys.exit(f"[ERROR]: 'key' must be positive!")

        #             except Exception:
        #                 print(f"[ERROR]: Invalid '{key}' value!")
