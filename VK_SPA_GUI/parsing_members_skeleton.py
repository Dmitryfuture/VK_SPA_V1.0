from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QSpinBox, QHeaderView, QTableWidgetItem, QFileDialog
import VK_SPA_Settings

RESULT_LIST_PARSING_MEMBERS = []


class RunThreadParsingMembers(QThread):
    """ Класс потока парсинга друзей/подписчиков юзера """
    thread_timer = QtCore.pyqtSignal()

    def __init__(self, vk_method, window_for_show, table, id_group, count_members):
        super().__init__()
        self.window_for_show = window_for_show
        self.vk_method = vk_method
        self.table = table
        self.id_group = id_group
        self.count_members = count_members

    def parsing(self, count_members, id_group):
        global RESULT_LIST_PARSING_MEMBERS
        RESULT_LIST_PARSING_MEMBERS.clear()
        a = 0
        full_list_id = []
        try:
            for i in range(1, int(count_members) + 1):
                data = self.vk_method.groups.getMembers(group_id=id_group, v=5.131, offset=a * 1000)["items"]
                a += 1
                full_list_id += data
        except Exception as err_pars:
            if 'group hide members' in str(err_pars):
                self.window_for_show.setText('Группа закрыта для парсинга')
            elif '[10]' or '[1]' in str(err_pars):
                self.window_for_show.setText('Произошла внутренняя ошибка сервера')
            else:
                print(err_pars)
                self.window_for_show.setText(f'Произошла внутренняя ошибка сервера {err_pars}')
            return None

        RESULT_LIST_PARSING_MEMBERS = full_list_id
        return full_list_id

    def making_table(self, data):
        self.table.setRowCount(len(data))
        number_row = 0

        for ID in data:
            item = QTableWidgetItem()
            item.setText(str(ID))
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table.setItem(number_row, 0, item)
            number_row += 1
        self.window_for_show.setText('Парсинг завершен')


    def run(self):
        """ Запуск потока """

        if self.vk_method is None:
            self.window_for_show.setText('Вы не прошли авторизацию в программе!')
            self.thread_timer.emit()
            return

        self.window_for_show.setText('Начали парсинг')

        self.data = self.parsing(count_members=self.count_members, id_group=self.id_group)
        if self.data is None:
            self.thread_timer.emit()
            return

        try:
            self.making_table(data=self.data)
        except Exception as err_table:
            self.window_for_show.setText(f'Произошла внутренняя ошибка сервера {err_table}')
            self.thread_timer.emit()
            return
        self.thread_timer.emit()


