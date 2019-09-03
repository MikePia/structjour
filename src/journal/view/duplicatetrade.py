# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\duplicatetrade.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(809, 602)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(30, 20, 757, 475))
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.infoBrowser = QtWidgets.QTextBrowser(self.widget)
        self.infoBrowser.setObjectName("infoBrowser")
        self.verticalLayout_2.addWidget(self.infoBrowser)
        self.showDuplicate = QtWidgets.QTextBrowser(self.widget)
        self.showDuplicate.setObjectName("showDuplicate")
        self.verticalLayout_2.addWidget(self.showDuplicate)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.deleteTxBtn = QtWidgets.QPushButton(self.widget)
        self.deleteTxBtn.setObjectName("deleteTxBtn")
        self.horizontalLayout.addWidget(self.deleteTxBtn)
        self.deleteTxEdit = QtWidgets.QLineEdit(self.widget)
        self.deleteTxEdit.setObjectName("deleteTxEdit")
        self.horizontalLayout.addWidget(self.deleteTxEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.deleteTradeBtn = QtWidgets.QPushButton(self.widget)
        self.deleteTradeBtn.setObjectName("deleteTradeBtn")
        self.horizontalLayout_2.addWidget(self.deleteTradeBtn)
        self.deleteTradeEdit = QtWidgets.QLineEdit(self.widget)
        self.deleteTradeEdit.setObjectName("deleteTradeEdit")
        self.horizontalLayout_2.addWidget(self.deleteTradeEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.keepRecordsBtn = QtWidgets.QPushButton(self.widget)
        self.keepRecordsBtn.setObjectName("keepRecordsBtn")
        self.horizontalLayout_3.addWidget(self.keepRecordsBtn)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        spacerItem = QtWidgets.QSpacerItem(338, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.infoBrowser.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Routine search for duplicate trades.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\"> </span><span style=\" font-size:12pt;\">Duplicate trades are most likley to be created by using multiple statement types like DAS export and IB Activity Statement. The trade time index may be a second or two different. Structjour will recommend which trade to delete but leave the decision to the user.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p></body></html>"))
        self.deleteTxBtn.setText(_translate("Dialog", "Delete Transaction Record"))
        self.deleteTradeBtn.setText(_translate("Dialog", "Delete Trade Record"))
        self.keepRecordsBtn.setText(_translate("Dialog", "Keep records"))


