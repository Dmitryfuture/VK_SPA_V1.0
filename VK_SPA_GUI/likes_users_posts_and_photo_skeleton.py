# -*- coding: utf-8 -*-

from random import randint
from time import sleep

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import VK_SPA_Settings


class ThreadTraversalLikes(QThread):
    """ Класс потока запуска прохода """
    thread_ended = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(str)

    def __init__(self, interval, list_ids, count, vk_method, window_for_change):
        """ :param interval - интервал между итерациями;
            :param list_ids - список id страниц для их прохода;
            :param count - кол-во записей и фотографий для лайков;
            :param vk_method - основной объект сессии для работоспособности данного класса;
            :param window_for_change - окно основного интерфейса, в него будет передаваться вся информация.
         """
        super().__init__()
        """ :param STOP_LIKES - для принудительной остановки цикла, False по умолчанию.  """
        self.interval = interval
        self.list_ids = list_ids
        self.count = count
        self.vk_method = vk_method
        self.STOP_LIKES = False
        self.window_for_change = window_for_change

    def get_info_about_user_page(self, user_id, count):
        """ Собирает информацию о странице юзера. Возвращает кортеж:
            ()[0] - информация(словарь) о постах на странице
            ()[1] - информация(словарь) о фотограифях на странице
         """
        post_user_info = self.vk_method.wall.get(owner_id=f'{int(user_id)}', offset=0, count=count, filter='all')
        user_photos = self.vk_method.photos.get(owner_id=f'{int(user_id)}', album_id='profile', count=count, rev=1)
        return post_user_info, user_photos

    def likes_functions(self, id_post_or_photo, user_id, search_object, vk_method):
        """ Функция для нажатия лайка на странице юзера.
            search_object - для определения где будут ставиться лайки, на постах или фотографиях"""

        def do_it(i):
            if search_object == 'post':
                return vk_method.likes.add(type='post',
                                           owner_id=f'{int(user_id)}',
                                           item_id=f'{id_post_or_photo["items"][i]["id"]}')
            elif search_object == 'photo':
                return vk_method.likes.add(type='photo', owner_id=f'{int(user_id)}',
                                           item_id=f'{id_post_or_photo["items"][i]["id"]}')

        return do_it

    def go_likes(self, vk_method):
        """ Функция, которая ставит лайки на фото и записи юзеров """
        self.progress.emit(' Начали проход '.center(65, '-'))

        for user_id in list(self.list_ids.split('\n')):
            if self.STOP_LIKES:
                break

            try:
                all_info_about_user_page = self.get_info_about_user_page(user_id=user_id, count=self.count, )
            except Exception as err_collect_info:
                if "This profile is private" in str(err_collect_info):
                    self.progress.emit('Не удалось собрать информацию на '
                                       f'<a href=https://vk.com/id{str(user_id)}>странице</a>'
                                       f'. Закрытый профиль!')
                else:
                    self.progress.emit('Не удалось собрать информацию на '
                                       f'<a href=https://vk.com/id{str(user_id)}>странице</a>')
                sleep(self.interval)
                continue

            try:
                func_for_like_post = self.likes_functions(id_post_or_photo=all_info_about_user_page[0],
                                                          vk_method=vk_method, user_id=user_id, search_object='post')
                [func_for_like_post(i) for i in range(self.count)]
                self.progress.emit(f'Поставили лайк на записи на <a href=https://vk.com/id{str(user_id)}>странице</a>')
            except Exception as err_likes_post:
                print(err_likes_post)
                self.progress.emit('Лайкнуты не все записи <a href=https://vk.com/id{str(user_id)}>в аккаунте</a>')

            try:
                func_for_like_photo = self.likes_functions(id_post_or_photo=all_info_about_user_page[1],
                                                           vk_method=vk_method,
                                                           user_id=user_id, search_object='photo')
                [func_for_like_photo(i) for i in range(self.count)]
                self.progress.emit(f'Поставили лайк на фото <a href=https://vk.com/id{str(user_id)}>пользователя</a>')
            except Exception as err_likes_photo:
                print(err_likes_photo)
                self.progress.emit('Лайкнуты не все фотографии <a href=https://vk.com/id{str(user_id)}>в аккаунте</a>')
            sleep(self.interval)
        if self.STOP_LIKES:
            self.STOP_LIKES = False
            self.progress.emit(' Рассылка остановлена пользователем '.center(46, '-'))
        else:
            self.progress.emit(' Закончили проход '.center(65, '-'))
        self.STOP_LIKES = False

    def run(self):
        self.go_likes(self.vk_method)
        self.thread_ended.emit()


