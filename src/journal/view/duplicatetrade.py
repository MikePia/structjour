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
        Dialog.resize(1457, 697)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(14, 24, 1441, 660))
        self.widget.setObjectName("widget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.infoBrowser = QtWidgets.QTextBrowser(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.infoBrowser.sizePolicy().hasHeightForWidth())
        self.infoBrowser.setSizePolicy(sizePolicy)
        self.infoBrowser.setMaximumSize(QtCore.QSize(16777215, 120))
        self.infoBrowser.setObjectName("infoBrowser")
        self.verticalLayout_4.addWidget(self.infoBrowser)
        self.showDuplicate = QtWebEngineWidgets.QWebEngineView(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(99)
        sizePolicy.setHeightForWidth(self.showDuplicate.sizePolicy().hasHeightForWidth())
        self.showDuplicate.setSizePolicy(sizePolicy)
        self.showDuplicate.setMinimumSize(QtCore.QSize(0, 450))
        self.showDuplicate.setProperty("url", QtCore.QUrl("about:blank"))
        self.showDuplicate.setObjectName("showDuplicate")
        self.verticalLayout_4.addWidget(self.showDuplicate)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.deleteTxBtn = QtWidgets.QPushButton(self.widget)
        self.deleteTxBtn.setObjectName("deleteTxBtn")
        self.verticalLayout_2.addWidget(self.deleteTxBtn)
        self.deleteTradeBtn = QtWidgets.QPushButton(self.widget)
        self.deleteTradeBtn.setObjectName("deleteTradeBtn")
        self.verticalLayout_2.addWidget(self.deleteTradeBtn)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.deleteTxEdit = QtWidgets.QLineEdit(self.widget)
        self.deleteTxEdit.setMaximumSize(QtCore.QSize(150, 16777215))
        self.deleteTxEdit.setObjectName("deleteTxEdit")
        self.verticalLayout_3.addWidget(self.deleteTxEdit)
        self.deleteTradeEdit = QtWidgets.QLineEdit(self.widget)
        self.deleteTradeEdit.setMaximumSize(QtCore.QSize(150, 16777215))
        self.deleteTradeEdit.setObjectName("deleteTradeEdit")
        self.verticalLayout_3.addWidget(self.deleteTradeEdit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.showDupBtn = QtWidgets.QPushButton(self.widget)
        self.showDupBtn.setObjectName("showDupBtn")
        self.horizontalLayout.addWidget(self.showDupBtn)
        self.showDupPrevBtn = QtWidgets.QPushButton(self.widget)
        self.showDupPrevBtn.setObjectName("showDupPrevBtn")
        self.horizontalLayout.addWidget(self.showDupPrevBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(818, 68, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)

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
        self.showDupBtn.setText(_translate("Dialog", "Show Next"))
        self.showDupPrevBtn.setText(_translate("Dialog", "Show  Previous"))


from PyQt5 import QtWebEngineWidgets
