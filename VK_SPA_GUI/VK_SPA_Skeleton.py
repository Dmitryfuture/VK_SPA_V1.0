# -*- coding: utf-8 -*-
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon

import hello_page_skeleton
import add_account_skeleton
import add_proxy_skeleton
import comment_spam_skeleton
import parsing_friend_skeleton
import parsing_group_for_spam_skeleton
import parsing_members_skeleton
import mailing_on_the_wall_skeleton
import likes_users_posts_and_photo_skeleton
import news_feed_walk_skeleton
import pump_account_skeleton
import VK_SPA_Settings


class VkSpaSkeleton(object):

    def __init__(self):
        super(VkSpaSkeleton, self).__init__()

    def setupUi(self, vk_spa_base):
        vk_spa_base.setObjectName("VK_SPA")
        vk_spa_base.resize(1062, 610)
        vk_spa_base.setStyleSheet("background-color: rgb(184, 254, 255);\n"
                                  "background-color: rgb(255, 255, 255);")
        vk_spa_base.setWindowIcon(QIcon(f'{VK_SPA_Settings.abspath_params}/Picture_gui/Vk_SPA_icon.jpg'))
        self.centralwidget_VKSPA = QtWidgets.QWidget(vk_spa_base)
        self.centralwidget_VKSPA.setObjectName("centralwidget")

        self.stackedWidget_VKSPA = QtWidgets.QStackedWidget(self.centralwidget_VKSPA)
        self.stackedWidget_VKSPA.setGeometry(QtCore.QRect(260, 140, 800, 450))
        self.stackedWidget_VKSPA.setObjectName("stackedWidget")

        """ Page HELLO PAGE. Index in  stackedWidget № 0 """

        self.PAGE_hello = hello_page_skeleton.Ui_HELLO_PAGE_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_hello.centralwidget_HELLO_PAGE)

        """ Page ADD_ACCOUNT. Index in  stackedWidget № 1 """

        self.PAGE_add_account = add_account_skeleton.UiVkSpaAddAccount_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_add_account.central_widget_ADD_ACCOUNT)

        """ Page ADD PROXY. Index in stackedWidget № 2 """

        self.PAGE_add_proxy = add_proxy_skeleton.UiVkSpaAddProxy_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_add_proxy.central_widget_ADD_PROXY)

        """ Page PARSING_USERS_FRIEND. Index in stackedWidget № 3 """

        self.PAGE_parsing_users_friend = parsing_friend_skeleton.UiVkSpaParsingFriend_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_parsing_users_friend.central_widget_PARSING_FRIEND)

        """ Page PARSING_MEMBERS_IN_GROUP. Index in stackedWidget № 4 """

        self.PAGE_parsing_members_in_group = parsing_members_skeleton.UiVkSpaParsingMembers_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_parsing_members_in_group.central_widget_PARSING_MEMBERS)

        """ Page SEARCH GROUPS BY REQUEST. Index in stackedWidget № 5 """

        self.PAGE_parsing_groups_by_request = parsing_group_for_spam_skeleton.UiVkSpaParsingGroupForSpam_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_parsing_groups_by_request.central_widget_Parsing_for_spam)

        """ Page SPAM ON THE WALL. Index in stackedWidget № 6 """

        self.PAGE_spam_on_the_wall = spam_on_the_wall_skeleton.UiVkSpaSpamOnTheWall_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_spam_on_the_wall.central_widget_SPAM_ON_THE_WALL)

        """ Page SPAM COMMENT. Index in stackedWidget № 7 """

        self.PAGE_comment_spam = comment_spam_skeleton.UiVkSpaSpamComment_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_comment_spam.central_widget_SPAM_COMMENT)

        """ Page LIKES ON THE WALL USERS. Index in stackedWidget № 8 """

        self.PAGE_likes_users_posts = likes_users_posts_and_photo_skeleton.Ui_VkSpa_LikesUsersPostsAndPhoto_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_likes_users_posts.central_widget_LIKES_UESERS_POST_AND_PHOTO)

        """ Page NEWS FEED WALK. Index in stackedWidget № 9 """

        self.PAGE_news_feed_walk = news_feed_walk_skeleton.UiVkSpaNewsFeedWalk_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_news_feed_walk.centralwidget_NEWS_FEED_WALK)

        """ Page PUMP ACCOUNT. Index in stackedWidget № 10 """

        self.PAGE_pump_account = pump_account_skeleton.UiVkSpaPumpAccount_SKELETON()
        self.stackedWidget_VKSPA.addWidget(self.PAGE_pump_account.centralwidget_PUMP_ACCOUNT)

        """  Все то, что относится к авторизации """

        self.label_status_picture = QtWidgets.QLabel(self.centralwidget_VKSPA)  # Label статуса авторизации, красный
        self.label_status_picture.setGeometry(QtCore.QRect(820, 53, 16, 16))
        self.label_status_picture.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_status_picture.setObjectName("label_status_picture")
        self.label_status_picture.setPixmap(QtGui.QPixmap(f'{VK_SPA_Settings.abspath_params}/Picture_gui/'
                                                          f'red_status_16x16.jpg'))
        self.label_status_picture.raise_()
        self.label_status = QtWidgets.QLabel(self.centralwidget_VKSPA)  # Label статуса аккаунта
        self.label_status.setGeometry(QtCore.QRect(845, 52, 235, 16))
        self.label_status.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_status.setObjectName("label_status")
        self.label_status.setText('Пользователь не авторизован')
        self.lable_photo_avatar = QtWidgets.QLabel(self.centralwidget_VKSPA)  # Label Аватарки
        self.lable_photo_avatar.setGeometry(QtCore.QRect(820, 0, 50, 50))

        self.label_status_name_and_ID = QtWidgets.QLabel(self.centralwidget_VKSPA)  # Label Имени и ID
        self.label_status_name_and_ID.setGeometry(QtCore.QRect(880, 0, 171, 34))
        self.label_status_name_and_ID.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_status_name_and_ID.setObjectName("label_status")
        self.button_authUser = QtWidgets.QPushButton(self.centralwidget_VKSPA)  # Кнопка авторизации
        self.button_authUser.setGeometry(QtCore.QRect(935, 80, 115, 41))
        self.button_authUser.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                           "font:75 9pt \"MS Shell Dlg 2\";")
        self.button_authUser.setText('Авторизовать\nпользователя')
        self.chooseAcc_comboBox_main = QtWidgets.QComboBox(self.centralwidget_VKSPA)
        self.chooseAcc_comboBox_main.setGeometry(QtCore.QRect(740, 95, 190, 25))
        self.chooseAcc_comboBox_main.setObjectName("chooseAcc_comboBox")
        self.chooseProxy_comboBox_main = QtWidgets.QComboBox(self.centralwidget_VKSPA)
        self.chooseProxy_comboBox_main.setGeometry(QtCore.QRect(580, 95, 155, 25))
        self.chooseProxy_comboBox_main.setObjectName("chooseAcc_comboBox")
        self.label_choose_acc = QtWidgets.QLabel(self.centralwidget_VKSPA)  # Label выбора аккаунта
        self.label_choose_acc.setGeometry(QtCore.QRect(740, 70, 170, 20))
        self.label_choose_acc.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_choose_acc.setObjectName("label_status")
        self.label_choose_acc.setText('Выберите аккаунт')
        self.label_choose_proxy = QtWidgets.QLabel(self.centralwidget_VKSPA)  # Label выбора прокси
        self.label_choose_proxy.setGeometry(QtCore.QRect(580, 70, 120, 20))
        self.label_choose_proxy.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_choose_proxy.setText('Выберите прокси')

        """ Все для капчи """

        self.label_captcha = QtWidgets.QLabel(self.centralwidget_VKSPA)
        self.label_captcha.setGeometry(QtCore.QRect(450, 5, 91, 26))
        self.label_captcha.setText('Введите капчу')
        self.label_captcha.close()
        self.InputCaptcha = QtWidgets.QLineEdit(self.centralwidget_VKSPA)
        self.InputCaptcha.setGeometry(QtCore.QRect(450, 30, 100, 31))
        self.InputCaptcha.setStyleSheet("font: 75 10pt\"MS Shell Dlg 2\";")
        self.InputCaptcha.setAlignment(Qt.AlignCenter)
        self.InputCaptcha.close()
        self.lableImageCaptcha = QtWidgets.QLabel(self.centralwidget_VKSPA)
        self.lableImageCaptcha.setGeometry(QtCore.QRect(280, 25, 151, 41))
        self.lableImageCaptcha.close()
        self.press_captcha_button = QtWidgets.QPushButton(self.centralwidget_VKSPA)
        self.press_captcha_button.setGeometry(QtCore.QRect(555, 30, 120, 30))
        self.press_captcha_button.setText('Подтвердить капчу')
        self.press_captcha_button.setStyleSheet("background-color: rgb(0, 85, 255);\n"
                                                "color: rgb(255, 255, 255);"
                                                "font: 75 8pt\"MS Shell Dlg 2\";")
        self.press_captcha_button.close()
        self.press_captcha_button.clicked.connect(lambda: None)

        """ Все остальное """

        self.line_down = QtWidgets.QFrame(self.centralwidget_VKSPA)
        self.line_down.setGeometry(QtCore.QRect(0, 590, 1061, 6))
        self.line_down.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_down.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_down.raise_()
        self.line_2 = QtWidgets.QFrame(self.centralwidget_VKSPA)
        self.line_2.setGeometry(QtCore.QRect(240, 0, 20, 591))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.pump_accaunt_pushButton = QtWidgets.QPushButton(self.centralwidget_VKSPA)
        self.pump_accaunt_pushButton.setGeometry(QtCore.QRect(10, 535, 230, 41))
        self.pump_accaunt_pushButton.setObjectName("pump_accaunt")
        self.pump_accaunt_pushButton.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                   "font: 75 10pt \"MS Shell Dlg 2\";")
        self.add_account = QtWidgets.QPushButton(self.centralwidget_VKSPA)  # Индекс 1
        self.add_account.setGeometry(QtCore.QRect(260, 75, 150, 45))
        self.add_account.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                       "font: 75 10pt \"MS Shell Dlg 2\";")
        self.add_account.setObjectName("add_account")
        self.add_proxy = QtWidgets.QPushButton(self.centralwidget_VKSPA)  # Индекс 2
        self.add_proxy.setGeometry(QtCore.QRect(420, 75, 150, 45))
        self.add_proxy.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                     "font: 75 10pt \"MS Shell Dlg 2\";")
        self.add_proxy.setObjectName("add_proxy")
        self.line = QtWidgets.QFrame(self.centralwidget_VKSPA)
        self.line.setGeometry(QtCore.QRect(0, 120, 1061, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.layoutWidget = QtWidgets.QWidget(self.centralwidget_VKSPA)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 140, 231, 396))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.layoutWidget.setFont(font)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.button_menu_parsing_friend_user = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.button_menu_parsing_friend_user.setFont(font)
        self.button_menu_parsing_friend_user.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                           "font: 75 10pt \"MS Shell Dlg 2\";")
        self.button_menu_parsing_friend_user.setObjectName("Parsing_friend_user")
        self.verticalLayout.addWidget(self.button_menu_parsing_friend_user)
        self.Parsing_user_in_groupButton = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.Parsing_user_in_groupButton.setFont(font)
        self.Parsing_user_in_groupButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.Parsing_user_in_groupButton.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                       "font: 75 10pt \"MS Shell Dlg 2\";")
        self.Parsing_user_in_groupButton.setObjectName("Parsing_user_in_group")
        self.verticalLayout.addWidget(self.Parsing_user_in_groupButton)
        self.Parsing_group_by_requestButton = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.Parsing_group_by_requestButton.setFont(font)
        self.Parsing_group_by_requestButton.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                          "font: 75 10pt \"MS Shell Dlg 2\";")
        self.Parsing_group_by_requestButton.setObjectName("parsing_group_for_spam")
        self.verticalLayout.addWidget(self.Parsing_group_by_requestButton)

        self.Spam_on_the_wallButton = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.Spam_on_the_wallButton.setFont(font)
        self.Spam_on_the_wallButton.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                  "font: 75 10pt \"MS Shell Dlg 2\";")
        self.Spam_on_the_wallButton.setObjectName("spam")
        self.verticalLayout.addWidget(self.Spam_on_the_wallButton)
        self.Random_commentButton = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.Random_commentButton.setFont(font)
        self.Random_commentButton.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                "font: 75 10pt \"MS Shell Dlg 2\";")
        self.Random_commentButton.setObjectName("random_comment")
        self.verticalLayout.addWidget(self.Random_commentButton)
        self.likes_photo_and_post_my_friends_button = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.likes_photo_and_post_my_friends_button.setFont(font)
        self.likes_photo_and_post_my_friends_button.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                                  "font: 75 10pt \"MS Shell Dlg 2\";")
        self.likes_photo_and_post_my_friends_button.setObjectName("likes_photo_and_post_my_friends")
        self.verticalLayout.addWidget(self.likes_photo_and_post_my_friends_button)
        self.neew_feed_walk_button = QtWidgets.QPushButton(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.neew_feed_walk_button.setFont(font)
        self.neew_feed_walk_button.setStyleSheet("background-color: rgb(0, 255, 255);\n"
                                                 "font: 75 10pt \"MS Shell Dlg 2\";")
        self.neew_feed_walk_button.setObjectName("neew_feed_walk")
        self.verticalLayout.addWidget(self.neew_feed_walk_button)

        self.label_logo = QtWidgets.QPushButton(self.centralwidget_VKSPA)
        self.label_logo.setGeometry(QtCore.QRect(70, 10, 101, 111))
        self.label_logo.setIconSize(QSize(101, 111))
        self.label_logo.setObjectName("label")
        self.layoutWidget.raise_()
        self.pump_accaunt_pushButton.raise_()
        self.add_account.raise_()
        self.line.raise_()
        self.line_2.raise_()
        self.add_proxy.raise_()
        self.label_logo.raise_()
        vk_spa_base.setCentralWidget(self.centralwidget_VKSPA)
        self.menuBar = QtWidgets.QMenuBar(vk_spa_base)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1062, 26))
        self.menuBar.setObjectName("menuBar")
        self.menuVK_SPA_c_1_0 = QtWidgets.QMenu(self.menuBar)
        self.menuVK_SPA_c_1_0.setObjectName("menuVK_SPA_c_1_0")
        vk_spa_base.setMenuBar(self.menuBar)
        self.action = QtWidgets.QAction(vk_spa_base)
        self.action.setObjectName("action")
        self.menuVK_SPA_c_1_0.addSeparator()
        self.menuVK_SPA_c_1_0.addAction(self.action)
        self.menuVK_SPA_c_1_0.addSeparator()
        self.menuBar.addAction(self.menuVK_SPA_c_1_0.menuAction())
        self.function()
        self.retranslateUi(vk_spa_base)
        QtCore.QMetaObject.connectSlotsByName(vk_spa_base)

    def retranslateUi(self, VK_SPA):
        _translate = QtCore.QCoreApplication.translate
        VK_SPA.setWindowTitle(_translate("VK_SPA", "VK_SPA"))
        self.pump_accaunt_pushButton.setText(_translate("VK_SPA", "Прокачка аккаунта"))
        self.add_account.setText(_translate("VK_SPA", "Добавить\nаккаунт"))
        self.add_proxy.setText(_translate("VK_SPA", "Добавить прокси"))
        self.button_menu_parsing_friend_user.setText(_translate("VK_SPA", "Парсинг друзей\n"
                                                                          " пользователя"))
        self.Parsing_user_in_groupButton.setText(_translate("VK_SPA", "Парсинг людей в группе"))
        self.Parsing_group_by_requestButton.setText(_translate("VK_SPA", "Парсинг групп \n по запросу"))

        self.Spam_on_the_wallButton.setText(_translate("VK_SPA", "Рассылка по стенам"))
        self.Random_commentButton.setText(_translate("VK_SPA", "Комментирование записей\nв группах"))
        self.likes_photo_and_post_my_friends_button.setText(_translate("VK_SPA", "Лайки на стену \n"
                                                                                 "пользователей"))
        self.neew_feed_walk_button.setText(_translate("VK_SPA", "Проход по \n"
                                                                "новостной ленте"))
        self.menuVK_SPA_c_1_0.setTitle(_translate("VK_SPA", "VK_SPA | v 1.0"))
        self.action.setText(_translate("VK_SPA", "Инструкция"))

    def open_instruction(self):
        try:
            return webbrowser.open('https://telegra.ph/Instrukciya-po-ispolzovaniyu-VK-SPA-03-09')
        except Exception as err_open_link:
            print(err_open_link)

    def function(self):
        self.action.triggered.connect(lambda: self.open_instruction())
