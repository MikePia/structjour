import sys

from structjour.view.forms.calendarform import Ui_Dialog as CalDlg
from structjour.stock.utilities import pd2qtime

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QDialog


class CalendarControl(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent=parent)
        self.settings = settings
        x_pos = parent.geometry().left() + parent.ui.calendarBtn.geometry().left()
        y_pos = parent.geometry().top() + parent.ui.calendarBtn.geometry().top()
        self.move(x_pos, y_pos)
        self.ui = CalDlg()
        self.ui.setupUi(self)

        self.ui.calendarWidget.clicked.connect(self.clickedDate)

        self.ui.calendarWidget.setSelectedDate(pd2qtime(settings.value('theDate'), qdate=True))
        # self.ui = ui
        self.exec()

    def clickedDate(self, theDate):
        self.settings.setValue('theDate', theDate)
        print(theDate)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = QSettings('zero_substance', 'structjour')
    w = CalendarControl(settings)
    sys.exit(app.exec_())
