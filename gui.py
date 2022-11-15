import sys
from PyQt5 import QtWidgets, QtCore
from elib_db_connector import *


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.elib_dbc = ElibDBConnector(host='localhost',
                                        user='root',
                                        password='root',
                                        database='elibrary')

        self.id_edit = QtWidgets.QLineEdit(self)
        self.id_edit.textChanged.connect(self.text_changed)
        self.id_edit.setPlaceholderText('Введите ID')

        self.author_edit = QtWidgets.QLineEdit(self)
        self.author_edit.textChanged.connect(self.text_changed)
        self.author_edit.setPlaceholderText('Введите ФИО')

        self.date_edit = QtWidgets.QLineEdit(self)
        self.date_edit.textChanged.connect(self.text_changed)
        self.date_edit.setPlaceholderText('Введите год')

        self.date_cbox = QtWidgets.QComboBox(self)
        self.date_cbox.currentIndexChanged.connect(self.boxclicked)
        self.date_cbox.addItems([">"])
        self.date_cbox.addItems(["<"])
        self.date_cbox.addItems(["="])

        self.name_edit = QtWidgets.QLineEdit(self)
        self.name_edit.textChanged.connect(self.text_changed)
        self.name_edit.setPlaceholderText('Введите название')

        self.author_strictbox = QtWidgets.QCheckBox(self)
        self.author_strictbox.clicked.connect(self.boxclicked)

        self.name_strictbox = QtWidgets.QCheckBox(self)
        self.name_strictbox.clicked.connect(self.boxclicked)

        #  self.year_edit.textChanged.connect(self.text_changed)
        #  self.year_edit.setPlaceholderText('Введите год')

        self.btn = QtWidgets.QPushButton("Искать")
        self.btn.clicked.connect(self.btn_clicked)

        layout = QtWidgets.QFormLayout(self)

        layout.addRow('ID', self.id_edit)
        layout.addRow('Автор', self.author_edit)
        layout.addRow('Строгое соответствие', self.author_strictbox)
        layout.addRow('Название', self.name_edit)
        layout.addRow('Строгое соответствие', self.name_strictbox)
        layout.addRow('Год', self.date_edit)
        layout.addRow('От/До/Cтрого', self.date_cbox)
        layout.addRow('Искать -->', self.btn)

    def text_changed(self, text):
        pass

    def boxclicked(self, text):
        pass

    def btn_clicked(self):
        # print(
        #     f'{self.id_edit.text()} {self.name_edit.text()} {self.author_edit.text()} {self.author_strictbox.isChecked()} {self.date_edit.text()} {self.date_cbox.currentIndex()}')
        author = self.author_edit.text()
        author_strict = self.author_strictbox.isChecked()
        name = self.name_edit.text()
        name_strict = self.name_strictbox.isChecked()
        year_of_publishing = self.date_edit.text()
        year_sign = self.date_cbox.currentIndex()
        print(self.elib_dbc.flexible_books_search(author,
                                                  year_of_publishing, year_sign))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
