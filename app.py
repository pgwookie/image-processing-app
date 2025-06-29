import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")

        self.img = None  # Загруженное изображение
        self.img_original = None  # Оригинал для восстановления

        # Кнопки для выбора действия
        self.load_button = tk.Button(root, text="Загрузить изображение", command=self.load_image)
        self.load_button.pack()

        self.webcam_button = tk.Button(root, text="Подключиться к веб-камере", command=self.capture_webcam)
        self.webcam_button.pack()

        self.red_button = tk.Button(root, text="Красный канал", command=lambda: self.show_channel("Red"))
        self.red_button.pack()

        self.green_button = tk.Button(root, text="Зеленый канал", command=lambda: self.show_channel("Green"))
        self.green_button.pack()

        self.blue_button = tk.Button(root, text="Синий канал", command=lambda: self.show_channel("Blue"))
        self.blue_button.pack()

        self.resize_button = tk.Button(root, text="Изменить размер изображения", command=self.resize_image)
        self.resize_button.pack()

        self.brightness_button = tk.Button(root, text="Понизить яркость", command=self.decrease_brightness)
        self.brightness_button.pack()

        self.circle_button = tk.Button(root, text="Нарисовать круг", command=self.draw_circle)
        self.circle_button.pack()

        self.canvas = tk.Canvas(root)
        self.canvas.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            # Проверка, существует ли файл
            if not os.path.isfile(file_path):
                messagebox.showerror("Ошибка", "Файл не найден. Проверьте путь к файлу.")
                return
            print(f"Загружен файл: {file_path}")  # Для проверки пути
            self.img = cv2.imread(file_path)
            if self.img is None:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {file_path}")
                print("Ошибка при загрузке изображения:", file_path)  # Дополнительный лог
                return
            self.img_original = self.img.copy()
            self.show_image(self.img)

    def capture_webcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удается подключиться к веб-камере.")
            return
        ret, frame = cap.read()
        cap.release()
        if ret:
            self.img = frame
            self.img_original = self.img.copy()
            self.show_image(self.img)

    def show_image(self, img):
        # Масштабирование изображения до размера канваса
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Получаем размеры изображения
        img_height, img_width = img.shape[:2]

        # Вычисляем масштаб
        scale_width = canvas_width / img_width
        scale_height = canvas_height / img_height
        scale = min(scale_width, scale_height)

        # Масштабируем изображение
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        img_resized = cv2.resize(img, (new_width, new_height))

        # Конвертируем изображение в формат для Tkinter
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(img_pil)

        # Отображаем изображение на канвасе
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        self.canvas.image = img_tk

    def show_channel(self, channel):
        if self.img is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        if channel == "Red":
            img_channel = self.img[:, :, 2]
        elif channel == "Green":
            img_channel = self.img[:, :, 1]
        elif channel == "Blue":
            img_channel = self.img[:, :, 0]

        img_channel_colored = cv2.merge([img_channel, img_channel, img_channel])
        self.show_image(img_channel_colored)

    def resize_image(self):
        if self.img is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        # Запрашиваем размеры через диалоговое окно
        width = simpledialog.askinteger("Изменение размера", "Введите новую ширину изображения:")
        height = simpledialog.askinteger("Изменение размера", "Введите новую высоту изображения:")

        if width is None or height is None:
            return

        self.img = cv2.resize(self.img, (width, height))
        self.show_image(self.img)

    def decrease_brightness(self):
        if self.img is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        # Запрашиваем значение яркости через диалоговое окно
        value = simpledialog.askinteger("Понижение яркости", "Введите величину понижения яркости (0-255):")
        if value is None:
            return

        if value < 0 or value > 255:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите значение от 0 до 255.")
            return

        # Преобразуем изображение в тип данных float32 для выполнения операции вычитания
        img_float = self.img.astype(np.float32)

        # Понижаем яркость по каждому каналу
        img_bright = img_float - value

        # Ограничиваем значения пикселей (чтобы они оставались в диапазоне 0-255)
        img_bright = np.clip(img_bright, 0, 255)

        # Преобразуем обратно в тип uint8 для отображения
        self.img = img_bright.astype(np.uint8)
        self.show_image(self.img)

    def draw_circle(self):
        if self.img is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return

        # Запрашиваем координаты и радиус через диалоговые окна
        center_x = simpledialog.askinteger("Рисование круга", "Введите координату X центра круга:")
        center_y = simpledialog.askinteger("Рисование круга", "Введите координату Y центра круга:")
        radius = simpledialog.askinteger("Рисование круга", "Введите радиус круга:")

        if center_x is None or center_y is None or radius is None:
            return

        color = (0, 0, 255)  # Красный цвет
        thickness = 2
        cv2.circle(self.img, (center_x, center_y), radius, color, thickness)
        self.show_image(self.img)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
