import sys

from PyQt6.QtWidgets import QApplication

from controller.catalog_controller import CatalogController
from model.catalog_manager import CatalogManager
# Импорты архитектуры MVC
from model.xml_handler import XMLHandler
from view.main_window import MainWindow


def main():
    # 1. Инициализация приложения PyQt6
    app = QApplication(sys.argv)
    app.setApplicationName("Каталог книг (Вариант 15)")
    app.setStyle("Fusion")  # Кроссплатформенный стиль интерфейса

    # Файл для автосохранения/загрузки по умолчанию
    DEFAULT_XML = "catalog_example.xml"

    # 2. Создание Model
    xml_handler = XMLHandler(DEFAULT_XML)
    model = CatalogManager(xml_handler)

    # 3. Автозагрузка данных (если файл уже существует)
    # if os.path.exists(DEFAULT_XML):
    # 4. Создание View и Controller
    # View создаётся без параметров (MVC: View не должен зависеть от Model)
    view = MainWindow()
    # Controller связывает View и Model, настраивает сигналы и первичную отрисовку
    controller = CatalogController(model, view)

    # 5. Запуск
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
