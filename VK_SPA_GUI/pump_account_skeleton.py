# -*- coding: utf-8 -*-

import os
import random
from random import randint
from time import sleep

import requests
import vk_api as VK

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QEventLoop, QTimer, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QGridLayout
import VK_SPA_Settings


class RunPumpAcc(QThread):
    """ Класс потока прокачки аккаунтв"""

    progress_pumping = QtCore.pyqtSignal(str)
    end_pumping = QtCore.pyqtSignal()

    def __init__(self, data, quantity_group, quantity_friend, quantity_photo):
        """ :param data - настройки, передающиеся в основном потоке
            :param quantity_group - число групп, на которые надо подписаться
            :param quantity_friend - количество людей, которым будет кинута заявка в друзья,
            :param quantity_photo - количество фотографий, которое будет добавленно в аккаунт"""

        super().__init__()
        self.login = data[0]
        self.password = data[1]
        self.proxy = data[2]
        self.interval = data[3]
        self.sex = data[4]
        self.status = data[5]
        self.quantity_group = quantity_group
        self.quantity_friend = quantity_friend
        self.quantity_photo = quantity_photo

    def try_proxy(self, proxy):
        """ Функция проверяет прокси на валидность, в случае успеха, возвращает данные прокси,
            в случае если прокси не рабочий будет возвращена текстовая ошибка """

        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        try:
            if 'Response [200]' in str(requests.get('https://www.vk.com/', proxies=proxies)):
                sess = requests.Session()
                sess.proxies.update({f'http': f'http://{proxy}',
                                     'https': f'http://{proxy}'})
                return proxies
        except Exception:
            return 'Данный прокси не рабочий!'

    def auth_for_pump(self, proxies):
        """ Функция авторизации аккаунта для его прокачки """
        try:
            self.vk_session = VK.VkApi(login=self.login, password=self.password)
            if proxies is not None:
                self.vk_session.http.proxies = proxies
            self.vk_session.auth()
            self.vk_object_sess = self.vk_session.get_api()
            base_info_account = self.vk_object_sess.account.getProfileInfo()
            return self.vk_object_sess

        except Exception as error_auth_pump2:
            if 'Bad password' in str(error_auth_pump2):
                return 'Неверный пароль'
            elif 'user is blocked' in str(error_auth_pump2):
                return 'Аккаунт заблокирован'
            elif 'Captcha' in str(error_auth_pump2):
                return 'Этот аккаунт не получится прокачать, попробуйте другой!'
            else:
                return str(error_auth_pump2)

    def ready_to_start_pump(self):
        """ Функция проверяет прокси на валидность, в случае его присутствия и проходит авторизацию,
            возвращает объект сессию """

        checked_proxy = self.try_proxy(self.proxy) if self.proxy else None
        if isinstance(checked_proxy, str):
            return checked_proxy

        auth_user = self.auth_for_pump(checked_proxy)

        return auth_user

    def change_acc_info(self, obj_sess, *args):
        """ Меняет основную информаю в профиле """

        try:
            if self.sex == 'female':
                obj_sess.account.saveProfileInfo(
                    maiden_name=random.choice(VK_SPA_Settings.girlish), relation=6, bdate_visibility=1,
                    status=self.status, country_id=1, city_id=2)

            elif self.sex == 'male':
                obj_sess.account.saveProfileInfo(relation=6, bdate_visibility=1, status=self.status, country_id=1,
                                                 city_id=2)

            return 'Поменяли информацию в аккаунте'

        except Exception as exc_profile:
            return f'<a title="{exc_profile}" href=# >Не удалось </a> поменять личную информацию'

    def join_groups(self, obj_sess, *args):
        """ Подписываемся на различные группы в вк """

        _err = 0
        for id_group in random.sample(VK_SPA_Settings.list_group_for_comment_and_likes_and_repost, self.quantity_group):
            try:
                obj_sess.groups.join(group_id=int(id_group))
                sleep(randint(1, 3))
            except Exception as err_join:
                _err = err_join
        return f'Вступили в {self.quantity_group} групп(ы)!' if _err == 0 else f'<a title="{_err}" href=# >Не удалось '\
                                                                               f'</a> вступить во все группы '

    def repost_some_post(self, obj_sess, *args):
        """ Делает репосты нескольких записей себе на страницу """

        _err_repost = ''
        count_news = 10
        news_list = obj_sess.newsfeed.get(count=count_news, max_photos=1, filters='post', source_ids='groups')
        for i in range(count_news):
            try:
                id_group = news_list['items'][i]['source_id']
                id_post = news_list['items'][i]['post_id']
                obj_sess.likes.add(type='post', owner_id=f'{id_group}', item_id=f'{id_post}')
                obj_sess.wall.repost(object=f'wall{str(id_group)}_{id_post}')
            except Exception as err_repost:
                _err_repost = err_repost
        if _err_repost == '':
            return f'Сделали несколько репостов для создания видимости жизни на странице!'
        else:
            return f'Часть постов <a title="{_err_repost}" href=# >не удалось </a> опублиоквать на странице '

    def add_friend(self, obj_sess, *args):
        """ Кидает заявки в друзья рандомным пользователям ВК """

        _err_add_friend = ''
        id_group = '43776215'
        first_1000 = obj_sess.groups.getMembers(group_id=id_group, v=5.131)  # Первое выполнение метода
        data = first_1000["items"]  # Присваиваем переменной первую тысячу id-шников
        for i in range(self.quantity_friend):
            try:
                id_future_friends = data[randint(0, len(data))]
                obj_sess.friends.add(user_id=id_future_friends)
            except Exception as err_add_friend:
                _err_add_friend = err_add_friend
        if _err_add_friend == '':
            return f'Сделали завяки на добавления в друзья рандомным пользователям'
        else:
            return f'Нескольким пользователям не удалось кинуть заявку в друзья'

    def add_video(self, obj_sess, my_id, *args):
        """ Добавляет несколько видео к себе на страницу """
        try:
            for id_video in VK_SPA_Settings.video:
                obj_sess.video.add(target_id=f'{my_id}',
                                   video_id=f'{id_video}', owner_id='-460389')
            return f'Добавили видео в профиль'
        except Exception as err_video:
            return f'<a title="{err_video} hre=# >"Не удалось </a> добавить видео'

    def set_avatar(self, obj_sess, my_id, *args):
        """ Устанавливает аватарку в профиль """
        url_photo = ''
        hash = ''
        result = ''
        try:  # прлучаем URL сервера для загрузки фото
            url_photo = obj_sess.photos.getOwnerPhotoUploadServer(owner_id=f'{my_id}')['upload_url']
        except BaseException as err_get_url:
            return f'<a title="{err_get_url}" href=# >Не удалось </a> поменять аватарку'
        file = {}
        try:
            if self.sex == 'female':
                dirname_pump = f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_female_pump/"
                ava = os.listdir(dirname_pump)
                photo_ava = random.choice(ava)
                file['photo'] = open(f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_female_pump/{photo_ava}",
                                     "rb")  # Рандомно выбираем 1 фото
            elif self.sex == 'male':
                dirname_pump = f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_male_pump/"
                ava = os.listdir(dirname_pump)
                photo_ava = random.choice(ava)
                file['photo'] = open(f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_male_pump/{photo_ava}",
                                     "rb")  # Рандомно выбираем 1 фото

            result = requests.post(url=url_photo, files=file)
            hash = result.json()['hash']

        except Exception as err_load:
            return f'<a title="{err_load}" href=# >Не удалось </a> поменять аватарку(ошибка при загрузке)'

        try:
            obj_sess.photos.saveOwnerPhoto(user_id=f'{my_id}', server=result.json()['server'], hash=f'{hash}',
                                           photo=result.json()['photo'])
            return 'Установили новую аватарку!'
        except Exception as err_photo:
            return f'<a title="{err_photo}" href=# >Не удалось </a> поменять аватарку(ошибка при установке)'

    def add_photo(self, obj_sess, my_id, *args):
        """ Добавляем фото в профиль """

        if self.quantity_photo == 0:
            return 'Вы не указали кол-во фото, поэтому фото не будут добавлены в профиль'

        url_album = ''
        hash = ''
        result_load = ''

        try:
            obj_sess.photos.createAlbum(title='Все мое))')  # Создаем новый альбом для добавления в него фото
        except Exception as err_new_album:
            return f'<a title="{err_new_album}" href=# >Не удалось </a> создать альбом'

        try:
            my_album = obj_sess.photos.getAlbums(owner_id=f'{my_id}')  # Получаем информацию об альбоме на странице
            url_for_load = obj_sess.photos.getUploadServer(album_id=my_album['items'][0]['id'])  # url для загрузки
            url_album = url_for_load['upload_url']
        except Exception as err_url:
            return f'<a title="{err_url}" href=# >Не удалось </a> загрузить фото'

        files = {}
        list_for_load = []
        for i in range(self.quantity_photo):  # Рандомно выбираем 8 фото
            if self.sex == 'female':
                dirname_pump = f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_female_pump/"
                list_photo_pump = os.listdir(dirname_pump)
                photo = random.choice(list_photo_pump)
                if photo not in list_for_load:
                    files[f'file{i + 1}'] = open(f"{VK_SPA_Settings.abspath_params}/"
                                                 f"Params_pump/photo_for_female_pump/{photo}", "rb")
            elif self.sex == 'male':
                dirname_pump = f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_male_pump/"
                list_photo_pump = os.listdir(dirname_pump)
                photo = random.choice(list_photo_pump)
                if photo not in list_for_load:
                    files[f'file{i + 1}'] = open(
                        f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_male_pump/{photo}",
                        "rb")
        try:
            result_load = requests.post(url=url_album, files=files)  # Посылаем запрос на загрузку фотографий
            hash = result_load.json()['hash']
        except Exception as err_load:
            return f'<a title="{err_load}" href=# >Не удалось </a> загрузить фото'
        try:
            my_album = obj_sess.photos.getAlbums(owner_id=f'{my_id}')  # Получаем id альбоме на странице
            obj_sess.photos.save(album_id=my_album['items'][0]['id'],  # Сохраняем фото с сервера в альбоме
                                 server=result_load.json()['server'],
                                 photos_list=result_load.json()['photos_list'],
                                 aid=result_load.json()['aid'],
                                 hash=f'{hash}')
            return 'Добавили фото в профиль'
        except Exception as err_save:
            return f'<a title="{err_save}" href=# >Не удалось </a> загрузить фото'

    def pumping_account(self, obj_sess):
        """ Основная функция прокачки аккаунта """
        my_id = obj_sess.account.getProfileInfo()['id']

        dict_func_and_description = {' Немного поменяем информацию в аккаунте ': self.change_acc_info,
                                     ' Добавляемся в популярные группы ': self.join_groups,
                                     ' Репостим несколько записей на страницу ': self.repost_some_post,
                                     ' Добавляемся в друзья к рандомным пользователям ': self.add_friend,
                                     ' Добавим немного видео в профиль ': self.add_video,
                                     ' Поменяем аватарку ': self.set_avatar,
                                     ' Добавим фото на страницу  ': self.add_photo}
        for description, func_action in dict_func_and_description.items():
            self.progress_pumping.emit(description.center(65, '-'))
            self.progress_pumping.emit(func_action(obj_sess, my_id))
            sleep(self.interval)

        self.progress_pumping.emit(f'Можете посмотреть на <a href=https://vk.com/id{my_id}>результат</a>')
        self.end_pumping.emit()

    def run(self):
        """ Запускает поток и запускает функцию прокачки """
        session = self.ready_to_start_pump()

        if isinstance(session, str):
            self.progress_pumping.emit(session)
            return self.end_pumping.emit()

        self.pumping_account(session)


