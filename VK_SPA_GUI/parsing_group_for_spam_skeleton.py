# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QHeaderView
import VK_SPA_Settings

RESULT_LIST_SEARCH = []


class RunThreadSearchGroup(QThread):
    """ Класс потока поиска групп по запросу """
    thread_timer = QtCore.pyqtSignal()

    def __init__(self, window, vk_method, settings, table):
        """ Поиск групп по запросу
            :param vk_method - объект сессии из основного потока;
            :param window - основное окно для визуального изменения информации;
            :param table - таблица для внесения в нее информации и ее отбражения;
            :param settings - настройки поиска, полученные из основного потока:
                settings[0] - показывать только группы, доступные для публикаций, True or False;
                settings[1] - минимальное число подписчиков групп, int;
                settings[2] - сам запрос для поиска, str;
                settings[3] - ограничения по выдаче результата в таблицу, int
        """
        super().__init__()
        self.window = window
        self.vk_method = vk_method
        self.settings = settings
        self.table = table
        self.only_open = self.settings[0]
        self.minimal_count = self.settings[1]
        self.query = self.settings[2]
        self.limit = self.settings[3]

    def parsing_group(self, query):
        """ Выполняет поиск групп по запросу.
            Т.к через vk_method.groups.search нет возможности найти все необходимую информацию, используем
            self.vk_method.groups.getById для всего списка групп из vk_method.groups.search """
        all_group = []
        if self.vk_method is None:
            self.window.setText('Вы не прошли авторизацию в программе!')
            return None
        try:
            self.window.setText('Начали поиск...')
            result_query_search = self.vk_method.groups.search(q=query, type=['group', 'page'], count=800, sort=6)

            for i in range(len(result_query_search['items'])):  # Для каждой группы в словаре ищем определенную инфу
                all_group.append(result_query_search['items'][i]['id'])

            all_info_group = self.vk_method.groups.getById(group_ids=all_group, fields=['members_count', 'can_post'])
            return result_query_search, all_info_group

        except Exception as err_pars:
            if '[30]' in str(err_pars):
                self.window.setText('Данный профиль закрыт')
            elif '[18]' in str(err_pars):
                self.window.setText('Данный профиль удален или забанен')
            elif '[10]' or '[1]' in str(err_pars):
                self.window.setText('Произошла внутренняя ошибка сервера')
            else:
                self.window.setText('При парсинге произошла ошибка, попробуйте позже')
            return None

    def apply_search_terms(self, limit, all_info, table):
        """ Применяет настройки поиска к полученным данным и передает окончательные значения в таблицу """

        if self.only_open and self.minimal_count == 0:
            for a in range(len(all_info[0]['items'])):
                if table.rowCount() == limit:
                    break
                ended_values = self.assign_values(all_info_group=all_info[1], position=a)
                if int(all_info[1][a]['can_post']) == 1:
                    self.add_row(value=ended_values, table=table)

        elif self.only_open and self.minimal_count != 0:
            for a in range(len(all_info[0]['items'])):
                if table.rowCount() == limit:
                    break
                ended_values = self.assign_values(all_info_group=all_info[1], position=a)

                if int(all_info[1][a]['can_post']) == 1 and all_info[1][a]['members_count'] >= self.minimal_count:
                    self.add_row(value=ended_values, table=table)

        elif self.only_open is False and self.minimal_count != 0:
            for a in range(len(all_info[0]['items'])):
                if table.rowCount() == limit:
                    break
                ended_values = self.assign_values(all_info_group=all_info[1], position=a)

                if all_info[1][a]['members_count'] >= self.minimal_count:
                    self.add_row(value=ended_values, table=table)

        elif self.only_open is False and self.minimal_count == 0:
            for a in range(len(all_info[0]['items'])):
                if table.rowCount() == limit:
                    break
                ended_values = self.assign_values(all_info_group=all_info[1], position=a)
                self.add_row(value=ended_values, table=table)
        self.window.setText('Поиск успешно завершен!')

    def assign_values(self, all_info_group, position):
        """ Форматирует полученные значения из all_info_group для понятного отображения в таблице и в дальнейшем
            передает их в таблицу для отображения """

        can_post = all_info_group[position]['can_post']
        open_close = all_info_group[position]['is_closed']

        can_post_str = 'Нет' if int(can_post) == 0 else 'Да'
        open_close_str = 'Открытая' if int(open_close) == 0 else 'Закрытая'
        ready_value = [all_info_group[position]['id'],
                       all_info_group[position]['name'],
                       open_close_str,
                       all_info_group[position]['members_count'],
                       can_post_str]

        return ready_value

    def add_row(self, table, value):
        """ Добовляет для каждого нового полученного значения строку в таблицу """
        global RESULT_LIST_SEARCH
        item1 = QTableWidgetItem()
        item2 = QTableWidgetItem()
        item3 = QTableWidgetItem()
        item4 = QTableWidgetItem()
        item5 = QTableWidgetItem()
        item1.setText(f'{value[0]}')
        item2.setText(f'{value[1]}')
        item4.setText(f'{value[2]}')
        item3.setText(f'{value[3]}')
        item5.setText(f'{value[4]}')
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)
        table.setItem(rowPosition, 0, item1)  # Первое значение это ряд, 2 - столбец
        table.setItem(rowPosition, 1, item2)
        table.setItem(rowPosition, 4, item5)
        table.setItem(rowPosition, 2, item3)
        table.setItem(rowPosition, 3, item4)
        RESULT_LIST_SEARCH.append(value[0])

        return RESULT_LIST_SEARCH

    def run(self):
        """ Запуск потока """
        global RESULT_LIST_SEARCH
        RESULT_LIST_SEARCH.clear()
        all_info = self.parsing_group(query=self.query)

        if all_info is None:
            self.thread_timer.emit()
            return

        try:
            self.apply_search_terms(limit=self.limit, all_info=all_info, table=self.table)
        except IndexError:
            self.window.setText("Подобраны подходящие варианты под ваш запрос")
            self.thread_timer.emit()
            return
        except Exception as err_table:
            print(err_table)
            self.thread_timer.emit()
            return
        self.thread_timer.emit()


