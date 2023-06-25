# -*- coding: utf-8 -*-

import os
import sys
import urllib.request
import webbrowser
from time import sleep

import vk_api as VK
import requests
import VK_SPA_Settings

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QSize, QThread, QUrl, Qt
from VK_SPA_Skeleton import VkSpaSkeleton
from VK_SPA_Settings import abspath_params
from fake_useragent import UserAgent

ua = UserAgent()
headers = {"User-Agent": ua.ie}


class BlockedAccountAlert(QThread):
    """ Запуск звукового уведомления """

    thread_blocked_account = QtCore.pyqtSignal()

    def run(self):
        self.thread_blocked_account.emit()


class CheckConnection(QThread):
    """ Проверяка доступа в интернет """

    thread_run_check = QtCore.pyqtSignal(str)
    reconnect = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def get_connection(self):
        """ Проверка соединения """
        try:
            result = requests.get('http://www.google.com')
            return result.status_code
        except requests.ConnectionError as err:
            return str(err)
        except requests.HTTPError as err1:
            return str(err1)

    def run(self):
        """ Запуск цикла, проверяющего наличие доступа в интернет """
        try:
            while True:
                res = self.get_connection()
                if res != 200:
                    VK_SPA_Settings.connection = False
                    self.thread_run_check.emit(str(res))
                    n = 0
                    while True:
                        res_again = self.get_connection()
                        if res_again == 200:
                            VK_SPA_Settings.connection = True
                            self.reconnect.emit('Соединение установленно! Для продолжения работы нажмите кнопку слева')
                            break
                        n += 1
                        if n in [10, 20, 30, 40, 50, 60, 70]:
                            self.reconnect.emit(
                                'Не можем установить соединение...Наш совет попробовать зайти позже, для выхода нажмите кнопку справа')
                        sleep(2)
                sleep(7)
        except Exception:
            pass


