# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\strategybrowser.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1228, 810)
        self.stackedWidget = QtWidgets.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(50, 100, 1111, 661))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.page)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.strategyNotes = MyTextEdit(self.page)
        self.strategyNotes.setObjectName("strategyNotes")
        self.horizontalLayout_2.addWidget(self.strategyNotes)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.chart1 = ClickLabel(self.page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chart1.sizePolicy().hasHeightForWidth())
        self.chart1.setSizePolicy(sizePolicy)
        self.chart1.setMinimumSize(QtCore.QSize(250, 0))
        self.chart1.setMaximumSize(QtCore.QSize(500, 400))
        self.chart1.setText("")
        self.chart1.setPixmap(QtGui.QPixmap("../../images/ZeroSubstanceCreation_220.png"))
        self.chart1.setScaledContents(True)
        self.chart1.setObjectName("chart1")
        self.verticalLayout_2.addWidget(self.chart1)
        self.chart2 = ClickLabel(self.page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.chart2.sizePolicy().hasHeightForWidth())
        self.chart2.setSizePolicy(sizePolicy)
        self.chart2.setMinimumSize(QtCore.QSize(250, 0))
        self.chart2.setMaximumSize(QtCore.QSize(500, 400))
        self.chart2.setText("")
        self.chart2.setPixmap(QtGui.QPixmap("../../images/ZeroSubstanceCreation_220.png"))
        self.chart2.setScaledContents(True)
        self.chart2.setObjectName("chart2")
        self.verticalLayout_2.addWidget(self.chart2)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.layoutWidget = QtWidgets.QWidget(self.page_2)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 30, 1081, 641))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_4)
        self.linkList = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.linkList.sizePolicy().hasHeightForWidth())
        self.linkList.setSizePolicy(sizePolicy)
        self.linkList.setMinimumSize(QtCore.QSize(300, 0))
        self.linkList.setObjectName("linkList")
        self.horizontalLayout_3.addWidget(self.linkList)
        self.addLink = QtWidgets.QLineEdit(self.layoutWidget)
        self.addLink.setMinimumSize(QtCore.QSize(300, 0))
        self.addLink.setObjectName("addLink")
        self.horizontalLayout_3.addWidget(self.addLink)
        self.addLinkBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.addLinkBtn.setObjectName("addLinkBtn")
        self.horizontalLayout_3.addWidget(self.addLinkBtn)
        self.removeLinkBtn = QtWidgets.QPushButton(self.layoutWidget)
        self.removeLinkBtn.setObjectName("removeLinkBtn")
        self.horizontalLayout_3.addWidget(self.removeLinkBtn)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.strategyBrowse = QtWebEngineWidgets.QWebEngineView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strategyBrowse.sizePolicy().hasHeightForWidth())
        self.strategyBrowse.setSizePolicy(sizePolicy)
        self.strategyBrowse.setUrl(QtCore.QUrl("about:blank"))
        self.strategyBrowse.setObjectName("strategyBrowse")
        self.verticalLayout_4.addWidget(self.strategyBrowse)
        self.stackedWidget.addWidget(self.page_2)
        self.layoutWidget1 = QtWidgets.QWidget(Form)
        self.layoutWidget1.setGeometry(QtCore.QRect(53, 30, 999, 67))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.strategyCb = QtWidgets.QComboBox(self.layoutWidget1)
        self.strategyCb.setMinimumSize(QtCore.QSize(300, 0))
        self.strategyCb.setObjectName("strategyCb")
        self.verticalLayout_5.addWidget(self.strategyCb)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.pageSelect = QtWidgets.QListWidget(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pageSelect.sizePolicy().hasHeightForWidth())
        self.pageSelect.setSizePolicy(sizePolicy)
        self.pageSelect.setMaximumSize(QtCore.QSize(150, 50))
        self.pageSelect.setObjectName("pageSelect")
        item = QtWidgets.QListWidgetItem()
        self.pageSelect.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.pageSelect.addItem(item)
        self.horizontalLayout.addWidget(self.pageSelect)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.strategyAddLbl = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.strategyAddLbl.sizePolicy().hasHeightForWidth())
        self.strategyAddLbl.setSizePolicy(sizePolicy)
        self.strategyAddLbl.setObjectName("strategyAddLbl")
        self.verticalLayout_3.addWidget(self.strategyAddLbl)
        self.strategyAdd = QtWidgets.QLineEdit(self.layoutWidget1)
        self.strategyAdd.setMinimumSize(QtCore.QSize(300, 0))
        self.strategyAdd.setObjectName("strategyAdd")
        self.verticalLayout_3.addWidget(self.strategyAdd)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.strategyAddBtn = QtWidgets.QPushButton(self.layoutWidget1)
        self.strategyAddBtn.setObjectName("strategyAddBtn")
        self.verticalLayout_6.addWidget(self.strategyAddBtn)
        self.strategyRemoveBtn = QtWidgets.QPushButton(self.layoutWidget1)
        self.strategyRemoveBtn.setObjectName("strategyRemoveBtn")
        self.verticalLayout_6.addWidget(self.strategyRemoveBtn)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.preferred = QtWidgets.QRadioButton(self.layoutWidget1)
        self.preferred.setObjectName("preferred")
        self.verticalLayout.addWidget(self.preferred)
        self.notPreferred = QtWidgets.QRadioButton(self.layoutWidget1)
        self.notPreferred.setObjectName("notPreferred")
        self.verticalLayout.addWidget(self.notPreferred)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_4.setText(_translate("Form", "Links"))
        self.addLinkBtn.setText(_translate("Form", "Add link"))
        self.removeLinkBtn.setText(_translate("Form", "Remove Link"))
        self.label.setText(_translate("Form", "Available Strategies"))
        __sortingEnabled = self.pageSelect.isSortingEnabled()
        self.pageSelect.setSortingEnabled(False)
        item = self.pageSelect.item(0)
        item.setText(_translate("Form", "Text and Images"))
        item = self.pageSelect.item(1)
        item.setText(_translate("Form", "Links"))
        self.pageSelect.setSortingEnabled(__sortingEnabled)
        self.strategyAddLbl.setText(_translate("Form", "New Strategies"))
        self.strategyAddBtn.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#0004e6;\">Add the strategy name in the edit box</span></p></body></html>"))
        self.strategyAddBtn.setText(_translate("Form", "Add Strategy"))
        self.strategyRemoveBtn.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:10pt; color:#2d04fa;\">Remove the currently selected strategy in the cobo box on the far left.</span></p></body></html>"))
        self.strategyRemoveBtn.setText(_translate("Form", "Remove Strategy"))
        self.preferred.setText(_translate("Form", "Preferred"))
        self.notPreferred.setText(_translate("Form", "Not preferred"))


from PyQt5 import QtWebEngineWidgets
from journal.view.clicklabel import ClickLabel
from journal.view.mytextedit import MyTextEdit
