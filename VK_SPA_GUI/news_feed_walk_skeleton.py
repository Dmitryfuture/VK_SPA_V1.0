# -*- coding: utf-8 -*-

from datetime import datetime
from random import randint, choice
from time import sleep

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox

import VK_SPA_Settings


class RunNewsWalk(QThread):
    """ Класс потока авторизации пользователя """
    thread_process = QtCore.pyqtSignal(str)
    thread_stop = QtCore.pyqtSignal()

    def __init__(self, settings):
        super().__init__()
        self.vk_method = settings[0]
        self.interval = settings[1]
        self.count_action = settings[2]
        self.STOP_NEWS_FEED_WALK = False

    def get_list_news_post(self):
        """ Получаем информацию из новостной ленты для дальнейшего взаимодействия с ней.
        В случае неудачи, возвращает str с ошибкой"""
        try:
            news_list = self.vk_method.newsfeed.get(count=self.count_action, max_photos=1, filters='post',
                                                    source_ids='groups')
            return news_list if len(news_list) >= 1 else 'Список новостной ленты пуст!'
        except Exception as error_news_1:
            return f'<a title="{error_news_1}" href=# >Не удалось </a> пройти по новостной ленте, попробуйте позже!'

    def only_repost_and_like(self, id_group, id_post, time_like, user_id):
        """ Делает только репост записи к себе на станицу и лайк на нее """
        try:
            self.vk_method.likes.add(type='post', owner_id=f'{id_group}', item_id=f'{id_post}')
            self.vk_method.wall.repost(object=f'wall{str(id_group)}_{id_post}')
            return f'В {time_like} на вашу страницу добавленна <a href=https://vk.com/id{user_id}>запись</a>'
        except Exception as err_repost:
            return f'<a title="{err_repost}" href=# >Не удалось</a> сделать репост записи из новостной ленты'

    def only_comment(self, id_group, id_post, time_like):
        """ Только написание коммнетария под записью """
        try:
            message = choice(VK_SPA_Settings.simple_comment)  # Рандомно выбранный коммент
            self.vk_method.wall.createComment(owner_id=f'{id_group}', post_id=f'{id_post}',
                                         message=message)
            return f'В {time_like} в <a href=https://vk.com/wall{str(id_group)}_{str(id_post)}>группе</a> ' \
                   f'написан коммент {message}'
        except Exception as err_comment:
            return f'<a title="{err_comment}" href=# >Не удалось </a> написать комментарий к записи в новостной ленте'

    def only_like(self, id_group, id_post, time_like):
        """ Ставит только лайк на запись в новостной ленте """
        try:
            self.vk_method.likes.add(type='post', owner_id=f'{id_group}', item_id=f'{id_post}')
            return f'В {time_like} в новостной ленте лайкнута ' \
                   f'<a href=https://vk.com/wall{str(id_group)}_{str(id_post)}>запись</a>'
        except Exception as err_like:
            return f'<a title="{err_like}" href=# >Не удалось </a> лайкнуть запись в новостной ленте'

    def ready_to_start_walking(self):
        """ Функция генератор,  проходит циклом по списку записей и возвращает функцию-действие"""
        news_list = self.get_list_news_post()
        if isinstance(news_list, str):
            return self.thread_process.emit(news_list)

        for i in range(self.count_action):
            try:
                n = randint(1, 10)  # Число для рандомного выбора действия
                user_id = self.vk_method.account.getProfileInfo()['id']  # Получаем ID своей страницы для отчетности
                time_like = datetime.now().strftime("%H:%M:%S")  # Время репоста записи
                id_group = news_list['items'][i]['source_id']
                id_post = news_list['items'][i]['post_id']

                if self.STOP_NEWS_FEED_WALK:
                    break

                if n in [1, 3, 5, 10, 9]:
                    yield self.only_like(id_group, id_post, time_like)
                elif n in [2, 7, 6]:
                    yield self.only_repost_and_like(id_group, id_post, time_like, user_id)
                elif n in [4, 8]:
                    yield self.only_comment(id_group, id_post, time_like)
            except IndexError as err_index:
                print(err_index)
                break
            sleep(randint(*self.interval))

        if self.STOP_NEWS_FEED_WALK is False:
            yield ' Проход по новостной ленте окончен '.center(60, '-')

    def run(self):
        """ Функция прохода по генератору """
        self.thread_process.emit(' Начали проход по новостной ленте '.center(60, '-'))
        generator_news_walking = self.ready_to_start_walking()
        for i in generator_news_walking:
            self.thread_process.emit(i)

        self.thread_stop.emit()


