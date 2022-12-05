import datetime

import BookAskWindow
import GivenbookAskWindow
import ReaderAskWindow
from Bibla2 import *
from elib_db_connector import *


class CheckedOutDelegate(QtWidgets.QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() == 4:
            return super(CheckedOutDelegate, self).createEditor(parent, option, index)

def fill_table(table, data):
    table.blockSignals(True)
    table.setRowCount(len(data))
    for m, row in enumerate(data):
        for n, elem in enumerate(row):
            if type(elem) == datetime.date:
                elem = elem.strftime('%d.%m.%Y')
            item = QtWidgets.QTableWidgetItem()
            item.setData(QtCore.Qt.EditRole, elem)
            table.setItem(m, n, item)
    table.resizeColumnsToContents()
    table.resizeRowsToContents()
    table.blockSignals(False)


class ELibraryMainWindow(Ui_MainWindow):
    def __init__(self):
        self.elib_dbc = ElibDBConnector(host='192.168.0.19',
                                        user='egor',
                                        password='egor',
                                        database='elibrary')

    def retranslateUi(self, MainWindow):
        super().retranslateUi(MainWindow)

        self.SearchButton.clicked.connect(self._search)
        self.DeleteButton.clicked.connect(self._delete)
        self.AddButton.clicked.connect(self._add_window)

        self.IdEdit.textEdited.connect(self._id_edit_changed)

        self.BooksTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ReadersTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # self.GivenTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        delegate = CheckedOutDelegate(self.GivenTable)
        self.GivenTable.setItemDelegate(delegate)

        self.update_table('books')
        self.update_table('readers')
        self.update_table('checked_out_books')

        self.GivenTable.cellChanged.connect(self._actual_return_date_enter)

        self.ResultsTab.currentChanged.connect(self._tab_changed)

    def _tab_changed(self):
        if self.ResultsTab.currentIndex() != 0:
            self.AuthorEdit.setDisabled(True)
            self.AuthorCheckBox.setDisabled(True)
            self.BooknameEdit.setDisabled(True)
            self.BookNameCheckbox.setDisabled(True)
            self.YearEdit.setDisabled(True)
            self.YearcomboBox.setDisabled(True)
            self.SearchButton.setDisabled(True)
            self.IdEdit.setDisabled(True)
        else:
            self.AuthorEdit.setDisabled(False)
            self.AuthorCheckBox.setDisabled(False)
            self.BooknameEdit.setDisabled(False)
            self.BookNameCheckbox.setDisabled(False)
            self.YearEdit.setDisabled(False)
            self.YearcomboBox.setDisabled(False)
            self.SearchButton.setDisabled(False)
            self.IdEdit.setDisabled(False)

    def _id_edit_changed(self):
        if self.IdEdit.text() != "":
            self.AuthorEdit.setDisabled(True)
            self.AuthorCheckBox.setDisabled(True)
            self.BooknameEdit.setDisabled(True)
            self.BookNameCheckbox.setDisabled(True)
            self.YearEdit.setDisabled(True)
            self.YearcomboBox.setDisabled(True)
        else:
            self.AuthorEdit.setDisabled(False)
            self.AuthorCheckBox.setDisabled(False)
            self.BooknameEdit.setDisabled(False)
            self.BookNameCheckbox.setDisabled(False)
            self.YearEdit.setDisabled(False)
            self.YearcomboBox.setDisabled(False)

    def _search(self):
        if self.ResultsTab.currentIndex() == 0:
            if (id := self.IdEdit.text()) != "":
                search_res = self.elib_dbc.search_book_by_id(id)
            else:
                author = self.AuthorEdit.text()
                author_strict = self.AuthorCheckBox.isChecked()
                name = self.BooknameEdit.text()
                name_strict = self.BookNameCheckbox.isChecked()
                year_of_publishing = self.YearEdit.text()
                year_sign = self.YearcomboBox.currentText()
                search_res = self.elib_dbc.flexible_books_search(author=author,
                                                                 title=name,
                                                                 year_of_publishing=year_of_publishing,
                                                                 author_accurate=author_strict,
                                                                 title_accurate=name_strict,
                                                                 year_sign=year_sign)
        fill_table(self.BooksTable, search_res)

    def _delete(self):
        if self.ResultsTab.currentIndex() == 0:
            row = self.BooksTable.currentRow()
            if row >= 0:
                id = self.BooksTable.item(row, 0).text()
                self.elib_dbc.delete_book_or_reader('books', id)
                self.update_table('books')
                self.update_table('checked_out_books')
        elif self.ResultsTab.currentIndex() == 1:
            row = self.ReadersTable.currentRow()
            if row >= 0:
                id = self.ReadersTable.item(row, 0).text()
                self.elib_dbc.delete_book_or_reader('readers', id)
                self.update_table('readers')
                self.update_table('checked_out_books')
        elif self.ResultsTab.currentIndex() == 2:
            row = self.GivenTable.currentRow()
            if row >= 0:
                book_id = self.GivenTable.item(row, 0).text()
                library_card = self.GivenTable.item(row, 1).text()
                check_out_date = self.GivenTable.item(row, 2).text().split('.')
                check_out_date = check_out_date[2] + '-' + check_out_date[1] + '-' + check_out_date[0]
                self.elib_dbc.delete_checked_book(book_id, library_card, check_out_date)
                self.update_table('checked_out_books')
        else:
            raise ValueError

    def _add_window(self):
        if self.ResultsTab.currentIndex() == 0:
            self.AddbookWindow = QtWidgets.QMainWindow()
            ui = ELibraryAddBookWindow(self, self.elib_dbc)
            ui.setupUi(self.AddbookWindow)
            self.AddbookWindow.show()
        elif self.ResultsTab.currentIndex() == 1:
            self.AddreaderWindow = QtWidgets.QMainWindow()
            ui = ELibraryAddReaderWindow(self, self.elib_dbc)
            ui.setupUi(self.AddreaderWindow)
            self.AddreaderWindow.show()
        elif self.ResultsTab.currentIndex() == 2:
            self.AddCheckedOutBookWindow = QtWidgets.QMainWindow()
            ui = ELibraryAddCheckedOutBookWindow(self, self.elib_dbc)
            ui.setupUi(self.AddCheckedOutBookWindow)
            self.AddCheckedOutBookWindow.show()

    def update_table(self, table_name):
        if table_name == 'books':
            table = self.BooksTable
        elif table_name == 'readers':
            table = self.ReadersTable
        elif table_name == 'checked_out_books':
            table = self.GivenTable
        else:
            raise ValueError('Неверное имя таблицы!')
        data = self.elib_dbc.get_table_data(table_name)
        fill_table(table, data)

    def _actual_return_date_enter(self, row, col):
        self.GivenTable.blockSignals(True)
        id = self.GivenTable.item(row, 0).text()
        card = self.GivenTable.item(row, 1).text()
        date = self.GivenTable.item(row, 2).text().split('.')
        date = date[2] + '-' + date[1] + '-' + date[0]
        actual_date = self.GivenTable.item(row, 4).text()
        if (col == 4) and actual_date != '':
            actual_date = actual_date.split('.')
            actual_date = actual_date[2] + '-' + actual_date[1] + '-' + actual_date[0]
            self.elib_dbc.actual_return_date_update(id, card, date, actual_date)
            # self.update_table('checked_out_books')
        self.GivenTable.blockSignals(False)


class ELibraryAddReaderWindow(ReaderAskWindow.Ui_AddbookWindow):
    def __init__(self, elib, elib_dbc):
        self.window = None
        self.elib_dbc = elib_dbc
        self.elib = elib

    def retranslateUi(self, AddReaderWindow):
        super().retranslateUi(AddReaderWindow)
        self.window = AddReaderWindow

        def cancel():
            self.window.hide()

        def insert():
            surname = self.SecondNameEdit.text()
            name = self.NameEdit.text()
            patronymic = self.FathernameEdit.text()
            address = self.AdresEdit.text()
            self.elib_dbc.add_reader(surname=surname,
                                     name=name,
                                     patronymic=patronymic,
                                     address=address)
            self.elib.update_table('readers')

        self.CancelButton.clicked.connect(cancel)
        self.InsertButton.clicked.connect(insert)


class ELibraryAddBookWindow(BookAskWindow.Ui_AddbookWindow):
    def __init__(self, elib, elib_dbc):
        self.window = None
        self.elib_dbc = elib_dbc
        self.elib = elib

    def retranslateUi(self, AddbookWindow):
        super().retranslateUi(AddbookWindow)
        self.window = AddbookWindow

        def cancel():
            self.window.hide()

        def insert():
            author = self.AuthorEdit.text()
            title = self.BooknameEdit.text()
            year_of_publishing = self.YearEdit.text()
            num_of_copies = self.AmountEdit.text()
            self.elib_dbc.add_book(author=author,
                                   title=title,
                                   year_of_publishing=year_of_publishing,
                                   num_of_copies=num_of_copies)
            self.elib.update_table('books')

        self.CancelButton.clicked.connect(cancel)
        self.InsertButton.clicked.connect(insert)
        # self.window = AddbookWindow


class ELibraryAddCheckedOutBookWindow(GivenbookAskWindow.Ui_AddbookWindow):
    def __init__(self, elib, elib_dbc):
        self._readers = None
        self._books = None
        self.window = None
        self.elib_dbc = elib_dbc
        self.elib = elib

    def retranslateUi(self, AddCheckedOutBookWindow):
        super().retranslateUi(AddCheckedOutBookWindow)
        self.window = AddCheckedOutBookWindow

        books, readers = self.elib_dbc.get_checked_out_data()
        print()

        books_view = [f"{book[0]} - {book[1]}" for book in books]
        readers_view = [f"{reader[0]} - {reader[1]} {reader[2]} {reader[3]}" for reader in readers]

        self._books = books
        self._readers = [(reader[0], f"{reader[1]} {reader[2]} {reader[3]}") for reader in readers]

        self.BookComboBox.addItems(books_view)
        self.BookComboBox.setEditable(True)
        self.CardComboBox.addItems(readers_view)
        self.CardComboBox.setEditable(True)

        def cancel():
            self.window.hide()

        def insert():
            reader_index = self.CardComboBox.currentIndex()
            reader = self._readers[reader_index][0]
            book_index = self.BookComboBox.currentIndex()
            book = self._books[book_index][0]
            checked_out_date = self.CheckedOutDateEdit.text().split('.')
            checked_out_date = checked_out_date[2] + '-' + checked_out_date[1] + '-' + checked_out_date[0]
            return_until = self.ReturnUntilEdit.text().split('.')
            return_until = return_until[2] + '-' + return_until[1] + '-' + return_until[0]
            try:
                self.elib_dbc.add_checked_out_book(book,
                                                   reader,
                                                   checked_out_date,
                                                   return_until)
            except:
                msgBox = QtWidgets.QMessageBox()
                msgBox.setIcon(QtWidgets.QMessageBox.Information)
                msgBox.setText("Такая выдача существует!")
                msgBox.setWindowTitle("Ошибка!")
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                # msgBox.buttonClicked.connect(msgButtonClick)
                msgBox.exec()
            self.elib.update_table('checked_out_books')

        self.CancelButton.clicked.connect(cancel)
        self.InsertButton.clicked.connect(insert)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    elib = ELibraryMainWindow()
    elib.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
