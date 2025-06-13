import json
import os
import random

class UserManager:
    def __init__(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

    def list(self):
        all_users = []

        for file_name in ["admin.json", "user.json"]:
            file_path = os.path.join(self.base_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        users = json.load(f)
                        all_users.extend(users)
                    except json.JSONDecodeError:
                        continue

        return all_users

    def generate_store_code(self):
        return "STORE-" + ''.join(random.choices('0123456789', k=6))

    def email_exists(self, email):
        for file_name in ["admin.json", "user.json"]:
            file_path = os.path.join(self.base_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        users = json.load(f)
                        for u in users:
                            if u.get("email") == email:
                                return True
                    except json.JSONDecodeError:
                        pass
        return False

    def save_user(self, user_data, role):
        file_path = os.path.join(self.base_dir, f"{role}.json")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

        try:
            users = []
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        users = json.load(f)
                    except json.JSONDecodeError:
                        pass

            users.append(user_data)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
        
    def delete(self, email):
        success = False
        for file_name in ["admin.json", "user.json"]:
            file_path = os.path.join(self.base_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        users = json.load(f)
                    except json.JSONDecodeError:
                        continue

                new_users = [u for u in users if u.get("email") != email]
                if len(new_users) < len(users):
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(new_users, f, indent=4, ensure_ascii=False)
                    success = True

        return success

