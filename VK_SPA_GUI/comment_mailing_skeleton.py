import os
from datetime import datetime
from random import randint
from time import sleep

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QWidget, QProgressBar
import VK_SPA_Settings as VK_set


class RunSpamComment(QThread):
    """ Класс потока авторизации пользователя
        pre_progress - передает длину ProgressBar в основной поток;
        progress - передает значение в ProgressBar;
        finally_part - выполняется в случае завершения потока. """
    pre_progress = QtCore.pyqtSignal(int)
    progress = QtCore.pyqtSignal(int)
    finally_part = QtCore.pyqtSignal()
    progress_comment = QtCore.pyqtSignal(str)

    def __init__(self, vk_method, settings, text, text_attachments_comment, progress_bar):
        """ self.settings - список настроек для комментирования,
            self.settings[0] - tuple интервал между итераицями при комментированиии,
            self.settings[1] - кол-во постов в группе для комментирования """
        super().__init__()
        self.STOP_SPAM_COMMENT = False
        self.vk_method = vk_method
        self.settings = settings
        self.text = text
        self.text_attachments_comment = text_attachments_comment
        self.progress_bar = progress_bar


    def open_file_with_groups(self):
        """ Открытие файла с группами """
        with open(file=f'{VK_set.abspath_params}/File_group_for_comment.txt', mode='r', encoding='utf8') \
                as file_group_parsing:  # Список id групп
            lines = file_group_parsing.readlines()
            return lines if len(lines) >= 1 else False

    def parsing_group(self, list_groups):
        """ Парсинг групп для комментирования, возвращает словарь, где:
            ключ - ID Группы, значение - список ID записей в этой группе """
        dict_group_and_entries_post = {}
        for group in list_groups:
            group_id = str(group).replace('\n', '')
            try:
                group_info = self.vk_method.wall.get(owner_id=f'-{int(group_id)}', offset=1, count=self.settings[1])
                dict_group_and_entries_post[group_id] = []
            except Exception:
                continue
            for i in range(self.settings[1]):
                try:
                    post_id = group_info['items'][i]['id']
                    dict_group_and_entries_post[group_id].append(post_id)
                except IndexError:
                    pass

        for elem in dict_group_and_entries_post.values():
            if len(elem) < self.settings[1]:
                self.progress_comment.emit('Собрали информацию, но не в полном объеме, возможно часть групп '
                                         'закрыта для комментирования')
                break
        else:
            self.progress_comment.emit('Собрали информацию в полном объеме!')

        return dict_group_and_entries_post

    def get_info_group(self):
        """ Функция проверяющая результат парсинга групп и также устанавливает размер ProgressBar """

        list_groups = self.open_file_with_groups()
        result = self.parsing_group(list_groups) if list_groups else None

        if result is None:
            return 'Проверьте правильность заполнения списка с группами!'

        else:
            maximum_bar = 0

            for i in result.values():
                maximum_bar += len(i)

            self.pre_progress.emit(maximum_bar)
            return result

    def write_comment(self, id_group, id_post, index_number):
        """ Функиция, которая стваит лайк на запись где будет оставлен комментарий, пишет сам комментарий и ставит
            лайк на сам комментарий. Возвращает текст для отображения его в TextBrowser """
        time_public = datetime.now().strftime("%H:%M:%S")

        try:
            self.vk_method.likes.add(type='post', owner_id=f'-{int(id_group)}',
                                     item_id=f'{int(id_post)}')  # Лайк на выбранную запись для комментирования

            my_comment = self.vk_method.wall.createComment(owner_id=f'-{int(id_group)}',
                                                           post_id=f'{int(id_post)}',
                                                           message=self.text,
                                                           attachments=self.text_attachments_comment)
            self.vk_method.likes.add(type='comment', owner_id=f'-{int(id_group)}',
                                     item_id=f"{my_comment['comment_id']}")

            return f'{index_number})В {time_public} в <a href=https://vk.com/wall-{str(id_group)}_{str(id_post)}>' \
                   f'группе</a> написан коммент\n'

        except Exception as err_create_comment:
            if '212' in str(err_create_comment):
                return f'{index_number})В {time_public} в <a href=https://vk.com/wall-{str(id_group)}_{str(id_post)}>' \
                       f'группе</a> доступ к комментариям запрещен\n'
            else:
                return f'{index_number})В {time_public} в <a href=https://vk.com/wall-{str(id_group)}_{str(id_post)}>' \
                       f'группе</a> не удалось оставить комментарий из-за ошибки - {err_create_comment}\n'

    def start_spam(self, base_info):
        """ Функция генератор, проходит по всем группам и выполняет в них функцию write_comment().
            Возвращает номер индекса для установки значения в ProgressBar """

        self.progress_comment.emit(' Начали рассылку комментариев '.center(65, '-'))
        self.progress_comment.emit(f'Текст для рассылки - {self.text}\n')

        index_number = 1
        for id_group in list(base_info.keys()):  # Выбираются группы по порядку

            if self.STOP_SPAM_COMMENT:
                break

            for id_post in base_info[id_group]:  # И в каждой группе выбираются записи по порядку

                if self.STOP_SPAM_COMMENT:
                    break

                text_for_browser = self.write_comment(id_group=id_group, id_post=id_post, index_number=index_number)
                self.progress_comment.emit(text_for_browser)

                yield index_number

                sleep(randint(*self.settings[0]))

                index_number += 1

        if self.STOP_SPAM_COMMENT is False:
            self.progress_comment.emit(' Рассылка комментариев закончена '.center(65, '-'))

    def run(self):
        """ Запуск потока """
        if self.vk_method is None:
            self.progress_comment.emit('Вы не прошли авторизацию в программе!')
            self.finally_part.emit()
            return

        group_for_spam = self.get_info_group()
        if isinstance(group_for_spam, str):
            self.progress_comment.emit(group_for_spam)
            self.finally_part.emit()
            return

        self.progress_bar.show()

        for i in self.start_spam(group_for_spam):
            self.progress.emit(i)

        self.finally_part.emit()


