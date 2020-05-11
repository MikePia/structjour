import sys

from structjour.view.forms.calendarform import Ui_Dialog as CalDlg
from structjour.stock.utilities import pd2qtime

from PyQt5.QtCore import QSettings, QDate
from PyQt5.QtWidgets import QApplication, QDialog


class DialogWClose(QDialog):
    def closeEvent(self, event):
        print('close it')
        if self.passme is not None:
            self.passme.append(self.ui.calendarWidget.selectedDate())
        print()


class CalendarControl(DialogWClose):
    def __init__(self, settings, parent=None, btn_widg=None, passme=None, initialDate=None):
        '''
        :params parent: The Qt Parent widget or None
        :params btn_wdg: A button widget to popup next to. Intended as the button that calls this dialog.
        :params passme: empty list: Retrive the selected value at passme[0] when the dialog closes.
        :params initialDate: QDate. Set the initial date.

        '''
        super().__init__(parent=parent)
        self.settings = settings
        self.passme = passme
        if btn_widg:
            self.move(btn_widg.mapToGlobal(btn_widg.rect().bottomRight()))
        self.ui = CalDlg()
        self.ui.setupUi(self)
        if initialDate is not None:
            assert isinstance(initialDate, QDate)
            self.ui.calendarWidget.setSelectedDate(initialDate)

        self.ui.calendarWidget.clicked.connect(self.clickedDate)

        # self.ui.calendarWidget.setSelectedDate(pd2qtime(settings.value('theDate'), qdate=True))
        self.exec()

    def clickedDate(self, theDate):
        if self.passme is None:
            self.settings.setValue('theDate', theDate)
        print(theDate)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = CalendarControl(settings)
    sys.exit(app.exec_())
