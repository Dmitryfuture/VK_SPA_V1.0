# -*- coding: utf-8 -*-

import webbrowser
from PyQt5 import QtCore, QtWidgets
import VK_SPA_Settings

class Ui_HELLO_PAGE_SKELETON(object):

    def __init__(self):
        self.centralwidget_HELLO_PAGE = QtWidgets.QWidget()

        self.line_hello_page = QtWidgets.QFrame(self.centralwidget_HELLO_PAGE)
        self.line_hello_page.setGeometry(QtCore.QRect(440, 18, 16, 421))
        self.line_hello_page.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_hello_page.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_hello_page.setObjectName("line")
        self.label_add_funct_hello_page = QtWidgets.QLabel(self.centralwidget_HELLO_PAGE)
        self.label_add_funct_hello_page.setGeometry(QtCore.QRect(490, 41, 251, 31))
        self.label_add_funct_hello_page.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.label_add_funct_hello_page.setObjectName("label_settings_pump")
        self.line_3_hello_page = QtWidgets.QFrame(self.centralwidget_HELLO_PAGE)
        self.line_3_hello_page.setGeometry(QtCore.QRect(9, 431, 769, 20))
        self.line_3_hello_page.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3_hello_page.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3_hello_page.setObjectName("line_3")
        self.line_2_hello_page = QtWidgets.QFrame(self.centralwidget_HELLO_PAGE)
        self.line_2_hello_page.setGeometry(QtCore.QRect(10, 10, 769, 16))
        self.line_2_hello_page.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2_hello_page.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2_hello_page.setObjectName("line_2")
        self.line_4_hello_page = QtWidgets.QFrame(self.centralwidget_HELLO_PAGE)
        self.line_4_hello_page.setGeometry(QtCore.QRect(10, 18, 3, 423))
        self.line_4_hello_page.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4_hello_page.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4_hello_page.setObjectName("line_4")
        self.line_5_hello_page = QtWidgets.QFrame(self.centralwidget_HELLO_PAGE)
        self.line_5_hello_page.setGeometry(QtCore.QRect(771, 18, 16, 422))
        self.line_5_hello_page.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5_hello_page.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5_hello_page.setObjectName("line_5")
        self.buy_ready_acc_pushButton_hello_page = QtWidgets.QPushButton(self.centralwidget_HELLO_PAGE)
        self.buy_ready_acc_pushButton_hello_page.setGeometry(QtCore.QRect(470, 110, 291, 51))
        self.buy_ready_acc_pushButton_hello_page.setStyleSheet("background-color: rgb(0, 255, 0);\n"
                                      "font: 75 10pt \"MS Shell Dlg 2\";")
        self.buy_ready_acc_pushButton_hello_page.setObjectName("pushButton")
        self.buy_proxy_pushButton_hello_page = QtWidgets.QPushButton(self.centralwidget_HELLO_PAGE)
        self.buy_proxy_pushButton_hello_page.setGeometry(QtCore.QRect(470, 180, 291, 51))
        self.buy_proxy_pushButton_hello_page.setStyleSheet("background-color: rgb(0, 255, 0);\n"
                                        "font: 75 10pt \"MS Shell Dlg 2\";")
        self.buy_proxy_pushButton_hello_page.setObjectName("pushButton_2")
        self.BitLy_pushButton_hello_page = QtWidgets.QPushButton(self.centralwidget_HELLO_PAGE)
        self.BitLy_pushButton_hello_page.setGeometry(QtCore.QRect(470, 250, 291, 51))
        self.BitLy_pushButton_hello_page.setStyleSheet("background-color: rgb(0, 255, 0);\n"
                                        "font: 75 10pt \"MS Shell Dlg 2\";")
        self.BitLy_pushButton_hello_page.setObjectName("pushButton_3")
        self.VK_short_pushButton_hello_page = QtWidgets.QPushButton(self.centralwidget_HELLO_PAGE)
        self.VK_short_pushButton_hello_page.setGeometry(QtCore.QRect(470, 320, 291, 51))
        self.VK_short_pushButton_hello_page.setStyleSheet("background-color: rgb(0, 255, 0);\n"
                                        "font: 75 10pt \"MS Shell Dlg 2\";")
        self.VK_short_pushButton_hello_page.setObjectName("pushButton_4")

        self.checkBox_use_proxy = QtWidgets.QCheckBox(self.centralwidget_HELLO_PAGE)  # CheckBox выбора прокси
        self.checkBox_use_proxy.setGeometry(QtCore.QRect(470, 390, 291, 20))
        self.checkBox_use_proxy.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.checkBox_use_proxy.setText('Использовать прокси')
        self.checkBox_use_proxy.raise_()

        self.textEdit_hello_page = QtWidgets.QTextEdit(self.centralwidget_HELLO_PAGE)
        self.textEdit_hello_page.setGeometry(QtCore.QRect(10, 18, 438, 423))
        self.textEdit_hello_page.setObjectName("textEdit")
        self.textEdit_hello_page.setReadOnly(True)

        self.label_add_funct_hello_page.raise_()
        self.line_3_hello_page.raise_()
        self.line_2_hello_page.raise_()
        self.line_4_hello_page.raise_()
        self.line_hello_page.raise_()
        self.line_5_hello_page.raise_()
        self.buy_ready_acc_pushButton_hello_page.raise_()
        self.buy_proxy_pushButton_hello_page.raise_()
        self.BitLy_pushButton_hello_page.raise_()
        self.VK_short_pushButton_hello_page.raise_()
        self.textEdit_hello_page.raise_()

        self.retranslateUi()

        self.function_hello_page()

        self.checkBox_use_proxy.setChecked(True)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label_add_funct_hello_page.setText(_translate("MainWindow", "Дополнительные функции"))
        self.buy_ready_acc_pushButton_hello_page.setText(_translate("MainWindow", "Купить готовые аккаунты"))
        self.buy_proxy_pushButton_hello_page.setText(_translate("MainWindow", "Купить прокси "))
        self.BitLy_pushButton_hello_page.setText(_translate("MainWindow", "Сервис для сокращения ссылок"))
        self.VK_short_pushButton_hello_page.setText(_translate("MainWindow", "Сервис для сокращения ссылок №2"))
        self.textEdit_hello_page.setHtml(_translate("MainWindow",
                                         "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" "
                                         "\"http://www.w3.org/TR/REC-html40/strict.dtd\">\n "
                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style "
                                         "type=\"text/css\">\n "
                                         "p, li { white-space: pre-wrap; }\n"
                                         "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; "
                                         "font-size:7.8pt; font-weight:400; font-style:normal;\">\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\"> ****         **** ****    ****          ********   "
                                         "***********          ** </span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\"> ****        ****  ****   ****          ****  ****  "
                                         "****      ****        ****</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\">  ****      ****   ****  ****            ****          "
                                         " ****      ****     *******</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\">   ****    ****    **** ****               ****        "
                                         " ***********   ****   ****</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\">    ****  ****     **** ****                 ****      "
                                         " ****               ****       ****</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\">       ******        ****  ****                  ****  "
                                         "   ****             **************</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\">         ****          ****   ****         ****  ****  "
                                         " ****           ****                ****</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:6pt; font-weight:600; "
                                         "font-style:italic;\">           **            ****    ****         ******** "
                                         "   ****         ****                    ****</span></p>\n "
                                         "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; "
                                         "margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px; font-size:6pt; font-weight:600; font-style:italic;\"><br "
                                         "/></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:18pt; font-weight:600;\">Добро "
                                         "пожаловать в программу VK SPA!</span></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600;\">Версия "
                                         "программы: v.1.0</span><span style=\" font-size:18pt; font-weight:600;\">   "
                                         " </span></p>\n "
                                         "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; "
                                         "font-size:18pt; font-weight:600;\"><br /></p>\n "
                                         "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; "
                                         "margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px;\"><span style=\" font-size:10pt;\">Перед началом работы "
                                         "рекомендую сначала изучить инструкицю по работе с программой, "
                                         "а также изучить советы по рассылке, во избежания частого бана "
                                         "аккаунтов.</span></p>\n "
                                         "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; "
                                         "margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                                         "text-indent:0px; font-size:10pt;\"><br /></p>\n "
                                         "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; "
                                         "margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" "
                                         "font-size:10pt;\">Приятного пользования!</span></p>\n "
                                         "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; "
                                         "margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" "
                                         "font-size:10pt;\">Купон на скидку при покупке прокси на сайте proxy6.net - "
                                         "1IsBQwqG88</span></p></body></html>"))


    def function_hello_page(self):
        self.buy_proxy_pushButton_hello_page.clicked.connect(lambda: webbrowser.open('https://proxy6.net/?r=400523'))
        self.BitLy_pushButton_hello_page.clicked.connect(lambda: webbrowser.open('https://app.bitly.com/'))
        self.VK_short_pushButton_hello_page.clicked.connect(lambda: webbrowser.open('https://vk.com/cc'))
        self.buy_ready_acc_pushButton_hello_page.clicked.connect(lambda: webbrowser.open('https://accsmarket.com/?ref=438551'))
        self.checkBox_use_proxy.stateChanged.connect(lambda: self.change_use_proxy_checkbox())

    def change_use_proxy_checkbox(self):
        if self.checkBox_use_proxy.isChecked():
            VK_SPA_Settings.use_proxy = True
        if self.checkBox_use_proxy.isChecked() is False:
            VK_SPA_Settings.use_proxy = False




