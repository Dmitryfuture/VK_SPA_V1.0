# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QCheckBox, QSpinBox, QHeaderView, QTableWidgetItem, QFileDialog
import VK_SPA_Settings

RESULT_LIST_FRIEND = []


class RunThreadParsingFriend(QThread):
    """ Класс потока парсинга друзей/подписчиков юзера """
    thread_timer = QtCore.pyqtSignal()

    def __init__(self, window_for_show, vk_method, id_user_for_parsing, friend_or_followers, data_count, table):
        """ :param table - сам объект таблицы, из основного потока;
            :param data_count - список настроек выбранных пользователем:
                data_count[0] - значение в SpinBox, кол-во друзей для парсинга;
                data_count[1] - число всех друзей_подписчиков пользователя;
                data_count[2] - True or False, парсить всех друзей(True) либо нет(False)
         """
        super().__init__()
        self.window_for_show = window_for_show
        self.vk_method = vk_method
        self.id_user_for_parsing = id_user_for_parsing
        self.friend_or_followers = friend_or_followers
        self.data_count = data_count
        self.table = table
        self.list_friends = []
        self.all_info = None

    def getting_exact_quantity_followers(self, len_list_followers):
        """ Получаем окончательное число аккаунтов для показа в таблице с учетом полученной информации и введенных
         настроек """

        if self.data_count[0] > 0:
            self.data_count[1] = self.data_count[0]

            if self.data_count[0] > len_list_followers:
                self.data_count[1] = len_list_followers

        elif self.data_count[2]:
            self.data_count[1] = len_list_followers

        return self.data_count[1]

    def parsing_thread(self, vk_method, id_user_for_parsing, friend_or_followers):
        """ Парсинг страницы пользователя
            :param vk_method - объект сессии из основного потока;
            :param id_user_for_parsing - ID юзера для парсинга;
            :param friend_or_followers - кого парсить, "friends" - друзей, "followers" - подписчиков
            quantity_all - Точное число друзей или подписчиков у пользователя,
            get_user_friends - Вся информация о друзьях/подписчиках пользователя
        """
        get_user_friends, quantity_all = None, None

        try:
            if friend_or_followers == 'friends':
                get_user_friends = vk_method.friends.get(user_id=id_user_for_parsing, order='random', fields='nickname')
                quantity_all = len(get_user_friends['items'])
            elif friend_or_followers == 'followers':
                quantity_all = vk_method.users.getFollowers(user_id=id_user_for_parsing)['count']
                get_user_friends = vk_method.users.getFollowers(user_id=id_user_for_parsing, fields='first_name',
                                                                count=quantity_all)

            return get_user_friends, quantity_all if get_user_friends and quantity_all else None, None

        except Exception as err_get_info:
            if '[30]' in str(err_get_info):
                self.window_for_show.setText('Данный профиль закрыт')
            elif '[18]' in str(err_get_info):
                self.window_for_show.setText('Данный профиль удален или забанен')
            elif '[10]' or '[1]' in str(err_get_info):
                self.window_for_show.setText('Произошла внутренняя ошибка сервера')
            else:
                self.window_for_show.setText('При парсинге произошла ошибка, попробуйте позже')
                print(f"err_get_info - {err_get_info}")
            return None

    def making_table(self, count_for_show, all_info):
        """ Создаем саму таблицу.
        (i, 0, item1.setText(str(number)))  # Первое значение это ряд, второе - столбец, третье - значение ячейки """
        global RESULT_LIST_FRIEND
        number = 1
        self.table.setRowCount(count_for_show)
        for i in range(count_for_show):
            first_name = all_info['items'][i]['first_name']
            last_name = all_info['items'][i]['last_name']
            friend_id = all_info['items'][i]['id']

            item1 = QTableWidgetItem()
            item2 = QTableWidgetItem()
            item3 = QTableWidgetItem()
            item1.setText(str(number))
            item2.setText(f'{first_name} {last_name}')
            item3.setText(f'{friend_id}')

            for item in [item1, item2, item3]:
                item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

            self.table.setItem(i, 0, item1)  # Первое значение это ряд, 2 - столбец
            self.table.setItem(i, 1, item2)
            self.table.setItem(i, 2, item3)
            number += 1
            self.list_friends.append(friend_id)
        self.table.update()
        self.window_for_show.setText('Парсинг завершен')
        RESULT_LIST_FRIEND = self.list_friends

    def run(self):
        """ Запуск потока """
        if self.vk_method is None:
            self.window_for_show.setText('Вы не прошли авторизацию в программе!')
            self.thread_timer.emit()
            return

        self.window_for_show.setText('Начали парсинг')
        self.all_info = self.parsing_thread(self.vk_method, self.id_user_for_parsing, self.friend_or_followers)

        if self.all_info is None:
            self.thread_timer.emit()
            return
        if self.all_info == (None, None):
            self.window_for_show.setText('При парсинге произошла ошибка, попробуйте позже [2]')
            self.thread_timer.emit()
            return

        count_for_show = self.getting_exact_quantity_followers(self.all_info[1])

        try:
            self.making_table(count_for_show=count_for_show, all_info=self.all_info[0])
        except Exception:
            self.window_for_show.setText('Внутренняя ошибка приложения')
            self.thread_timer.emit()
            return

        self.thread_timer.emit()


