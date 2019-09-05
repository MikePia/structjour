# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\disciplinedform.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(788, 337)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../images/ZSLogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(30, 10, 741, 317))
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.importDateRadio = QtWidgets.QRadioButton(self.widget)
        self.importDateRadio.setObjectName("importDateRadio")
        self.verticalLayout.addWidget(self.importDateRadio)
        self.importSinceDateRadio = QtWidgets.QRadioButton(self.widget)
        self.importSinceDateRadio.setObjectName("importSinceDateRadio")
        self.verticalLayout.addWidget(self.importSinceDateRadio)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.importDateEdit = QtWidgets.QDateEdit(self.widget)
        self.importDateEdit.setObjectName("importDateEdit")
        self.horizontalLayout.addWidget(self.importDateEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.showResults = QtWidgets.QTextBrowser(self.widget)
        self.showResults.setObjectName("showResults")
        self.verticalLayout_2.addWidget(self.showResults)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.startBtn = QtWidgets.QPushButton(self.widget)
        self.startBtn.setObjectName("startBtn")
        self.horizontalLayout_2.addWidget(self.startBtn)
        spacerItem1 = QtWidgets.QSpacerItem(568, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Export to Disciplined Trade Log"))
        self.label.setText(_translate("Dialog", "Import Data into the Disciplined Trader Log"))
        self.importDateRadio.setText(_translate("Dialog", "Import data from the date:"))
        self.importSinceDateRadio.setText(_translate("Dialog", "Import all data since the date:"))
        self.startBtn.setText(_translate("Dialog", "Start"))


