"""
Import this file before running anything. It tests that setting has the db and directory locations.
If not, it will fire up the file settings dialog.
"""
from PyQt5.QtCore import QSettings
settings = QSettings('zero_substance', 'structjour')

if not settings.value('journal') or not settings.value('tradeDb'):
    from structjour.view.filesetcontrol import FileSetCtrl
    from PyQt5 import QtWebEngineWidgets
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication
    import sys

    app = QApplication(sys.argv)
    w = FileSetCtrl(settings)
    # sys.exit(w.show())
    # sys.exit(app.exec_())
    # app.exec_()
    print('Back from show, before quit')
    QCoreApplication.exit(0)
    print('Back from quit, hopefully moving on')
