import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import visualization_point_clouds as visualization


class FileLoader(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.fileName = None

        self.label = QLabel('Załaduj plik', self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 16, QFont.Bold))
        self.label.setStyleSheet("color: white;")


        self.open_button = QPushButton('Wybierz plik', self)
        self.open_button.clicked.connect(self.open_file)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.open_button)

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filters = "LAS Files (*.las);;STL Files (*.stl);;LAZ Files (*.laz);;OBJ Files (*.obj);;All Files (*)"
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Wybierz plik", "", filters, options=options)
        if self.fileName:
            self.label.setText(f'Załadowano plik. Uruchom wizualizację')


class VisualizationRunner(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.run_button = QPushButton('Uruchom wizualizację', self)
        self.run_button.clicked.connect(self.run_visualization)

        layout = QVBoxLayout(self)
        layout.addWidget(self.run_button)

    def run_visualization(self):
        if self.parent().file_loader.fileName:
            visualization.point_clouds(self.parent().file_loader.fileName)
        else:
            print("Wybierz plik przed uruchomieniem funkcji.")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 200)
        self.setWindowTitle('LassStormClouds')
        self.setStyleSheet("background-color: #333; color: white")

        self.file_loader = FileLoader(self)
        self.visualization_runner = VisualizationRunner(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.file_loader)
        layout.addWidget(self.visualization_runner)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