class UiVkSpaParsingMembers_SKELETON:

    def __init__(self):

        self.central_widget_PARSING_MEMBERS = QtWidgets.QWidget()

        self.label_result_members_search = QtWidgets.QLabel(self.central_widget_PARSING_MEMBERS)
        self.label_result_members_search.setGeometry(QtCore.QRect(20, 155, 440, 20))
        self.label_result_members_search.setText('Результаты поиска')
        self.label_result_members_search.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";")

        self.gif_label_members = QtWidgets.QLabel(self.central_widget_PARSING_MEMBERS)
        self.gif_label_members.setGeometry(QtCore.QRect(0, 155, 20, 20))
        self.gif_parsing_members = QtGui.QMovie(f'{VK_SPA_Settings.abspath_params}/Picture_gui/load_main.gif')
        self.gif_parsing_members.setScaledSize(QtCore.QSize(20, 20))
        self.gif_label_members.setMovie(self.gif_parsing_members)

        self.label_id_group_members_search = QtWidgets.QLabel(self.central_widget_PARSING_MEMBERS)
        self.label_id_group_members_search.setGeometry(QtCore.QRect(0, 70, 151, 16))
        self.label_id_group_members_search.setText("ID группы, только цифры")
        self.label_ChooseCountGroup_members_search = QtWidgets.QLabel(self.central_widget_PARSING_MEMBERS)
        self.label_ChooseCountGroup_members_search.setGeometry(QtCore.QRect(510, 170, 241, 46))
        self.label_ChooseCountGroup_members_search.setText(
            'Выберите сколько учатников \nгруппы спарсить, 1 = 1000, \n2 = 2000 и т.д. Макс - 20')

        self.lineEdit_id_group_for_search = QtWidgets.QLineEdit(self.central_widget_PARSING_MEMBERS)
        self.lineEdit_id_group_for_search.setGeometry(QtCore.QRect(0, 93, 781, 31))
        self.tableView_search_result_members_search = QtWidgets.QTableWidget(self.central_widget_PARSING_MEMBERS)
        self.tableView_search_result_members_search.setGeometry(QtCore.QRect(0, 180, 411, 261))
        self.tableView_search_result_members_search.setColumnCount(1)
        self.tableView_search_result_members_search.setHorizontalHeaderLabels(['ID'])
        self.tableView_search_result_members_search.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_search_result_members_search.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView_search_result_members_search.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.button_parsing_members = QtWidgets.QPushButton(self.central_widget_PARSING_MEMBERS)
        self.button_parsing_members.setGeometry(QtCore.QRect(0, 20, 781, 41))
        self.button_parsing_members.setStyleSheet("background-color: rgb(0, 170, 255);"
                                                  "font: 75 12pt \"MS Shell Dlg 2\";")

        self.button_parsing_members.setText("Спарсить")
        self.button_make_list_txt = QtWidgets.QPushButton(self.central_widget_PARSING_MEMBERS)
        self.button_make_list_txt.setGeometry(QtCore.QRect(440, 260, 344, 61))
        self.button_make_list_txt.setStyleSheet("background-color: rgb(0, 170, 255);"
                                                "font: 75 12pt \"MS Shell Dlg 2\";")
        self.button_make_list_txt.setText("Сформировать список \nв текстовом файле")

        self.spinBox_count_members_search = QSpinBox(self.central_widget_PARSING_MEMBERS)
        self.spinBox_count_members_search.setGeometry(440, 180, 61, 31)
        self.spinBox_count_members_search.setMaximum(20)
        self.spinBox_count_members_search.setMinimum(1)

        self.function_for_button()
        self.VK_PARSING_MEMBERS_METHOD_FROM_MAIN = None

    def function_for_button(self):
        self.button_parsing_members.clicked.connect(lambda: self.gif_start())
        self.button_parsing_members.clicked.connect(lambda: self.create_and_run_thread())
        self.button_make_list_txt.clicked.connect(lambda: self.from_members_group_into_text_file())

    def gif_start(self):
        """ Запускает и показывает гифку """

        self.label_result_members_search.setGeometry(QtCore.QRect(23, 155, 440, 20))
        self.gif_parsing_members.start()
        self.gif_label_members.show()

    def gif_end(self):
        """ Останавливает и закрывает гифку """
        self.label_result_members_search.setGeometry(QtCore.QRect(0, 155, 440, 20))
        self.gif_parsing_members.stop()
        self.gif_label_members.close()

    def check_entered_settings(self, id_group):
        """ Проверка входящих настроек """
        if len(id_group) == 0:
            self.label_result_members_search.setText('Вы не ввели ID группы!')
            return False
        elif len(id_group) > 13:
            self.label_result_members_search.setText('Вы ввели неккоректный ID!')
            return False
        elif id_group.isdigit() is False:
            self.label_result_members_search.setText('ID должен содержать только цифры!')
            return False
        else:
            return id_group

    def create_and_run_thread(self):
        """ Функция, создающая и запускающая поток парсинга подписчиков """
        id_group = self.check_entered_settings(self.lineEdit_id_group_for_search.text())
        count_members = self.spinBox_count_members_search.text()

        if id_group is False:
            self.gif_end()
            return

        self.thread_parsing_members = RunThreadParsingMembers(vk_method=self.VK_PARSING_MEMBERS_METHOD_FROM_MAIN,
                                                              id_group=id_group,
                                                              count_members=count_members,
                                                              table=self.tableView_search_result_members_search,
                                                              window_for_show=self.label_result_members_search)
        self.thread_parsing_members.thread_timer.connect(self.gif_end)
        self.thread_parsing_members.start()

    def from_members_group_into_text_file(self):
        """ Создает файл .txt с найдеными ID """

        global RESULT_LIST_PARSING_MEMBERS
        if len(RESULT_LIST_PARSING_MEMBERS) == 0:
            self.label_result_members_search.setText("Список пуст!")
            return
        path_members_group = QFileDialog.getSaveFileName()[0]
        try:
            with open(f'{path_members_group}.txt', 'w') as f:
                for line_ID in RESULT_LIST_PARSING_MEMBERS:
                    f.writelines(f'{line_ID}\n')
        except Exception as err:
            print(err)
