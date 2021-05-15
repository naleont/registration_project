import telebot
import json
import string

bot = telebot.TeleBot('TOKEN')


def find_application(appl_no):
    application = None
    # Ищем заявку а рабочем файле
    with open('work_file.json', encoding='utf-8') as work_file:
        file = json.load(work_file)
        # Проходимся по рабочему файлу и проверяем, есть ли в нем словарь с нашим номером заявки
        for line in file:
            if line['id'] == str(appl_no):
                # Всю информацию по заявке кладем в переменную
                application = line
                break
    if application is None:
        application = new_application(appl_no)
    return application


def new_application(appl_no):
    with open('vernadsky.info.json', encoding='utf-8') as initial_file:
        file = json.load(initial_file)
        # Проходимся по рабочему файлу и проверяем, есть ли в нем словарь с нашим номером заявки
        for line in file:
            if line['id'] == str(appl_no):
                # Всю информацию по заявке кладем в переменную
                application = line
                add_fields(application)
                return application


def add_fields(application):
    # Добавить поле "изменены ФИО участника делегации"
    for member in application['delegation']['members']:
        member['changed'] = True
    # Добавить поля "изменено название работы" и "работа участвует во 2 туре"
    for work in application['works']:
        work['changed'] = True
        work['coming'] = False
        # Добавить поле "изменены ФИО автора"
        for author in work['authors']:
            author['changed'] = True
        # Добавить поле "изменены ФИО руководителя"
        work['teacher']['changed'] = True
    application['arrival_date'] = None
    application['arrival_time'] = None
    with open('work_file.json', encoding='utf-8') as work_file:
        file = json.load(work_file)
        file.append(application)
    with open('work_file.json', 'w', encoding='utf-8') as work_file:
        json.dump(file, work_file, indent=2, ensure_ascii=False)
    return application


def write_application(application):
    # Записываем найденную или исправленную заявку в рабочий файл
    with open('work_file.json', encoding='utf-8') as work_file:
        file = json.load(work_file)
        for line_no in range(len(file)):
            if file[line_no]['id'] == application['id']:
                n = line_no
    # Перезаписываем заявку в рабочем файле
    file[n] = application
    with open('work_file.json', 'w', encoding='utf-8') as work_file:
        json.dump(file, work_file, indent=2, ensure_ascii=False)


def correct_number(appl_nom):
    correct = None
    # Проверяем, что номер заявки имеет правильную длину
    if len(str(appl_nom)) != 5:
        return False
    else:
        for char in str(appl_nom):
            # Проверяем, что номер заявки состоит из цифр
            if char not in [char for char in string.digits]:
                return False
            else:
                correct = True
    return correct


def existing_number(appl_nom):
    with open('vernadsky.info.json', encoding='utf-8') as initial_file:
        file = json.load(initial_file)
        if str(appl_nom) in [appl['id'] for appl in file]:
            return True
        else:
            return False


def menu(appl_no):
    mark_up = telebot.types.InlineKeyboardMarkup()
    item = telebot.types.InlineKeyboardButton(text='Подтвердить информацию о работах', callback_data='works,' + appl_no)
    mark_up.add(item)
    # item = telebot.types.InlineKeyboardButton(text='Подтвердить информацию об участниках',
    #                                           callback_data='participants,' + appl_no)
    # mark_up.add(item)
    # item = telebot.types.InlineKeyboardButton(text='Выбрать дату и время приезда за бейджами',
    #                                           callback_data='arrival,' + appl_no)
    # mark_up.add(item)
    # item = telebot.types.InlineKeyboardButton(text='Подтвердить заявку', callback_data='confirm,' + appl_no)
    # mark_up.add(item)
    return mark_up


def send_menu(chat_id, appl_no):
    bot.send_message(chat_id, '*Заявка *' + str(appl_no), parse_mode='MarkdownV2', reply_markup=menu(appl_no))


def form_work_list(appl_no):
    application = find_application(appl_no)
    mark_up = telebot.types.InlineKeyboardMarkup()
    for work in application['works']:
        button = work['number'] + ' - ' + ', '.join([author['name'] for author in work['authors']])
        item = telebot.types.InlineKeyboardButton(text=button, callback_data='choose work,' + appl_no + ','
                                                                             + work['number'])
        mark_up.add(item)
    item = telebot.types.InlineKeyboardButton(text='Вернуться в меню', callback_data='back to menu,' + appl_no)
    mark_up.add(item)
    return mark_up


