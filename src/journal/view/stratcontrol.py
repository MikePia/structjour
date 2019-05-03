import os
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMenu, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSettings, QUrl

from journal.xlimage import XLImage
from journal.view.strategybrowser import Ui_Form
from strategy.strategies import Strategy

class StratControl(QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.ui = Ui_Form()
        self.settings = QSettings('zero_substance', 'structjour')
        defimage = "C:/python/E/structjour/src/images/ZeroSubstanceCreation_220.png"
        if not os.path.exists(defimage):
            print('========== its not there', defimage)
        self.settings.setValue("defaultImage", defimage)
        self.ui.setupUi(self)

        self.ui.strategyAddBtn.pressed.connect(self.addStrategy)
        self.ui.strategyRemoveBtn.pressed.connect(self.removeStrategy)
        self.ui.strategyCb.currentTextChanged.connect(self.loadStrategy)
        self.ui.strategyNotes.textChanged.connect(self.stratNotesChanged)
        self.ui.preferred.released.connect(self.setPreferred)
        self.ui.notPreferred.released.connect(self.setPreferred)
        self.ui.chart1.clicked.connect(self.loadImage)
        self.ui.chart2.clicked.connect(self.loadImage)
        self.ui.strategyNotes.clicked.connect(self.saveNotes)
        self.ui.pageSelect.currentItemChanged.connect(self.changePage)

        self.ui.addLinkBtn.pressed.connect(self.addLinkToList)
        self.ui.removeLinkBtn.pressed.connect(self.removeLink)
        self.ui.linkList.currentTextChanged.connect(self.loadPage)
        self.strat = Strategy()
        self.loadStrategies()

    def loadPage(self, val):
        print('val', val)
        self.ui.strategyBrowse.load(QUrl(val))

    def removeLink(self):
        index = self.ui.linkList.currentIndex()
        self.ui.linkList.removeItem(index)


    def addLinkToList(self):
        link = self.ui.addLink.text()
        if link:
            self.ui.linkList.addItem(link)
            self.ui.addLink.setText('')
            index = self.ui.linkList.findText(link)
            self.ui.linkList.setCurrentIndex(index)

    def changePage(self, val):
        print("changePage", val)
        if val.data(0) == 'Text and Images':
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.stackedWidget.setCurrentIndex(1)

    def loadImage(self, x, event):
        '''
        A signal from ClickLabel
        :params x: The object origin (a ClickLabel object)
        :params event: QContextMenuEvent object

        :Programming Notes:
        The mapTo thing -- Found no docs or discussions in answers.
        None of the other map{To/From}{Parent/Global}({pos/globalPos}) things mapped correctly. By
        Trial and error I finally tried None. That does not seem like it should be right but its
        the only argument to mapTo() that didn't fail quietly-crashing the program. The fact that
        it failed without comment is weird. I am expecting their undocumented code to change.
        '''
        print('loadIm1ge1', x.objectName(), event.pos(), event.globalPos())
        img = x
        cmenu = QMenu(img)

        pi1 = cmenu.addAction("psych 1")
        pi2 = cmenu.addAction("fractal 2")
        pi3 = cmenu.addAction("starry night 3")
        pi4 = cmenu.addAction("Paste from clipboard")

        # This is the line in question and None arg is the crux
        action = cmenu.exec_(self.mapTo(None, event.globalPos()))

        if action == pi1:
            fn = 'C:/python/E/structjour/src/images/psych.jpg'
            x.setPixmap(QPixmap(fn))

        if action == pi2:
            fn = 'C:/python/E/structjour/src/images/fractal-art-fractals.jpg'
            x.setPixmap(QPixmap(fn))

        if action == pi3:
            fn = 'C:/python/E/structjour/src/images/van_gogh-starry-night.jpg'
            x.setPixmap(QPixmap(fn))
        if action == pi4:
            key = self.ui.strategyCb.currentText()
            print('Are we ready?', key, x.objectName())
            journalDir = self.settings.value('journal')
            if not journalDir:
                print('Please set your journal directory before adding images')
                return
            else:
                imagedir = os.path.join(journalDir, 'images/')
                if os.path.exists(journalDir):
                    if not os.path.exists(imagedir):
                        os.makedirs(imagedir)
                    iName = 'strat_{}_{}.png'.format(key, x.objectName())
                    imageName = os.path.join(imagedir, iName)
                    if x.objectName() == 'chart1':
                        self.strat.setImage1(key, imageName)
                    else:
                        self.strat.setImage2(key, imageName)

            pname = self.pasteToLabel(x, imageName)
            if pname != imageName:
                if x.objectName() == 'chart1':
                        self.strat.setImage1(key, imageName)
                else:
                    self.strat.setImage2(key, imageName)


    def pasteToLabel(self, widg, name):
        '''
        Rather than paste, we call a method that saves the clipboard to a file, then we open it with QPixmap
        '''
        xlimg = XLImage()
        img, pname = xlimg.getPilImageNoDramaForReal(name)
        if not img:
            mbox = QMessageBox()
            msg = pname + " Failed to get an image. Please select and copy an image."
            mbox.setText(msg)
            mbox.exec()
            return

        pixmap = QPixmap(pname)
        widg.setPixmap(pixmap)
        return pname   
    
    def saveNotes(self, event):
        print('Here ..... .....', event)
        desc = self.ui.strategyNotes.toPlainText()
        key = self.ui.strategyCb.currentText()
        self.strat.setDescription(key, desc)
        self.setWindowTitle('Strategy Browser')

    def setPreferred(self):
        val = self.ui.preferred.isChecked()
        key = self.ui.strategyCb.currentText()
        val = 1 if val == True else 0

        strat = self.strat.getStrategy(key)
        if strat[1] != val:
            self.strat.setPreferred(key, val)

    def stratNotesChanged(self):
        print('Notes changed')
        self.setWindowTitle('Strategy Browser ... text edited')

    def loadStrategy(self, key):
        strat = self.strat.getStrategy(key)
        check = True if strat[1] == 1 else False
        self.ui.preferred.setChecked(check)
        desc = self.strat.getDescription(key)
        self.ui.strategyNotes.setText(desc[1])
        self.setWindowTitle('Strategy Browser')

        image1 = self.strat.getImage1(key)

        if not image1:
            image1 = self.settings.value('defaultImage')
            pixmap = QPixmap(image1)
            self.ui.chart1.setPixmap(pixmap)
        elif not os.path.exists(image1):
            self.strat.removeImage1(key)
        else:
            pixmap = QPixmap(image1)
            self.ui.chart1.setPixmap(pixmap)

        image2 = self.strat.getImage2(key)
        if not image2:
            image2 = self.settings.value('defaultImage')
            pixmap = QPixmap(image2)
            self.ui.chart2.setPixmap(pixmap)
        elif not os.path.exists(image2):
            self.strat.removeImage2(key)
        else:
            pixmap = QPixmap(image2)
            self.ui.chart2.setPixmap(pixmap)


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
            ix = self.ui.strategyCb.findText(addthis)
            self.ui.strategyCb.setCurrentIndex(ix)
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