class Ui_VkSpa_LikesUsersPostsAndPhoto_SKELETON:

    def __init__(self):
        self.central_widget_LIKES_UESERS_POST_AND_PHOTO = QtWidgets.QWidget()

        self.label_ID_users_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_ID_users_likes.setGeometry(QtCore.QRect(440, 170, 231, 16))
        self.label_ID_users_likes.setObjectName("label_report_2")
        self.label_from_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_from_likes.setGeometry(QtCore.QRect(470, 420, 21, 21))
        self.label_from_likes.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_from_likes.setText('От')
        self.label_to_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_to_likes.setGeometry(QtCore.QRect(580, 420, 21, 21))
        self.label_to_likes.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_to_likes.setText('до')
        self.label_interval_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_interval_likes.setGeometry(QtCore.QRect(460, 394, 281, 21))
        self.label_interval_likes.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_interval_likes.setText('Выберите интервал между действиями')
        self.label_count_post_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_count_post_likes.setGeometry(QtCore.QRect(530, 330, 241, 41))
        self.label_count_post_likes.setObjectName("label_count_post")
        self.label_count_post_likes.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")

        self.label_report_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_report_likes.setGeometry(QtCore.QRect(0, 166, 51, 16))
        self.label_report_likes.setObjectName("label_report")
        self.label_report_likes.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";")

        self.gif_auth = QtGui.QMovie(f'{VK_SPA_Settings.abspath_params}/Picture_gui/load_main.gif')
        self.gif_auth.setScaledSize(QtCore.QSize(20, 20))

        self.label_gif = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_gif.setGeometry(QtCore.QRect(50, 165, 20, 20))
        self.label_gif.setMovie(self.gif_auth)

        self.label_description_likes = QtWidgets.QLabel(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.label_description_likes.setGeometry(QtCore.QRect(30, 10, 741, 61))
        self.label_description_likes.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_description_likes.setObjectName("label_description")

        self.Go_users_like_button = QtWidgets.QPushButton(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.Go_users_like_button.setGeometry(QtCore.QRect(0, 78, 781, 41))
        self.Go_users_like_button.setStyleSheet("font: 75 12pt \"MS Shell Dlg 2\";"
                                                "background-color: rgb(0, 170, 255);")
        self.Go_users_like_button.setObjectName("button_news_feed_walk")
        self.Stop_users_like_button = QtWidgets.QPushButton(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.Stop_users_like_button.setGeometry(QtCore.QRect(0, 133, 781, 25))
        self.Stop_users_like_button.setStyleSheet("background-color: rgb(255, 0, 0);\n"
                                                  "font: 10pt \"MS Shell Dlg 2\";")
        self.Stop_users_like_button.setObjectName("button_news_feed_walk_3")

        self.search_result_textBrowser_likes = QtWidgets.QTextBrowser(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.search_result_textBrowser_likes.setGeometry(QtCore.QRect(0, 190, 381, 241))
        self.search_result_textBrowser_likes.setObjectName("listView_search_result")
        self.search_result_textBrowser_likes.setOpenExternalLinks(True)
        self.ID_users_textEdit_likes = QtWidgets.QTextEdit(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.ID_users_textEdit_likes.setGeometry(QtCore.QRect(440, 190, 341, 141))
        self.ID_users_textEdit_likes.setObjectName("textEdit")

        self.count_posts_on_page_spinBox_likes = QtWidgets.QSpinBox(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.count_posts_on_page_spinBox_likes.setGeometry(QtCore.QRect(450, 340, 61, 31))
        self.count_posts_on_page_spinBox_likes.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        self.count_posts_on_page_spinBox_likes.setObjectName("count_news_spinBox")
        self.fromInterval_spinBox_likes = QtWidgets.QSpinBox(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.fromInterval_spinBox_likes.setGeometry(QtCore.QRect(510, 420, 51, 21))
        self.fromInterval_spinBox_likes.setObjectName("fromInterval_spinBox")
        self.toInterval_spinBox_likes = QtWidgets.QSpinBox(self.central_widget_LIKES_UESERS_POST_AND_PHOTO)
        self.toInterval_spinBox_likes.setGeometry(QtCore.QRect(620, 420, 51, 21))
        self.toInterval_spinBox_likes.setObjectName("toInterval_spinBox")

        self.Go_users_like_button.raise_()
        self.search_result_textBrowser_likes.raise_()
        self.count_posts_on_page_spinBox_likes.raise_()
        self.label_count_post_likes.raise_()
        self.label_report_likes.raise_()
        self.label_description_likes.raise_()
        self.ID_users_textEdit_likes.raise_()
        self.label_ID_users_likes.raise_()
        self.Stop_users_like_button.raise_()

        self.retranslateUi()
        self.function_likes_users_post()

        self.toInterval_spinBox_likes.setValue(22)
        self.fromInterval_spinBox_likes.setValue(12)
        self.count_posts_on_page_spinBox_likes.setValue(5)

        self.Stop_users_like_button.setEnabled(False)
        self.VK_LIKES_USERS_METHOD_FROM_MAIN = None

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate

        self.Go_users_like_button.setText(_translate("MainWindow", "Начать проход по списку пользователей"))
        self.label_count_post_likes.setText(_translate("MainWindow", "Кол-во записей на которые\n   будет ставиться"
                                                                     " лайк"))
        self.label_report_likes.setText(_translate("MainWindow", "Отчет"))
        self.label_description_likes.setText(_translate("MainWindow", "                   Данная функция делает проход "
                                                                      "по страницам выбранных пользователей.\n"
                                                                      "                          Ставит им лайки на "
                                                                      "фото и на последние записи на странице"))
        self.label_ID_users_likes.setText(_translate("MainWindow", "ID пользователей"))
        self.Stop_users_like_button.setText(_translate("MainWindow", "Остановить проход"))

    def function_likes_users_post(self):

        self.Go_users_like_button.clicked.connect(lambda: self.go_likes_traversal(
            vk_method=self.VK_LIKES_USERS_METHOD_FROM_MAIN))
        self.Stop_users_like_button.clicked.connect(lambda: self.stop_likes())

    def clear_text_browser(self, action):
        """ Делает кнопки недоступными для нажатия и наоборот, также очистка поля вывода текста
            :param action True - делает нажатие возможным
            :param action False - делает нажатие невозможным """
        if action is False:
            self.search_result_textBrowser_likes.clear()
            self.Go_users_like_button.setEnabled(False)
            self.Stop_users_like_button.setEnabled(True)
        else:
            self.thread_go_likes.STOP_LIKES = True
            self.Go_users_like_button.setEnabled(True)
            self.Stop_users_like_button.setEnabled(False)

    def check_conditions(self, list_id, count):
        """ Проверка правильности заполнения настроек и ввода данных. Возвращает кортеж:
             ()[0] - текст ошибки в случае её появления;
             ()[1] - False - в случае ошибки, True - в случае успешной проверки """

        if self.VK_LIKES_USERS_METHOD_FROM_MAIN is None:
            return ('Сначала авторизуйте пользователя!',
                    'Возможно вы не прошли авторизацию, для использования этой функции нужна авторизация!'), False
        elif len(list_id) <= 1:
            return 'Список с ID пустой!\nЗаполните список перед началом работы!', False
        elif False in list(map(lambda i: i.replace('\n', '').isdigit(), list_id.split('\n'))):
            return ('Список с ID заполнен неправильно!', 'В списке не должно быть пробелом и букв, только цифры'), False
        elif count <= 0:
            return 'Выберите количество записей для лайков', False
        else:
            return None, True

    def go_likes_traversal(self, vk_method):
        """ Запускает поток прохода (traversal) по списку пользователей """
        interval = randint(int(self.fromInterval_spinBox_likes.text()), int(self.toInterval_spinBox_likes.text()))
        IDs = self.ID_users_textEdit_likes.toPlainText()
        count = int(self.count_posts_on_page_spinBox_likes.text())
        result_checking = self.check_conditions(list_id=IDs, count=count)

        if result_checking[1] is False:
            self.error_window_likes(result_checking[0])
            return
        elif result_checking[1]:
            self.clear_text_browser(False)
            self.thread_go_likes = ThreadTraversalLikes(interval=interval, list_ids=IDs, count=count,
                                                        vk_method=vk_method,
                                                        window_for_change=self.search_result_textBrowser_likes)
            self.thread_go_likes.thread_ended.connect(self.ending_traversal)
            self.thread_go_likes.progress.connect(lambda value: self.search_result_textBrowser_likes.append(value))
            self.thread_go_likes.start()

    def ending_traversal(self):
        """ Функция вызывающаяся при нормальном завершении цикла в потоке """
        self.clear_text_browser(True)

    def stop_likes(self):
        """ Функция принудительного завершения цикла в потоке """
        self.Stop_users_like_button.setEnabled(False)
        self.thread_go_likes.STOP_LIKES = True

    def error_window_likes(self, text_error, err_detail=None):
        """ Функция для визуального отображения окна с ошибками """
        if type(text_error) is tuple:
            err_detail = text_error[1]
            text_error = text_error[0]
        error_wind = QMessageBox()
        error_wind.setWindowTitle('Ошибка')
        error_wind.setText(f'{text_error}')
        error_wind.setWindowIcon(QIcon(f'{VK_SPA_Settings.abspath_params}/Picture_gui/error.png'))
        error_wind.setIcon(QMessageBox.Warning)
        error_wind.setStandardButtons(QMessageBox.Ok)
        if err_detail:
            error_wind.setDetailedText(str(err_detail))
        error_wind.exec_()
