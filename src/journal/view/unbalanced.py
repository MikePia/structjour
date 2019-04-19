# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'unbalanced.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1151, 429)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.explain = QtWidgets.QTextBrowser(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.explain.sizePolicy().hasHeightForWidth())
        self.explain.setSizePolicy(sizePolicy)
        self.explain.setMinimumSize(QtCore.QSize(450, 180))
        self.explain.setMaximumSize(QtCore.QSize(16777215, 180))
        self.explain.setStyleSheet("p,\n"
"        li {\n"
"            white-space: pre-wrap;\n"
"        }\n"
"\n"
"        h3 {\n"
"            margin-top: 6px;\n"
"            margin-bottom: 12px;\n"
"            margin-left: 0px;\n"
"            margin-right: 0px;\n"
"            text-indent: 0px;\n"
"        }\n"
"\n"
"        body {\n"
"            font-family: Arial, Helvetica, sans-serif;\n"
"\n"
"            font-size: 7.8pt;\n"
"            font-weight: 400;\n"
"            font-style: normal;\n"
"        }\n"
"\n"
"        .large {\n"
"            font-size: large;\n"
"            font-weight: 600;\n"
"        }\n"
"\n"
"        .blue {\n"
"\n"
"            font-size: large;\n"
"            font-weight: 600;\n"
"            color: #0000ff;\n"
"        }\n"
"\n"
"        .red {\n"
"            font-weight: 600;\n"
"            color: #aa0000;\n"
"        }\n"
"\n"
"        .green {\n"
"            font-weight: 600;\n"
"            color: #00ff00;\n"
"        }\n"
"\n"
"        .explain {\n"
"            margin-top: 12px;\n"
"            margin-bottom: 12px;\n"
"            margin-left: 0px;\n"
"            margin-right: 0px;\n"
"            text-indent: 10px;\n"
"\n"
"        }\n"
"\n"
"        ul {\n"
"\n"
"            margin-top: 0px;\n"
"            margin-bottom: 0px;\n"
"            margin-left: 0px;\n"
"            margin-right: 0px;\n"
"\n"
"        }\n"
"\n"
"        li {\n"
"            font-size: 8pt;\n"
"            margin-top: 12px;\n"
"            margin-bottom: 0px;\n"
"            margin-left: 0px;\n"
"            margin-right: 0px;\n"
"            text-indent: 0px;\n"
"        }\n"
"\n"
"        .li2 {\n"
"            margin-top: 0px;\n"
"        }\n"
"\n"
"        .li3 {\n"
"            margin-top: 0px;\n"
"            margin-bottom: 12px;\n"
"        }")
        self.explain.setAcceptRichText(False)
        self.explain.setObjectName("explain")
        self.horizontalLayout_3.addWidget(self.explain)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.unbalShares = QtWidgets.QLineEdit(Dialog)
        self.unbalShares.setFocusPolicy(QtCore.Qt.NoFocus)
        self.unbalShares.setStyleSheet("background-color: rgb(7, 23, 255);\n"
"color: rgb(255, 255, 255);\n"
"font: 14pt \"Arial Narrow\";")
        self.unbalShares.setAlignment(QtCore.Qt.AlignCenter)
        self.unbalShares.setObjectName("unbalShares")
        self.verticalLayout_3.addWidget(self.unbalShares)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.unbalBefore = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(12)
        self.unbalBefore.setFont(font)
        self.unbalBefore.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.unbalBefore.setAlignment(QtCore.Qt.AlignCenter)
        self.unbalBefore.setObjectName("unbalBefore")
        self.verticalLayout.addWidget(self.unbalBefore)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.unbalAfter = QtWidgets.QLineEdit(Dialog)
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(12)
        self.unbalAfter.setFont(font)
        self.unbalAfter.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.unbalAfter.setAlignment(QtCore.Qt.AlignCenter)
        self.unbalAfter.setObjectName("unbalAfter")
        self.verticalLayout_2.addWidget(self.unbalAfter)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.okBtn = QtWidgets.QPushButton(Dialog)
        self.okBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.okBtn.setObjectName("okBtn")
        self.horizontalLayout_2.addWidget(self.okBtn)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_4.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_4.addItem(spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout_4.addItem(spacerItem2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.tradeTable = QtWidgets.QTableView(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tradeTable.sizePolicy().hasHeightForWidth())
        self.tradeTable.setSizePolicy(sizePolicy)
        self.tradeTable.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tradeTable.setObjectName("tradeTable")
        self.verticalLayout_5.addWidget(self.tradeTable)
        self.gridLayout.addLayout(self.verticalLayout_5, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Unbalanced shares."))
        self.explain.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<h3 style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Unbalanced shares of {{ticker}} for {{shares1}} shares </span></h3>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Adjust the shares held before and after this statement to bring the unbalanced shares to 0. Solutions might look like one of the following </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" font-size:8pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">-{{shares1}} shares held before and 0 shares held after </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">0 shares held before and {{shares1}} shares held after </li>\n"
"<li style=\" font-size:8pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">{{shares2}}100 shares held before and {{shares3}}. shares held after </li></ul></body></html>"))
        self.label.setText(_translate("Dialog", "Unbalanced Shares"))
        self.unbalShares.setText(_translate("Dialog", "0"))
        self.label_2.setText(_translate("Dialog", "Held Before statement"))
        self.unbalBefore.setText(_translate("Dialog", "0"))
        self.label_3.setText(_translate("Dialog", "Held After statement"))
        self.unbalAfter.setText(_translate("Dialog", "0"))
        self.okBtn.setText(_translate("Dialog", "OK"))


