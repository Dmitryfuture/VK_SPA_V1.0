import os
import requests
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import VK_SPA_Settings


class CheckProxy(QThread):
    thread_timer = QtCore.pyqtSignal()

    def __init__(self, proxy):
        super().__init__()
        self.proxy = proxy

    def run(self):
        if self.proxy:
            proxies = {'https': f'http://{self.proxy}'}  # user:pass@10.10.1.10:3128 или просто IP 10.10.1.10:3128
            try:
                result_check = requests.get('https://www.vk.com/', proxies=proxies)
                if 'Response [200]' in str(result_check):
                    VK_SPA_Settings.result_check_proxy = '[1]', str(result_check)
                else:
                    VK_SPA_Settings.result_check_proxy = '[4]', str(result_check)
            except Exception as err_check:
                VK_SPA_Settings.result_check_proxy = '[2]', str(err_check)
        elif not self.proxy:
            VK_SPA_Settings.result_check_proxy = '[3]', None

        self.thread_timer.emit()


class UiVkSpaAddProxy_SKELETON(object):

    def __init__(self):

        self.central_widget_ADD_PROXY = QtWidgets.QWidget()
        self.name_proxy_label_add_proxy = QtWidgets.QLabel(self.central_widget_ADD_PROXY)
        self.name_proxy_label_add_proxy.setGeometry(QtCore.QRect(140, 15, 481, 90))
        self.name_proxy_label_add_proxy.setText("Введите данные прокси сервера в формате:\n"
                                                "user:pass@10.10.1.10:3128\n"
                                                "или просто\n"
                                                "10.10.1.10:3128")
        self.name_proxy_label_add_proxy.setStyleSheet("font: 75 11pt MS Shell Dlg 2")
        self.add_proxy_Lineinput_add_proxy = QtWidgets.QLineEdit(self.central_widget_ADD_PROXY)
        self.add_proxy_Lineinput_add_proxy.setGeometry(QtCore.QRect(141, 110, 431, 31))
        self.add_proxy_Lineinput_add_proxy.setObjectName("add_login")
        self.add_proxy_Lineinput_add_proxy.setStyleSheet("font: 75 9pt MS Shell Dlg 2")
        self.try_proxy_pushButton_add_proxy = QtWidgets.QPushButton(self.central_widget_ADD_PROXY)
        self.try_proxy_pushButton_add_proxy.setGeometry(QtCore.QRect(200, 220, 301, 41))
        self.try_proxy_pushButton_add_proxy.setStyleSheet("background-color: rgb(85, 170, 255);\n"
                                                          "font: 10pt \"MS Shell Dlg 2\";"
                                                          "color: rgb(255, 255, 255)")
        self.try_proxy_pushButton_add_proxy.setObjectName("add_account_button")
        self.save_proxy_pushButton_add_proxy = QtWidgets.QPushButton(self.central_widget_ADD_PROXY)
        self.save_proxy_pushButton_add_proxy.setGeometry(QtCore.QRect(210, 280, 281, 51))
        self.save_proxy_pushButton_add_proxy.setStyleSheet("background-color: rgb(85, 170, 255);\n"
                                                           "font: 10pt \"MS Shell Dlg 2\";"
                                                           "color: rgb(255, 255, 255)")
        self.save_proxy_pushButton_add_proxy.setObjectName("buy_account")
        self.open_file_proxy_pushButton_add_proxy = QtWidgets.QPushButton(self.central_widget_ADD_PROXY)
        self.open_file_proxy_pushButton_add_proxy.setGeometry(QtCore.QRect(650, 25, 130, 80))
        self.open_file_proxy_pushButton_add_proxy.setStyleSheet("background-color: rgb(85, 170, 255);\n"
                                                                "font: 10pt \"MS Shell Dlg 2\";"
                                                                "color: rgb(255, 255, 255)")
        self.open_file_proxy_pushButton_add_proxy.setObjectName("add_account_button")

        self.gif_auth = QtGui.QMovie(f'{VK_SPA_Settings.abspath_params}/Picture_gui/checking_proxy.gif')
        self.gif_auth.setScaledSize(QtCore.QSize(41, 41))
        self.label_gif = QtWidgets.QLabel(self.central_widget_ADD_PROXY)
        self.label_gif.setGeometry(QtCore.QRect(515, 220, 41, 41))
        self.label_gif.setMovie(self.gif_auth)

        self.class_checking_proxy_thread = None

        self.retranslateUI_ADD_PROXY()
        self.function_ADD_PROXY()

    def retranslateUI_ADD_PROXY(self):
        self.try_proxy_pushButton_add_proxy.setText("Проверить прокси на валидность")
        self.save_proxy_pushButton_add_proxy.setText("Сохранить прокси")
        self.open_file_proxy_pushButton_add_proxy.setText("Изменить файл\n с прокси")

    def function_ADD_PROXY(self):
        """ Все связи между кнопками и действиями """
        self.try_proxy_pushButton_add_proxy.clicked.connect(lambda: self.create_thread())
        self.try_proxy_pushButton_add_proxy.clicked.connect(lambda: self.gif_start(True))
        self.open_file_proxy_pushButton_add_proxy.clicked.connect(lambda: self.open_file_proxy())
        self.save_proxy_pushButton_add_proxy.clicked.connect(self.save_entered_proxy)

    def create_thread(self):
        """ Создает экземпляр класса CheckProxy, в котором происходит проверка прокси на валидность """
        self.class_checking_proxy_thread = CheckProxy(self.add_proxy_Lineinput_add_proxy.text())
        self.class_checking_proxy_thread.thread_timer.connect(self.visual_output)
        self.class_checking_proxy_thread.start()

    def gif_start(self, action):
        """ Запуск gif анимации при заупске потока,
         :param action:
            True - если надо запустить анимацию,
            False - елси надо остановить.
        """
        if action:
            self.try_proxy_pushButton_add_proxy.setEnabled(False)
            self.gif_auth.start()
            self.label_gif.show()
        else:
            self.try_proxy_pushButton_add_proxy.setEnabled(True)
            self.gif_auth.stop()
            self.label_gif.close()

    def visual_output(self):
        """ Визуальный вывод проверки прокси """
        if "[1]" in VK_SPA_Settings.result_check_proxy:
            self.error_window_add_proxy(name_window='Проверка прокси', type_info=QMessageBox.Information,
                                        text_error='Этот прокси действителен!', name_picture='ok')

        elif "[2]" in VK_SPA_Settings.result_check_proxy:
            self.error_window_add_proxy(name_window='Проверка прокси', type_info=QMessageBox.Warning,
                                        text_error='Этот прокси не валиден',
                                        err_detail=str(VK_SPA_Settings.result_check_proxy[1]),
                                        name_picture='error')

        elif '[3]' in VK_SPA_Settings.result_check_proxy:
            self.error_window_add_proxy(name_window='Проверка прокси', type_info=QMessageBox.Warning,
                                        text_error='Вы ничего не ввели!', name_picture='error')

        elif '[4]' in VK_SPA_Settings.result_check_proxy:
            self.error_window_add_proxy(name_window='Проверка прокси', type_info=QMessageBox.Warning,
                                        text_error='Этим прокси лучше не пользоваться', name_picture='error',
                                        err_detail=str(VK_SPA_Settings.result_check_proxy[1]))
        else:
            self.error_window_add_proxy(name_window='Проверка прокси', type_info=QMessageBox.Warning,
                                        text_error='Неизвестная ошибка!', name_picture='error',
                                        err_detail='Обратитесь к администратору')
        self.try_proxy_pushButton_add_proxy.setEnabled(True)
        self.gif_start(False)

    def save_entered_proxy(self):
        """ Сохраняет в файл PROXY.txt введенный прокси """
        proxy = self.add_proxy_Lineinput_add_proxy.text()
        with open(f'{VK_SPA_Settings.abspath_params}/PROXY.txt', 'a') as f:
            f.writelines(f"\n{proxy}")
            self.add_proxy_Lineinput_add_proxy.clear()
            self.error_window_add_proxy(name_window='Проверка пркоси', type_info=QMessageBox.Warning,
                                        text_error='Прокси сохранен!', name_picture='ok')

    def open_file_proxy(self):
        """ Открывает файл с прокси, .txt """
        file = 'PROXY.txt'
        os.startfile(f'{VK_SPA_Settings.abspath_params}/{file}')

    def error_window_add_proxy(self, name_window: str, text_error: str, type_info, err_detail=None, name_picture='error'):
        """ Функция вызова всплывающего окна,
        :param name_window - имя окна,
        :param text_error - основной информационный текст,
        :param err_detail - дополнительный текст к основной информации, None по умолчанию
        :param type_info - тип окна, например QMessageBox.Warning
        :param name_picture - имя картинки в коне оповещения, по умолчанию 'error'
         """
        error_wind = QMessageBox()
        error_wind.setWindowTitle(f'{name_window}')
        error_wind.setText(f'{text_error}')
        error_wind.setWindowIcon(QIcon(f'{VK_SPA_Settings.abspath_params}/Picture_gui/{name_picture}.png'))
        error_wind.setIcon(type_info)
        error_wind.setStandardButtons(QMessageBox.Ok)
        if err_detail:
            error_wind.setDetailedText(str(err_detail))
        error_wind.exec_()
