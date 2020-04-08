# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\dailyform.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1736, 1377)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\../images/ZSLogo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(Form)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.mstkForm = QtWidgets.QTableView(self.splitter)
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
        self.dailyStatTab = QtWidgets.QTableView(self.splitter)
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
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial Rounded MT Bold")
        font.setPointSize(24)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tradeTable = QtWidgets.QTableView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tradeTable.sizePolicy().hasHeightForWidth())
        self.tradeTable.setSizePolicy(sizePolicy)
        self.tradeTable.setMinimumSize(QtCore.QSize(0, 300))
        self.tradeTable.setObjectName("tradeTable")
        self.verticalLayout.addWidget(self.tradeTable)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.mstkForm.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:12pt; color:#0000ff;\">The mistake/pertinent feature note is populated from the erroror/summarized field in the trade summaries. The lost plays is populated from the Amt Lost field.</span></p></body></html>"))
        self.label_3.setText(_translate("Form", "Trade Table"))