class UiVkSpaParsingFriend_SKELETON:

    def __init__(self):

        self.central_widget_PARSING_FRIEND = QtWidgets.QWidget()

        self.label_status_parsing = QtWidgets.QLabel(self.central_widget_PARSING_FRIEND)
        self.label_status_parsing.setGeometry(QtCore.QRect(20, 130, 790, 20))
        self.label_status_parsing.setStyleSheet('font: 9pt "MS Shell Dlg 2";')

        self.gif_label = QtWidgets.QLabel(self.central_widget_PARSING_FRIEND)
        self.gif_label.setGeometry(QtCore.QRect(0, 130, 20, 20))
        self.gif_parsing = QtGui.QMovie(f'{VK_SPA_Settings.abspath_params}/Picture_gui/load_main.gif')
        self.gif_parsing.setScaledSize(QtCore.QSize(20, 20))
        self.gif_label.setMovie(self.gif_parsing)

        self.label_input_id_parsing_friend = QtWidgets.QLabel(self.central_widget_PARSING_FRIEND)
        self.label_input_id_parsing_friend.setGeometry(QtCore.QRect(0, 18, 351, 16))
        self.label_input_id_parsing_friend.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_input_id_parsing_friend.setText("Введите в поле ID пользователя (только цифры)")
        self.label_ChooseBox_parsing_friend = QtWidgets.QLabel(self.central_widget_PARSING_FRIEND)
        self.label_ChooseBox_parsing_friend.setGeometry(QtCore.QRect(627, 10, 164, 31))
        self.label_ChooseBox_parsing_friend.setText("Спарсить определенное\nкол-во друзей\подписчиков")
        self.label_ChooseBox_parsing_friend.setStyleSheet('font: 8pt "MS Shell Dlg 2";')

        self.check_box_all_friend_pars = QCheckBox(self.central_widget_PARSING_FRIEND)
        self.check_box_all_friend_pars.setGeometry(410, 10, 171, 30)
        self.check_box_all_friend_pars.setText('Парсинг всех \nдрузей\подписчиков')
        self.spinBoxChooseCountFriend = QSpinBox(self.central_widget_PARSING_FRIEND)
        self.spinBoxChooseCountFriend.setGeometry(562, 17, 61, 22)
        self.spinBoxChooseCountFriend.setMaximum(5000)

        self.button_parsing_friend_user = QtWidgets.QPushButton(self.central_widget_PARSING_FRIEND)
        self.button_parsing_friend_user.setGeometry(QtCore.QRect(0, 95, 260, 35))
        self.button_parsing_friend_user.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                      "font: 75 10pt \"MS Shell Dlg 2\";")
        self.button_parsing_friend_user.setObjectName("Parsing_friend_user")
        self.button_parsing_friend_user.setText("Начать парсинг друзей")

        self.button_parsing_follower_user = QtWidgets.QPushButton(self.central_widget_PARSING_FRIEND)
        self.button_parsing_follower_user.setGeometry(QtCore.QRect(270, 95, 260, 35))
        self.button_parsing_follower_user.setText("Начать парсинг подписчиков")
        self.button_parsing_follower_user.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                        "font: 75 10pt \"MS Shell Dlg 2\";")
        self.button_parsing_follower_user.setObjectName("Parsing_follower_user")

        self.do_file_from_result_parsing_friend_pushButton = QtWidgets.QPushButton(self.central_widget_PARSING_FRIEND)
        self.do_file_from_result_parsing_friend_pushButton.setGeometry(QtCore.QRect(540, 95, 250, 35))
        self.do_file_from_result_parsing_friend_pushButton.setText("Сформировать файл")
        self.do_file_from_result_parsing_friend_pushButton.setStyleSheet("background-color: rgb(0, 255, 127);\n"
                                                                         "font: 75 10pt \"MS Shell Dlg 2\";")
        self.do_file_from_result_parsing_friend_pushButton.setObjectName("do_file_from_result_parsing_friend")

        self.input_ID_friend_parsing_friend = QtWidgets.QLineEdit(self.central_widget_PARSING_FRIEND)
        self.input_ID_friend_parsing_friend.setGeometry(QtCore.QRect(0, 50, 790, 31))
        self.input_ID_friend_parsing_friend.setStyleSheet("font: 75 9pt MS Shell Dlg 2")
        self.input_ID_friend_parsing_friend.setMaxLength(15)
        self.tableViewResult_parsing_friend = QtWidgets.QTableWidget(self.central_widget_PARSING_FRIEND)
        self.tableViewResult_parsing_friend.setGeometry(QtCore.QRect(0, 152, 790, 290))
        self.tableViewResult_parsing_friend.setObjectName("tableViewResult")
        self.tableViewResult_parsing_friend.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableViewResult_parsing_friend.setColumnCount(3)
        self.tableViewResult_parsing_friend.verticalHeader().setVisible(False)
        self.tableViewResult_parsing_friend.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableViewResult_parsing_friend.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableViewResult_parsing_friend.setHorizontalHeaderLabels(['№', 'Имя и фамилия', 'ID пользователя'])

        self.functions_for_button()
        self.count_friend_or_followers = 0

        self.VK_PARSING_FRIEND_METHOD_FROM_MAIN = None

    def functions_for_button(self):
        self.button_parsing_friend_user.clicked.connect(lambda: self.start_gif())
        self.button_parsing_friend_user.clicked.connect(lambda: self.create_and_run_thread(who='friends'))
        self.button_parsing_follower_user.clicked.connect(lambda: self.start_gif())
        self.button_parsing_follower_user.clicked.connect(lambda: self.create_and_run_thread(who='followers'))
        self.do_file_from_result_parsing_friend_pushButton.clicked.connect(lambda: self.do_file_from_result_parsing())

    def clear_table(self):
        """ Очистка данных таблицы перед показом """
        self.count_friend_or_followers = 0

    def return_all_base_info(self):
        """ Возвращает список данных в поток парсинга """
        return [self.spinBoxChooseCountFriend.value(), self.count_friend_or_followers,
                self.check_box_all_friend_pars.isChecked()]

    def start_gif(self):
        """ Запускает гифку поиска """
        self.label_status_parsing.setGeometry(QtCore.QRect(23, 130, 790, 20))
        self.gif_parsing.start()
        self.gif_label.show()

    def end_gif(self):
        """ Останавливает гифку поиска """
        self.label_status_parsing.setGeometry(QtCore.QRect(0, 130, 790, 20))
        self.gif_parsing.stop()
        self.gif_label.close()

    def validation_of_entered(self, input_id: str):
        """ Проверка правильности введнных данных, в случае еспеха возвращает ID для парсинга"""

        if len(input_id) == 0:
            self.label_status_parsing.setText('Вы не ввели ID пользователя!')
            return False
        elif len(input_id) > 13:
            self.label_status_parsing.setText('Вы ввели неккоректный ID!')
            return False
        elif input_id.isdigit() is False:
            self.label_status_parsing.setText('ID должен содержать только цифры!')
            return False
        elif self.spinBoxChooseCountFriend.value() == 0 and self.check_box_all_friend_pars.isChecked() is False:
            self.label_status_parsing.setText(f'Вы ничего не отметили в настройках!')
            return False
        else:
            return input_id

    def create_and_run_thread(self, who):
        self.clear_table()

        id_user_for_parsing = self.validation_of_entered(self.input_ID_friend_parsing_friend.text())

        if id_user_for_parsing is False:
            return self.end_gif()

        elif id_user_for_parsing:
            self.thread_parsing = RunThreadParsingFriend(window_for_show=self.label_status_parsing,
                                                         vk_method=self.VK_PARSING_FRIEND_METHOD_FROM_MAIN,
                                                         id_user_for_parsing=id_user_for_parsing,
                                                         friend_or_followers=who,
                                                         data_count=self.return_all_base_info(),
                                                         table=self.tableViewResult_parsing_friend)
            self.thread_parsing.thread_timer.connect(self.end_gif)
            self.thread_parsing.start()

    def do_file_from_result_parsing(self):
        """ Создает файл .txt с найдеными ID """
        global RESULT_LIST_FRIEND

        if len(RESULT_LIST_FRIEND) == 0:
            self.label_status_parsing.setText("Список пуст!")
            return
        path_friend_user = QFileDialog.getSaveFileName()[0]
        try:
            with open(f'{path_friend_user}.txt', 'w') as f:
                for line_ID in RESULT_LIST_FRIEND:
                    f.writelines(f'{line_ID}\n')
        except Exception as err:
            print('Здесь ошибка' + str(err))
