# Импорт необходимых модулей Kivy для создания интерфейса
from kivy.app import App  # Базовый класс для приложения Kivy
from kivy.uix.boxlayout import BoxLayout  # Контейнер для виджетов
from kivy.uix.button import Button  # Кнопка
from kivy.uix.textinput import TextInput  # Поле ввода текста
from kivy.uix.label import Label  # Текстовая метка
from kivy.uix.popup import Popup  # Всплывающее окно
from kivy.uix.scrollview import ScrollView  # Прокручиваемая область
from kivy.uix.gridlayout import GridLayout  # Сеточный макет

# Импорт модулей для шифрования и работы с файлами
from cryptography.fernet import Fernet  # Шифрование данных
import json  # Работа с JSON
import os  # Работа с файловой системой

class EncryptedNotesApp(App):
    def build(self):
        # Инициализация ключа шифрования и загрузка заметок
        self.key = self.load_or_generate_key()  # Получаем или создаем ключ
        self.notes = self.load_notes()  # Загружаем сохраненные заметки
        
        # Основной вертикальный контейнер
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Заголовок приложения
        self.title_label = Label(text="Шифрованные заметки", size_hint=(1, 0.1))
        self.layout.add_widget(self.title_label)
        
        # Поле для ввода новой заметки
        self.note_input = TextInput(hint_text="Введите текст заметки...", size_hint=(1, 0.3))
        self.layout.add_widget(self.note_input)
        
        # Горизонтальный контейнер для кнопок
        buttons_layout = BoxLayout(spacing=5, size_hint=(1, 0.1))
        
        # Кнопка сохранения
        self.save_btn = Button(text="Сохранить")
        self.save_btn.bind(on_press=self.save_note)  # Привязка обработчика
        buttons_layout.add_widget(self.save_btn)
        
        # Кнопка очистки
        self.clear_btn = Button(text="Очистить")
        self.clear_btn.bind(on_press=self.clear_input)  # Привязка обработчика
        buttons_layout.add_widget(self.clear_btn)
        
        self.layout.add_widget(buttons_layout)
        
        # Область с прокруткой для списка заметок
        self.notes_scroll = ScrollView(size_hint=(1, 0.5))
        self.notes_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.notes_grid.bind(minimum_height=self.notes_grid.setter('height'))
        self.notes_scroll.add_widget(self.notes_grid)
        self.layout.add_widget(self.notes_scroll)
        
        # Обновление списка заметок
        self.update_notes_list()
        return self.layout
    
    def load_or_generate_key(self):
        """Загружает существующий ключ или генерирует новый"""
        key_file = "encryption_key.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()  # Чтение существующего ключа
        else:
            key = Fernet.generate_key()  # Генерация нового ключа
            with open(key_file, "wb") as f:
                f.write(key)  # Сохранение ключа
            return key
    
    def encrypt(self, text):
        """Шифрует текст"""
        cipher = Fernet(self.key)
        return cipher.encrypt(text.encode()).decode()  # Возвращает зашифрованную строку
    
    def decrypt(self, encrypted_text):
        """Расшифровывает текст"""
        cipher = Fernet(self.key)
        return cipher.decrypt(encrypted_text.encode()).decode()  # Возвращает расшифрованную строку
    
    def load_notes(self):
        """Загружает заметки из файла"""
        notes_file = "notes.json"
        if os.path.exists(notes_file):
            with open(notes_file, "r") as f:
                encrypted_notes = json.load(f)
                return [{"text": self.decrypt(note["text"])} for note in encrypted_notes]  # Расшифровка всех заметок
        return []  # Возвращает пустой список, если файла нет
    
    def save_notes(self):
        """Сохраняет заметки в файл"""
        notes_file = "notes.json"
        encrypted_notes = [{"text": self.encrypt(note["text"])} for note in self.notes]  # Шифрование всех заметок
        with open(notes_file, "w") as f:
            json.dump(encrypted_notes, f)  # Сохранение в JSON
    
    def save_note(self, instance):
        """Обработчик сохранения заметки"""
        note_text = self.note_input.text.strip()
        if note_text:
            self.notes.append({"text": note_text})  # Добавление новой заметки
            self.save_notes()  # Сохранение в файл
            self.update_notes_list()  # Обновление интерфейса
            self.clear_input()  # Очистка поля ввода
        else:
            self.show_popup("Ошибка", "Заметка не может быть пустой!")  # Показ ошибки
    
    def clear_input(self, instance=None):
        """Очищает поле ввода"""
        self.note_input.text = ""
    
    def update_notes_list(self):
        """Обновляет список заметок в интерфейсе"""
        self.notes_grid.clear_widgets()  # Очистка текущего списка
        
        # Добавление каждой заметки с кнопкой удаления
        for note in self.notes:
            note_layout = BoxLayout(size_hint_y=None, height=40)
            note_label = Label(text=note["text"], size_hint=(0.8, 1), halign="left", valign="middle")
            note_label.bind(size=note_label.setter('text_size'))
            
            delete_btn = Button(text="✕", size_hint=(0.2, 1))
            delete_btn.note = note  # Сохраняем ссылку на заметку
            delete_btn.bind(on_press=self.delete_note)  # Привязка обработчика
            
            note_layout.add_widget(note_label)
            note_layout.add_widget(delete_btn)
            self.notes_grid.add_widget(note_layout)
    
    def delete_note(self, instance):
        """Удаляет заметку"""
        self.notes.remove(instance.note)  # Удаление из списка
        self.save_notes()  # Сохранение изменений
        self.update_notes_list()  # Обновление интерфейса
    
    def show_popup(self, title, message):
        """Показывает всплывающее окно"""
        popup = Popup(title=title, size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint=(1, 0.3))
        ok_btn.bind(on_press=popup.dismiss)  # Закрытие по нажатию
        content.add_widget(ok_btn)
        popup.content = content
        popup.open()

# Запуск приложения
if __name__ == "__main__":
    EncryptedNotesApp().run()