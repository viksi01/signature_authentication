import json
import tkinter as tk
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from encryption import encrypt, decrypt
from signature_processor import normalize_signature, interpolate_signature
from user_manager import UserManager

class SignatureAuth:
    def __init__(self, root):
        self.root = root
        self.root.title("Автентифікація за підписом")
        self.root.geometry("850x650")
        self.root.configure(bg='#f4f4f4')

        self.create_widgets()
        self.user_manager = UserManager()
        self.tolerance_threshold = 0.15
        self.sign_count = 0
        self.first_signature = None
        self.second_signature = None
        self.signature_data = []

    def create_widgets(self):
        # Заголовок
        self.title_label = tk.Label(self.root, text="Автентифікація за підписом", font=('Courier', 24, 'bold'),
                                    bg='#f4f4f4', fg='#333333')
        self.title_label.pack(pady=20)

        # Поле для вводу імені користувача
        self.name_frame = tk.Frame(self.root, bg='#f4f4f4')
        self.name_frame.pack(pady=10)

        self.name_label = tk.Label(self.name_frame, text="Ім'я користувача:", font=('Courier', 16), bg='#f4f4f4',
                                   fg='#555555')
        self.name_label.grid(row=0, column=0, padx=10, pady=5)

        self.name_entry = tk.Entry(self.name_frame, font=('Courier', 16), width=25, bg='#e8e8e8', fg='#333333',
                                   relief='flat', bd=1)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        # Полотно для підпису
        self.canvas_frame = tk.Frame(self.root, bg='#ffffff', relief='flat', bd=5)
        self.canvas_frame.pack(pady=20)

        self.canvas_label = tk.Label(self.canvas_frame, text="Полотно для підпису", font=('Courier', 14), bg='#ffffff',
                                     fg='#555555')
        self.canvas_label.pack(pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, width=500, height=250, bg='#ffffff', highlightthickness=0)
        self.canvas.pack()

        # Кнопки управління
        self.button_frame = tk.Frame(self.root, bg='#f4f4f4')
        self.button_frame.pack(pady=20)

        button_style = {
            'font': ('Courier', 14),
            'width': 22,
            'height': 2,
            'bg': '#88BF9A',
            'fg': '#333333',
            'relief': 'flat',
        }

        self.save_button = tk.Button(self.button_frame, text="Зберегти користувача", command=self.save_signature,
                                     **button_style)
        self.save_button.grid(row=0, column=0, padx=10)

        self.verify_button = tk.Button(self.button_frame, text="Перевірити користувача", command=self.verify_signature,
                                       **button_style)
        self.verify_button.grid(row=0, column=1, padx=10)

        self.clear_button = tk.Button(self.button_frame, text="Очистити полотно", command=self.clear_canvas,
                                      **button_style)
        self.clear_button.grid(row=0, column=2, padx=10)

        # Статус
        self.status_label = tk.Label(self.root, text="Очікування вводу...", font=('Courier', 14), bg='#f4f4f4',
                                     fg='#777777')
        self.status_label.pack(pady=10)

        # Підключення подій для малювання
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

    def start_draw(self, event):
        self.is_drawing = True
        self.signature_data = [(event.x, event.y)]

    def draw(self, event):
        if self.is_drawing:
            x, y = event.x, event.y
            self.signature_data.append((x, y))
            self.canvas.create_line(self.signature_data[-2][0], self.signature_data[-2][1], x, y, width=3)

    def end_draw(self, event):
        self.is_drawing = False

    def clear_canvas(self):
        self.canvas.delete("all")
        self.signature_data = []


    def save_signature(self):
        username = self.name_entry.get().strip()
        if not username:
            self.status_label.config(text="Статус: Введіть ім'я користувача.")
            return

        if username in self.user_manager.users:
            self.status_label.config(text="Статус: Ім'я користувача вже існує.")
            return

        if not self.signature_data:
            self.status_label.config(text="Статус: Намалюйте підпис.")
            return

        if self.signature_data:
            normalized_signature = normalize_signature(self.signature_data)
            interpolated_signature = interpolate_signature(normalized_signature)

            if self.sign_count == 0:
                self.first_signature = interpolated_signature
                self.sign_count += 1
                self.status_label.config(text="Статус: Намалюйте підпис ще раз для підтвердження.")
                self.clear_canvas()
            elif self.sign_count == 1:
                average_signature = [
                    ((x1 + x2) / 2, (y1 + y2) / 2)
                    for (x1, y1), (x2, y2) in zip(self.first_signature, interpolated_signature)
                ]

                # Шифруємо підпис перед збереженням
                signature_str = json.dumps(average_signature)
                encrypted_signature = encrypt(signature_str)

                self.user_manager.users[username] = encrypted_signature
                self.user_manager.save_users()
                self.status_label.config(text="Статус: Підпис успішно збережений.")
                self.sign_count = 0
                self.clear_canvas()

    def verify_signature(self):
        username = self.name_entry.get().strip()
        if not username:
            self.status_label.config(text="Статус: Введіть ім'я користувача.")
            return

        if username not in self.user_manager.users:
            self.status_label.config(text="Статус: Користувача не знайдено.")
            return

        if not self.signature_data:
            self.status_label.config(text="Статус: Намалюйте підпис.")
            return

        if self.signature_data:
            encrypted_signature = self.user_manager.users[username]
            decrypted_signature_str = decrypt(encrypted_signature)
            saved_signature = json.loads(decrypted_signature_str)

            normalized_signature = normalize_signature(self.signature_data)
            interpolated_signature = interpolate_signature(normalized_signature)

            distance, _ = fastdtw(saved_signature, interpolated_signature, dist=euclidean)
            if distance < self.tolerance_threshold * len(saved_signature):
                self.status_label.config(text=f"Статус: Підпис підтверджено")
            else:
                self.status_label.config(text=f"Статус: Підпис не збігається")
            self.clear_canvas()