class RunLoadAuth(QThread):
    """ Класс потока авторизации пользователя """

    thread_run_auth = QtCore.pyqtSignal()
    thread_set_visual_info_auth = QtCore.pyqtSignal(dict)
    thread_error_proxy = QtCore.pyqtSignal(dict)

    def __init__(self, captcha_thread, log_pass_token, proxy, check_use_proxy):
        super().__init__()
        self.login = log_pass_token[0]
        self.password = log_pass_token[1]
        self.proxy = proxy
        self.check_use_proxy = check_use_proxy
        self.captcha_thread = captcha_thread
        self.vk_session = None
        self.vk_main = None
        self.ua = UserAgent()
        self.headers = {"User-Agent": self.ua.ie}

    def try_proxy(self, proxy):
        """ Функция проверяет прокси на валидность, в случае успеха, возвращает данные прокси """

        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        try:
            if 'Response [200]' in str(requests.get('https://www.vk.com/', proxies=proxies, headers=self.headers)):
                sess = requests.Session()
                sess.proxies.update({f'http': f'http://{proxy}',
                                     'https': f'http://{proxy}'})
                sess.headers.update(headers)
                return proxies

        except Exception as error_proxy:
            return {'text_error': 'Данный прокси не рабочий!', 'err_detail': error_proxy}

    def authorization_user(self, check_use_proxy, proxy):
        """ Функция авторизация пользователя по номеру телефона и прокси
            :param check_use_proxy - CheckBox использования прокси при авторизации,
            :param proxy - данные прокси
            Возвращает кортеж:
                ()[0] - передача информационного сообщения в основной поток;
                ()[1] - объект авторизации(если авторизация успешна) """

        result_dict = {'id_account': None,
                       'first_name': None,
                       'last_name': None,
                       'url_avatar': None,
                       'information_text': None}

        if check_use_proxy:
            result_proxy = self.try_proxy(proxy)
            if 'text_error' in result_proxy.keys():
                return self.thread_error_proxy.emit(result_proxy)
            else:
                proxies = result_proxy
        else:
            proxies = None

        """ Попытка авторизациии """
        try:
            self.vk_session = VK.VkApi(login=self.login, password=self.password, captcha_handler=self.show_captcha)
            if proxies is not None:
                self.vk_session.http.proxies = proxies
                self.vk_session.http.headers = headers
            self.vk_session.auth()
            self.vk_main = self.vk_session.get_api()
            base_info_account = self.vk_main.account.getProfileInfo()
            url_avatar = self.vk_main.users.get(fields='photo_50')[0]['photo_50']
            result_dict = {'id_account': base_info_account['id'],
                           'first_name': base_info_account['first_name'],
                           'last_name': base_info_account['last_name'],
                           'url_avatar': url_avatar,
                           'information_text': 'Пользователь авторизован'}
            return self.thread_set_visual_info_auth.emit(result_dict), self.vk_main

        except Exception as exc:
            if 'remixsid' in str(exc):
                result_dict['information_text'] = 'Аккаунт заблокировали'
                return self.thread_set_visual_info_auth.emit(result_dict), None
            elif 'Bad password' in str(exc):
                result_dict['information_text'] = 'Не правильный пароль'
                return self.thread_set_visual_info_auth.emit(result_dict), None
            elif 'blocked' in str(exc):
                result_dict['information_text'] = 'Аккаунт забанен'
                return self.thread_set_visual_info_auth.emit(result_dict), None
            else:
                result_dict['information_text'] = 'Не удается авторизоваться'
                print(exc)
                return self.thread_set_visual_info_auth.emit(result_dict), None

    def show_captcha(self, captcha):
        """ Функция принимает объект капчи, через функцию captcha.try_again передает капчу на проверку.
            Если капча успешна - успешное завершение авторизации, иначе - повторный показ новой капчи"""

        VK_SPA_Settings.captcha_input_text = ''
        self.captcha_thread(self.get_captcha_image(captcha))
        while True:
            if len(VK_SPA_Settings.captcha_input_text) >= 1:
                VK_SPA_Settings.was_captcha = True
                captcha.try_again(key=VK_SPA_Settings.captcha_input_text)
                break

    def get_captcha_image(self, captcha):
        """ Функция получает объект капча, скачивает изображени и возвращает путь к изображению """
        URL = captcha.get_url()
        url_ava = f'{URL}'
        img = urllib.request.urlopen(url_ava).read()
        with open(f"{abspath_params}/Picture_gui/load_avatar/captcha.jpg", "wb") as captcha_image:
            captcha_image.write(img)
        return f"{abspath_params}/Picture_gui/load_avatar/captcha.jpg"

    def run(self):
        VK_SPA_Settings.object_user_session = self.authorization_user(proxy=self.proxy,
                                                                      check_use_proxy=self.check_use_proxy)
        self.thread_run_auth.emit()


class ErrorWindow(QMessageBox):
    """ Класс высплывающего окна с ошибкой """

    def __init__(self, base_info, detail_info):
        super().__init__()

        self.error_wind = QMessageBox()
        self.error_wind.setWindowTitle('Что то пошло не так')
        self.base_info = base_info
        self.detail_info = detail_info

    def __call__(self, *args, **kwargs):
        self.error_wind.exec_()

    def set_settings(self):
        try:
            self.error_wind.setText(self.base_info)
            self.error_wind.setWindowIcon(QIcon(f"{abspath_params}/Picture_gui/error.png"))
            self.error_wind.setIcon(QMessageBox.Warning)
            if self.detail_info:
                self.error_wind.setDetailedText(str(self.detail_info))
        except Exception as err_set:
            print(err_set)


