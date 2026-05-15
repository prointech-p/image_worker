"""Главный модуль приложения для работы с изображениями"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from threading import Thread
from modules.config_manager import ConfigManager
from modules.image_copier import ImageCopier
from modules.xlsx_creator import XlsxCreator


class ImageProcessingApp:
    """Главное приложение для обработки изображений"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка изображений")
        self.root.geometry("800x700")
        
        # Инициализация менеджера конфигурации
        self.config_manager = ConfigManager()
        
        # Переменные для интерфейса
        self.source_var = tk.StringVar(value=self.config_manager.get('img_source_folder', ''))
        self.dest_var = tk.StringVar(value=self.config_manager.get('img_destination_folder', ''))
        self.xlsx_source_var = tk.StringVar(value=self.config_manager.get('xlsx_source_folder', ''))
        self.xlsx_output_var = tk.StringVar(value=self.config_manager.get('xlsx_output_file', 'result.xlsx'))
        self.base_url_var = tk.StringVar(value=self.config_manager.get('base_url', 'https://example.com/images'))
        
        self.status_var = tk.StringVar(value="Готов к работе")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Создаем notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка копирования
        self.copy_frame = ttk.Frame(notebook)
        notebook.add(self.copy_frame, text="Копирование изображений")
        self.create_copy_tab()
        
        # Вкладка создания Excel
        self.excel_frame = ttk.Frame(notebook)
        notebook.add(self.excel_frame, text="Создание Excel")
        self.create_excel_tab()
        
    def create_copy_tab(self):
        """Создание вкладки копирования изображений"""
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.copy_frame, text="Настройки", padding=10)
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
        ttk.Button(buttons_frame, text="Сохранить настройки", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Загрузить настройки", command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        # Рамка для процесса копирования
        process_frame = ttk.LabelFrame(self.copy_frame, text="Копирование", padding=10)
        process_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(process_frame, text="Начать копирование", command=self.start_copying,
                  style="Accent.TButton").pack(pady=10)
        
        # Индикатор прогресса
        self.copy_progress_bar = ttk.Progressbar(process_frame, variable=self.progress_var,
                                                maximum=100, length=400)
        self.copy_progress_bar.pack(pady=5)
        
        ttk.Label(process_frame, textvariable=self.status_var).pack(pady=5)
        
        # Рамка для результатов
        results_frame = ttk.LabelFrame(self.copy_frame, text="Результаты выполнения", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Настраиваем вес строк в results_frame
        results_frame.grid_rowconfigure(0, weight=1)  # строка с текстовым полем растягивается
        results_frame.grid_rowconfigure(1, weight=0)  # строка с кнопкой не растягивается
        results_frame.grid_columnconfigure(0, weight=1)

        # Текстовое поле (строка 0)
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Кнопка очистки (строка 1)
        ttk.Button(results_frame, text="Очистить результаты",
                command=self.clear_results).grid(row=1, column=0, columnspan=2, pady=(5, 0))
    
    def create_excel_tab(self):
        """Создание вкладки создания Excel"""
        # Рамка для настроек
        settings_frame = ttk.LabelFrame(self.excel_frame, text="Настройки Excel", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Папка с изображениями
        ttk.Label(settings_frame, text="Папка с изображениями:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.xlsx_source_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="Обзор...", command=self.select_xlsx_source_folder).grid(row=0, column=2, padx=5)
        
        # Базовый URL
        ttk.Label(settings_frame, text="Базовый URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.base_url_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        
        # Выходной файл
        ttk.Label(settings_frame, text="Выходной файл:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(settings_frame, textvariable=self.xlsx_output_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(settings_frame, text="Выбрать...", command=self.select_output_file).grid(row=2, column=2, padx=5)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=10)
        ttk.Button(buttons_frame, text="Сохранить настройки", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Загрузить настройки", command=self.load_config).pack(side=tk.LEFT, padx=5)
        
        # Рамка для процесса создания Excel
        process_frame = ttk.LabelFrame(self.excel_frame, text="Создание Excel", padding=10)
        process_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(process_frame, text="Создать Excel файл", command=self.start_excel_creation,
                  style="Accent.TButton").pack(pady=10)
        
        # Индикатор прогресса
        self.excel_progress_var = tk.DoubleVar(value=0)
        self.excel_progress_bar = ttk.Progressbar(process_frame, variable=self.excel_progress_var,
                                                 maximum=100, length=400)
        self.excel_progress_bar.pack(pady=5)
        
        self.excel_status_var = tk.StringVar(value="Готов к созданию Excel")
        ttk.Label(process_frame, textvariable=self.excel_status_var).pack(pady=5)
        
        # Рамка для результатов Excel
        results_frame = ttk.LabelFrame(self.excel_frame, text="Результаты выполнения", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Настраиваем вес строк
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=0)
        results_frame.grid_columnconfigure(0, weight=1)

        # Текстовое поле (строка 0)
        self.excel_results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        excel_scrollbar = ttk.Scrollbar(results_frame, command=self.excel_results_text.yview)
        self.excel_results_text.configure(yscrollcommand=excel_scrollbar.set)

        self.excel_results_text.grid(row=0, column=0, sticky="nsew")
        excel_scrollbar.grid(row=0, column=1, sticky="ns")

        # Кнопка очистки (строка 1)
        ttk.Button(results_frame, text="Очистить результаты",
                command=self.clear_excel_results).grid(row=1, column=0, columnspan=2, pady=(5, 0))
    
    def select_source_folder(self):
        """Выбор исходной папки"""
        folder = filedialog.askdirectory(title="Выберите исходную папку")
        if folder:
            self.source_var.set(folder)
    
    def select_dest_folder(self):
        """Выбор папки назначения"""
        folder = filedialog.askdirectory(title="Выберите папку назначения")
        if folder:
            self.dest_var.set(folder)
    
    def select_xlsx_source_folder(self):
        """Выбор папки с изображениями для Excel"""
        folder = filedialog.askdirectory(title="Выберите папку с изображениями")
        if folder:
            self.xlsx_source_var.set(folder)
    
    def select_output_file(self):
        """Выбор выходного Excel файла"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить Excel файл как",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            self.xlsx_output_var.set(file_path)
    
    def save_config(self):
        """Сохранение текущих настроек"""
        self.config_manager.set('img_source_folder', self.source_var.get())
        self.config_manager.set('img_destination_folder', self.dest_var.get())
        self.config_manager.set('xlsx_source_folder', self.xlsx_source_var.get())
        self.config_manager.set('xlsx_output_file', self.xlsx_output_var.get())
        self.config_manager.set('base_url', self.base_url_var.get())
        
        if self.config_manager.save_config():
            messagebox.showinfo("Успех", "Настройки сохранены")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить настройки")
    
    def load_config(self):
        """Загрузка настроек из файла"""
        self.config_manager.reload()
        self.source_var.set(self.config_manager.get('img_source_folder', ''))
        self.dest_var.set(self.config_manager.get('img_destination_folder', ''))
        self.xlsx_source_var.set(self.config_manager.get('xlsx_source_folder', ''))
        self.xlsx_output_var.set(self.config_manager.get('xlsx_output_file', 'result.xlsx'))
        self.base_url_var.set(self.config_manager.get('base_url', 'https://example.com/images'))
        messagebox.showinfo("Успех", "Настройки загружены из файла")
    
    def log_message(self, message, error=False, excel_tab=False):
        """Добавление сообщения в текстовое поле результатов"""
        if excel_tab:
            self.excel_results_text.insert(tk.END, f"{message}\n")
            self.excel_results_text.see(tk.END)
        else:
            self.results_text.insert(tk.END, f"{message}\n")
            self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_results(self):
        """Очистка текстового поля результатов копирования"""
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_var.set("Готов к работе")
    
    def clear_excel_results(self):
        """Очистка текстового поля результатов Excel"""
        self.excel_results_text.delete(1.0, tk.END)
        self.excel_progress_var.set(0)
        self.excel_status_var.set("Готов к созданию Excel")
    
    def copy_images_thread(self):
        """Запуск копирования в отдельном потоке"""
        source_folder = Path(self.source_var.get())
        dest_folder = Path(self.dest_var.get())
        
        def progress_callback(progress, current, total):
            self.progress_var.set(progress)
            self.status_var.set(f"Копирование: {current} из {total}")
        
        def logger(message, error=False):
            self.log_message(message, error)
        
        copier = ImageCopier(logger)
        stats = copier.copy_images(source_folder, dest_folder, progress_callback)
        
        self.status_var.set("Копирование завершено")
        
        # Показываем сообщение о завершении
        self.root.after(0, lambda: messagebox.showinfo("Завершено",
                        f"Копирование завершено!\n"
                        f"Скопировано файлов: {stats['copied']}\n"
                        f"Перезаписано файлов: {stats['overwritten']}\n"
                        f"Ошибок: {stats['errors']}"))
    
    def start_copying(self):
        """Запуск процесса копирования"""
        if not self.source_var.get():
            messagebox.showwarning("Предупреждение", "Укажите исходную папку")
            return
        
        if not self.dest_var.get():
            messagebox.showwarning("Предупреждение", "Укажите папку назначения")
            return
        
        self.status_var.set("Выполняется копирование...")
        self.progress_var.set(0)
        self.clear_results()
        
        thread = Thread(target=self.copy_images_thread, daemon=True)
        thread.start()
    
    def create_excel_thread(self):
        """Запуск создания Excel в отдельном потоке"""
        folder_path = Path(self.xlsx_source_var.get())
        base_url = self.base_url_var.get()
        output_file = self.xlsx_output_var.get()
        
        def progress_callback(progress, current, total):
            self.excel_progress_var.set(progress)
            if total > 0:
                self.excel_status_var.set(f"Обработка: {current} из {total} товаров")
            else:
                self.excel_status_var.set(f"Прогресс: {progress:.1f}%")
        
        def logger(message, error=False):
            self.log_message(message, error, excel_tab=True)
        
        creator = XlsxCreator(logger)
        success = creator.create_excel(folder_path, base_url, output_file, progress_callback)
        
        self.excel_status_var.set("Создание Excel завершено" if success else "Ошибка при создании Excel")
        
        # Показываем сообщение о завершении
        result_msg = "Excel файл успешно создан!" if success else "Ошибка при создании Excel файла"
        self.root.after(0, lambda: messagebox.showinfo("Завершено", result_msg))
    
    def start_excel_creation(self):
        """Запуск процесса создания Excel"""
        if not self.xlsx_source_var.get():
            messagebox.showwarning("Предупреждение", "Укажите папку с изображениями")
            return
        
        if not self.base_url_var.get():
            messagebox.showwarning("Предупреждение", "Укажите базовый URL")
            return
        
        if not self.xlsx_output_var.get():
            messagebox.showwarning("Предупреждение", "Укажите имя выходного файла")
            return
        
        self.excel_status_var.set("Создание Excel файла...")
        self.excel_progress_var.set(0)
        self.clear_excel_results()
        
        thread = Thread(target=self.create_excel_thread, daemon=True)
        thread.start()


def main():
    root = tk.Tk()
    
    # Настройка стилей
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    app = ImageProcessingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()