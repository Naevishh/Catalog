import sys

from PyQt6.QtWidgets import QApplication

from controller.catalog_controller import CatalogController
from model.catalog_manager import CatalogManager
from model.db_handler import DatabaseHandler
from model.xml_handler import XMLHandler
from view.main_window import MainWindow
from init_db import init_database
from seed_db import seed_database


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Каталог книг (Вариант 15)")
    app.setStyle("Fusion")

    # Автоматически инициализируем БД при запуске
    init_database()
    seed_database()

    DEFAULT_XML = "catalog_example.xml"

    xml_handler = XMLHandler(DEFAULT_XML)
    db_handler = DatabaseHandler()
    model = CatalogManager(xml_handler, db_handler)

    view = MainWindow()

    controller = CatalogController(model, view)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
