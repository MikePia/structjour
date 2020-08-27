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
Display and modify tags. Allow to change activate and to delete tag

Created on April 22, 2020

@author: Mike Petersen
'''
import sys

from structjour.models.trademodels import Tags
from structjour.models.meta import ModelBase

from structjour.view.clicklabel import ClickLabel

from PyQt5.QtWidgets import (QWidget, QApplication, QCheckBox, QMenu, QHBoxLayout,
                             QMessageBox, QVBoxLayout, QGridLayout, QScrollArea, QDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class EditTagsDlg(QDialog):
    def __init__(self, parent=None, labels=None):
        super().__init__(parent=parent)
        tags = Tags.getTags()
        self.tagDict = {name: [tag] for (name, tag) in zip([x.name for x in tags], tags)}
        if labels is not None:
            self.labels = labels
        else:
            self.labels = [x.name for x in tags]
        self.setWindowModality(Qt.ApplicationModal)

        self.topWidget = QScrollArea(widgetResizable=True)

        self.topgrid = QGridLayout(self)
        self.topgrid.addWidget(self.topWidget)

        self.cbDict = dict()

        self.initUI()
        self.show()

    def updateLayout(self):
        for t in self.tagDict:
            self.tagDict[t][2].disconnect()
            self.tagDict[t][2].deleteLater()
        self.cbDict = dict()

        # Note that this starts a new session held in ModelBase
        tags = Tags.getTags()
        self.labels = [x.name for x in tags]
        self.cbDict = dict()
        self.tagDict = {name: [tag] for (name, tag) in zip([x.name for x in tags], tags)}

        self.initUI()
        self.show()

    def initUI(self):

        content_widget = QWidget()
        vbox = QVBoxLayout(content_widget)
        self.topWidget.setWidget(content_widget)

        for t in self.labels:
            widget = QWidget()
            hlayout = QHBoxLayout(widget)

            lab = ClickLabel(t)
            hlayout.addWidget(lab)
            lab.clicked.connect(self.labelClicked)

            cb = QCheckBox("activate")
            hlayout.addWidget(cb)

            if t in self.tagDict:
                self.tagDict[t].append(cb)
                self.tagDict[t].append(lab)
                cb.setChecked(self.tagDict[t][0].active)
            else:
                cb.setEnabled(False)
                cb.setText('Not a tag')
            self.cbDict[lab] = [cb]
            cb.clicked.connect(self.cbClicked)

            vbox.addWidget(widget)

        self.setWindowTitle("Edit Tags")
        self.setWindowIcon(QIcon("structjour/images/ZSLogo.png"))
        ttip = '''<span style=\" font-size:10pt; color:#0633c6;\">Right click a label to select delete tag.</span>'''
        self.setToolTip(ttip)

    def cbClicked(self, val):
        for key in self.tagDict:
            if len(self.tagDict[key]) > 1 and self.tagDict[key][1].isChecked() != self.tagDict[key][0].active:
                print(key, f'widget: {self.tagDict[key][1].isChecked()}, tag:{self.tagDict[key][0].active}')
                self.tagDict[key][0].active = self.tagDict[key][1].isChecked()
                ModelBase.session.commit()
                ModelBase.session.close()

    def labelClicked(self, x, event):
        print('got a click', x, event)
        print()
        cmenu = QMenu(x)
        deleteTag = cmenu.addAction("delete Tag")
        action = cmenu.exec_(self.mapTo(None, event.globalPos()))

        if action == deleteTag:
            if x.text() in self.tagDict:
                numRelations = len(self.tagDict[x.text()][0].trade_sums)
                if numRelations > 0:
                    msg = f'The tag "{x.text()}" is attached to {numRelations} trades. Are you sure you want to delete it?'
                    ok = QMessageBox.question(self, 'Delete tag?', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if ok != QMessageBox.Yes:
                        return
                ModelBase.session.delete(self.tagDict[x.text()][0])
                ModelBase.session.commit()
                ModelBase.session.close()
                # self.updateLayout()
                self.tagDict[x.text()][1].setHidden(True)
                self.tagDict[x.text()][2].setHidden(True)
                self.tagDict[x.text()][2].parent().setHidden(True)
                self.show()

            else:
                print(f'inform that {x.text()} is not a tag')


def getTags():
    ''' A local proof of concept helper function'''
    tags = Tags.getTags()
    tags = [x.name for x in tags]
    return tags


if __name__ == '__main__':
    labs = getTags()
    app = QApplication(sys.argv)
    # labs = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    #         'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    #         'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    #         'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    #         'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    #         'A very long and self important tag that pretends to explain the meaning of 42 and everything']
    # labs = ['Zero Substance', 'Tutorial', 'For Life!!!', 'An extension',
    #         'dynamically processed', 'and placed', 'on the page',
    #         'wherever I want', 'it to be placed', 'Zero Substance', 'Tutorial',
    #         'For Life!!!', 'An extension', 'dynamically processed',
    #         'and placed', 'on the page', 'wherever I want', 'it to be placed']
    # 'A very long and self important tag that pretneds to describe the precise nature of the universe']

    # labs = ['Zero Substance', 'Tutorial', 'For Life!!!', 'Showing',
    #          'the docs', 'do not tell', 'the whole', 'story!!!', 'Greed']
    ex = EditTagsDlg()
    sys.exit(app.exec_())
