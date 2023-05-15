import os

""" object_user_session - base session object """
object_user_session = None
""" use_proxy - will the user use proxy or not """
use_proxy = False
""" was_captcha - was shown captcha to the user during authorization or not """
was_captcha = False
""" captcha_input_text - entered text of captcha users """
captcha_input_text = ''
""" last_used_proxy - last used user proxy """
last_used_proxy = ''
""" result_check_proxy - result check proxy on valid """
result_check_proxy = None
""" check connection """
connection = True

abspath_VK_SPA_Settings = os.getcwd().replace("\\", '/')
abspath_params = abspath_VK_SPA_Settings.replace("VK_SPA_GUI", 'params')

"""Keys is russia char, value - english"""

alphabet = {'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T',
            'а': 'a', 'е': 'e', 'к': 'k', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'ф': 'f'}

alphabet_v2 = {'Е': 'Ě', 'К': 'Ќ', 'М': 'Ḿ', 'Р': 'Ҏ', 'Т': 'Ṫ',
               'а': 'ά', 'к': 'ќ', 'с': 'ĉ', 'у': 'ẏ', 'ф': 'Ⴔ'}

"""Dict for replace word in text"""
dict_replace_word = {'делаем': ['создаем', 'оформляем', 'совершаем', 'регистрируем', 'составляем', 'формируем'],
                     'создаем': ['оформляем', 'совершаем', 'регистрируем', 'составляем', 'формируем'],
                     'оформляем': ['создаем', 'совершаем', 'регистрируем', 'составляем', 'формируем'],
                     'совершаем': ['создаем', 'оформляем', 'регистрируем', 'составляем', 'формируем'],
                     'составляем': ['создаем', 'оформляем', 'совершаем', 'регистрируем', 'формируем'],
                     'формируем': ['создаем', 'оформляем', 'совершаем', 'регистрируем', 'составляем'],
                     'получить': ['заполучить', 'заиметь', 'урвать', 'забрать', 'ухватить'],
                     'получаем': ['заполучаем', 'урываем', 'забираем', 'ухватываем'],
                     'переходим': ['следуем', 'идем', 'заходим', 'направляемся', 'отправляемся'],
                     'навсегда': ['навечно', 'постоянно', 'перманетно', 'на совсем', 'на все время'],
                     'бесплатно': ['на халяву', 'даром', 'задаром'],
                     'бесплатно!': ['на халяву!', 'даром!', 'задаром!'],
                     'абсолютно': ['полностью', 'совершенно', ',безусловно', 'всецело'],
                     'совершенно': ['полностью', 'абсолютно', ',безусловно', 'всецело'],
                     'решение': ['ответ', 'результат', 'заключение'],
                     'заказываем': ['оформляем', 'делаем заявку на', 'оформляем заявку на', 'совершаем заявку на']
                     }


""" simple message for comment """
simple_comment = ['Круто!😅', 'Прикольная тема!😅', 'Классно!', 'В точку🤣', 'Ахахах,жиза🤣', 'Такое вообще возможно?)',
                  'Хахах)', 'Такое бывает?)', 'Блин, почему так сучно((', 'Как дальше то жить...', 'Ну что поделать)',
                  'Другого и не ожидалось',
                  'Я в шоке)', 'Интересно на это посмотреть😅', 'Мне бы кто нибудь так))',
                  'Ничего себе...😅', 'Прям жиза жизная, ахах😅😅)', 'Точно 😔', '🤣🤣🤣', 'Это прям в точку🤣🤣',
                  '😅😅 нереально просто', '🧐🧐', '🧐', 'Это как это??',
                  'Какая вероятность найти тут хороших собеседников?',
                  'Есть тут адекватные люди?',
                  'Ничего особенного', '😍😘', 'Обожаю когда так😍😘)',
                  'У меня тут вопросик появился🧐',
                  'Разве так бывает?)', 'Ахааахх, я в шоке)', 'Кто все это придумывает?)',
                  'Сейчас бы так, а не вот это все', 'Денег нет, но вы держитесь🤣🤣🤣', 'Просто шик!🤣',
                  'Реально, почему бы и нет',
                  'Так и живем', 'На мой взгляд банально',
                  'Превосходно))', 'Изумительно', 'Необычно', 'Все нормально)', 'Все хорошо))', 'Как то тихо тут у вас',
                  ]

list_group_for_comment_and_likes_and_repost = [191215235, 30022666, 23245066, 32477579, 67797649, 28261265, 12382740,
                                               147260439,
                                               57846937, 34491673, 40835481, 80377885, 139886499, 26419239, 35061290,
                                               23064236,
                                               123695926, 26669118, 140848576, 26519873, 26858816, 23148107, 41883468,
                                               31976785,
                                               39924694, 43776215, 43215063, 83075547, 45441631, 27972579, 165841893,
                                               460389, 46232553,
                                               23243883, 95287151, 171439088, 76520569, 30532220, 76132198, 55212627,
                                               35075445,
                                               36166439, 144625498, 102090470, 68319550, 38285632, 79421595, 27243668,
                                               84875607,
                                               63012307, 88640919, 54288674, 77177875, 77093415, 86225575, 54809759,
                                               28210851,
                                               33770645, 127012432, 115335023, 47610600, 145510087, 132564166, 47610608,
                                               31513532, 29868090]


girlish = ['Иванова', 'Шарапова', 'Медведева', 'Дергачева', 'Андреева', 'Антипова', 'Дубова', 'Гаврилова', 'Ермилова',
           'Ермакова', 'Аникина', 'Волошина', 'Воробъева', 'Мышкина', 'Котова', 'Заяц', 'Горохова', 'Ушакова',
           'Сердюкова', 'Безрукова', 'Степанова', 'Алексеева', 'Казанцева', 'Коробухина', 'Исаева', 'Демидова',
           'Виноградова', 'Бурова', 'Быкова', 'Богданова', 'Гуляева', 'Столихина', 'Блинова', 'Зотова']

video = ['456280705', '456280629', '456280584', '456280497', '456280425', '456283034', '456283020',
         '456282978', '456282969', '456282952', '456282946']

