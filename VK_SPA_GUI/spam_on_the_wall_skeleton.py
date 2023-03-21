import urllib.request
from time import sleep

import requests
import os
import vk_api as VK
from fake_useragent import UserAgent

import VK_SPA_Settings
from datetime import datetime
from random import randint, choice
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, QUrl, Qt
from PyQt5.QtGui import QIcon, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QMessageBox
from VK_SPA_Settings import abspath_params as params_path


class StopPublicAlert(QThread):
    thread_stop_public = QtCore.pyqtSignal()

    def run(self):
        self.thread_stop_public.emit()


class RunSpamWall(QThread):
    """ Класс потока авторизации пользователя"""

    progress_mailing_log = QtCore.pyqtSignal(str)
    stop = QtCore.pyqtSignal()
    syntax_highlighter = QtCore.pyqtSignal()

    def __init__(self, type_spam, vision_for_captcha, settings, info_spam, texts, proxy=None, log_pass=None,
                 vk_method=None, dict_logpass_for_multispam=None, list_acc=None):
        """ self.settings[0] - rocker(True - use, False - not use),
            self.settings[1] - randomaizer(True - use, False - not use),
            self.settings[2] - join_to_group(True - use, False - not use);
            self.texts[0] - Изначальный текст,
            self.texts[1] - основной текст, который берет на себя все изменения,
            self.texts[2] - текст с прикриплениями к основной записи;
            self.info_spam['list_groups'] - список групп для рассылки,
            self.info_spam['quantity'] - кол-во записей для одного аккаунта,
            self.info_spam['interval'] - интервал между публикациями. """
        super().__init__()
        ua = UserAgent()
        self.headers = {"User-Agent": ua.ie}
        self.proxy = proxy
        self.log_pass = log_pass
        self.vision_for_captcha = vision_for_captcha
        self.STOP_SPAM_WALL = False
        self.settings = settings
        self.vk_method = vk_method
        self.info_spam = info_spam
        self.texts = texts
        self.type_spam = type_spam
        self.dict_logpass_for_multispam = dict_logpass_for_multispam
        self.list_acc = list_acc

    def change_position_in_file_group(self, counter_rz):
        with open(f'{VK_SPA_Settings.abspath_params}/File_group_for_spam_wall.txt',
                  'r') as ff:
            first_count = []
            group = ff.readlines()
            for i in range(0, counter_rz):
                if '\n' in str(group[len(group) - 1]):
                    first_count.append(group[i])
                else:
                    if i == 0:
                        first_count.append('\n' + str(group[i]))
                    else:
                        first_count.append(group[i])
            del group[0:counter_rz]
        with open(f'{VK_SPA_Settings.abspath_params}/File_group_for_spam_wall.txt',
                  'w') as ff:
            ff.writelines(group + first_count)

    def randomize_char(self, text):
        """ Функция меняющая русские символы на иностранные """

        a = randint(0, 60)
        b = randint(61, len(text))
        RANDOM = randint(1, 2)
        if RANDOM == 1:
            text_for_rand = text[a:b + 1]
            for i in text_for_rand:
                if i in VK_SPA_Settings.alphabet_v2.keys():
                    text_for_rand = text_for_rand.replace(i, VK_SPA_Settings.alphabet_v2[i])
            text = text[0:a] + text_for_rand + text[b:len(text) + 1]
        elif RANDOM == 2:
            text_for_rand = text[a:b + 1]
            for i in text_for_rand:
                if i in VK_SPA_Settings.alphabet.keys():
                    text_for_rand = text_for_rand.replace(i, VK_SPA_Settings.alphabet[i])
            text = text[0:a] + text_for_rand + text[b:len(text) + 1]
        return text

    def randomize_words(self, text):
        """ Функция меняющая некоторые слова на синонимы """

        for word in text.split():
            n = 0
            if word.istitle():
                n = 1
            word = word.lower()
            if word in VK_SPA_Settings.dict_replace_word.keys():
                end_list = len(VK_SPA_Settings.dict_replace_word[word]) - 1
                new_word = VK_SPA_Settings.dict_replace_word[word][randint(0, end_list)]
                if n == 1:
                    new_word = new_word.capitalize()
                    text = text.replace(word, new_word.capitalize())
                else:
                    text = text.replace(word, new_word)
        return text

    def apply_randomaizer(self, number, first_text):
        try:
            if number in list(range(5, 200, 10)):
                text_spam_wall = self.randomize_char(first_text)
            elif number in list(range(10, 200, 10)):
                text_spam_wall = first_text
            elif number in list(range(15, 200, 10)):
                text_spam_wall = self.randomize_words(first_text)
            return text_spam_wall
        except Exception as err:
            print(err)

    def try_proxy(self, proxy):
        """ Функция проверяет прокси на валидность, в случае успеха, возвращает данные прокси """

        proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
        try:
            if 'Response [200]' in str(requests.get('https://www.vk.com/', proxies=proxies, headers=self.headers)):
                return proxies, self.headers
            else:
                return False
        except Exception as error_proxy:
            self.progress_mailing_log.emit(f'Данный прокси не рабочий!\n {error_proxy}')

    def auth(self):
        result_proxy = self.try_proxy(self.proxy) if VK_SPA_Settings.use_proxy else False
        try:
            prx = self.proxy if VK_SPA_Settings.use_proxy else '(Без прокси)'
            self.progress_mailing_log.emit(f'Пробуем авторизацию для аккаунта {self.log_pass} с прокси {prx}')
            self.vk_session = VK.VkApi(login=self.log_pass[:self.log_pass.find(';')],
                                       password=self.log_pass[self.log_pass.find(';') + 1: self.log_pass.find(':')],
                                       captcha_handler=self.show_captcha)
            if result_proxy:
                self.vk_session.http.proxies = result_proxy[0]
                self.vk_session.http.headers = result_proxy[1]
            self.vk_session.auth()
            self.vk_main = self.vk_session.get_api()
            id_account = self.vk_main.account.getProfileInfo()['id']
            self.progress_mailing_log.emit(f'Авторизация пользователя прошла успешно, id - {id_account}')
            return self.vk_main
        except Exception as err_auth:
            # if 'Captcha' in str(err_auth):
            #     pass
            if 'remixsid' in str(err_auth):
                return 'Аккаунт заблокировали'
            elif 'Bad password' in str(err_auth):
                return 'Не правильный пароль'
            elif 'blocked' in str(err_auth):
                return 'Аккаунт забанен'
            else:
                return 'Не удается авторизоваться'

    def show_captcha(self, captcha):
        """ Функция принимает объект капчи, через функцию captcha.try_again передает капчу на проверку.
            Если капча успешна - успешное завершение авторизации, иначе - повторный показ новой капчи"""

        VK_SPA_Settings.captcha_input_text = ''
        self.vision_for_captcha(self.get_captcha_image(captcha))
        while True:
            if len(VK_SPA_Settings.captcha_input_text) >= 1:
                VK_SPA_Settings.was_captcha = True
                captcha.try_again(key=VK_SPA_Settings.captcha_input_text)
                break

    def get_captcha_image(self, captcha):
        """ Функция получает объект капча, скачивает изображени и возвращает путь к изображению """
        img = urllib.request.urlopen(f'{captcha.get_url()}').read()
        with open(f"{VK_SPA_Settings.abspath_params}/Picture_gui/load_avatar/captcha.jpg", "wb") as captcha_image:
            captcha_image.write(img)
        return f"{VK_SPA_Settings.abspath_params}/Picture_gui/load_avatar/captcha.jpg"

    def join_to_group(self, line_id):
        try:
            self.vk_method.groups.join(group_id=int(line_id))
            return '(Вступили в группу)'
        except Exception as err_join:
            if '[15]' in str(err_join):
                return '(Вы уже в группе)'
            return '(Не удалось вступить в группу)'

    def news_feed_walk(self):
        """ Функция прохода по записям в новостной ленте"""

        count_news = randint(7, 12)
        news_list = self.vk_method.newsfeed.get(count=count_news, max_photos=1, filters='post',
                                                source_ids='groups')
        for i in range(count_news):
            n = randint(1, 10)

            if self.STOP_SPAM_WALL is True:
                yield ' Рассылка закончена пользователем '.center(65, '-')
                return

            time = datetime.now().strftime("%H:%M:%S")  # Время репоста записи
            user_id = self.vk_method.account.getProfileInfo()['id']  # Получаем ID своей страницы
            id_group = news_list['items'][i]['source_id']  # Получаем id группы
            id_post = news_list['items'][i]['post_id']  # Получаем id поста

            if n in [1, 3, 5, 10, 9]:  # Только лайк
                try:
                    self.vk_method.likes.add(type='post', owner_id=f'{id_group}', item_id=f'{id_post}')
                    yield f'В {time} в ленте лайкнута <a href=https://vk.com/wall {str(id_group)}_{str(id_post)}>' \
                          f'запись</a>'
                except Exception:
                    yield 'Не удалось лайкнуть запись в новостной ленте'

            elif n in [2, 7, 6]:  # Лайк и репост записи к себе на страницу
                try:
                    self.vk_method.likes.add(type='post', owner_id=f'{id_group}', item_id=f'{id_post}')
                    self.vk_method.wall.repost(object=f'wall{str(id_group)}_{id_post}')
                    yield f'В {time} на вашу страницу добавлена <a href=https://vk.com/id{user_id}>запись</a>'
                except Exception:
                    yield 'Не удалось сделать репост записи из новостной ленты'

            elif n in [4, 8]:  # Написание комментария под записью в ленте
                try:
                    message = choice(VK_SPA_Settings.simple_comment)  # Рандомно выбранный коммент
                    self.vk_method.wall.createComment(owner_id=f'{id_group}', post_id=f'{id_post}',
                                                      message=message)
                    yield f'В {time} в <a href=https://vk.com/wall{str(id_group)}_{str(id_post)}>группе</a> ' \
                          f'написан комментарий {message}'
                except Exception:
                    yield 'Не удалось написать комментарий к записи в новостной ленте'

            sleep(randint(12, 14))

    def write_post(self, line_id, text, attachment, number_spam_wall):
        time_public = datetime.now().strftime("%H:%M:%S")

        try:
            post = self.vk_method.wall.post(owner_id=f'-{int(line_id)}', message=text, attachments=attachment)
            self.vk_method.likes.add(type='post', owner_id=f'-{int(line_id)}', item_id=f'{post["post_id"]}')

            return f'{number_spam_wall})В {time_public} опубликована запись в ' \
                   f'<a href=https://vk.com/club{int(line_id)}> группе</a>.\n'

        except Exception as error_spam:

            if 'Access to adding post denied' in str(error_spam):
                return f'Error. <a> href=https://vk.com/wall-{int(line_id)}> Группа</a> закрыта. Нельзя опубликовать запись'
            elif 'Too' in str(error_spam):
                return 'Error. Слишком много публикаций с этого аккаунта,надо сменить аккаунт, рассылка остановлена'
            elif 'user is blocked' in str(error_spam):
                return 'Error. Аккаунт заблокировали'
            elif '[15]' in str(error_spam):
                return f'Error. В группе <a href=http://vk.com/club{int(line_id)}>https://vk.com/wall-{int(line_id)}</a> ' \
                       f'не удалось опубликовать запись. Вы должны быть администратором сообщества!'
            else:
                return f'Error. В группе <a href=http://vk.com/club{int(line_id)}>https://vk.com/wall-{int(line_id)}</a> ' \
                       f'не удалось опубликовать запись\n из-за ошибки {error_spam}'

    def simple_spam(self, list_groups, first_text, text, quantity_post, text_attachments, interval):

        number_log = 1
        for line_id in list_groups[:quantity_post]:

            self.syntax_highlighter.emit()

            if self.STOP_SPAM_WALL:
                self.progress_mailing_log.emit(' Рассылка закончена пользователем '.center(65, '-'))
                return

            if self.settings[0]:
                if number_log in list(range(0, 200, 16)):
                    for i in self.news_feed_walk():
                        self.progress_mailing_log.emit(i)
                        if i == ' Рассылка закончена пользователем '.center(65, '-'):
                            return

            if self.settings[1]:
                if number_log in list(range(0, 200, 5)):
                    try:
                        text = self.apply_randomaizer(number=number_log, first_text=first_text)
                    except Exception as err:
                        print(err)

            if quantity_post == 0:
                self.change_position_in_file_group(number_log)
                break

            result_join = self.join_to_group(line_id=line_id) if self.settings[2] else ''

            result_writing_post = self.write_post(line_id=line_id, text=text, attachment=text_attachments,
                                                  number_spam_wall=number_log)

            number_log += 1
            quantity_post -= 1

            sleep(7)
            if 'Error. Аккаунт заблокировали' == str(result_writing_post):
                break
            if 'Error' in str(result_writing_post):
                self.progress_mailing_log.emit(result_writing_post)
                continue

            self.progress_mailing_log.emit(f"{result_writing_post} {result_join}")

            sleep(randint(*interval))

        if self.STOP_SPAM_WALL is False:
            self.change_position_in_file_group(number_log - 1)

    def run(self):
        """ Запуск потока """

        if self.type_spam == 'simple':
            self.simple_spam(list_groups=self.info_spam['list_groups'], first_text=self.texts[0], text=self.texts[1],
                             quantity_post=self.info_spam['quantity'], text_attachments=self.texts[2],
                             interval=self.info_spam['interval'])

        if self.type_spam == 'multi_and_different_proxies':

            login_pass = self.dict_logpass_for_multispam.keys()
            for i in login_pass:

                if self.STOP_SPAM_WALL:
                    self.progress_mailing_log.emit(' Рассылка закончена пользователем '.center(65, '-'))
                    break

                self.log_pass = i
                self.proxy = self.dict_logpass_for_multispam[i]

                self.vk_method = self.auth()

                if isinstance(self.vk_method, str):
                    self.progress_mailing_log.emit(self.vk_method)
                    continue

                self.simple_spam(list_groups=self.info_spam['list_groups'], first_text=self.texts[0],
                                 text=self.texts[1],
                                 quantity_post=self.info_spam['quantity'], text_attachments=self.texts[2],
                                 interval=self.info_spam['interval'])

        if self.type_spam == 'multi_one_proxies':
            for acc in self.list_acc:

                if self.STOP_SPAM_WALL:
                    self.progress_mailing_log.emit(' Рассылка закончена пользователем '.center(65, '-'))
                    break

                self.log_pass = acc
                self.vk_method = self.auth()

                if isinstance(self.vk_method, str):
                    self.progress_mailing_log.emit(self.vk_method)
                    continue

                self.simple_spam(list_groups=self.info_spam['list_groups'], first_text=self.texts[0],
                                 text=self.texts[1],
                                 quantity_post=self.info_spam['quantity'], text_attachments=self.texts[2],
                                 interval=self.info_spam['interval'])
        if self.STOP_SPAM_WALL is False:
            self.progress_mailing_log.emit(' Рассылка закончена '.center(65, '-'))
        self.stop.emit()