def coming_works(appl_no):
    application = find_application(appl_no)
    coming_list = []
    for work in application['works']:
        if work['coming'] is True:
            line = work['number'] + ' – ' + ', '.join([author['name'] for author in work['authors']])
            coming_list.append(line)
    if not coming_list:
        coming = 'Нет участвующих работ'
    else:
        coming = '\n'.join(coming_list)
    return coming


def works(chat_id, appl_no):
    coming = coming_works(appl_no)
    bot.send_message(chat_id, '*Работы, участвующие во 2 туре*:\n\n' + coming + '\n\n*Работы в заявке:*',
                     parse_mode='MarkdownV2', reply_markup=form_work_list(appl_no))


def buttoms_for_work_info(appl_no, work_no):
    # кнопочки
    mark_up = telebot.types.InlineKeyboardMarkup()
    item = telebot.types.InlineKeyboardButton(text='Подтвердить',
                                              callback_data='confirm work,' + appl_no + ',' + work_no)
    mark_up.add(item)
    item = telebot.types.InlineKeyboardButton(text='Исправить', callback_data='fix work,' + appl_no + ',' + work_no)
    mark_up.add(item)
    item = telebot.types.InlineKeyboardButton(text='Работа не участвует во 2 туре',
                                              callback_data='delete work,' + appl_no + ',' + work_no)
    mark_up.add(item)
    return mark_up


def make_work_info_dict(appl_no, work_no):
    application = find_application(appl_no)
    work_info_list = []
    keys_list = ['Номер работы', 'Название работы', 'Секция', 'Руководитель', 'Автор 1', 'Автор 2', 'Автор 3']
    for work in application['works']:
        if work['number'] == work_no:
            work_info_list.extend([work['number'], work['title'], work['section']['title']])
            work_info_list.append(work['teacher']['name'])
            work_info_list.extend([author['name'] for author in work['authors']])
    work_info_dict = dict(zip(keys_list, work_info_list))
    return work_info_dict


def work_info(chat_id, appl_no, work_no):
    work_info_dict = make_work_info_dict(appl_no, work_no)
    # выводит инфу о данной работе
    work_info_string = ''
    for key in work_info_dict.keys():
        work_info_string += key
        work_info_string += ': '
        work_info_string += work_info_dict[key]
        work_info_string += '\n\n'
    bot.send_message(chat_id, work_info_string, reply_markup=buttoms_for_work_info(appl_no, work_no))


def confirm_work(chat_id, appl_no, work_no):
    application = find_application(appl_no)
    for work in application['works']:
        if work['number'] == work_no:
            work['coming'] = True
            write_application(application)
    works(chat_id, appl_no)


def delete_work(chat_id, appl_no, work_no):
    application = find_application(appl_no)
    for work in application['works']:
        if work['number'] == work_no:
            work['coming'] = False
            write_application(application)
    works(chat_id, appl_no)


def fields_to_edit(chat_id, appl_no, work_no):
    work_info_dict = make_work_info_dict(appl_no, work_no)
    mark_up = telebot.types.InlineKeyboardMarkup()
    item = telebot.types.InlineKeyboardButton(text=work_info_dict['Название работы'],
                                              callback_data='edit_work_name,' + appl_no + ',' + work_no)
    mark_up.add(item)
    item = telebot.types.InlineKeyboardButton(text=work_info_dict['Руководитель'],
                                              callback_data='edit_teacher_name,' + appl_no + ',' + work_no)
    mark_up.add(item)
    item = telebot.types.InlineKeyboardButton(text=work_info_dict['Автор 1'],
                                              callback_data='edit_author1_name,' + appl_no + ',' + work_no)
    mark_up.add(item)
    if 'Автор 2' in work_info_dict.keys():
        item = telebot.types.InlineKeyboardButton(text=work_info_dict['Автор 2'],
                                                  callback_data='edit_author2_name,' + appl_no + ',' + work_no)
        mark_up.add(item)
    elif 'Автор 3' in work_info_dict.keys():
        item = telebot.types.InlineKeyboardButton(text=work_info_dict['Автор 3'],
                                                  callback_data='edit_author3_name,' + appl_no + ',' + work_no)
        mark_up.add(item)
    item = telebot.types.InlineKeyboardButton(text='Назад к списку работ', callback_data='back_to_work_list,' + appl_no)
    mark_up.add(item)
    bot.send_message(chat_id, 'Работа ' + work_no + '\n\nВыберите поле для редактирования',
                     reply_markup=mark_up)