class VkSpaMain(VkSpaSkeleton, QMainWindow):
    """ Класс основного потока окна """

    def __init__(self):
        super().__init__()
        self.already_in_base = False
        self.login = ''
        self.password = ''
        self.abspath_VK_SPA_GUI = os.getcwd().replace("\\", '/')
        self.abspath_params = os.getcwd().replace("VK_SPA_GUI", 'params')

        self.setupUi(self)
        self.retranslateUi(self)
        self.label_logo.setIcon(QIcon(f"{self.abspath_params}/Picture_gui/Vk SPA_LABLE.jpg"))
        self.function_MAIN_VKSPA()

        self.blocked_needed = BlockedAccountAlert()
        self.blocked_needed.thread_blocked_account.connect(self.play_blocked_acc)

        self.label_photo_avatar_button = QtWidgets.QPushButton(self.centralwidget_VKSPA)  # Кнопка-Label Аватарки
        self.label_photo_avatar_button.setGeometry(QtCore.QRect(820, 0, 50, 50))
        self.label_photo_avatar_button.setIconSize(QSize(50, 50))
        self.label_photo_avatar_button.setStyleSheet("border: none;")

        self.label_load_auth = QtWidgets.QLabel(self.centralwidget_VKSPA)
        self.label_load_auth.setGeometry(QtCore.QRect(795, 51, 20, 20))
        self.gif_auth = QtGui.QMovie(f'{abspath_params}/Picture_gui/load_main.gif')
        self.gif_auth.setScaledSize(QtCore.QSize(20, 20))
        self.label_load_auth.setMovie(self.gif_auth)

        self.get_list_accounts()
        self.get_list_proxy()

    def visual_display_captcha(self, path=None):
        """ При возникновении капчи в потоке авторизации, вызывается эта функция и ей передается изображение капчи.
            В основном интерфейсе появляется изображение и строка ввода капчи. """

        self.label_status.setText('Нужен ввод капчи')
        self.label_status_picture.setPixmap(QtGui.QPixmap(
            f'{self.abspath_params}/Picture_gui/orange_status.jpg'))
        self.label_captcha.show()
        self.InputCaptcha.show()
        self.lableImageCaptcha.setPixmap(QtGui.QPixmap(f'{path}'))
        self.lableImageCaptcha.show()
        self.press_captcha_button.clicked.disconnect()

        self.press_captcha_button.clicked.connect(self.press_captcha)

        self.press_captcha_button.show()

    def press_captcha(self):
        """ Переопределяет VK_SPA_Settings.captcha_input_text из '' в веденный текст капчи. Нужна для выполнения условия
            ввода текста в потоке авторизации в случае появления капчи. """

        VK_SPA_Settings.captcha_input_text = self.InputCaptcha.text()

    def function_MAIN_VKSPA(self):
        """ Все связи между кнопками и действями, которые они выполняют """

        self.button_authUser.clicked.connect(lambda: self.gif_start_auth())
        self.button_authUser.clicked.connect(lambda: self.auth_user())
        self.PAGE_add_account.addAccount_pushButton_add_account.clicked.connect(lambda: self.update_combo_acc_proxy())
        self.chooseAcc_comboBox_main.currentTextChanged.connect(lambda: self.change_acc_comboBox())
        self.chooseProxy_comboBox_main.currentTextChanged.connect(lambda: self.fixed_proxy())

        """ StackWidget - переключение между виджетами"""
        self.label_logo.clicked.connect(
            lambda: (self.stackedWidget_VKSPA.setCurrentIndex(0), self.update_combo_acc_proxy()))
        self.add_account.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(1))
        self.add_proxy.clicked.connect(lambda: (self.stackedWidget_VKSPA.setCurrentIndex(2)))
        self.button_menu_parsing_friend_user.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(3))
        self.Parsing_user_in_groupButton.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(4))
        self.Parsing_group_by_requestButton.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(5))
        self.Spam_on_the_wallButton.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(6))
        self.Random_commentButton.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(7))
        self.likes_photo_and_post_my_friends_button.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(8))
        self.neew_feed_walk_button.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(9))
        self.pump_accaunt_pushButton.clicked.connect(lambda: self.stackedWidget_VKSPA.setCurrentIndex(10))

    def fixed_proxy(self):
        """ Фиксирует прокси для последующего его использования """
        VK_SPA_Settings.last_used_proxy = self.chooseProxy_comboBox_main.currentText()

    def assignment_session(self):
        """ Присваивает всем страницам программы методы API """

        self.PAGE_parsing_users_friend.VK_PARSING_FRIEND_METHOD_FROM_MAIN = \
            VK_SPA_Settings.object_user_session[1]
        self.PAGE_parsing_members_in_group.VK_PARSING_MEMBERS_METHOD_FROM_MAIN = \
            VK_SPA_Settings.object_user_session[1]
        self.PAGE_parsing_groups_by_request.VK_PARSING_GROUP_METHOD_FROM_MAIN = \
            VK_SPA_Settings.object_user_session[1]
        self.PAGE_spam_on_the_wall.VK_SPAM_WALL_METHOD = VK_SPA_Settings.object_user_session[1]
        self.PAGE_comment_spam.VK_SPAM_COMMENT_METHOD_FROM_MAIN = VK_SPA_Settings.object_user_session[1]
        self.PAGE_likes_users_posts.VK_LIKES_USERS_METHOD_FROM_MAIN = VK_SPA_Settings.object_user_session[1]
        self.PAGE_news_feed_walk.VK_NEWS_FEED_METHOD_FROM_MAIN = VK_SPA_Settings.object_user_session[1]

    def do_button_auth_enable(self):
        """ Делает кнопку авторизации доступной для нажатия, если авторизация прошла неудачно"""

        self.login = ''
        self.change_acc_comboBox()

    def run_check_end_auth(self):
        """ Вызывется в конце потока авторизации, если была капча - закрывает окно с капчей.
            Нужна для доступа всех страниц приложения к методоам API.
            Также закрывает гифку авторизации """

        if VK_SPA_Settings.was_captcha is True:
            self.press_captcha_button.close()
            self.InputCaptcha.close()
            self.lableImageCaptcha.close()
            self.label_captcha.close()
            VK_SPA_Settings.was_captcha = False
        try:
            self.gif_auth.stop()
            self.label_load_auth.close()
            if VK_SPA_Settings.object_user_session:
                self.assignment_session()
        except Exception as err_gif:
            print(f'1  -{err_gif}')

    def run_err_window_proxy(self, dict_err):
        """ В случае если прокси не валиден запускает окно с ошибкой из потока авторизации """

        self.do_button_auth_enable()
        return self.error_window_main(dict_err)

    def run_err_window_conn(self, text):
        """ Создает окно с ошибкой, в случае если разрывается соеденинение с интернетом """

        self.window_no_connect = QtWidgets.QMainWindow()
        self.window_no_connect.setWindowTitle("Connection Error")
        self.window_no_connect.setGeometry(QtCore.QRect(750, 500, 481, 188))
        self.window_no_connect.setFixedSize(481, 188)
        self.window_no_connect.setWindowModality(Qt.ApplicationModal)

        self.label_err_connect = QtWidgets.QLabel(self.window_no_connect)
        self.label_err_connect.setText("Пропало соединение с интернетом...")
        self.label_err_connect.setStyleSheet('font: 75 10pt "MS Shell Dlg 2";')
        self.label_err_connect.setGeometry(QtCore.QRect(90, 0, 300, 20))

        self.label_err_connect_description = QtWidgets.QLabel(self.window_no_connect)
        self.label_err_connect_description.setText(text)
        self.label_err_connect_description.setGeometry(QtCore.QRect(30, 30, 441, 61))
        self.label_err_connect_description.setWordWrap(True)

        self.label_try_connect = QtWidgets.QLabel(self.window_no_connect)
        self.label_try_connect.setText("Пытаемся соедениться...")
        self.label_try_connect.setStyleSheet('font: 75 10pt "MS Shell Dlg 2";')
        self.label_try_connect.setGeometry(QtCore.QRect(130, 100, 201, 21))
        self.label_try_connect.setWordWrap(True)

        self.label_after_trying = QtWidgets.QLabel(self.window_no_connect)
        self.label_after_trying.setGeometry(QtCore.QRect(100, 130, 281, 51))
        self.label_after_trying.setWordWrap(True)

        self.window_no_connect.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Window)
        self.button_next_step = QtWidgets.QPushButton(self.window_no_connect)
        self.button_next_step.close()

        self.window_no_connect.raise_()
        self.window_no_connect.show()

    def close_window_error_connect(self, result_trying):
        """ Закрывает окно с ошибкой отсутствия интернета """

        try:
            self.button_next_step.disconnect()
        except Exception:
            pass
        if 'установленно' in result_trying:
            self.label_try_connect.close()
            self.button_next_step.setText('Продолжить')
            self.button_next_step.setGeometry(QtCore.QRect(0, 160, 91, 28))
            self.button_next_step.clicked.connect(lambda: self.window_no_connect.close())

        elif 'Не можем' in result_trying:
            self.button_next_step.setText('Выйти')
            self.button_next_step.setGeometry(QtCore.QRect(390, 160, 91, 28))
            self.button_next_step.clicked.connect(lambda: self.window_no_connect.close())
            self.button_next_step.clicked.connect(lambda: self.close())

        self.button_next_step.show()
        self.label_after_trying.setText(result_trying)

    def check_settings(self, log_pass):
        """ Проверяет логин и прокси на правильность """

        if VK_SPA_Settings.use_proxy:
            if self.chooseProxy_comboBox_main.currentText() == '---------':
                none_proxy_description = 'Возможно файл с прокси серверами пустой. Проверьте файл, либо уберите ' \
                                         'галочку в настройках - "Использовать прокси", Настоятельно рекомендуем вам ' \
                                         'использовать прокси во избежания частого бана аккаунтов'
                self.gif_stop()
                self.do_button_auth_enable()
                return {'text_error': 'Не выбран прокси!', 'err_detail': none_proxy_description}

        check_list = ['', None, '---------']
        login = log_pass[0:log_pass.find(';')]
        password = log_pass[log_pass.find(';') + 1: log_pass.find(':')]

        if log_pass in check_list:
            self.gif_stop()
            return {'text_error': 'Вы не выбрали аккаунт', 'err_detail': None}
        elif len(login) > 14 or len(login) < 7:
            self.gif_stop()
            return {'text_error': 'Данные аккаунта не верны!', 'err_detail': None}
        else:
            return login, password

    def gif_start_auth(self):
        """ Функиця, запускающая гифку авторизации, запускается параллельно с запуском потоком авторизации """
        self.button_authUser.setEnabled(False)
        self.gif_auth.start()
        self.label_load_auth.show()

    def gif_stop(self):
        self.gif_auth.stop()
        self.label_load_auth.close()

    def auth_user(self):
        """ Функция, создающая поток, в котором происходит авторизация """

        name_current_login = self.chooseAcc_comboBox_main.currentText()
        result_check_log_pass = self.check_settings(name_current_login)
        if isinstance(result_check_log_pass, dict):
            return self.error_window_main(result_check_log_pass)

        # Передача логина, для предотвращения повторного нажатия кнопки авторизации
        if name_current_login != "---------":
            self.login = name_current_login[0:name_current_login.find(';')]

        self.thread_connection = CheckConnection()
        self.thread_connection.thread_run_check.connect(self.run_err_window_conn)
        self.thread_connection.reconnect.connect(self.close_window_error_connect)
        self.thread_connection.start()

        self.thread_auth = RunLoadAuth(captcha_thread=self.visual_display_captcha,
                                       log_pass_token=result_check_log_pass,
                                       check_use_proxy=VK_SPA_Settings.use_proxy,
                                       proxy=self.chooseProxy_comboBox_main.currentText())
        self.thread_auth.thread_run_auth.connect(self.run_check_end_auth)
        self.thread_auth.thread_set_visual_info_auth.connect(self.set_info_account)
        self.thread_auth.thread_error_proxy.connect(self.run_err_window_proxy)
        self.thread_auth.start()

    def play_blocked_acc(self):
        """ Звуковое увдеомление, если аккаунт забанен """

        self.media_player = QMediaPlayer()
        self.url = QUrl.fromLocalFile(f"{self.abspath_params}/Alert/blocked_account.wav")
        self.content = QMediaContent(self.url)
        self.media_player.setMedia(self.content)
        self.media_player.play()

    def launch_blocked_threads(self):
        """ Запуск звукового уведомления """

        self.blocked_needed.start()

    def load_avatar(self, url):
        """ Функиция для загрузки аватарки. Возвращает путь расположения аватарки """

        url_ava = f'{url}'
        img = urllib.request.urlopen(url_ava).read()
        name_avatar = 'img_avatar' + str(url)[50:57]
        with open(f"{self.abspath_params}/Picture_gui/load_avatar/{name_avatar}_50x50.jpg", "wb") as avatar:
            avatar.write(img)
        path = f"{self.abspath_params}/Picture_gui/load_avatar/{name_avatar}_50x50.jpg"
        return path

    def set_info_account(self, dict_sett_acc):
        """ Функция для графического отображения результатов авторизации """

        try:
            if dict_sett_acc['url_avatar'] is not None:
                try:
                    path = self.load_avatar(url=dict_sett_acc['url_avatar'])
                    self.label_photo_avatar_button.setIcon(QIcon(f'{path}'))
                    self.label_photo_avatar_button.show()
                    self.label_photo_avatar_button.clicked.connect(
                        lambda: webbrowser.open(f'https://vk.com/id{dict_sett_acc["id_account"]}'))
                except Exception:
                    self.lable_photo_avatar.setPixmap(QtGui.QPixmap(
                        f'{self.abspath_params}/Picture_gui/load_avatar/empty_avatar_50x50.png'))

            if dict_sett_acc["id_account"] is not None:
                self.label_status_picture.setPixmap(QtGui.QPixmap(f'{self.abspath_params}/Picture_gui/'
                                                                  f'green_status16x16.jpg'))
                self.label_status_name_and_ID.setText(
                    f'ID - {dict_sett_acc["id_account"]}\n{dict_sett_acc["first_name"]} '
                    f'{dict_sett_acc["last_name"]}')

            elif dict_sett_acc["information_text"] in \
                    ['Аккаунт забанен', 'Не удается авторизоваться', 'Не правильный пароль']:
                if dict_sett_acc["information_text"] == 'Аккаунт забанен':
                    self.launch_blocked_threads()
                self.do_button_auth_enable()
                self.label_status_name_and_ID.clear()
                self.label_photo_avatar_button.close()
                self.lable_photo_avatar.setPixmap(QtGui.QPixmap(
                    f'{self.abspath_params}/Picture_gui/load_avatar/empty_avatar_50x50.png'))
                self.label_status_picture.setPixmap(QtGui.QPixmap(
                    f'{self.abspath_params}/Picture_gui/red_status_16x16.jpg'))
            self.label_status.setText(dict_sett_acc["information_text"])
        except Exception as err_set_info:
            print(err_set_info)

    def error_window_main(self, dict_err):
        """ Функция для графического отображения ошибок в основном потоке """

        self.error_window = ErrorWindow(base_info=dict_err["text_error"], detail_info=dict_err["err_detail"])
        self.error_window.set_settings()
        self.error_window()

    def get_list_accounts(self):
        """ Показывает список всех возможных аккаунтов для авторизации """

        self.chooseAcc_comboBox_main.addItem('---------')
        with open(f"{self.abspath_params}/ACCOUNTS.txt", 'r', encoding='utf8') as accs:
            name_accounts = accs.readlines()
            for acc in name_accounts:
                if acc == '\n':
                    pass
                else:
                    self.chooseAcc_comboBox_main.addItem(acc.replace('\n', ''))

    def get_list_proxy(self):
        """ Показывает список всех прокси """

        self.chooseProxy_comboBox_main.addItem('---------')
        with open(f"{self.abspath_params}/PROXY.txt", 'r') as prx:
            name_proxy = prx.readlines()
            for _ in name_proxy:
                if _ == '\n':
                    pass
                else:
                    self.chooseProxy_comboBox_main.addItem(_.replace('\n', ''))

    def update_combo_acc_proxy(self):
        """ Обновляет список прокси """
        self.chooseAcc_comboBox_main.clear()
        self.chooseProxy_comboBox_main.clear()
        self.get_list_accounts()
        self.get_list_proxy()

    def change_acc_comboBox(self):
        """ Функция, не дающая повторно нажать кнопку авторизации для пользователя, который уже авторизован """
        name_current_acc = self.chooseAcc_comboBox_main.currentText()
        if name_current_acc[0:name_current_acc.find(';')] != self.login:
            self.button_authUser.setEnabled(True)
        elif name_current_acc == '---------':
            self.button_authUser.setEnabled(True)
        else:
            self.button_authUser.setEnabled(False)


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        Work_VkSpa = VkSpaMain()
        Work_VkSpa.setFixedSize(1062, 636)
        Work_VkSpa.show()
        sys.exit(app.exec_())
    except Exception as err:
        if "No such file or directory" in str(err):
            name_file = str(err)[str(err).rfind("/") + 1:len(str(err)) - 1]
            name_directory = str(err)[str(err).find(': '):]
            error = ErrorWindow(base_info='Не хватает файлов для работы программы',
                                detail_info=f'Не хватает файла {name_file}\n'
                                            f'Файл должен располагаться в {name_directory}')
            error.set_settings()
            error()
        else:
            error = ErrorWindow(base_info='Произошел сбой в программе', detail_info=f'{str(err)}')
            error.set_settings()
            error()
