# Structjour -- a daily trade review helper
# Copyright (C) 2019 Zero Substance Trading
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

'''
Created on Apr 1, 2019

@author: Mike Petersen
'''
import os
import sys
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSettings, QUrl

from structjour.xlimage import XLImage
from structjour.view.strategybrowser import Ui_Form 
from structjour.strategy.strategies import Strategy

# pylint: disable = C0103

class StratControl(QDialog):
    '''
    Control module for the ui created strategybrowser
    '''
    def __init__(self):
        super().__init__(parent=None)
        self.ui = Ui_Form()
        self.settings = QSettings('zero_substance', 'structjour')
        self.apiset = QSettings('zero_substance/stockapi', 'structjour')
        self.justloaded = False

        ddiirr = os.path.dirname(__file__)
        os.chdir(os.path.realpath(ddiirr))
        os.chdir(os.path.realpath('../../'))

        self.setWindowIcon(QIcon('images/ZSLogo.png'))


        defimage = "images/ZeroSubstanceCreation_220.png"
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
        url = self.ui.linkList.currentText()
        self.ui.linkList.removeItem(index)
        key = self.ui.strategyCb.currentText()
        self.strat.removeLink(key, url)


    def addLinkToList(self):
        link = self.ui.addLink.text()
        if link:
            self.ui.linkList.addItem(link)
            self.ui.addLink.setText('')
            index = self.ui.linkList.findText(link)
            self.ui.linkList.setCurrentIndex(index)
            key = self.ui.strategyCb.currentText()
            self.strat.setLink(key, link)

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

        # pi1 = cmenu.addAction("psych 1")
        # pi2 = cmenu.addAction("fractal 2")
        # pi3 = cmenu.addAction("starry night 3")
        pi4 = cmenu.addAction("Paste from clipboard")
        pi5 = cmenu.addAction("Browse for picture")

        # This is the line in question and None arg is the crux
        action = cmenu.exec_(self.mapTo(None, event.globalPos()))

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
        if not self.justloaded:
            print('Notes changed')
            self.setWindowTitle('Strategy Browser ... text edited')
        self.justloaded = False

    def loadStrategy(self, key):
        if not key:
            return
        strat = self.strat.getStrategy(key)
        if strat:
            check = True if strat[1] == 1 else False
            if check:
                self.ui.preferred.setChecked(True)
            else:
                self.ui.notPreferred.setChecked(True)
        desc = self.strat.getDescription(key)
        if desc:
            self.justloaded = True
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
        daLinks = self.strat.getLinks(key)
        self.ui.linkList.clear()
        for l in daLinks:
            self.ui.linkList.addItem(l)


        


    def loadStrategies(self):
        '''Load the strategy combo box from the db'''
        if not self.apiset.value('dbsqlite'):
            return
        
        strats = self.strat.getStrategies()
        self.ui.strategyCb.clear()
        for row in strats:
            self.ui.strategyCb.addItem(row[1])
            # if row[3] == 1:
            #     self.ui.preferred.setChecked(True)
            # else:
            #     self.ui.notPreferred.setChecked(True)


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
