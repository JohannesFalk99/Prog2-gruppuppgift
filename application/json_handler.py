# JSON reader/writer/updater for handling JSON files
import json

class JsonHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def write_json(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def update_json(self, data):
        current_data = {}
        try:
            current_data = self.read_json()
        except Exception:
            # file may not exist or be empty
            current_data = {}
        current_data.update(data)
        self.write_json(current_data)