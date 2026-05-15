"""Модуль для создания Excel файла со ссылками на изображения"""
from pathlib import Path
from collections import defaultdict
import openpyxl
from openpyxl.styles import Alignment
from typing import Dict, List, Callable


class XlsxCreator:
    """Класс для создания Excel файлов со ссылками на изображения"""
    
    # Поддерживаемые расширения изображений
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(self, logger: Callable = None):
        """
        Инициализация создателя Excel файлов
        
        Args:
            logger: Функция для логирования сообщений
        """
        self.logger = logger or print
    
    def log(self, message: str, error: bool = False):
        """Логирование сообщений"""
        prefix = "ОШИБКА: " if error else ""
        self.logger(prefix + message, error)
    
    def extract_product_code(self, filename: str) -> str:
        """
        Извлечение кода товара из имени файла (все что до последнего '_')
        
        Args:
            filename: Имя файла
            
        Returns:
            Код товара
        """
        # Убираем расширение
        name_without_ext = Path(filename).stem
        # Ищем последнее подчеркивание
        if '_' in name_without_ext:
            return name_without_ext.rsplit('_', 1)[0]
        return name_without_ext
    
    def process_images(self, folder_path: Path, base_url: str) -> Dict[str, List[str]]:
        """
        Обработка всех изображений в папке
        
        Args:
            folder_path: Путь к папке с изображениями
            base_url: Базовый URL для формирования ссылок
            
        Returns:
            Словарь {код_товара: [список_имен_файлов]}
        """
        products = defaultdict(list)
        
        # Проверка существования папки
        if not folder_path.exists():
            self.log(f"Папка не существует: {folder_path}", error=True)
            return {}
        
        # Проходим по всем файлам в папке
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.IMAGE_EXTENSIONS:
                product_code = self.extract_product_code(file_path.name)
                products[product_code].append(file_path.name)
        
        # Сортируем файлы для каждого товара
        for code in products:
            products[code].sort()
        
        return products
    
    def create_excel(self, folder_path: Path, base_url: str, 
                    output_file: str, progress_callback: Callable = None) -> bool:
        """
        Создание Excel файла с результатами
        
        Args:
            folder_path: Путь к папке с изображениями
            base_url: Базовый URL для формирования ссылок
            output_file: Имя выходного файла
            progress_callback: Функция обратного вызова для обновления прогресса
            
        Returns:
            True в случае успеха, False в случае ошибки
        """
        try:
            self.log(f"Обработка папки: {folder_path}")
            self.log(f"Базовый URL: {base_url}")
            
            # Обработка изображений
            products = self.process_images(folder_path, base_url)
            
            if not products:
                self.log("В папке не найдено изображений!", error=True)
                return False
            
            if progress_callback:
                progress_callback(10, 0, len(products))
            
            # Создание Excel файла
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Products"
            
            # Заголовки
            sheet["A1"] = "Id"
            sheet["B1"] = "ImageUrls"
            sheet.column_dimensions["A"].width = 20
            sheet.column_dimensions["B"].width = 80
            
            # Заполнение данных
            row = 2
            total_rows = len(products)
            
            for idx, (product_code, images) in enumerate(products.items()):
                # Формируем ссылки
                links = [f"{base_url}/{img_name}" for img_name in images]
                links_str = " | ".join(links)
                
                # Записываем в ячейки
                sheet[f"A{row}"] = product_code
                sheet[f"B{row}"] = links_str
                
                # Настройка переноса текста
                sheet[f"B{row}"].alignment = Alignment(wrap_text=True, vertical="top")
                
                row += 1
                
                # Обновление прогресса
                if progress_callback:
                    progress = 10 + (idx + 1) / total_rows * 90
                    progress_callback(progress, idx + 1, total_rows)
            
            # Сохраняем файл
            output_path = Path(output_file)
            workbook.save(output_path)
            
            self.log(f"Excel файл создан: {output_path.absolute()}")
            self.log(f"Обработано товаров: {len(products)}")
            self.log(f"Всего файлов: {sum(len(imgs) for imgs in products.values())}")
            
            return True
            
        except Exception as e:
            self.log(f"Ошибка при создании Excel файла: {e}", error=True)
            return False