class UiVkSpaPumpAccount_SKELETON(object):

    def __init__(self):

        self.centralwidget_PUMP_ACCOUNT = QtWidgets.QWidget()

        self.label_choose_from_list = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.label_choose_from_list.setGeometry(QtCore.QRect(25, 40, 201, 41))
        self.label_choose_from_list.setText('Если аккаунт уже есть в списке,\n    выберите его в поле ниже')
        self.label_result_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.label_result_pump.setGeometry(QtCore.QRect(2, 145, 141, 16))
        self.label_settings_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.label_settings_pump.setGeometry(QtCore.QRect(460, 40, 171, 20))
        self.label_settings_pump.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";")
        self.count_photo_label_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.count_photo_label_pump.setGeometry(QtCore.QRect(510, 145, 141, 31))
        self.count_group_label_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.count_group_label_pump.setGeometry(QtCore.QRect(510, 186, 111, 31))
        self.label_input_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.label_input_pump.setGeometry(QtCore.QRect(230, 20, 171, 41))
        self.interval_label_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.interval_label_pump.setGeometry(QtCore.QRect(510, 270, 191, 21))
        self.status_text_label_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.status_text_label_pump.setGeometry(QtCore.QRect(460, 340, 191, 16))
        self.count_friend_label_pump = QtWidgets.QLabel(self.centralwidget_PUMP_ACCOUNT)
        self.count_friend_label_pump.setGeometry(QtCore.QRect(510, 230, 141, 21))

        self.line_pump = QtWidgets.QFrame(self.centralwidget_PUMP_ACCOUNT)
        self.line_pump.setGeometry(QtCore.QRect(440, 18, 16, 421))
        self.line_pump.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_pump.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2_pump = QtWidgets.QFrame(self.centralwidget_PUMP_ACCOUNT)
        self.line_2_pump.setGeometry(QtCore.QRect(0, 10, 769, 16))
        self.line_2_pump.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2_pump.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3_pump = QtWidgets.QFrame(self.centralwidget_PUMP_ACCOUNT)
        self.line_3_pump.setGeometry(QtCore.QRect(357, 431, 411, 20))
        self.line_3_pump.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3_pump.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4_pump = QtWidgets.QFrame(self.centralwidget_PUMP_ACCOUNT)
        self.line_4_pump.setGeometry(QtCore.QRect(0, 18, 3, 142))
        self.line_4_pump.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4_pump.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5_pump = QtWidgets.QFrame(self.centralwidget_PUMP_ACCOUNT)
        self.line_5_pump.setGeometry(QtCore.QRect(761, 18, 16, 422))
        self.line_5_pump.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5_pump.setFrameShape(QtWidgets.QFrame.VLine)

        self.choose_male_checkBox_pump = QtWidgets.QCheckBox(self.centralwidget_PUMP_ACCOUNT)
        self.choose_male_checkBox_pump.setGeometry(QtCore.QRect(460, 110, 231, 20))
        self.choose_female_checkBox_pump = QtWidgets.QCheckBox(self.centralwidget_PUMP_ACCOUNT)
        self.choose_female_checkBox_pump.setGeometry(QtCore.QRect(460, 80, 231, 20))

        self.handle_input_checkbox = QtWidgets.QCheckBox(self.centralwidget_PUMP_ACCOUNT)
        self.handle_input_checkbox.setGeometry(QtCore.QRect(260, 50, 171, 20))
        self.handle_input_checkbox.setText('Ввести данные вручную')

        self.use_proxy_checkbox = QtWidgets.QCheckBox(self.centralwidget_PUMP_ACCOUNT)
        self.use_proxy_checkbox.setGeometry(QtCore.QRect(460, 310, 161, 21))
        self.use_proxy_checkbox.setText('Использовать прокси')

        self.interval_spinBox_pump = QtWidgets.QSpinBox(self.centralwidget_PUMP_ACCOUNT)
        self.interval_spinBox_pump.setGeometry(QtCore.QRect(460, 270, 42, 22))
        self.count_group_spinBox_pump = QtWidgets.QSpinBox(self.centralwidget_PUMP_ACCOUNT)
        self.count_group_spinBox_pump.setGeometry(QtCore.QRect(460, 190, 42, 22))
        self.count_group_spinBox_pump.setMaximum(35)
        self.count_foto_spinBox_pump = QtWidgets.QSpinBox(self.centralwidget_PUMP_ACCOUNT)
        self.count_foto_spinBox_pump.setGeometry(QtCore.QRect(460, 150, 42, 22))
        self.count_foto_spinBox_pump.setMinimum(0)
        self.count_friend_spinBox_pump = QtWidgets.QSpinBox(self.centralwidget_PUMP_ACCOUNT)
        self.count_friend_spinBox_pump.setGeometry(QtCore.QRect(460, 230, 42, 22))
        self.count_friend_spinBox_pump.setMinimum(40)
        self.choose_acc_comboBox_pump = QtWidgets.QComboBox(self.centralwidget_PUMP_ACCOUNT)
        self.choose_acc_comboBox_pump.setGeometry(QtCore.QRect(10, 90, 220, 27))
        self.choose_proxy_comboBox_pump = QtWidgets.QComboBox(self.centralwidget_PUMP_ACCOUNT)
        self.choose_proxy_comboBox_pump.setGeometry(QtCore.QRect(620, 310, 145, 23))
        self.choose_proxy_comboBox_pump.close()

        self.go_pump_pushButton_pump = QtWidgets.QPushButton(self.centralwidget_PUMP_ACCOUNT)
        self.go_pump_pushButton_pump.setGeometry(QtCore.QRect(460, 390, 191, 41))
        self.go_pump_pushButton_pump.setStyleSheet("background-color: rgb(0, 255, 127);\n"
                                                   "font: 75 11pt \"MS Shell Dlg 2\";")
        self.add_new_photo_pushButton_pump = QtWidgets.QPushButton(self.centralwidget_PUMP_ACCOUNT)
        self.add_new_photo_pushButton_pump.setGeometry(QtCore.QRect(660, 145, 101, 31))
        self.add_new_photo_pushButton_pump.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                         "color: rgb(255, 255, 255);\n"
                                                         "font: 75 8pt \"MS Shell Dlg 2\";")

        self.status_text_lineEdit_pump = QtWidgets.QLineEdit(self.centralwidget_PUMP_ACCOUNT)
        self.status_text_lineEdit_pump.setGeometry(QtCore.QRect(460, 358, 171, 22))
        self.status_text_lineEdit_pump.setPlaceholderText("")
        self.status_text_lineEdit_pump.setPlaceholderText("Всем привет!")
        self.login_lineEdit_pump = QtWidgets.QLineEdit(self.centralwidget_PUMP_ACCOUNT)
        self.login_lineEdit_pump.setGeometry(QtCore.QRect(260, 80, 151, 22))
        self.login_lineEdit_pump.setText("")
        self.login_lineEdit_pump.setPlaceholderText("Номер телефона")
        self.password_lineEdit_pump = QtWidgets.QLineEdit(self.centralwidget_PUMP_ACCOUNT)
        self.password_lineEdit_pump.setGeometry(QtCore.QRect(260, 110, 151, 22))
        self.password_lineEdit_pump.setText("")
        self.password_lineEdit_pump.setPlaceholderText("Пароль")
        self.result_textBrowser_pump = QtWidgets.QTextBrowser(self.centralwidget_PUMP_ACCOUNT)
        self.result_textBrowser_pump.setGeometry(QtCore.QRect(0, 160, 438, 281))
        self.result_textBrowser_pump.setOpenExternalLinks(True)

        self.update_list_acc = QtWidgets.QPushButton(self.centralwidget_PUMP_ACCOUNT)
        self.update_list_acc.setGeometry(QtCore.QRect(230, 90, 18, 25))
        self.update_list_acc.setStyleSheet("background-color: rgb(0, 255, 127);\n"
                                           "font: 75 11pt \"MS Shell Dlg 2\";")

        self.line_3_pump.raise_()
        self.line_2_pump.raise_()
        self.line_4_pump.raise_()
        self.line_pump.raise_()
        self.line_5_pump.raise_()

        self.retranslateUi()
        self.function_pump()
        self.choose_acc_pump()

        self.interval_spinBox_pump.setValue(17)
        self.count_friend_spinBox_pump.setValue(10)
        self.count_group_spinBox_pump.setValue(30)

        self.grid = QGridLayout()
        self.grid.addWidget(self.result_textBrowser_pump)

        self.proxy_for_pump = None

        self.choose_female_checkBox_pump.setChecked(True)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate

        self.label_result_pump.setText(_translate("MainWindow", "Результаты прокачки"))

        self.label_settings_pump.setText(_translate("MainWindow", "Настройки прокачки"))
        self.choose_female_checkBox_pump.setText(_translate("MainWindow", "Прокачка женского акаунта"))
        self.count_photo_label_pump.setText(_translate("MainWindow", "Сколько фото добавить\n"
                                                                     "на страницу"))
        self.go_pump_pushButton_pump.setText(_translate("MainWindow", "Начать прокачку"))
        self.count_group_label_pump.setText(_translate("MainWindow", "На сколько групп\n"
                                                                     "подписаться"))

        self.choose_male_checkBox_pump.setText(_translate("MainWindow", "Прокачка мужского акаунта"))
        self.interval_label_pump.setText(_translate("MainWindow", "Интервал между действиями"))
        self.status_text_label_pump.setText(_translate("MainWindow", "Какой текст указать в статусе"))
        self.count_friend_label_pump.setText(_translate("MainWindow", "Кол-во заявок в друзья"))
        self.add_new_photo_pushButton_pump.setText(_translate("MainWindow", "Добавить фото "))

    def function_pump(self):
        self.use_proxy_checkbox.stateChanged.connect(lambda: self.choose_proxy_pump())
        self.update_list_acc.clicked.connect(lambda: self.update_list_acc_func())
        self.add_new_photo_pushButton_pump.clicked.connect(lambda: self.add_new_photo_pump())
        self.go_pump_pushButton_pump.clicked.connect(lambda: self.go_pump())

        self.choose_male_checkBox_pump.stateChanged.connect(lambda: self.get_quantity_photo_in_photo_folder('male'))
        self.choose_female_checkBox_pump.stateChanged.connect(lambda: self.get_quantity_photo_in_photo_folder('female'))


    def get_quantity_photo_in_photo_folder(self, sex):
        """ Устанавливает максимальное кол-во фото для добавления в аккаунт, в зависимости от кол-ва фото в папке """

        dirname_folder = f"{VK_SPA_Settings.abspath_params}/Params_pump/photo_for_{sex}_pump/"
        list_photo_pump = os.listdir(dirname_folder)

        if self.choose_male_checkBox_pump.isChecked() and sex == 'male':
            self.count_foto_spinBox_pump.setMaximum(len(list_photo_pump)-1)
            self.choose_female_checkBox_pump.setChecked(False)

        elif self.choose_female_checkBox_pump.isChecked() and sex == 'female':
            self.count_foto_spinBox_pump.setMaximum(len(list_photo_pump)-1)
            self.choose_male_checkBox_pump.setChecked(False)

    def add_new_photo_pump(self):
        """ Открывает папку для добавления фото """

        os.system(rf"explorer.exe {os.getcwd().replace('VK_SPA_GUI', 'params')}\Params_pump")

    def choose_acc_pump(self):
        self.choose_acc_comboBox_pump.addItem('---------')
        with open(f'{VK_SPA_Settings.abspath_params}/ACCOUNTS.txt', 'r') as accs:
            name_accounts = accs.readlines()
            for acc in name_accounts:
                if acc == '\n':
                    pass
                else:
                    self.choose_acc_comboBox_pump.addItem(acc.replace('\n', ''))

    def choose_proxy_pump(self):
        if self.use_proxy_checkbox.isChecked():
            self.choose_proxy_comboBox_pump.addItem('---------')
            with open(f'{VK_SPA_Settings.abspath_params}/PROXY.txt', 'r') as prx:
                name_proxy = prx.readlines()
            for px in name_proxy:
                if px == '\n':
                    pass
                else:
                    self.choose_proxy_comboBox_pump.addItem(px.replace('\n', ''))
            self.choose_proxy_comboBox_pump.show()
        elif self.use_proxy_checkbox.isChecked() is False:
            self.choose_proxy_comboBox_pump.close()
            self.choose_proxy_comboBox_pump.clear()

    def update_list_acc_func(self):
        self.choose_acc_comboBox_pump.clear()
        self.choose_acc_pump()

    def check_settings(self, login, password, proxy, interval):
        """ Проверки настроек аккаунта, по умолчанию пол выбран женский"""

        sex = 'female'

        if self.choose_female_checkBox_pump.isChecked() and self.choose_male_checkBox_pump.isChecked():
            return 'Выберите либо женский аккаунт, либо мужской!'

        if self.handle_input_checkbox.isChecked() and self.choose_acc_comboBox_pump.currentText() != '---------':
            return 'Либо выберите аккаунт из списка, либо введите его данные вручную!'

        if self.handle_input_checkbox.isChecked() is False and self.choose_acc_comboBox_pump.currentText() == '---------':
            return 'Вы не выбрали аккаунт из списка'

        if self.handle_input_checkbox.isChecked():
            if len(login) == 0 or login.isdigit() is False or login.isspace() or login is None:
                return 'Неверно введены данные логина'
            if len(password) == 0 or password.isspace() or password is None:
                return 'Строка с паролем пуста!'

        if self.use_proxy_checkbox.isChecked():
            if '-' in proxy or len(proxy) == 0 or proxy is None:
                return 'Вы не выбрали прокси'

        if interval == 0:
            interval = randint(17, 25)

        if self.choose_male_checkBox_pump.isChecked():
            sex = 'male'

        status = self.status_text_lineEdit_pump.text()
        if len(status) < 1:
            status = 'Всем привет!'

        return login, password, proxy, interval, sex, status

    def get_log_pass(self, type_entered_account):
        """ Проверяем выбранные логин и пароль в зависимости от способа выбора на корректность
            list - логин и пароль выбраны из файла,
            handle - логин и пароль введены вручную """

        login, password = None, None

        if type_entered_account == 'handle':
            login = self.login_lineEdit_pump.text()
            password = self.password_lineEdit_pump.text()

        elif type_entered_account == 'list':
            log_pass = self.choose_acc_comboBox_pump.currentText()
            login = log_pass[0:log_pass.find(';')]
            password = log_pass[log_pass.find(';') + 1: log_pass.find(':')]

        return login, password

    def go_pump(self):
        """ Запускает поток по прокачке аккааунта из основного потока """

        log_pass = self.get_log_pass('handle') if self.handle_input_checkbox.isChecked() else self.get_log_pass('list')
        proxy = self.choose_proxy_comboBox_pump.currentText() if self.use_proxy_checkbox.isChecked() else None

        result_checking = self.check_settings(log_pass[0], log_pass[1], proxy, self.interval_spinBox_pump.value())

        if isinstance(result_checking, str):
            return self.error_window_pump(result_checking)

        self.disable_button()
        self.thread_pump = RunPumpAcc(data=result_checking,
                                      quantity_group=self.count_group_spinBox_pump.value(),
                                      quantity_friend=self.count_friend_spinBox_pump.value(),
                                      quantity_photo=self.count_foto_spinBox_pump.value())
        self.thread_pump.progress_pumping.connect(lambda vl: self.result_textBrowser_pump.append(vl))
        self.thread_pump.start()
        self.thread_pump.end_pumping.connect(self.enable_button)

    def disable_button(self):
        """ Делает кнопки недоступными для нажатия """

        self.result_textBrowser_pump.clear()
        self.go_pump_pushButton_pump.setEnabled(False)
        self.use_proxy_checkbox.setEnabled(False)
        self.choose_proxy_comboBox_pump.setEnabled(False)
        self.add_new_photo_pushButton_pump.setEnabled(False)

    def enable_button(self):
        """ Делает кнопки доступными для нажатия """

        self.go_pump_pushButton_pump.setEnabled(True)
        self.use_proxy_checkbox.setEnabled(True)
        self.choose_proxy_comboBox_pump.setEnabled(True)
        self.add_new_photo_pushButton_pump.setEnabled(True)
        self.add_new_photo_pushButton_pump.setEnabled(True)

    def error_window_pump(self, text_error, err_detail=None):
        """ Показывает окно с ошибкой """

        error_wind = QMessageBox()
        error_wind.setWindowTitle('Ошибка')
        error_wind.setText(f'{text_error}')
        error_wind.setWindowIcon(QIcon(f'{VK_SPA_Settings.abspath_params}/Picture_gui/error.png'))
        error_wind.setIcon(QMessageBox.Warning)
        error_wind.setStandardButtons(QMessageBox.Ok)
        if err_detail:
            error_wind.setDetailedText(str(err_detail))
        error_wind.exec_()
        return error_wind
