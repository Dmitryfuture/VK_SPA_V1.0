# -*- coding: utf-8 -*-

import os
import webbrowser
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import VK_SPA_Settings


class UiVkSpaAddAccount_SKELETON(object):

    def __init__(self):

        self.central_widget_ADD_ACCOUNT = QtWidgets.QWidget()
        self.name_login_add_account = QtWidgets.QLabel(self.central_widget_ADD_ACCOUNT)
        self.name_login_add_account.setGeometry(QtCore.QRect(140, 15, 481, 40))
        self.name_login_add_account.setText('Введите логин (номер телефона) от аккаунта')
        self.name_login_add_account.setStyleSheet("font: 75 12pt MS Shell Dlg 2")
        self.textEdit_login_add_account = QtWidgets.QLineEdit(self.central_widget_ADD_ACCOUNT)
        self.textEdit_login_add_account.setGeometry(QtCore.QRect(210, 60, 281, 31))
        self.textEdit_login_add_account.setPlaceholderText('Введите логин')
        self.textEdit_login_add_account.setStyleSheet("font: 75 9pt MS Shell Dlg 2")
        self.textEdit_login_add_account.setMaxLength(16)
        self.name_password_add_account = QtWidgets.QLabel(self.central_widget_ADD_ACCOUNT)
        self.name_password_add_account.setGeometry(QtCore.QRect(220, 125, 281, 31))
        self.name_password_add_account.setText('Введите пароль от аккаунта')
        self.name_password_add_account.setStyleSheet("font: 75 12pt MS Shell Dlg 2")
        self.textEdit_password_add_account = QtWidgets.QLineEdit(self.central_widget_ADD_ACCOUNT)
        self.textEdit_password_add_account.setGeometry(QtCore.QRect(210, 166, 281, 31))
        self.textEdit_password_add_account.setPlaceholderText('Введите пароль')
        self.textEdit_password_add_account.setStyleSheet("font: 75 9pt MS Shell Dlg 2")
        self.addAccount_pushButton_add_account = QtWidgets.QPushButton(self.central_widget_ADD_ACCOUNT)
        self.addAccount_pushButton_add_account.setGeometry(QtCore.QRect(230, 240, 231, 31))
        self.addAccount_pushButton_add_account.setStyleSheet("background-color: rgb(85, 170, 255);\n"
                                                             "font: 11pt \"MS Shell Dlg 2\";"
                                                             "color: rgb(255, 255, 255)")
        self.addAccount_pushButton_add_account.setObjectName("pushButton")
        self.buy_ReadyAcc_pushButton_add_account = QtWidgets.QPushButton(self.central_widget_ADD_ACCOUNT)
        self.buy_ReadyAcc_pushButton_add_account.setGeometry(QtCore.QRect(200, 290, 291, 51))
        self.buy_ReadyAcc_pushButton_add_account.setStyleSheet("background-color: rgb(85, 170, 255);\n"
                                                               "font: 11pt \"MS Shell Dlg 2\";"
                                                               "color: rgb(255, 255, 255)")
        self.buy_ReadyAcc_pushButton_add_account.setObjectName("pushButton_2")
        self.open_file_account_pushButton_add_account = QtWidgets.QPushButton(self.central_widget_ADD_ACCOUNT)
        self.open_file_account_pushButton_add_account.setGeometry(QtCore.QRect(650, 25, 120, 80))
        self.open_file_account_pushButton_add_account.setStyleSheet("background-color: rgb(85, 170, 255);\n"
                                                                    "font: 10pt \"MS Shell Dlg 2\";"
                                                                    "color: rgb(255, 255, 255)")
        self.open_file_account_pushButton_add_account.setObjectName("pushButton")

        self.retranslateUi_ADD_ACCOUNT()
        self.function_ADD_ACCOUNT()

    def retranslateUi_ADD_ACCOUNT(self):
        """ Установка текста на кнопки """

        self.addAccount_pushButton_add_account.setText("Добавить аккаунт")
        self.buy_ReadyAcc_pushButton_add_account.setText("Купить готовый аккаунт")
        self.open_file_account_pushButton_add_account.setText("Изменить\n файл\n с аккаунтами")

    def function_ADD_ACCOUNT(self):
        """ Привязка к кнопкам функций """
        self.addAccount_pushButton_add_account.clicked.connect(self.get_text_loginPass)
        self.buy_ReadyAcc_pushButton_add_account.clicked.connect(
            lambda: webbrowser.open('https://accsmarket.com/?ref=438551'))
        self.open_file_account_pushButton_add_account.clicked.connect(lambda: self.open_file_accounts())

    def clear_line_input(self):
        """ Очищает строку вводу данных после нажатия кнопки 'Добавить аккаунт' """

        self.textEdit_login_add_account.clear()
        self.textEdit_password_add_account.clear()

    def get_text_loginPass(self):
        """ Получает номер телефона и пароль введенные пользователем и записывает их в файл ACCOUNTS.txt """

        login = self.textEdit_login_add_account.text()
        password = self.textEdit_password_add_account.text()
        if len(login) >= 11 and login.isdigit() and password:
            with open(f'{VK_SPA_Settings.abspath_params}/ACCOUNTS.txt', 'a', encoding='utf8') as f:
                try:
                    f.writelines(f'{login};{password}:\n')
                except Exception as err_add:
                    if "charmap" in str(err_add):
                        self.clear_line_input()
                        return self.error_window_add_acc(name_window='Добавление аккаунта',
                                                         text_error='Ошибка при добавлении аккаунта',
                                                         err_detail='Использованы недопустимые символы, попробуйте '
                                                                    'добавить аккаунт вручную',
                                                         type_info=QMessageBox.Information, name_picture='error')
                self.clear_line_input()
                self.error_window_add_acc(name_window='Добавление аккаунта', text_error='Аккаунт успешно добавлен!',
                                          type_info=QMessageBox.Information, name_picture='ok')
        else:
            self.error_window_add_acc(name_window="Ошибка", text_error='Неправильно заполнены поля ввода',
                                      type_info=QMessageBox.Warning, name_picture='error')

    def open_file_accounts(self):
        """ Открытие файла с аккаунтами """

        file = 'ACCOUNTS.txt'
        os.startfile(f'{VK_SPA_Settings.abspath_params}/{file}')

    def error_window_add_acc(self, name_window, text_error, err_detail=None, type_info=None, name_picture=None):
        """ Вызывает окно с ошибкой """

        error_wind = QMessageBox()
        error_wind.setWindowTitle(f'{name_window}')
        error_wind.setText(f'{text_error}')
        error_wind.setWindowIcon(QIcon(f'{VK_SPA_Settings.abspath_params}/Picture_gui/{name_picture}.png'))
        error_wind.setIcon(type_info)
        error_wind.setStandardButtons(QMessageBox.Ok)
        if err_detail:
            error_wind.setDetailedText(str(err_detail))
        error_wind.exec_()