def find_info(appl_no, work_no, info_type):
    works_dict = find_application(appl_no)['works']
    if info_type == 'title':
        for work in works_dict:
            if work['number'] == work_no:
                return work[info_type]
    elif info_type == 'teacher':
        for work in works_dict:
            if work['number'] == work_no:
                return work[info_type]['name']
    else:
        for work in works_dict:
            if work['number'] == work_no:
                author_no = int(info_type[6]) - 1
                return work['authors'][author_no]['name']


def new_data_title(message, appl_no, work_no):
    new = message.text
    if new == '/start' or new == '/cancel':
        return start_button(message)
    edit_work('title', new, appl_no, work_no, message)


def new_data_teacher(message, appl_no, work_no):
    new = message.text
    if new == '/start' or new == '/cancel':
        return start_button(message)
    edit_work('teacher', new, appl_no, work_no, message)


def new_data_a1(message, appl_no, work_no):
    new = message.text
    if new == '/start' or new == '/cancel':
        return start_button(message)
    edit_work('author1', new, appl_no, work_no, message)


def new_data_a2(message, appl_no, work_no):
    new = message.text
    if new == '/start' or new == '/cancel':
        return start_button(message)
    edit_work('author2', new, appl_no, work_no, message)


def new_data_a3(message, appl_no, work_no):
    new = message.text
    if new == '/start' or new == '/cancel':
        return start_button(message)
    edit_work('author3', new, appl_no, work_no, message)


def edit_work(field_to_change, fixed, appl_no, work_no, message):
    application = find_application(appl_no)
    for work in application['works']:
        if work['number'] == work_no:
            # проходим по ключам в "works", чтобы найти то поле, значение в котором нужно исправить
            # 1 - изменяется название работы
            if field_to_change == 'title':
                work[field_to_change] = fixed.strip()
                work['changed'] = False
            # 2 - изменяется ФИО руководителя работы
            if field_to_change == 'teacher':
                work['teacher']['name'] = fixed.strip()
                work['teacher']['changed'] = False

            # 3 - без прохода по ключам, работа со списком имен авторов
            if field_to_change == 'author1':
                work['authors'][0]['name'] = fixed.strip()
                work['authors'][0]['changed'] = False
            elif field_to_change == 'author2':
                work['authors'][1]['name'] = fixed.strip()
                work['authors'][1]['changed'] = False
            elif field_to_change == 'author3':
                work['authors'][2]['name'] = fixed.strip()
                work['authors'][2]['changed'] = False
    write_application(application)
    work_info(message.chat.id, appl_no, work_no)


def exit_editing(appl_no, work_no):
    mark_up = telebot.types.InlineKeyboardMarkup()
    item = telebot.types.InlineKeyboardButton('Не редактировать', callback_data='fix work,' + appl_no + ',' + work_no)
    mark_up.add(item)
    return mark_up


@bot.message_handler(commands=['start', 'cancel'])
def start_button(message):
    # markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # item1 = telebot.types.KeyboardButton('Начать заново')
    # item2 = telebot.types.KeyboardButton('❔')
    # markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Введите номер заявки')  # , reply_markup=markup)


# @bot.message_handler(commands=['help'])
# def welcome(message):
#     bot.reply_to(message, 'Для начала регистрации введите номер заявки')


@bot.message_handler(func=lambda m: True)
def check_number(message):
    appl_no = message.text
    appl_no = appl_no.strip()
    appl_no = appl_no.strip('№')
    correct = correct_number(appl_no)
    if correct is False:
        bot.reply_to(message, 'Некорректный номер заявки. Попробуйте ещё раз')
    else:
        existing = existing_number(appl_no)
        if existing is False:
            bot.reply_to(message, 'Несуществующий номер заявки. Попробуйте ещё раз')
        else:
            bot.send_message(message.chat.id, 'Заявка ' + str(
                appl_no) + ' найдена.\n\nДля регистрации пройдите шаги ниже.\n\nВносимую информацию можно будет '
                           'отредактировать позже.\n\nПодтвердить заявку необходимо не позднее, чем за полчаса до '
                           'приезда')
            send_menu(message.chat.id, appl_no)
            find_application(appl_no)


