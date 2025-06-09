import os
import json

class AuthManager:
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

    def verify_login(self, username, password):
        for file_name in ["admin.json", "user.json"]:
            file_path = os.path.join(self.base_dir, file_name)
            if not os.path.exists(file_path):
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    users = json.load(f)
                    for user in users:
                        if user["username"] == username and user["password"] == password:
                            return file_name.replace(".json", "")
                except json.JSONDecodeError:
                    continue
        return None
