"""Модуль для работы с конфигурацией"""
import tomllib
import tomli_w
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """Класс для управления конфигурацией приложения"""
    
    DEFAULT_CONFIG = {
        'img_source_folder': '',
        'img_destination_folder': '',
        'xlsx_source_folder': '',
        'xlsx_output_file': 'result.xlsx',
        'base_url': 'https://example.com/images'
    }
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из TOML файла"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'rb') as f:
                    config = tomllib.load(f)
                    # Заполняем недостающие значения по умолчанию
                    for key, value in self.DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Создаем файл конфигурации по умолчанию
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Сохранение конфигурации в TOML файл"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_path, 'wb') as f:
                tomli_w.dump(config, f)
            self.config = config
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Получение значения из конфигурации"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Установка значения в конфигурации"""
        self.config[key] = value
    
    def reload(self):
        """Перезагрузка конфигурации из файла"""
        self.config = self.load_config()