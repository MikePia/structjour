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
Overridden Qt objects for use with designer

Created on April 8, 2020

@author: Mike Petersen
'''
from PyQt5.QtWidgets import QListWidget, QMenu
from PyQt5.QtGui import QContextMenuEvent

from PyQt5.QtCore import QEvent, pyqtSignal


class MyListWidget(QListWidget):
    '''Add a context menu to a QLabel'''
    clicked = pyqtSignal(QListWidget, QContextMenuEvent)

    # def __init__(self, *args, **kwargs):
    #     super(MyListWidget, self).__init__(*args, **kwargs)

    def contextMenuEvent(self, event):
        ''' Override and add emit'''
        self.clicked.emit(self, event)
        QListWidget.contextMenuEvent(self, event)

        # menu = QMenu()
        # menu.addAction('Add Tag')
        # menu.addAction('Remove Tag')
        # menu.addAction('Edit Tag List')
        # if menu.exec_(event.globalPos()):
        #     # item = source.itemAt(event.pos())
        #     print('got something')

    def eventFilter(self, source, event):
        if (event.type() == QEvent.ContextMenu and source is self):
            menu = QMenu()
            menu.addAction('Open Window')
            if menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())
                print(item.text())
            return True
        return super(MyListWidget, self).eventFilter(source, event)