@bot.callback_query_handler(func=None)
def work_list(message):
    if message.data.split(',')[0] == 'works':
        works(message.from_user.id, message.data.split(',')[1])
        bot.delete_message(message.from_user.id, message.message.id)
    elif message.data.split(',')[0] == 'back to menu':
        send_menu(message.from_user.id, message.data.split(',')[1])
        bot.delete_message(message.from_user.id, message.message.id)
    elif message.data.split(',')[0] == 'choose work':
        work_no = message.data.split(',')[2]
        appl_no = message.data.split(',')[1]
        work_info(message.from_user.id, appl_no, work_no)
        bot.delete_message(message.from_user.id, message.message.id)
    elif message.data.split(',')[0] == 'confirm work':
        confirm_work(message.from_user.id, message.data.split(',')[1], message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)
    elif message.data.split(',')[0] == 'fix work':
        fields_to_edit(message.from_user.id, message.data.split(',')[1], message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)
    elif message.data.split(',')[0] == 'delete work':
        delete_work(message.from_user.id, message.data.split(',')[1], message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)

    # редактирование работ
    # редактирование названия работы
    elif message.data.split(',')[0] == 'edit_work_name':
        work_no = message.data.split(',')[2]
        old = find_info(message.data.split(',')[1], work_no, 'title')
        msg_edit = bot.send_message(message.from_user.id, 'Работа ' + work_no + ', старое название: "' + old
                                    + '"''\n\nВведите исправленное название',
                                    reply_markup=exit_editing(message.data.split(',')[1], work_no))
        bot.register_next_step_handler(msg_edit, new_data_title, appl_no=message.data.split(',')[1],
                                       work_no=message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)
    # редактироование ФИО руководителя
    elif message.data.split(',')[0] == 'edit_teacher_name':
        work_no = message.data.split(',')[2]
        old = find_info(message.data.split(',')[1], work_no, 'teacher')
        msg_edit = bot.send_message(message.from_user.id, 'Работа ' + work_no + ', руководитель: ' + old
                                    + '\n\nВведите исправленные ФИО руководителя',
                                    reply_markup=exit_editing(message.data.split(',')[1], work_no))
        bot.register_next_step_handler(msg_edit, new_data_teacher, appl_no=message.data.split(',')[1],
                                       work_no=message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)
    # редактирование ФИО автора 1
    elif message.data.split(',')[0] == 'edit_author1_name':
        work_no = message.data.split(',')[2]
        old = find_info(message.data.split(',')[1], work_no, 'author1')
        msg_edit = bot.send_message(message.from_user.id, 'Работа ' + work_no + ', автор 1: ' + old
                                    + '\n\nВведите исправленные ФИО автора 1',
                                    reply_markup=exit_editing(message.data.split(',')[1], work_no))
        bot.register_next_step_handler(msg_edit, new_data_a1, appl_no=message.data.split(',')[1],
                                       work_no=message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)
    # редактирование ФИО автора 2
    elif message.data.split(',')[0] == 'edit_author2_name':
        work_no = message.data.split(',')[2]
        old = find_info(message.data.split(',')[1], work_no, 'author2')
        msg_edit = bot.send_message(message.from_user.id, 'Работа ' + work_no + ', автор 2: ' + old
                                    + '\n\nВведите исправленные ФИО автора 2',
                                    reply_markup=exit_editing(message.data.split(',')[1], work_no))
        bot.register_next_step_handler(msg_edit, new_data_a2, appl_no=message.data.split(',')[1],
                                       work_no=message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)
    # редактирование ФИО автора 3
    elif message.data.split(',')[0] == 'edit_author3_name':
        work_no = message.data.split(',')[2]
        old = find_info(message.data.split(',')[1], work_no, 'author3')
        msg_edit = bot.send_message(message.from_user.id, 'Работа ' + work_no + ', автор 3: ' + old
                                    + '\n\nВведите исправленные ФИО автора 3',
                                    reply_markup=exit_editing(message.data.split(',')[1], work_no))
        bot.register_next_step_handler(msg_edit, new_data_a3, appl_no=message.data.split(',')[1],
                                       work_no=message.data.split(',')[2])
        bot.delete_message(message.from_user.id, message.message.id)


bot.polling(none_stop=True)