class UiVkSpaParsingGroupForSpam_SKELETON(object):

    def __init__(self):
        self.central_widget_Parsing_for_spam = QtWidgets.QWidget()

        self.label_settings_parsing_group = QtWidgets.QLabel(self.central_widget_Parsing_for_spam)
        self.label_settings_parsing_group.setGeometry(QtCore.QRect(520, 140, 121, 16))

        self.label_result_parsing_group = QtWidgets.QLabel(self.central_widget_Parsing_for_spam)
        self.label_result_parsing_group.setGeometry(QtCore.QRect(0, 140, 400, 20))
        self.label_result_parsing_group.setStyleSheet("color: rgb(0, 0, 0);\n"
                                                      "font: 75 9pt \"MS Shell Dlg 2\";\n")
        self.gif_label = QtWidgets.QLabel(self.central_widget_Parsing_for_spam)
        self.gif_label.setGeometry(QtCore.QRect(0, 140, 20, 20))
        self.gif_parsing = QtGui.QMovie(f'{VK_SPA_Settings.abspath_params}/Picture_gui/load_main.gif')
        self.gif_parsing.setScaledSize(QtCore.QSize(20, 20))
        self.gif_label.setMovie(self.gif_parsing)

        self.label_query_parsing_group = QtWidgets.QLabel(self.central_widget_Parsing_for_spam)
        self.label_query_parsing_group.setGeometry(QtCore.QRect(0, 10, 361, 16))
        self.count_groups_label_parsing_group = QtWidgets.QLabel(self.central_widget_Parsing_for_spam)
        self.count_groups_label_parsing_group.setGeometry(QtCore.QRect(590, 215, 171, 16))
        self.minimal_followers_label_parsing_group = QtWidgets.QLabel(self.central_widget_Parsing_for_spam)
        self.minimal_followers_label_parsing_group.setGeometry(QtCore.QRect(590, 244, 131, 31))
        self.line_parsing_group = QtWidgets.QFrame(self.central_widget_Parsing_for_spam)
        self.line_parsing_group.setGeometry(QtCore.QRect(500, 121, 20, 332))
        self.line_parsing_group.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_parsing_group.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.do_file_group_button_parsing_group = QtWidgets.QPushButton(self.central_widget_Parsing_for_spam)
        self.do_file_group_button_parsing_group.setGeometry(QtCore.QRect(520, 310, 191, 51))
        self.do_file_group_button_parsing_group.setStyleSheet("color: rgb(0, 0, 0);\n"
                                                              "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                                              "background-color: rgb(85, 255, 0);")
        self.do_file_group_button_parsing_group.setObjectName("do_file_group_button")
        self.go_search_button_parsing_group = QtWidgets.QPushButton(self.central_widget_Parsing_for_spam)
        self.go_search_button_parsing_group.setGeometry(QtCore.QRect(0, 80, 781, 41))
        self.go_search_button_parsing_group.setStyleSheet("background-color: rgb(0, 170, 255);"
                                                          "font: 75 12pt \"MS Shell Dlg 2\";\n")

        self.input_query_textEdit_parsing_group = QtWidgets.QLineEdit(self.central_widget_Parsing_for_spam)
        self.input_query_textEdit_parsing_group.setGeometry(QtCore.QRect(0, 30, 781, 31))
        self.input_query_textEdit_parsing_group.setObjectName("input_query_textEdit")
        self.input_query_textEdit_parsing_group.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";\n")

        self.only_open_group_checkBox = QtWidgets.QCheckBox(self.central_widget_Parsing_for_spam)
        self.only_open_group_checkBox.setGeometry(QtCore.QRect(520, 170, 231, 20))
        self.count_group_spinBox = QtWidgets.QSpinBox(self.central_widget_Parsing_for_spam)
        self.count_group_spinBox.setGeometry(QtCore.QRect(520, 210, 62, 22))
        self.count_group_spinBox.setMaximum(500)
        self.minimal_followers_spinBox = QtWidgets.QSpinBox(self.central_widget_Parsing_for_spam)
        self.minimal_followers_spinBox.setGeometry(QtCore.QRect(520, 250, 62, 22))
        self.minimal_followers_spinBox.setMaximum(10_000_000)

        self.go_search_button_parsing_group.raise_()
        self.label_result_parsing_group.raise_()
        self.input_query_textEdit_parsing_group.raise_()
        self.label_query_parsing_group.raise_()
        self.line_parsing_group.raise_()
        self.label_settings_parsing_group.raise_()
        self.only_open_group_checkBox.raise_()
        self.count_group_spinBox.raise_()
        self.count_groups_label_parsing_group.raise_()
        self.do_file_group_button_parsing_group.raise_()
        self.minimal_followers_spinBox.raise_()
        self.minimal_followers_label_parsing_group.raise_()

        self.retranslateUi()
        self.function_parsing_group_for_spam()

        self.VK_PARSING_GROUP_METHOD_FROM_MAIN = None

    def retranslateUi(self):
        """ Визуализация названий всех кнопок и лэйблов """
        _translate = QtCore.QCoreApplication.translate
        self.go_search_button_parsing_group.setText(_translate("MainWindow", "Начать поиск"))
        self.label_result_parsing_group.setText(_translate("MainWindow", "Результаты поиска"))
        self.label_query_parsing_group.setText(_translate("MainWindow", "Введите запрос для поиска"))
        self.label_settings_parsing_group.setText(_translate("MainWindow", "Настройки поиска"))
        self.only_open_group_checkBox.setText(_translate("MainWindow", "Выдать только открытые группы"))
        self.count_groups_label_parsing_group.setText(_translate("MainWindow", "Сколько групп выдать"))
        self.do_file_group_button_parsing_group.setText(_translate("MainWindow", "Сформировать файл с\n"
                                                                                 " найденными групами"))
        self.minimal_followers_label_parsing_group.setText(_translate("MainWindow", "Минимальное число \n"
                                                                                    "участников группы"))

    def function_parsing_group_for_spam(self):
        """ Описание всех связей между кнопками и функциями, которые они выполняют """
        self.do_file_group_button_parsing_group.clicked.connect(lambda: self.from_result_search_into_text_file())
        self.go_search_button_parsing_group.clicked.connect(lambda: self.start_gif())
        self.go_search_button_parsing_group.clicked.connect(lambda: self.run_parsing())

    def validation_entered_query(self, query):
        """ Проверка правильность запроса """
        if len(query) == 0:
            self.label_result_parsing_group.setText('Строка поиска пустая!')
            return False
        elif len(query) > 35:
            self.label_result_parsing_group.setText('Слишком длинный запрос!')
            return False
        elif query.isspace():
            self.label_result_parsing_group.setText('В запросе одни пробелы!')
            return False
        else:
            return query

    def return_base_setting_in_thread(self, query, limit):
        """ Возвращает список с настройками поиска, нужна для передачи в поток """
        return [self.only_open_group_checkBox.isChecked(), self.minimal_followers_spinBox.value(),
                query, limit]

    def start_gif(self):
        """ Запускает гифку поиска """
        self.label_result_parsing_group.setGeometry(QtCore.QRect(23, 140, 400, 20))
        self.gif_parsing.start()
        self.gif_label.show()

    def end_gif(self):
        """ Останавливает гифку поиска """
        self.label_result_parsing_group.setGeometry(QtCore.QRect(0, 140, 400, 20))
        self.gif_parsing.stop()
        self.gif_label.close()

    def run_parsing(self):
        """ Фукнция поиска групп по запросу пользователя.
            СОздает объект таблицу, который потом передает в отдельный поток поиска """

        self.table = self.create_table()
        query = self.validation_entered_query(self.input_query_textEdit_parsing_group.text())
        if query is False:
            self.end_gif()
            return

        limit = self.count_group_spinBox.value()

        self.thread_search = RunThreadSearchGroup(vk_method=self.VK_PARSING_GROUP_METHOD_FROM_MAIN,
                                                  window=self.label_result_parsing_group,
                                                  table=self.table,
                                                  settings=self.return_base_setting_in_thread(query=query, limit=limit))
        self.thread_search.thread_timer.connect(self.end_gif)
        self.thread_search.start()

    def create_table(self):
        """ Функция для создания таблицы"""
        self.result_listView_parsing_group = QtWidgets.QTableWidget(self.central_widget_Parsing_for_spam)
        self.result_listView_parsing_group.setGeometry(QtCore.QRect(0, 160, 481, 281))
        self.result_listView_parsing_group.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.result_listView_parsing_group.raise_()
        self.table_settings(self.result_listView_parsing_group)
        return self.result_listView_parsing_group

    def table_settings(self, table):
        """ Установка настроек и шапки таблицы """
        table.show()
        table.setColumnCount(5)
        table_names = ['id', 'Имя группы', 'Кол-во \nучастников', 'Открытая ли\n группа',
                       'Можно ли\n публиковать']
        table.setHorizontalHeaderLabels(table_names)
        table.setStyleSheet("font: 7pt \"MS Shell Dlg 2\";\n")
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def from_result_search_into_text_file(self):
        """ Функция для создания файла .txt  с конечным списком ID найденных групп """
        global RESULT_LIST_SEARCH
        if len(RESULT_LIST_SEARCH) == 0:
            self.label_result_parsing_group.setText('Список пуст!')
            return
        path_members_group = QFileDialog.getSaveFileName()[0]
        try:
            with open(f'{path_members_group}.txt', 'w') as f:
                for line_ID in RESULT_LIST_SEARCH:
                    f.writelines(f'{line_ID}\n')
        except Exception as err:
            print(err)