class UiVkSpaSpamOnTheWall_SKELETON(object):

    def __init__(self):

        self.central_widget_SPAM_ON_THE_WALL = QtWidgets.QWidget()

        self.mailingLog_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.mailingLog_label.setGeometry(QtCore.QRect(20, 220, 111, 16))
        self.listGroups_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.listGroups_label.setGeometry(QtCore.QRect(570, 20, 141, 16))
        self.listGroups_label.setLineWidth(1)
        self.chooseText_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.chooseText_label.setGeometry(QtCore.QRect(20, 20, 171, 16))
        self.settings_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.settings_label.setGeometry(QtCore.QRect(20, 92, 71, 16))
        self.choose_attachments = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.choose_attachments.setGeometry(QtCore.QRect(280, 20, 211, 16))
        self.to_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.to_label.setGeometry(QtCore.QRect(362, 110, 21, 16))
        self.to_label.setStyleSheet("font: 75 8pt \"MS Shell Dlg 2\";")

        self.sec_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.sec_label.setGeometry(QtCore.QRect(440, 110, 21, 16))
        self.to_label.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")

        self.auto_change_account_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.auto_change_account_label.setGeometry(QtCore.QRect(365, 134, 230, 31))
        self.auto_change_account_label.setText('Число публикаций\nдля одного аккаунта')

        self.join_to_group_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.join_to_group_label.setGeometry(QtCore.QRect(242, 134, 120, 31))
        self.join_to_group_label.setText('      Добавиться\n в группы рассылки')

        self.choose_attachments_label = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.choose_attachments_label.setGeometry(QtCore.QRect(388, 172, 141, 16))
        self.interval_label_spam_wall = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.interval_label_spam_wall.setGeometry(QtCore.QRect(247, 110, 60, 16))
        self.interval_label_spam_wall.setStyleSheet("font: 75 8pt \"MS Shell Dlg 2\";")

        self.line_1_spam_wall = QtWidgets.QFrame(self.central_widget_SPAM_ON_THE_WALL)
        self.line_1_spam_wall.setGeometry(QtCore.QRect(11, 20, 792, 20))
        self.line_1_spam_wall.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1_spam_wall.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2_spam_wall = QtWidgets.QFrame(self.central_widget_SPAM_ON_THE_WALL)
        self.line_2_spam_wall.setGeometry(QtCore.QRect(12, 100, 544, 4))
        self.line_2_spam_wall.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2_spam_wall.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4_spam_wall = QtWidgets.QFrame(self.central_widget_SPAM_ON_THE_WALL)
        self.line_4_spam_wall.setGeometry(QtCore.QRect(10, 182, 544, 4))
        self.line_4_spam_wall.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4_spam_wall.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5_spam_wall = QtWidgets.QFrame(self.central_widget_SPAM_ON_THE_WALL)
        self.line_5_spam_wall.setGeometry(QtCore.QRect(12, 227, 790, 5))
        self.line_5_spam_wall.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5_spam_wall.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6_spam_wall = QtWidgets.QFrame(self.central_widget_SPAM_ON_THE_WALL)
        self.line_6_spam_wall.setGeometry(QtCore.QRect(10, 30, 5, 199))
        self.line_6_spam_wall.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.line_6_spam_wall.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_6_spam_wall.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8_spam_wall = QtWidgets.QFrame(self.central_widget_SPAM_ON_THE_WALL)
        self.line_8_spam_wall.setGeometry(QtCore.QRect(555, 30, 5, 199))
        self.line_8_spam_wall.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_8_spam_wall.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.mailing_log_text_browser = QtWidgets.QTextBrowser(self.central_widget_SPAM_ON_THE_WALL)
        self.mailing_log_text_browser.setGeometry(QtCore.QRect(10, 240, 620, 201))
        self.list_groups_tableView = QtWidgets.QTextBrowser(self.central_widget_SPAM_ON_THE_WALL)
        self.list_groups_tableView.setGeometry(QtCore.QRect(565, 41, 221, 121))
        self.input_attachments_lineEdit = QtWidgets.QLineEdit(self.central_widget_SPAM_ON_THE_WALL)
        self.input_attachments_lineEdit.setGeometry(QtCore.QRect(380, 190, 168, 31))

        self.start_spam_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.start_spam_button.setGeometry(QtCore.QRect(18, 190, 141, 28))
        self.start_spam_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                             "color: rgb(255, 255, 255);\n"
                                             "font: 75 9pt \"MS Shell Dlg 2\";")
        self.stop_spam_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.stop_spam_button.setGeometry(QtCore.QRect(178, 190, 161, 28))
        self.stop_spam_button.setStyleSheet("color: rgb(255, 255, 255);\n"
                                            "background-color: rgb(255, 0, 0);\n"
                                            "font: 75 9pt \"MS Shell Dlg 2\";")
        self.add_newText_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.add_newText_button.setGeometry(QtCore.QRect(20, 70, 201, 21))
        self.add_newText_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                              "color: rgb(255, 255, 255);\n"
                                              "font: 75 8pt \"MS Shell Dlg 2\";")
        self.update_text_list_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.update_text_list_button.setGeometry(QtCore.QRect(228, 70, 20, 21))
        self.update_text_list_button.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.add_newAttachments_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.add_newAttachments_button.setGeometry(QtCore.QRect(280, 70, 201, 21))
        self.add_newAttachments_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                     "color: rgb(255, 255, 255);\n"
                                                     "font: 75 8pt \"MS Shell Dlg 2\";")
        self.update_attachments_list_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.update_attachments_list_button.setGeometry(QtCore.QRect(488, 70, 20, 21))
        self.update_attachments_list_button.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.change_list_group_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.change_list_group_button.setGeometry(QtCore.QRect(565, 200, 221, 21))
        self.change_list_group_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                    "color: rgb(255, 255, 255);\n"
                                                    "font: 75 9pt \"MS Shell Dlg 2\";")
        self.change_list_group_button.setObjectName("changeListGroup_pushButton")
        self.view_list_group_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.view_list_group_button.setGeometry(QtCore.QRect(565, 170, 221, 21))
        self.view_list_group_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                  "color: rgb(255, 255, 255);\n"
                                                  "font: 75 8pt \"MS Shell Dlg 2\";")
        self.choose_text_comboBox = QtWidgets.QComboBox(self.central_widget_SPAM_ON_THE_WALL)
        self.choose_text_comboBox.setGeometry(QtCore.QRect(20, 40, 231, 21))
        self.choose_attachments_comboBox = QtWidgets.QComboBox(self.central_widget_SPAM_ON_THE_WALL)
        self.choose_attachments_comboBox.setGeometry(QtCore.QRect(280, 40, 231, 21))
        self.from_interval_spinBox = QtWidgets.QSpinBox(self.central_widget_SPAM_ON_THE_WALL)
        self.from_interval_spinBox.setGeometry(QtCore.QRect(310, 105, 42, 22))
        self.to_interval_spinBox = QtWidgets.QSpinBox(self.central_widget_SPAM_ON_THE_WALL)
        self.to_interval_spinBox.setGeometry(QtCore.QRect(390, 105, 42, 22))
        self.quantity_post_spinBox = QtWidgets.QSpinBox(self.central_widget_SPAM_ON_THE_WALL)
        self.quantity_post_spinBox.setGeometry(QtCore.QRect(495, 140, 51, 21))
        self.quantity_post_spinBox.setMinimum(1)
        self.use_or_not_randomaizer_checkBox = QtWidgets.QCheckBox(self.central_widget_SPAM_ON_THE_WALL)
        self.use_or_not_randomaizer_checkBox.setGeometry(QtCore.QRect(20, 126, 191, 20))
        self.use_or_not_rocker_checkBox = QtWidgets.QCheckBox(self.central_widget_SPAM_ON_THE_WALL)
        self.use_or_not_rocker_checkBox.setGeometry(QtCore.QRect(20, 144, 211, 20))
        self.use_auto_change_account_checkBox = QtWidgets.QCheckBox(self.central_widget_SPAM_ON_THE_WALL)
        self.use_auto_change_account_checkBox.setGeometry(QtCore.QRect(20, 162, 161, 20))
        self.use_standard_spam_checkBox = QtWidgets.QCheckBox(self.central_widget_SPAM_ON_THE_WALL)
        self.use_standard_spam_checkBox.setGeometry(QtCore.QRect(20, 108, 161, 20))
        self.join_to_group_checkBox = QtWidgets.QCheckBox(self.central_widget_SPAM_ON_THE_WALL)
        self.join_to_group_checkBox.setGeometry(QtCore.QRect(295, 166, 16, 16))

        self.line_1_spam_wall.raise_()
        self.list_groups_tableView.raise_()
        self.listGroups_label.raise_()
        self.start_spam_button.raise_()
        self.mailing_log_text_browser.raise_()
        self.choose_text_comboBox.raise_()
        self.chooseText_label.raise_()
        self.choose_attachments_comboBox.raise_()
        self.choose_attachments.raise_()
        self.stop_spam_button.raise_()
        self.line_6_spam_wall.raise_()
        self.line_4_spam_wall.raise_()
        self.line_2_spam_wall.raise_()
        self.settings_label.raise_()
        self.use_standard_spam_checkBox.raise_()
        self.add_newText_button.raise_()
        self.add_newAttachments_button.raise_()
        self.from_interval_spinBox.raise_()
        self.to_interval_spinBox.raise_()
        self.to_label.raise_()
        self.sec_label.raise_()
        self.interval_label_spam_wall.raise_()
        self.use_or_not_randomaizer_checkBox.raise_()
        self.use_or_not_rocker_checkBox.raise_()
        self.use_auto_change_account_checkBox.raise_()
        self.line_8_spam_wall.raise_()
        self.line_5_spam_wall.raise_()
        self.mailingLog_label.raise_()
        self.choose_attachments_label.raise_()
        self.input_attachments_lineEdit.raise_()
        self.change_list_group_button.raise_()
        self.view_list_group_button.raise_()

        self.AUTH_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.AUTH_pushButton.setGeometry(QtCore.QRect(365, 470, 421, 221))
        self.AUTH_pushButton.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                           "color: rgb(255, 255, 255);\n"
                                           "font: 75 8pt \"MS Shell Dlg 2\";")
        self.AUTH_pushButton.setObjectName("AUTH_pushButton")

        self.label_captcha = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.label_captcha.setGeometry(QtCore.QRect(655, 250, 120, 16))
        self.label_captcha.close()

        self.InputCaptcha = QtWidgets.QLineEdit(self.central_widget_SPAM_ON_THE_WALL)
        self.InputCaptcha.setGeometry(QtCore.QRect(640, 330, 151, 31))
        self.InputCaptcha.setStyleSheet("font: 75 10pt\"MS Shell Dlg 2\";")
        self.InputCaptcha.setAlignment(Qt.AlignCenter)
        self.InputCaptcha.close()

        self.label_ImageCaptcha = QtWidgets.QLabel(self.central_widget_SPAM_ON_THE_WALL)
        self.label_ImageCaptcha.setGeometry(QtCore.QRect(640, 280, 151, 41))
        self.label_ImageCaptcha.close()

        self.press_captcha_button = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
        self.press_captcha_button.setGeometry(QtCore.QRect(655, 370, 120, 31))
        self.press_captcha_button.setText('Подтвердить капчу')
        self.press_captcha_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                "color: rgb(255, 255, 255);"
                                                "font: 75 8pt\"MS Shell Dlg 2\";")
        self.press_captcha_button.close()

        self.from_interval_spinBox.setValue(19)
        self.to_interval_spinBox.setValue(28)
        self.quantity_post_spinBox.setValue(50)

        self.get_texts_for_spam()
        self.get_attachments_for_spam()

        self.STOP_SPAM_WALL = True
        self.use_standard_spam_checkBox.setChecked(True)
        self.stop_spam_button.setEnabled(False)

        self.retranslationSPAM()
        self.functionSPAM()

        self.VK_SPAM_WALL_METHOD = None
        self.mailing_log_text_browser.setOpenExternalLinks(True)

        self.signal_sound_stop_public = StopPublicAlert()
        self.signal_sound_stop_public.thread_stop_public.connect(self.play_stop_public)

        self.count_acc_multispam = self.return_info_quantity_acc()[0]  # Параметр кол-ва акк для мультиспама
        self.with_first_acc_multispam = 1  # Параметр для определения аккаунта, с которого начнется мультиспам
        self.connect_log_and_prx = False  # Параметр показывающий есть ли связь между лог и прокси. включается в настройках
        #  при нажатии кнопки "Сохранить"
        self.dict_log_prx = {}  # Словарь логинов и прокси при выборе подвязки логина к прокси
        self.list_log = []  # Список объектов ComboBox, содержащих логины. Используется для доступа к объектам ComboBox
        self.list_rpx = []  # Список объектов ComboBox, содержащих прокси. Используется для доступа к объектам ComboBox
        self.disposable_list = []  # Временный список, используется для показа ComboBox, с уже подвязанными логинами и
        # и прокси, используется для показа существующих настроек
        self.previous = 1  # Хранит предыдущее значение, при смене значения with_first_acc.SpinBox

        self.count_highlighter = 0  # Счетчик строк для подсветки при рассылке

    def visual_display_captcha(self, path=None):
        """ При возникновении капчи в потоке авторизации, вызывается эта функция и ей передается изображение капчи.
            В основном интерфейсе появляется изображение и строка ввода капчи. """
        self.label_captcha.setText('Нужен ввод капчи')
        self.label_captcha.show()
        self.InputCaptcha.show()
        self.label_ImageCaptcha.setPixmap(QtGui.QPixmap(f'{path}'))
        self.label_ImageCaptcha.show()
        self.press_captcha_button.show()

    def press_captcha(self):
        """ Переопределяет VK_SPA_Settings.captcha_input_text из '' в веденный текст капчи. Нужна для выполнения условия
            ввода текста в потоке авторизации в случае появления капчи. """

        VK_SPA_Settings.captcha_input_text = self.InputCaptcha.text()

    def change_list_group_spam(self):
        """ Открывает файл со списком групп """

        file = 'File_group_for_spam_wall.txt'
        os.startfile(f'{params_path}/{file}')

    def functionSPAM(self):

        self.add_newText_button.clicked.connect(lambda: self.add_new_text_spam())
        self.update_text_list_button.clicked.connect(lambda: self.update_text_spam())
        self.add_newAttachments_button.clicked.connect(lambda: self.add_new_attachments_spam())
        self.update_attachments_list_button.clicked.connect(lambda: self.update_attachments_spam())
        self.view_list_group_button.clicked.connect(lambda: self.view_groups_list_spam())
        self.change_list_group_button.clicked.connect(lambda: self.change_list_group_spam())
        self.stop_spam_button.clicked.connect(lambda: self.press_forced_stop_spam_wall())
        self.start_spam_button.clicked.connect(lambda: self.spam())
        self.use_auto_change_account_checkBox.stateChanged.connect(lambda: self.show_button_settings())
        self.press_captcha_button.clicked.connect(lambda: self.press_captcha())

    def retranslationSPAM(self):
        _translate = QtCore.QCoreApplication.translate

        self.mailingLog_label.setText(_translate("MainWindow", "Журнал рассылки"))
        self.listGroups_label.setText(_translate("MainWindow", "Группы для рассылки"))
        self.start_spam_button.setText(_translate("MainWindow", "Начать рассылку"))
        self.chooseText_label.setText(_translate("MainWindow", "Выбор текста для рассылки"))
        self.settings_label.setText(_translate("MainWindow", "Настройки"))
        self.choose_attachments.setText(_translate("MainWindow", "Выбор изображения для рассылки"))
        self.stop_spam_button.setText(_translate("MainWindow", "Остановить рассылку"))
        self.use_standard_spam_checkBox.setText(_translate("MainWindow", "Стандартная рассылка"))
        self.add_newText_button.setText(_translate("MainWindow", "Добавить новый текст"))
        self.add_newAttachments_button.setText(_translate("MainWindow", "Добавить новое изображение"))
        self.to_label.setText(_translate("MainWindow", "до"))
        self.sec_label.setText(_translate("MainWindow", "сек"))
        self.interval_label_spam_wall.setText(_translate("MainWindow", "Интервал"))
        self.use_or_not_randomaizer_checkBox.setText(_translate("MainWindow", "Использовать рандомайзер"))
        self.use_or_not_rocker_checkBox.setText(_translate("MainWindow", "Использовать режим \"шатуна\""))
        self.choose_attachments_label.setText(_translate("MainWindow", "Прикрепление к тексту"))
        self.change_list_group_button.setText(_translate("MainWindow", "Изменить список групп"))
        self.view_list_group_button.setText(_translate("MainWindow", "Добавить группы из файла"))
        self.use_auto_change_account_checkBox.setText(_translate("MainWindow", "Автозамена аккаунтов"))

    def play_stop_public(self):
        """ Запуск звукового уведомления при превышении лимита рассылки """

        self.media_player = QMediaPlayer()
        self.url = QUrl.fromLocalFile(f'{params_path}/Alert/many_post_break.wav')
        self.content = QMediaContent(self.url)
        self.media_player.setMedia(self.content)
        self.media_player.play()

    def launch_threads(self):
        self.signal_sound_stop_public.start()

    def get_texts_for_spam(self):
        """ Создает список текстов для рассылки """

        self.choose_text_comboBox.addItem('-------')
        name_files = os.listdir(f'{params_path}/Text_for_spam')
        name_files.remove('__init__.py')
        for name in name_files:
            if '.txt' in str(name):
                name = str(name).replace('.txt', '')
                self.choose_text_comboBox.addItem(name)

    def get_attachments_for_spam(self):
        """ Создает список прикрипений для рассылки """

        self.choose_attachments_comboBox.addItem('-------')
        picture_files = os.listdir(f'{params_path}/Attachments_for_spam/')
        picture_files.remove('__init__.py')
        for name in picture_files:
            if '.txt' in str(name):
                name = str(name).replace('.txt', '')
                self.choose_attachments_comboBox.addItem(name)

    def add_new_text_spam(self):
        os.system(fr"explorer.exe {os.getcwd().replace('VK_SPA_GUI', 'params')}\Text_for_spam")

    def add_new_attachments_spam(self):
        os.system(rf"explorer.exe {os.getcwd().replace('VK_SPA_GUI', 'params')}\Attachments_for_spam")

    def update_text_spam(self):
        self.choose_text_comboBox.clear()
        self.get_texts_for_spam()

    def update_attachments_spam(self):
        self.choose_attachments_comboBox.clear()
        self.get_attachments_for_spam()

    def view_groups_list_spam(self):
        """ Показывает список групп в отдельном поле """

        with open(f'{params_path}/File_group_for_spam_wall.txt', 'r') as f:
            text = f.read()
            self.list_groups_tableView.setText(str(text))
            self.list_groups_tableView.setTextInteractionFlags(Qt.NoTextInteraction)

    def check_settings(self, interval, name_text, list_groups):

        if not self.use_standard_spam_checkBox.isChecked() and not self.use_auto_change_account_checkBox.isChecked():
            return 'Вы не выбрали тип рассылки!'

        if self.use_standard_spam_checkBox.isChecked() and self.use_auto_change_account_checkBox.isChecked():
            return 'Выберите один вид рассылки'

        if interval[0] >= interval[1]:
            return 'Неверно указан интервал!'

        if name_text == '-------':
            return 'Вы не выбрали текст для рассылки!'

        if len(list_groups) == 0:
            return 'Список с ID группами пуст!'

        for i in list_groups:
            if len(i) <= 1:
                return 'Неправильно заполнен файл с группами!'

        return {'interval': (interval[0], interval[1]),
                'name_text': name_text,
                'list_groups': list_groups,
                'quantity': self.quantity_post_spinBox.value()}

    def open_file_text(self, name):
        with open(f'{params_path}/Text_for_spam/{name}.txt', 'r', encoding="utf-8") as f:
            text_spam_wall = f.read()
        return text_spam_wall

    def open_file_attachment(self, name):
        with open(f'{params_path}/Attachments_for_spam/{name}.txt', 'r', encoding="utf-8") as f:
            text_attachments_spam = f.read()
        return text_attachments_spam

    def open_file_with_id_groups(self):
        with open(file=f'{params_path}/File_group_for_spam_wall.txt', mode='r', encoding='utf8') as file_id:
            group_id = file_id.readlines()
        return group_id

    def get_attachments_text(self, name):
        if name != '-------':
            text_attachments_spam = self.open_file_attachment(name)
        else:
            text_attachments_spam = self.input_attachments_lineEdit.text()
        return text_attachments_spam

    def check_settings_count_acc_multispam(self):

        with open(file=f'{params_path}/ACCOUNTS.txt', mode='r') as file:
            list_accounts = [elem.replace('\n', '') for elem in file.readlines()]

        if len(list_accounts) == 0:
            return 'Список с аккаунтами пуст!'

        list_for_thread = list_accounts[self.with_first_acc_multispam - 1:
                                        self.with_first_acc_multispam + self.count_acc_multispam - 1]

        if self.with_first_acc_multispam + self.count_acc_multispam > self.return_info_quantity_acc()[0] + 1:
            return 'Неверно указаны настройки выбора числа аккаунтов!', \
                   f'Если вы выбираете рассылку с {self.with_first_acc_multispam}-го аккаунта, то кол-во аккаунтов ' \
                   f'для спама должно быть максимум - ' \
                   f'{self.return_info_quantity_acc()[0] - self.with_first_acc_multispam + 1}'

        return list_for_thread

    def spam(self):
        self.clear_log()
        result_check_settings = self.check_settings(interval=(self.from_interval_spinBox.value(),
                                                              self.to_interval_spinBox.value()),
                                                    name_text=self.choose_text_comboBox.currentText(),
                                                    list_groups=self.open_file_with_id_groups())
        if isinstance(result_check_settings, str):
            self.enable_button('end')
            return self.error_window_spam_wall(result_check_settings)

        first_text_spam_wall = self.open_file_text(result_check_settings['name_text'])
        text_spam_wall = first_text_spam_wall
        text_attachments_spam = self.get_attachments_text(self.choose_attachments_comboBox.currentText())

        # Ниже условие для простого спама на 1 акк
        self.mailing_log_text_browser.append(' Начали рассылку '.center(65, '-'))

        if self.use_standard_spam_checkBox.isChecked() and not self.use_auto_change_account_checkBox.isChecked():

            if self.VK_SPAM_WALL_METHOD is None:
                self.enable_button('end')
                return self.error_window_spam_wall('Для начала работы, пройдите авторизацию!')

            self.thread_spam = RunSpamWall(vision_for_captcha=self.visual_display_captcha,
                                           settings=[self.use_or_not_rocker_checkBox.isChecked(),
                                                     self.use_or_not_randomaizer_checkBox.isChecked(),
                                                     self.join_to_group_checkBox.isChecked()],
                                           vk_method=self.VK_SPAM_WALL_METHOD,
                                           info_spam=result_check_settings,
                                           texts=[first_text_spam_wall, text_spam_wall, text_attachments_spam],
                                           type_spam='simple')

        # Ниже условие для спама на несколько аккаунтов
        elif self.use_auto_change_account_checkBox.isChecked() and not self.use_standard_spam_checkBox.isChecked():
            if self.connect_log_and_prx:  # Если есть связь между лог и прокси

                self.thread_spam = RunSpamWall(vision_for_captcha=self.visual_display_captcha,
                                               settings=[
                                                   self.use_or_not_rocker_checkBox.isChecked(),
                                                   self.use_or_not_randomaizer_checkBox.isChecked(),
                                                   self.join_to_group_checkBox.isChecked()],
                                               info_spam=result_check_settings,
                                               texts=[first_text_spam_wall, text_spam_wall,
                                                      text_attachments_spam],
                                               type_spam='multi_and_different_proxies',
                                               dict_logpass_for_multispam=self.dict_log_prx)

            # Если нет связи между лог и прокси
            elif self.connect_log_and_prx is False:

                list_for_thread = self.check_settings_count_acc_multispam()

                if isinstance(list_for_thread, str) or isinstance(list_for_thread, tuple):
                    self.end()
                    return self.error_window_spam_wall(list_for_thread) if type(list_for_thread) is str \
                        else self.error_window_spam_wall(*list_for_thread)

                self.thread_spam = RunSpamWall(vision_for_captcha=self.visual_display_captcha,
                                               settings=[self.use_or_not_rocker_checkBox.isChecked(),
                                                         self.use_or_not_randomaizer_checkBox.isChecked(),
                                                         self.join_to_group_checkBox.isChecked()],
                                               info_spam=result_check_settings,
                                               texts=[first_text_spam_wall, text_spam_wall,
                                                      text_attachments_spam],
                                               type_spam='multi_one_proxies',
                                               proxy=VK_SPA_Settings.last_used_proxy,
                                               list_acc=list_for_thread)

        self.thread_spam.progress_mailing_log.connect(lambda vl: self.mailing_log_text_browser.append(vl))
        self.thread_spam.start()
        self.thread_spam.stop.connect(self.end)
        self.thread_spam.syntax_highlighter.connect(self.highlighter_line_id_group)

    def clear_log(self):
        """ Очистка поля рассылки """

        self.mailing_log_text_browser.clear()
        self.start_spam_button.setEnabled(False)
        self.stop_spam_button.setEnabled(True)

    def enable_button(self, end_or_start='start'):
        """ Делает доступными кнопки для нажатия либо наоборот, блокирует их"""

        if end_or_start == 'end':
            self.start_spam_button.setEnabled(True)
            self.stop_spam_button.setEnabled(False)
        else:
            self.start_spam_button.setEnabled(False)
            self.stop_spam_button.setEnabled(True)

    def end(self):
        """ Вызывается при принудительной остановке рассылки """
        self.enable_button('end')
        self.connect_log_and_prx = False

    def press_forced_stop_spam_wall(self):
        """ Обрабатывает нажатие кнопки 'Остановить рассылку' """

        self.stop_spam_button.setEnabled(False)
        try:
            self.thread_spam.STOP_SPAM_WALL = True
        except Exception as err:
            self.mailing_log_text_browser.append(f'Рассылку нельзя остановить из-за ошибки - {err}')

    def return_info_quantity_acc(self):
        """ Возвращает кол-во аккаунтов(n) и их данные(acc) """

        with open(file=f"{params_path}/ACCOUNTS.txt", mode='r', encoding='utf-8') as f:
            acc = []
            n = 0
            file = f.readlines()
            for i in file:
                if len(i) <= 1:
                    continue
                n += 1
                acc.append(i)
            return n, acc

    def show_button_settings(self):
        """ Функция создающая и показывающая кнопку 'Настройки' при нажатии checkbox(Автозамена аккаунтов) """

        if self.use_auto_change_account_checkBox.isChecked():
            self.autoChangeAccount_checkBox3_spam_wall = QtWidgets.QPushButton(self.central_widget_SPAM_ON_THE_WALL)
            self.autoChangeAccount_checkBox3_spam_wall.setGeometry(QtCore.QRect(180, 165, 87, 16))
            self.autoChangeAccount_checkBox3_spam_wall.setText('Настройки')
            self.autoChangeAccount_checkBox3_spam_wall.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                                     "color: rgb(255, 255, 255);\n"
                                                                     "font: 75 9pt \"MS Shell Dlg 2\";")
            self.autoChangeAccount_checkBox3_spam_wall.show()
            self.autoChangeAccount_checkBox3_spam_wall.clicked.connect(lambda: self.window_settings())
        elif not self.use_auto_change_account_checkBox.isChecked():
            self.autoChangeAccount_checkBox3_spam_wall.close()

    def change_value_quantity_acc(self):
        """ Динамическое изменение кол-ва акк для спама от начального аккаунта """

        if self.with_first_acc.value() > self.previous:
            self.count_acc.setValue(self.count_acc.value() - 1)
            self.previous = self.with_first_acc.value()

        elif self.with_first_acc.value() < self.previous:
            self.count_acc.setValue(self.count_acc.value() + 1)
            self.previous = self.with_first_acc.value()

    def open_connect_log_and_proxy(self):
        """ Создание ComboBox с логинами и прокси """
        try:
            y = 140
            if len(self.dict_log_prx) != 0 and self.connection_checkBox.isChecked():
                self.connect_log_and_prx = True
                for i in self.dict_log_prx.keys():
                    log = QtWidgets.QComboBox(self.sett_window_VKSPA)
                    log.setGeometry(QtCore.QRect(10, y, 170, 25))
                    log.addItem(str(i))
                    self.disposable_list.append(log)
                    log.show()
                    prx = QtWidgets.QComboBox(self.sett_window_VKSPA)
                    prx.setGeometry(QtCore.QRect(200, y, 170, 25))
                    prx.addItem(self.dict_log_prx[i])
                    self.disposable_list.append(prx)
                    prx.show()
                    y += 35
            elif not self.connection_checkBox.isChecked():
                # self.conn_log_and_prx = False
                self.sett_window.resize(400, 400)
                self.sett_window_VKSPA.setGeometry(QtCore.QRect(10, 10, 400, 400))
                self.save_sett_pushButton.setGeometry(QtCore.QRect(30, 330, 150, 40))
                self.reset_sett_pushButton.setGeometry(QtCore.QRect(200, 330, 150, 40))
                for lg in self.list_log:
                    if len(self.list_log) > 0:
                        lg.close()
                for pr in self.list_rpx:
                    if len(self.list_rpx) > 0:
                        pr.close()
                for lgp in self.disposable_list:
                    lgp.close()
                self.disposable_list.clear()

            else:
                quant_acc = self.return_info_quantity_acc()[1]  # Возвращает имена аккаунтов из файла
                max = 0
                for i in quant_acc:
                    if max < 18:
                        i = QtWidgets.QComboBox(self.sett_window_VKSPA)
                        i.setGeometry(QtCore.QRect(10, y, 170, 25))
                        i.show()
                        self.list_log.append(i)
                        max += 1
                        with open(f"{VK_SPA_Settings.abspath_params}/ACCOUNTS.txt", 'r') as accs:
                            name_accounts = accs.readlines()
                            for acc in name_accounts:
                                if acc != '\n':
                                    i.addItem(acc.replace('\n', ''))
                        y += 35
                y = 140
                max = 0
                for a in quant_acc:
                    if max < 18:
                        a = QtWidgets.QComboBox(self.sett_window_VKSPA)
                        a.setGeometry(QtCore.QRect(200, y, 170, 25))
                        a.show()
                        self.list_rpx.append(a)
                        max += 1
                        with open(f"{VK_SPA_Settings.abspath_params}/PROXY.txt", 'r') as prx:
                            proxy = prx.readlines()
                            for elem in proxy:
                                if elem != '\n':
                                    a.addItem(elem.replace('\n', ''))
                        y += 35

            self.sett_window.resize(400, y + 100)
            self.sett_window.setFixedSize(400, y + 100)
            self.sett_window_VKSPA.setGeometry(QtCore.QRect(10, 10, 400, y + 100))
            self.save_sett_pushButton.setGeometry(QtCore.QRect(30, y + 25, 150, 40))
            self.reset_sett_pushButton.setGeometry(QtCore.QRect(200, y + 25, 150, 40))
        except Exception as err_open_combo:
            self.error_window_spam_wall(text_error='Ошибка, попробуйте перезагрузить приложение',
                                        err_detail=f'Ошибка при открытии combo с аккаунтами\n{err_open_combo}')

    def window_settings(self):
        """ Открытие окна с настройками мультиспама """
        try:
            self.sett_window = QtWidgets.QDialog()
            self.sett_window.setModal(True)
            self.sett_window.setWindowTitle('Настройки')
            self.sett_window.resize(400, 400)
            self.sett_window.setStyleSheet("background-color: rgb(184, 254, 255);\n"
                                           "background-color: rgb(255, 255, 255);")
            self.sett_window.setWindowIcon(QIcon(f'{params_path}/Picture_gui/settings_picture.jpg'))
            self.sett_window_VKSPA = QtWidgets.QWidget(self.sett_window)
            self.sett_window_VKSPA.setGeometry(QtCore.QRect(10, 10, 400, 400))
            self.sett_window_VKSPA.setObjectName("Настройки")
            self.connection_checkBox = QtWidgets.QCheckBox(self.sett_window_VKSPA)
            self.connection_checkBox.setText('Подвязать аккаунты к прокси')
            self.connection_checkBox.setGeometry(QtCore.QRect(10, 107, 220, 20))
            self.connection_checkBox.stateChanged.connect(lambda: self.open_connect_log_and_proxy())

            """ Установка значения кол-ва аккаунтов для мульти спама """
            maximum = self.return_info_quantity_acc()[0]  # Возвращает кол-во аккаунтов из файла
            self.count_acc = QtWidgets.QSpinBox(self.sett_window_VKSPA)
            self.count_acc.setMaximum(maximum)
            self.count_acc.setGeometry(QtCore.QRect(10, 30, 41, 21))
            self.count_acc.setMinimum(1)
            self.count_acc.setValue(self.count_acc_multispam)
            self.count_acc_lable = QtWidgets.QLabel(self.sett_window_VKSPA)
            self.count_acc_lable.setGeometry(QtCore.QRect(60, 31, 170, 16))
            self.count_acc_lable.setText('Кол-во аккаунтов для спама')

            """ Установка значения для выбора номера аккаунта, с которого начнется рассылка """
            self.with_first_acc_lable = QtWidgets.QLabel(self.sett_window_VKSPA)
            self.with_first_acc_lable.setGeometry(QtCore.QRect(60, 71, 250, 16))
            self.with_first_acc_lable.setText('С какого аккаунта начать рассылку')
            self.with_first_acc = QtWidgets.QSpinBox(self.sett_window_VKSPA)
            self.with_first_acc.setGeometry(QtCore.QRect(10, 70, 41, 21))
            self.with_first_acc.setMinimum(1)
            self.with_first_acc.setMaximum(maximum)
            self.with_first_acc.setValue(self.with_first_acc_multispam)
            self.with_first_acc.valueChanged.connect(lambda: self.change_value_quantity_acc())
        except Exception as err_open_base_window:
            self.error_window_spam_wall(text_error='Ошибка, попробуйте перезагрузить приложение',
                                        err_detail=f'Ошибка при открытии базового окна\n{err_open_base_window}')
        try:
            self.save_sett_pushButton = QtWidgets.QPushButton(self.sett_window_VKSPA)
            self.save_sett_pushButton.setGeometry(QtCore.QRect(30, 330, 150, 40))
            self.save_sett_pushButton.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                    "color: rgb(255, 255, 255);\n"
                                                    "font: 75 10pt \"MS Shell Dlg 2\";")
            self.save_sett_pushButton.setText('Сохранить')
            self.save_sett_pushButton.clicked.connect(lambda: (self.save_settings(self.count_acc.text(),
                                                                                  self.with_first_acc.text()),
                                                               self.list_rpx.clear(),
                                                               self.list_log.clear(),
                                                               self.sett_window.close()
                                                               )
                                                      )
            self.reset_sett_pushButton = QtWidgets.QPushButton(self.sett_window_VKSPA)
            self.reset_sett_pushButton.setGeometry(QtCore.QRect(200, 330, 150, 40))
            self.reset_sett_pushButton.setStyleSheet("background-color: rgb(255, 0, 0);\n"
                                                     "color: rgb(255, 255, 255);\n"
                                                     "font: 75 10pt \"MS Shell Dlg 2\";")
            self.reset_sett_pushButton.setText('Сбросить\nнастройки')
            self.reset_sett_pushButton.clicked.connect(lambda: self.reset_sett(maximum=maximum))

            if self.connect_log_and_prx:
                self.connection_checkBox.setChecked(True)

            self.sett_window.show()
        except Exception as err_open_window:
            self.error_window_spam_wall(text_error='Ошибка, попробуйте перезагрузить приложение',
                                        err_detail=f'Ошибка при открытии окна с настройками\n{err_open_window}')

    def save_settings(self, count, first):
        """ Сохраняет настройки при подвязке прокси к аккаунтам """
        try:
            i = 0
            if self.connection_checkBox.isChecked():
                if len(self.dict_log_prx) == 0:
                    self.connect_log_and_prx = True
                    for log in self.list_log:
                        self.dict_log_prx[log.currentText()] = self.list_rpx[i].currentText()
                        i += 1
                self.disposable_list.clear()  # Очищает список с временной подвязкой лог к прокси, для того, чтоб в будущем
                # когда он будет создаваться, создавался с нуля и КО ВСЕМ ЕГО ОБЪЕКТАМ можно было нормально обращаться
            elif self.connection_checkBox.isChecked() is False:
                self.connect_log_and_prx = False
            else:
                print('Без привязки лог к прокси')
            self.count_acc_multispam = int(count)
            self.with_first_acc_multispam = int(first)
        except Exception as err_save_sett:
            self.error_window_spam_wall(text_error='Не удалось сохранить настройки, попробуйте перезагрузить приложение',
                                        err_detail=str(err_save_sett))

    def reset_sett(self, maximum):
        """ Сброс настроек подвязки прокси к аккаунту """
        try:
            self.save_sett_pushButton.setEnabled(True)
            for i in self.list_log:
                i.close()
            self.list_log.clear()
            for i in self.list_rpx:
                i.close()
            for lgp in self.disposable_list:
                lgp.close()
            self.disposable_list.clear()

            self.list_rpx.clear()
            self.dict_log_prx.clear()
            self.connection_checkBox.setChecked(False)
            self.connect_log_and_prx = False
            self.count_acc.setValue(maximum)
            self.with_first_acc.setValue(1)
            self.previous = 1
            self.error_window_spam_wall('Настройки сброшены')
        except Exception as err_reset:
            self.error_window_spam_wall(text_error='Не удалось сбросить настройки, попробуйте перезагрузить приложение',
                                        err_detail=str(err_reset))

    def highlighter_line_id_group(self):
        """ Выделяет строку с id группы, в которой будет оставляться запись """

        text_format = QTextCharFormat()
        text_format.setBackground(Qt.blue)
        text_format.setForeground(Qt.white)

        normal_format = QTextCharFormat()
        normal_format.setBackground(Qt.white)
        normal_format.setForeground(Qt.black)

        try:
            if self.count_highlighter > 0:
                cursor = self.list_groups_tableView.textCursor()
                cursor.movePosition(QTextCursor.Up)
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

                cursor.setCharFormat(normal_format)

                cursor.movePosition(QTextCursor.Down)
                cursor.movePosition(QTextCursor.StartOfLine)

                self.list_groups_tableView.setTextCursor(cursor)

        except Exception as err_0:
            print(err_0)

        try:

            cursor = self.list_groups_tableView.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

            cursor.setCharFormat(text_format)

            cursor.movePosition(QTextCursor.Down)
            cursor.movePosition(QTextCursor.StartOfLine)

            self.list_groups_tableView.setTextCursor(cursor)

        except Exception as err:
            print(err)

        self.count_highlighter += 1

    def error_window_spam_wall(self, text_error, err_detail=None):
        """ Создает всплывающее окно с ошибкой """

        error_wind = QMessageBox()
        error_wind.setWindowTitle('Предупреждение')
        error_wind.setText(f'{text_error}')
        error_wind.setWindowIcon(QIcon("../params/Picture_gui/error.png"))
        error_wind.setIcon(QMessageBox.Warning)
        error_wind.setStandardButtons(QMessageBox.Ok)
        if err_detail:
            error_wind.setDetailedText(str(err_detail))
        error_wind.exec_()
        return error_wind
