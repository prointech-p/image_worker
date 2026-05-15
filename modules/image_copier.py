"""Модуль для копирования изображений"""
import shutil
from pathlib import Path
from typing import List, Tuple, Callable
from datetime import datetime


class ImageCopier:
    """Класс для копирования изображений из структуры папок"""
    
    # Поддерживаемые расширения изображений
    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
        '.webp', '.ico', '.svg', '.raw', '.cr2', '.nef', '.arw', '.jfif'
    }
    
    def __init__(self, logger: Callable = None):
        """
        Инициализация копировщика
        
        Args:
            logger: Функция для логирования сообщений
        """
        self.logger = logger or print
        self.copied_count = 0
        self.overwritten_count = 0
        self.error_count = 0
    
    def log(self, message: str, error: bool = False):
        """Логирование сообщений"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "ОШИБКА: " if error else ""
        self.logger(f"[{timestamp}] {prefix}{message}", error)
    
    def find_photo_dirs(self, source_path: Path) -> List[Tuple[str, Path]]:
        """
        Поиск папок с подпапкой 'исх' (регистронезависимо)
        
        Args:
            source_path: Путь к исходной папке
            
        Returns:
            Список кортежей (имя_папки, путь_к_исх)
        """
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
                        self.log(f"Папка '{item.name}' пропущена: нет подпапки 'исх'")
        except Exception as e:
            self.log(f"Ошибка при поиске папок: {e}", error=True)
        
        return photo_dirs
    
    def copy_images(self, source_folder: Path, dest_folder: Path, 
                   progress_callback: Callable = None) -> dict:
        """
        Основной процесс копирования изображений
        
        Args:
            source_folder: Исходная папка
            dest_folder: Папка назначения
            progress_callback: Функция обратного вызова для обновления прогресса
            
        Returns:
            Словарь со статистикой копирования
        """
        # Сброс счетчиков
        self.copied_count = 0
        self.overwritten_count = 0
        self.error_count = 0
        
        # Проверка существования папок
        if not source_folder.exists():
            self.log(f"Исходная папка не существует: {source_folder}", error=True)
            return self._get_stats()
        
        if not dest_folder.exists():
            try:
                dest_folder.mkdir(parents=True)
                self.log(f"Создана папка назначения: {dest_folder}")
            except Exception as e:
                self.log(f"Не удалось создать папку назначения: {e}", error=True)
                return self._get_stats()
        
        # Поиск папок с изображениями
        self.log("Поиск папок с подпапкой 'исх'...")
        photo_dirs = self.find_photo_dirs(source_folder)
        
        if not photo_dirs:
            self.log("Не найдено папок с подпапкой 'исх'")
            return self._get_stats()
        
        self.log(f"Найдено папок с изображениями: {len(photo_dirs)}")
        
        # Сбор всех файлов для копирования
        all_files = []
        for folder_name, ish_folder in photo_dirs:
            try:
                for file_path in ish_folder.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                        all_files.append((folder_name, file_path))
            except Exception as e:
                self.log(f"Ошибка при чтении папки {folder_name}: {e}", error=True)
        
        if not all_files:
            self.log("Не найдено изображений для копирования")
            return self._get_stats()
        
        self.log(f"Найдено изображений для копирования: {len(all_files)}")
        
        # Копирование файлов
        for i, (folder_name, file_path) in enumerate(all_files):
            # Формируем новое имя файла
            new_filename = f"{folder_name}_{file_path.stem}{file_path.suffix}"
            dest_path = dest_folder / new_filename
            
            # Проверка на существование файла
            is_overwrite = dest_path.exists()
            
            try:
                shutil.copy2(file_path, dest_path)
                self.copied_count += 1
                
                if is_overwrite:
                    self.overwritten_count += 1
                    self.log(f"Перезаписан: {new_filename}")
                else:
                    self.log(f"Скопирован: {file_path.name} -> {new_filename}")
                
                # Обновление прогресса
                if progress_callback:
                    progress = (i + 1) / len(all_files) * 100
                    progress_callback(progress, self.copied_count, len(all_files))
                
            except Exception as e:
                self.error_count += 1
                self.log(f"Ошибка при копировании {file_path.name}: {e}", error=True)
        
        # Итоговый отчет
        self.log("\n" + "="*50)
        self.log("ИТОГИ КОПИРОВАНИЯ:")
        self.log(f"Всего найдено папок: {len(photo_dirs)}")
        self.log(f"Всего найдено изображений: {len(all_files)}")
        self.log(f"Успешно скопировано: {self.copied_count}")
        self.log(f"Из них перезаписано: {self.overwritten_count}")
        self.log(f"Ошибок при копировании: {self.error_count}")
        self.log(f"Папка назначения: {dest_folder}")
        self.log("="*50)
        
        return self._get_stats()
    
    def _get_stats(self) -> dict:
        """Получение статистики копирования"""
        return {
            'copied': self.copied_count,
            'overwritten': self.overwritten_count,
            'errors': self.error_count
        }