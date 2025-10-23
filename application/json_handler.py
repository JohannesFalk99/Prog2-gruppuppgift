# #JsonReader, writer och updater för att hantera JSON-filer
# import jsonify
class JsonHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_json(self):
        with open(self.file_path, 'r') as file:
            return jsonify.load(file)

    def write_json(self, data):
        with open(self.file_path, 'w') as file:
            jsonify.dump(data, file)

    def update_json(self, data):
        current_data = self.read_json()
        current_data.update(data)
        self.write_json(current_data)