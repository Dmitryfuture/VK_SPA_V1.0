# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Reg_page_skeleton.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtWidgets
import sqlite3
import random
from VK_SPA_Settings import abspath_params as params_path


class UiVkSpaRegistration_SKELETON(object):

    def __init__(self):

        self.centralwidget_REGISTRATION = QtWidgets.QWidget()

        self.label_registration = QtWidgets.QLabel(self.centralwidget_REGISTRATION)
        self.label_registration.setGeometry(QtCore.QRect(240, 60, 321, 51))
        self.label_registration.setStyleSheet("font: 75 16pt \"MS Shell Dlg 2\";")
        self.label_registration.setObjectName("label_settings_pump")
        self.line_3 = QtWidgets.QFrame(self.centralwidget_REGISTRATION)
        self.line_3.setGeometry(QtCore.QRect(9, 431, 769, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_2 = QtWidgets.QFrame(self.centralwidget_REGISTRATION)
        self.line_2.setGeometry(QtCore.QRect(10, 10, 769, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_4 = QtWidgets.QFrame(self.centralwidget_REGISTRATION)
        self.line_4.setGeometry(QtCore.QRect(10, 18, 3, 423))
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.centralwidget_REGISTRATION)
        self.line_5.setGeometry(QtCore.QRect(771, 18, 16, 422))
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setObjectName("line_5")
        self.enter_email_lineEdit = QtWidgets.QLineEdit(self.centralwidget_REGISTRATION)
        self.enter_email_lineEdit.setGeometry(QtCore.QRect(160, 190, 490, 31))
        self.enter_email_lineEdit.setObjectName("lineEdit")
        self.enter_email_lineEdit.setText('VK')
        self.label_input_email = QtWidgets.QLabel(self.centralwidget_REGISTRATION)
        self.label_input_email.setGeometry(QtCore.QRect(160, 160, 191, 21))
        self.label_input_email.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";")
        self.label_input_email.setObjectName("label_settings_pump_2")
        self.registration_pushButton = QtWidgets.QPushButton(self.centralwidget_REGISTRATION)
        self.registration_pushButton.setGeometry(QtCore.QRect(160, 250, 240, 50))
        self.registration_pushButton.setStyleSheet("background-color: rgb(85, 255, 0);\n"
                                                   "font: 75 12pt \"MS Shell Dlg 2\";")
        self.registration_pushButton.setObjectName("pushButton")
        self.enter_pushButton = QtWidgets.QPushButton(self.centralwidget_REGISTRATION)
        self.enter_pushButton.setGeometry(QtCore.QRect(410, 250, 240, 50))
        self.enter_pushButton.setText('Войти')
        self.enter_pushButton.setStyleSheet("background-color: rgb(85, 255, 0);\n"
                                                   "font: 75 12pt \"MS Shell Dlg 2\";")
        self.enter_pushButton.setObjectName("pushButton_enter")

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label_registration.setText(_translate("MainWindow", "Регистрация в программе"))
        self.label_input_email.setText(_translate("MainWindow", "Введите свой email"))
        self.registration_pushButton.setText(_translate("MainWindow", "Зарегистрироваться"))

