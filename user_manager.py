import json
import os

class UserManager:
    def __init__(self, user_data_file = 'users_data.json'):
        self.user_data_file = user_data_file
        self.users = self.load_users()

    #Завантажує користувачів з файлу
    def load_users(self):
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError):
                return {}
        return {}

    #Зберігає користувачів у файл
    def save_users(self):
        with open(self.user_data_file, 'w') as f:
            json.dump(self.users, f)