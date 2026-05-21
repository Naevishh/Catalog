import sys

from PyQt6.QtWidgets import QApplication

from controller.catalog_controller import CatalogController
from model.catalog_manager import CatalogManager
from model.xml_handler import XMLHandler
from view.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Каталог книг (Вариант 15)")
    app.setStyle("Fusion")

    DEFAULT_XML = "catalog_example.xml"

    xml_handler = XMLHandler(DEFAULT_XML)
    model = CatalogManager(xml_handler)

    view = MainWindow()

    controller = CatalogController(model, view)

    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