class UiVkSpaNewsFeedWalk_SKELETON(object):

    def __init__(self):

        self.centralwidget_NEWS_FEED_WALK = QtWidgets.QWidget()

        self.label_count_post_news_feed = QtWidgets.QLabel(self.centralwidget_NEWS_FEED_WALK)
        self.label_count_post_news_feed.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_count_post_news_feed.setText("Выберите число записей для\nкомментирования/лайка/репоста")
        self.label_count_post_news_feed.setGeometry(QtCore.QRect(518, 260, 250, 50))
        self.label_report_news_feed = QtWidgets.QLabel(self.centralwidget_NEWS_FEED_WALK)
        self.label_report_news_feed.setGeometry(QtCore.QRect(0, 180, 411, 16))
        self.label_report_news_feed.setText("Отчет")
        self.label_description_news_feed = QtWidgets.QLabel(self.centralwidget_NEWS_FEED_WALK)
        self.label_description_news_feed.setGeometry(QtCore.QRect(30, 10, 741, 61))
        self.label_description_news_feed.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_description_news_feed.setText("                   Данная функция делает проход выбранным "
                                                 "аккаунтом по новостной ленте.\n"
                                                 "                         Рекомендуется делать проход "
                                                 "перед рассылкой спама по стенам.\n"
                                                 " Для работоспособности функции рекомендуется сначала "
                                                 "воспользоваться функцией \"Прокачка аккаунта\"")
        self.label_interval_news_feed = QtWidgets.QLabel(self.centralwidget_NEWS_FEED_WALK)
        self.label_interval_news_feed.setGeometry(QtCore.QRect(460, 320, 281, 21))
        self.label_interval_news_feed.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_interval_news_feed.setText('Выберите интервал между действиями')
        self.label_from_news_feed = QtWidgets.QLabel(self.centralwidget_NEWS_FEED_WALK)
        self.label_from_news_feed.setGeometry(QtCore.QRect(470, 350, 21, 21))
        self.label_from_news_feed.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_from_news_feed.setText('От')
        self.label_to_news_feed = QtWidgets.QLabel(self.centralwidget_NEWS_FEED_WALK)
        self.label_to_news_feed.setGeometry(QtCore.QRect(580, 350, 21, 21))
        self.label_to_news_feed.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_to_news_feed.setText('до')

        self.listView_result_news_feed = QtWidgets.QTextBrowser(self.centralwidget_NEWS_FEED_WALK)
        self.listView_result_news_feed.setGeometry(QtCore.QRect(0, 200, 445, 241))
        self.listView_result_news_feed.setReadOnly(True)
        self.listView_result_news_feed.setOpenExternalLinks(True)

        self.Go_button_news_feed_walk = QtWidgets.QPushButton(self.centralwidget_NEWS_FEED_WALK)
        self.Go_button_news_feed_walk.setGeometry(QtCore.QRect(0, 88, 781, 41))
        self.Go_button_news_feed_walk.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";"
                                                    "background-color: rgb(0, 170, 255);")
        self.Go_button_news_feed_walk.setText("Начать проход по новостной ленте")
        self.Stop_button_news_feed_walk = QtWidgets.QPushButton(self.centralwidget_NEWS_FEED_WALK)
        self.Stop_button_news_feed_walk.setGeometry(QtCore.QRect(0, 144, 781, 33))

        self.Stop_button_news_feed_walk.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";"
                                                      "background-color: rgb(255, 0, 0);")
        self.Stop_button_news_feed_walk.setText('Остановить проход')

        self.fromInterval_spinBox_news_feed = QtWidgets.QSpinBox(self.centralwidget_NEWS_FEED_WALK)
        self.fromInterval_spinBox_news_feed.setGeometry(QtCore.QRect(510, 350, 51, 21))
        self.toInterval_spinBox_news_feed = QtWidgets.QSpinBox(self.centralwidget_NEWS_FEED_WALK)
        self.toInterval_spinBox_news_feed.setGeometry(QtCore.QRect(620, 350, 51, 21))
        self.count_news_spinBox_news_feed = QtWidgets.QSpinBox(self.centralwidget_NEWS_FEED_WALK)
        self.count_news_spinBox_news_feed.setGeometry(QtCore.QRect(450, 270, 61, 31))
        self.count_news_spinBox_news_feed.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";")

        self.function_news_feed_walk()

        self.Stop_button_news_feed_walk.setEnabled(False)

        self.VK_NEWS_FEED_METHOD_FROM_MAIN = None

    def function_news_feed_walk(self):
        self.Go_button_news_feed_walk.clicked.connect(lambda: self.news_feed_walk(
            vk_method=self.VK_NEWS_FEED_METHOD_FROM_MAIN))
        self.Stop_button_news_feed_walk.clicked.connect(lambda: self.stop_news_feed_walk())

    def check_settings(self, vk_method, interval: tuple, count: int):
        """ Проверят настройки пользователя.
            :param vk_method - object, сам объект сессии
            :param interval - type tuple(from, to)
            :param count - int, число записей в новостонйо ленте для взаимодействия с ними
            """
        if vk_method is None:
            return 'Вы не прошли авторизацию в программе!'

        if interval[0] >= interval[1]:
            return 'Вы неправильно указали интервал!'

        if count == 0:
            return 'Вы не выбрали число записей!'

        return vk_method, interval, count

    def buttons_disabled(self):
        """ Делает часть кнопок недоступными для нажатия """
        self.listView_result_news_feed.clear()
        self.Go_button_news_feed_walk.setEnabled(False)
        self.Stop_button_news_feed_walk.setEnabled(True)

    def buttons_enabled(self):
        """ Делает часть кнопок доступными для нажатия """
        self.Go_button_news_feed_walk.setEnabled(True)
        self.Stop_button_news_feed_walk.setEnabled(False)
        self.STOP_NEWS_FEED_WALK = False

    def news_feed_walk(self, vk_method):
        """ Функция прохода по записям в новостной ленте"""

        interval = (self.fromInterval_spinBox_news_feed.value(), self.toInterval_spinBox_news_feed.value())
        result_checking_settings = self.check_settings(vk_method, interval, self.count_news_spinBox_news_feed.value())

        if isinstance(result_checking_settings, str):
            return self.error_window_news_feed(result_checking_settings)

        self.buttons_disabled()

        self.thread_launch = RunNewsWalk(settings=result_checking_settings)
        self.thread_launch.thread_process.connect(lambda value: self.listView_result_news_feed.append(value))
        self.thread_launch.start()
        self.thread_launch.thread_stop.connect(self.buttons_enabled)

    def stop_news_feed_walk(self):
        self.listView_result_news_feed.append(' Проход по ленте окончен закончен пользователем! '.center(65, '-'))
        self.thread_launch.STOP_NEWS_FEED_WALK = True
        self.Go_button_news_feed_walk.setEnabled(True)
        self.Stop_button_news_feed_walk.setEnabled(False)

    def error_window_news_feed(self, text_error, err_detail=None):
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

