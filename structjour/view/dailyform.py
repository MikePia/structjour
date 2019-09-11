# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\dailyform.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1493, 1377)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.dailyNotes = MyTextEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dailyNotes.sizePolicy().hasHeightForWidth())
        self.dailyNotes.setSizePolicy(sizePolicy)
        self.dailyNotes.setMinimumSize(QtCore.QSize(0, 150))
        self.dailyNotes.setMaximumSize(QtCore.QSize(16777215, 150))
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(11)
        self.dailyNotes.setFont(font)
        self.dailyNotes.setAutoFillBackground(False)
        self.dailyNotes.setStyleSheet("background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(221, 232, 118, 255), stop:1 rgba(255, 255, 255, 255));")
        self.dailyNotes.setObjectName("dailyNotes")
        self.verticalLayout.addWidget(self.dailyNotes)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.mstkForm = QtWidgets.QTableView(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mstkForm.sizePolicy().hasHeightForWidth())
        self.mstkForm.setSizePolicy(sizePolicy)
        self.mstkForm.setMinimumSize(QtCore.QSize(0, 150))
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(10)
        self.mstkForm.setFont(font)
        self.mstkForm.setStyleSheet("background-color: rgba(148, 148, 148, 248);\n"
"color: rgb(255, 255, 255);\n"
"")
        self.mstkForm.setObjectName("mstkForm")
        self.mstkForm.horizontalHeader().setVisible(False)
        self.mstkForm.horizontalHeader().setStretchLastSection(True)
        self.mstkForm.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.mstkForm)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.dailyStatTab = QtWidgets.QTableView(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dailyStatTab.sizePolicy().hasHeightForWidth())
        self.dailyStatTab.setSizePolicy(sizePolicy)
        self.dailyStatTab.setMinimumSize(QtCore.QSize(0, 275))
        self.dailyStatTab.setMaximumSize(QtCore.QSize(16777215, 275))
        font = QtGui.QFont()
        font.setFamily("Arial Narrow")
        font.setPointSize(10)
        self.dailyStatTab.setFont(font)
        self.dailyStatTab.setStyleSheet("background-color: rgba(148, 148, 148, 248);\n"
"color: rgb(255, 255, 255);")
        self.dailyStatTab.setObjectName("dailyStatTab")
        self.dailyStatTab.horizontalHeader().setVisible(False)
        self.dailyStatTab.horizontalHeader().setStretchLastSection(True)
        self.dailyStatTab.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.dailyStatTab)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_3 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("Arial Rounded MT Bold")
        font.setPointSize(24)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.tradeTable = QtWidgets.QTableView(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tradeTable.sizePolicy().hasHeightForWidth())
        self.tradeTable.setSizePolicy(sizePolicy)
        self.tradeTable.setMinimumSize(QtCore.QSize(0, 300))
        self.tradeTable.setObjectName("tradeTable")
        self.verticalLayout.addWidget(self.tradeTable)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.dailyNotes.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial Narrow\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:7.8pt;\"><br /></p></body></html>"))
        self.dailyNotes.setPlaceholderText(_translate("Form", "Notes for daily summary"))
        self.mstkForm.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:12pt; color:#0000ff;\">The mistake/pertinent feature note is populated from the erroror/summarized field in the trade summaries. The lost plays is populated from the Amt Lost field.</span></p></body></html>"))
        self.label_3.setText(_translate("Form", "Trade Table"))

from structjour.view.mytextedit import MyTextEdit
