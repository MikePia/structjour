import os
import sys
from PyQt5.QtWidgets import QWidget, QApplication

from journal.view.strategybrowser import Ui_Form
from strategy.strategies import Strategy

class StratControl(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.strategyAddBtn.pressed.connect(self.addStrategy)
        self.ui.strategyRemoveBtn.pressed.connect(self.removeStrategy)
        self.ui.strategyCb.currentTextChanged.connect(self.loadStrategy)
        self.ui.strategyNotes.textChanged.connect(self.stratNotesChanged)
        self.strat = Strategy()
        self.loadStrategies()
    

    
    def stratNotesChanged(self):
        print('Notes changed')
        self.setWindowTitle('Strategy Browser ... text edited')

    def loadStrategy(self, key):
        pass
    def loadStrategies(self):
        '''Load the strategy combo box from the db'''
        
        cursor = self.strat.getStrategies()
        self.ui.strategyCb.clear()
        for row in cursor:
            self.ui.strategyCb.addItem(row[1])
            if row[3] == 1:
                self.ui.preferred.setChecked(True)
            else:
                self.ui.notPreferred.setChecked(True)


    def addStrategy(self):
        addthis = self.ui.strategyAdd.text()
        if addthis:
            self.strat.addStrategy(addthis)
            self.loadStrategies()
        else:
            print('Nothing to add. No action taken')

    def removeStrategy(self):
        removethis = self.ui.strategyCb.currentText()
        if removethis:
            self.strat.removeStrategy(removethis)
            self.loadStrategies()




if __name__ == '__main__':
    ddiirr = os.path.dirname(__file__)
    os.chdir(os.path.realpath(ddiirr))
    print(ddiirr)
    app = QApplication(sys.argv)
    w = StratControl()
    w.show()
    sys.exit(app.exec_())