class UiVkSpaSpamComment_SKELETON(QWidget):

    def __init__(self):

        QWidget.__init__(self)

        self.central_widget_SPAM_COMMENT = QtWidgets.QWidget()

        self.mailingLogComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.mailingLogComment_label.setGeometry(QtCore.QRect(20, 220, 201, 16))
        self.listGroupsComments_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.listGroupsComments_label.setGeometry(QtCore.QRect(565, 20, 221, 16))
        self.listGroupsComments_label.setLineWidth(1)
        self.chooseTextComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.chooseTextComment_label.setGeometry(QtCore.QRect(20, 20, 251, 16))
        self.SettingsComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.SettingsComment_label.setGeometry(QtCore.QRect(20, 103, 71, 16))
        self.to_labelComment = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.to_labelComment.setGeometry(QtCore.QRect(136, 122, 21, 16))
        self.to_labelComment.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")

        self.secComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.secComment_label.setGeometry(QtCore.QRect(210, 120, 21, 16))
        self.secComment_label.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")

        self.intervalComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.intervalComment_label.setGeometry(QtCore.QRect(20, 122, 61, 16))
        self.intervalComment_label.setStyleSheet("font: 75 8pt \"MS Shell Dlg 2\";")

        self.InputTextComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.InputTextComment_label.setGeometry(QtCore.QRect(290, 20, 211, 16))
        self.autoChangeAccontComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.autoChangeAccontComment_label.setGeometry(QtCore.QRect(20, 148, 161, 31))
        self.InputAttComment_label = QtWidgets.QLabel(self.central_widget_SPAM_COMMENT)
        self.InputAttComment_label.setGeometry(QtCore.QRect(310, 120, 211, 16))
        self.InputAttComment_label.setText('Добавить изображение к рассылке')
        self.InputAttCommentEditComment = QtWidgets.QTextEdit(self.central_widget_SPAM_COMMENT)
        self.InputAttCommentEditComment.setGeometry(QtCore.QRect(290, 140, 257, 26))

        self.line_1Comment = QtWidgets.QFrame(self.central_widget_SPAM_COMMENT)
        self.line_1Comment.setGeometry(QtCore.QRect(11, 20, 776, 20))
        self.line_1Comment.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1Comment.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2Comment = QtWidgets.QFrame(self.central_widget_SPAM_COMMENT)
        self.line_2Comment.setGeometry(QtCore.QRect(12, 110, 544, 4))
        self.line_2Comment.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2Comment.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4Comment = QtWidgets.QFrame(self.central_widget_SPAM_COMMENT)
        self.line_4Comment.setGeometry(QtCore.QRect(10, 182, 544, 4))
        self.line_4Comment.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4Comment.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5Comment = QtWidgets.QFrame(self.central_widget_SPAM_COMMENT)
        self.line_5Comment.setGeometry(QtCore.QRect(12, 227, 790, 5))
        self.line_5Comment.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5Comment.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6Comment = QtWidgets.QFrame(self.central_widget_SPAM_COMMENT)
        self.line_6Comment.setGeometry(QtCore.QRect(10, 30, 5, 199))
        self.line_6Comment.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.line_6Comment.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_6Comment.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8Comment = QtWidgets.QFrame(self.central_widget_SPAM_COMMENT)
        self.line_8Comment.setGeometry(QtCore.QRect(555, 30, 5, 199))
        self.line_8Comment.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_8Comment.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.listGroupsComment_tableWidget = QtWidgets.QTextEdit(self.central_widget_SPAM_COMMENT)
        self.listGroupsComment_tableWidget.setGeometry(QtCore.QRect(565, 41, 221, 121))
        self.listGroupsComment_tableWidget.setStyleSheet("font: 75 7pt \"MS Shell Dlg 2\";")

        self.fromIntervalComment_spinBox = QtWidgets.QSpinBox(self.central_widget_SPAM_COMMENT)
        self.fromIntervalComment_spinBox.setGeometry(QtCore.QRect(90, 120, 42, 21))
        self.fromIntervalComment_spinBox.setMinimum(1)
        self.toIntervalComment_spinBox = QtWidgets.QSpinBox(self.central_widget_SPAM_COMMENT)
        self.toIntervalComment_spinBox.setGeometry(QtCore.QRect(160, 120, 42, 21))
        self.toIntervalComment_spinBox.setMinimum(2)

        self.mailingLogComment_textBrowser = QtWidgets.QTextBrowser(self.central_widget_SPAM_COMMENT)
        self.mailingLogComment_textBrowser.setReadOnly(True)
        self.mailingLogComment_textBrowser.ensureCursorVisible()
        self.mailingLogComment_textBrowser.setGeometry(QtCore.QRect(10, 240, 776, 201))
        self.mailingLogComment_textBrowser.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.mailingLogComment_textBrowser.setOpenExternalLinks(True)
        self.textEditComment = QtWidgets.QTextEdit(self.central_widget_SPAM_COMMENT)
        self.textEditComment.setGeometry(QtCore.QRect(290, 40, 257, 61))

        self.chooseTextComment_comboBox = QtWidgets.QComboBox(self.central_widget_SPAM_COMMENT)
        self.chooseTextComment_comboBox.setGeometry(QtCore.QRect(20, 40, 231, 21))
        self.autoChangeAccontComment_spinBox = QtWidgets.QSpinBox(self.central_widget_SPAM_COMMENT)
        self.autoChangeAccontComment_spinBox.setGeometry(QtCore.QRect(190, 157, 50, 20))

        self.go_Comment_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_COMMENT)
        self.go_Comment_pushButton.setGeometry(QtCore.QRect(18, 190, 141, 28))
        self.go_Comment_pushButton.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                 "color: rgb(255, 255, 255);\n"
                                                 "font: 75 9pt \"MS Shell Dlg 2\";")
        self.stopComment_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_COMMENT)
        self.stopComment_pushButton.setGeometry(QtCore.QRect(178, 190, 161, 28))
        self.stopComment_pushButton.setStyleSheet("color: rgb(255, 255, 255);\n"
                                                  "background-color: rgb(255, 0, 0);\n"
                                                  "font: 75 9pt \"MS Shell Dlg 2\";")
        self.addNewTextComment_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_COMMENT)
        self.addNewTextComment_pushButton.setGeometry(QtCore.QRect(20, 70, 205, 21))
        self.addNewTextComment_pushButton.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                        "color: rgb(255, 255, 255);\n"
                                                        "font: 75 8pt \"MS Shell Dlg 2\";")
        self.changeListGroupComment_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_COMMENT)
        self.changeListGroupComment_pushButton.setGeometry(QtCore.QRect(565, 200, 221, 21))
        self.changeListGroupComment_pushButton.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                             "color: rgb(255, 255, 255);\n"
                                                             "font: 75 9pt \"MS Shell Dlg 2\";")
        self.addGroupFormFileComment_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_COMMENT)
        self.addGroupFormFileComment_pushButton.setGeometry(QtCore.QRect(565, 170, 221, 21))
        self.addGroupFormFileComment_pushButton.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                              "color: rgb(255, 255, 255);\n"
                                                              "font: 75 8pt \"MS Shell Dlg 2\";")
        self.update_texts_pushButton = QtWidgets.QPushButton(self.central_widget_SPAM_COMMENT)
        self.update_texts_pushButton.setGeometry(QtCore.QRect(230, 70, 18, 21))
        self.update_texts_pushButton.setStyleSheet("background-color: rgb(85, 255, 0);")

        self.progress_bar = QProgressBar(self.central_widget_SPAM_COMMENT)
        self.progress_bar.setGeometry(QtCore.QRect(350, 200, 201, 16))
        self.progress_bar.close()

        self.get_texts_for_comment_spam()
        self.translateUi_SPAM_COMMENT()
        self.raise__()
        self.function_SPAM_COMMENT()

        self.VK_SPAM_COMMENT_METHOD_FROM_MAIN = None

        self.stopComment_pushButton.setEnabled(False)

    def raise__(self):
        self.line_1Comment.raise_()
        self.listGroupsComment_tableWidget.raise_()
        self.listGroupsComments_label.raise_()
        self.go_Comment_pushButton.raise_()
        self.mailingLogComment_textBrowser.raise_()
        self.chooseTextComment_comboBox.raise_()
        self.chooseTextComment_label.raise_()
        self.stopComment_pushButton.raise_()
        self.line_6Comment.raise_()
        self.line_4Comment.raise_()
        self.line_2Comment.raise_()
        self.SettingsComment_label.raise_()
        self.addNewTextComment_pushButton.raise_()
        self.fromIntervalComment_spinBox.raise_()
        self.toIntervalComment_spinBox.raise_()
        self.to_labelComment.raise_()
        self.secComment_label.raise_()
        self.intervalComment_label.raise_()
        self.line_8Comment.raise_()
        self.line_5Comment.raise_()
        self.mailingLogComment_label.raise_()
        self.changeListGroupComment_pushButton.raise_()
        self.addGroupFormFileComment_pushButton.raise_()
        self.autoChangeAccontComment_label.raise_()
        self.autoChangeAccontComment_spinBox.raise_()
        self.InputTextComment_label.raise_()
        self.textEditComment.raise_()
        self.update_texts_pushButton.raise_()

    def translateUi_SPAM_COMMENT(self):

        _translate = QtCore.QCoreApplication.translate
        self.mailingLogComment_label.setText(_translate("MainWindow", "Журнал рассылки комментариев"))
        self.listGroupsComments_label.setText(_translate("MainWindow", "Группы для рассылки комментариев"))
        self.go_Comment_pushButton.setText(_translate("MainWindow", "Начать рассылку"))
        self.chooseTextComment_label.setText(_translate("MainWindow", "Выбор текста комментария для рассылки"))
        self.SettingsComment_label.setText(_translate("MainWindow", "Настройки"))
        self.stopComment_pushButton.setText(_translate("MainWindow", "Остановить рассылку"))
        self.addNewTextComment_pushButton.setText(_translate("MainWindow", "Добавить новый текст"))
        self.to_labelComment.setText(_translate("MainWindow", "до"))
        self.secComment_label.setText(_translate("MainWindow", "сек"))
        self.intervalComment_label.setText(_translate("MainWindow", "Интервал"))
        self.changeListGroupComment_pushButton.setText(_translate("MainWindow", "Изменить список групп"))
        self.addGroupFormFileComment_pushButton.setText(_translate("MainWindow", "Добавить группы из файла"))
        self.autoChangeAccontComment_label.setText(_translate("MainWindow", "Число публикация в группе \n"
                                                                            " для комментирования"))
        self.InputTextComment_label.setText(_translate("MainWindow", "Можете ввести текст в окне ниже"))

    def function_SPAM_COMMENT(self):
        self.changeListGroupComment_pushButton.clicked.connect(lambda: self.change_list_group_comment())
        self.addNewTextComment_pushButton.clicked.connect(lambda: self.add_new_text_comment_spam())
        self.update_texts_pushButton.clicked.connect(lambda: self.update_text_comment_spam())
        self.addGroupFormFileComment_pushButton.clicked.connect(lambda: self.view_groups_list_comment_spam())
        self.stopComment_pushButton.clicked.connect(lambda: self.stop_spam_comment())
        self.go_Comment_pushButton.clicked.connect(lambda: self.start_commenting())

    def change_list_group_comment(self):
        """ Функция для изменения списка групп """
        file = 'File_group_for_comment.txt'
        os.startfile(f'{VK_set.abspath_params}/{file}')

    def add_new_text_comment_spam(self):
        """ Функция для добавления файла с новым комметарием """
        os.system(rf"explorer.exe {os.getcwd().replace('VK_SPA_GUI', 'params')}\text_for_comment_spam")

    def get_texts_for_comment_spam(self):
        """ Показывает в ComboBox все доступные текста """
        self.chooseTextComment_comboBox.addItem('-------')
        name_files = os.listdir(f'{VK_set.abspath_params}/Text_for_comment_spam/')
        name_files.remove('__init__.py')
        for name in name_files:
            if '.txt' in str(name):
                name = str(name).replace('.txt', '')
                self.chooseTextComment_comboBox.addItem(name)

    def update_text_comment_spam(self):
        """ Обновление ComboBox с текстами """
        self.chooseTextComment_comboBox.clear()
        self.get_texts_for_comment_spam()

    def view_groups_list_comment_spam(self):
        """ Просмотр в отдельном окне списка групп для комментирования """
        with open(f'{VK_set.abspath_params}/File_group_for_comment.txt', 'r') as f:
            text = f.read()
            self.listGroupsComment_tableWidget.setText(str(text))
            self.listGroupsComment_tableWidget.setReadOnly(True)

    def return_settings(self, interval: tuple, quantity_post_in_one_group):
        """ Вовзращает интервал(tuple) и кол-во постов в группе для комментрования.
            Нужна для передачи данных в поток """
        return [interval, quantity_post_in_one_group]

    def validation_settings(self, text_for_check):
        """ Проверка настроек """
        if self.autoChangeAccontComment_spinBox.value() == 0:
            self.error_window_comment('Выберите число публикаций для одной группы!')
            return None

        elif self.fromIntervalComment_spinBox.value() >= self.toIntervalComment_spinBox.value():
            self.error_window_comment('Неверно указан интервал!')
            return None

        elif text_for_check == "" or None:
            self.error_window_comment('Вы не выбрали текст для рассылки!')
            return None

        else:
            return text_for_check

    def clear_browser(self):
        """ Очистка браузера вывода текста """
        self.mailingLogComment_textBrowser.clear()
        self.go_Comment_pushButton.setEnabled(False)
        self.stopComment_pushButton.setEnabled(True)

    def open_file_with_text(self, name_file):
        """ Откртыие файла .txt с текстом для рассылки """
        with open(f'{VK_set.abspath_params}/Text_for_comment_spam/{name_file}.txt', 'r', encoding="utf-8") as f:
            text = f.read()
        return text

    def start_commenting(self):
        """ Начало рассылки и создание отдлеьного потока """

        text_attachments_comment = None
        self.clear_browser()

        if self.chooseTextComment_comboBox.currentText() != '-------':  # Выбор текста для рассылки
            text_for_check = self.open_file_with_text(self.chooseTextComment_comboBox.currentText())
        else:
            text_for_check = self.textEditComment.toPlainText()

        text = self.validation_settings(text_for_check)

        if text is None:
            self.go_Comment_pushButton.setEnabled(True)
            self.stopComment_pushButton.setEnabled(False)
            return

        if len(self.InputAttCommentEditComment.toPlainText()) > 1:
            text_attachments_comment = self.InputAttCommentEditComment.toPlainText()

        self.thread_spam_comment = RunSpamComment(vk_method=self.VK_SPAM_COMMENT_METHOD_FROM_MAIN,
                                                  settings=self.return_settings(
                                                      interval=(self.fromIntervalComment_spinBox.value(),
                                                                self.toIntervalComment_spinBox.value()),
                                                      quantity_post_in_one_group=self.autoChangeAccontComment_spinBox.value()),
                                                  text_attachments_comment=text_attachments_comment,
                                                  text=text, progress_bar=self.progress_bar)
        self.thread_spam_comment.pre_progress.connect(lambda size_bar: self.progress_bar.setMaximum(size_bar))
        self.thread_spam_comment.progress.connect(lambda value: self.progress_bar.setValue(value))
        self.thread_spam_comment.progress_comment.connect(lambda vl: self.mailingLogComment_textBrowser.append(vl))
        self.thread_spam_comment.finally_part.connect(self.end)
        self.thread_spam_comment.start()

    def end(self):
        """ Функция вызывающаяся при завершении рассылки, делает кнопки активнымми и сбрасывает настройки """
        self.go_Comment_pushButton.setEnabled(True)
        self.stopComment_pushButton.setEnabled(False)
        self.thread_spam_comment.STOP_SPAM_COMMENT = False

    def stop_spam_comment(self):
        """ Вызывается в случае принудительной остановки рассылки """
        self.stopComment_pushButton.setEnabled(False)
        self.thread_spam_comment.STOP_SPAM_COMMENT = True
        self.progress_bar.setValue(0)
        self.mailingLogComment_textBrowser.setText('Рассылка комментариев принудительно закончена пользователем')

    def error_window_comment(self, text_error, err_detail=None):
        """ Вызывает высплывающее окно в случаем ошибки """
        error_wind = QMessageBox()
        error_wind.setWindowTitle('Ошибка')
        error_wind.setText(f'{text_error}')
        error_wind.setWindowIcon(QIcon(f'{VK_set.abspath_params}/Picture_gui/error.png'))
        error_wind.setIcon(QMessageBox.Warning)
        error_wind.setStandardButtons(QMessageBox.Ok)
        if err_detail:
            error_wind.setDetailedText(str(err_detail))
        error_wind.exec_()
        return error_wind

