import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import tomllib
import tomli_w
from threading import Thread
import time
from datetime import datetime

class ImageCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Копирование изображений")
        self.root.geometry("700x600")
        
        # Поддерживаемые расширения изображений
        self.image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
            '.webp', '.ico', '.svg', '.raw', '.cr2', '.nef', '.arw',
            '.jfif'
        }
        
        # Загрузка конфигурации
        self.config_file = Path("config.toml")
        self.config = self.load_config()
        
        # Переменные для интерфейса
        self.source_var = tk.StringVar(value=self.config.get('source_folder', ''))
        self.dest_var = tk.StringVar(value=self.config.get('destination_folder', ''))
        self.status_var = tk.StringVar(value="Готов к работе")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Создание интерфейса
        self.create_widgets()
        
    def load_config(self):
        """Загрузка конфигурации из TOML файла"""
        default_config = {
            'source_folder': '',
            'destination_folder': ''
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'rb') as f:
                    config = tomllib.load(f)
                    return config
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                return default_config
        else:
            # Создаем файл конфигурации по умолчанию
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Сохранение конфигурации в TOML файл"""
        if config is None:
            config = {
                'source_folder': self.source_var.get(),
                'destination_folder': self.dest_var.get()
            }
        
        try:
            with open(self.config_file, 'wb') as f:
                tomli_w.dump(config, f)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {e}")
            return False
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Исходная папка
        ttk.Label(settings_frame, text="Исходная папка:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.source_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="Обзор...", command=self.select_source_folder).grid(row=0, column=2, padx=5)
        
        # Папка назначения
        ttk.Label(settings_frame, text="Папка назначения:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.dest_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="Обзор...", command=self.select_dest_folder).grid(row=1, column=2, padx=5)
        
        # Кнопки управления настройками
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(buttons_frame, text="Сохранить настройки", command=self.save_current_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Загрузить настройки", command=self.reload_config).pack(side=tk.LEFT, padx=5)
        
        # Рамка для процесса копирования
        process_frame = ttk.LabelFrame(self.root, text="Копирование", padding=10)
        process_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(process_frame, text="Начать копирование", command=self.start_copying, 
                  style="Accent.TButton").pack(pady=10)
        
        # Индикатор прогресса
        self.progress_bar = ttk.Progressbar(process_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=5)
        
        ttk.Label(process_frame, textvariable=self.status_var).pack(pady=5)
        
        # Рамка для результатов
        results_frame = ttk.LabelFrame(self.root, text="Результаты выполнения", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Текстовое поле для вывода результатов
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка очистки результатов
        ttk.Button(results_frame, text="Очистить результаты", 
                  command=self.clear_results).pack(pady=5)
    
    def select_source_folder(self):
        """Выбор исходной папки через диалог"""
        folder = filedialog.askdirectory(title="Выберите исходную папку")
        if folder:
            self.source_var.set(folder)
    
    def select_dest_folder(self):
        """Выбор папки назначения через диалог"""
        folder = filedialog.askdirectory(title="Выберите папку назначения")
        if folder:
            self.dest_var.set(folder)
    
    def save_current_config(self):
        """Сохранение текущих настроек"""
        if self.save_config():
            messagebox.showinfo("Успех", "Настройки сохранены")
    
    def reload_config(self):
        """Перезагрузка настроек из файла"""
        self.config = self.load_config()
        self.source_var.set(self.config.get('source_folder', ''))
        self.dest_var.set(self.config.get('destination_folder', ''))
        messagebox.showinfo("Успех", "Настройки загружены из файла")
    
    def log_message(self, message, error=False):
        """Добавление сообщения в текстовое поле результатов"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if error:
            formatted_msg = f"[{timestamp}] ОШИБКА: {message}\n"
        else:
            formatted_msg = f"[{timestamp}] {message}\n"
        
        self.results_text.insert(tk.END, formatted_msg)
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_results(self):
        """Очистка текстового поля результатов"""
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Готов к работе")
    
    def find_photo_dirs(self, source_path):
        """Поиск папок с подпапкой 'исх' (регистронезависимо)"""
        photo_dirs = []
        
        try:
            for item in source_path.iterdir():
                if item.is_dir():
                    # Ищем подпапку 'исх' (регистронезависимо)
                    ish_folder = None
                    for subitem in item.iterdir():
                        if subitem.is_dir() and subitem.name.lower() == 'исх':
                            ish_folder = subitem
                            break
                    
                    if ish_folder:
                        photo_dirs.append((item.name, ish_folder))
                    else:
                        self.log_message(f"Папка '{item.name}' пропущена: нет подпапки 'исх'")
        except Exception as e:
            self.log_message(f"Ошибка при поиске папок: {e}", error=True)
        
        return photo_dirs
    
    def copy_images(self):
        """Основной процесс копирования изображений"""
        source_folder = Path(self.source_var.get())
        dest_folder = Path(self.dest_var.get())
        
        # Проверка существования папок
        if not source_folder.exists():
            self.log_message(f"Исходная папка не существует: {source_folder}", error=True)
            self.status_var.set("Ошибка: исходная папка не найдена")
            return
        
        if not dest_folder.exists():
            try:
                dest_folder.mkdir(parents=True)
                self.log_message(f"Создана папка назначения: {dest_folder}")
            except Exception as e:
                self.log_message(f"Не удалось создать папку назначения: {e}", error=True)
                self.status_var.set("Ошибка: не удалось создать папку назначения")
                return
        
        # Поиск папок с изображениями
        self.log_message("Поиск папок с подпапкой 'исх'...")
        photo_dirs = self.find_photo_dirs(source_folder)
        
        if not photo_dirs:
            self.log_message("Не найдено папок с подпапкой 'исх'")
            self.status_var.set("Завершено: папки не найдены")
            return
        
        self.log_message(f"Найдено папок с изображениями: {len(photo_dirs)}")
        
        # Сбор всех файлов для копирования
        all_files = []
        for folder_name, ish_folder in photo_dirs:
            try:
                for file_path in ish_folder.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in self.image_extensions:
                        all_files.append((folder_name, file_path))
            except Exception as e:
                self.log_message(f"Ошибка при чтении папки {folder_name}: {e}", error=True)
        
        if not all_files:
            self.log_message("Не найдено изображений для копирования")
            self.status_var.set("Завершено: изображения не найдены")
            return
        
        self.log_message(f"Найдено изображений для копирования: {len(all_files)}")
        
        # Копирование файлов (с перезаписью)
        copied_count = 0
        overwritten_count = 0
        error_count = 0
        
        for i, (folder_name, file_path) in enumerate(all_files):
            # Формируем новое имя файла
            name_without_ext = file_path.stem
            extension = file_path.suffix
            new_filename = f"{folder_name}_{name_without_ext}{extension}"
            
            # Путь назначения
            dest_path = dest_folder / new_filename
            
            # Проверка на существование файла
            is_overwrite = dest_path.exists()
            
            try:
                # Копирование файла (copy2 автоматически перезаписывает)
                shutil.copy2(file_path, dest_path)
                copied_count += 1
                
                if is_overwrite:
                    overwritten_count += 1
                    self.log_message(f"Перезаписан: {new_filename}")
                else:
                    self.log_message(f"Скопирован: {file_path.name} -> {new_filename}")
                
                # Обновление прогресса
                progress = (i + 1) / len(all_files) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Копирование: {copied_count} из {len(all_files)}")
                
            except Exception as e:
                error_count += 1
                self.log_message(f"Ошибка при копировании {file_path.name}: {e}", error=True)
        
        # Итоговый отчет
        self.progress_var.set(100)
        self.status_var.set("Копирование завершено")
        
        self.log_message("\n" + "="*50)
        self.log_message("ИТОГИ КОПИРОВАНИЯ:")
        self.log_message(f"Всего найдено папок: {len(photo_dirs)}")
        self.log_message(f"Всего найдено изображений: {len(all_files)}")
        self.log_message(f"Успешно скопировано: {copied_count}")
        self.log_message(f"Из них перезаписано: {overwritten_count}")
        self.log_message(f"Ошибок при копировании: {error_count}")
        self.log_message(f"Папка назначения: {dest_folder}")
        self.log_message("="*50)
    
        # Показываем сообщение о завершении
        messagebox.showinfo("Завершено", 
                        f"Копирование завершено!\n"
                        f"Скопировано файлов: {copied_count}\n"
                        f"Перезаписано файлов: {overwritten_count}\n"
                        f"Ошибок: {error_count}")
    
    def start_copying(self):
        """Запуск процесса копирования в отдельном потоке"""
        # Проверка заполнения полей
        if not self.source_var.get():
            messagebox.showwarning("Предупреждение", "Укажите исходную папку")
            return
        
        if not self.dest_var.get():
            messagebox.showwarning("Предупреждение", "Укажите папку назначения")
            return
        
        # Блокировка кнопки на время выполнения
        self.status_var.set("Выполняется копирование...")
        self.progress_var.set(0)
        
        # Запуск в отдельном потоке
        thread = Thread(target=self.copy_images, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    
    # Настройка стилей
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    app = ImageCopierApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()