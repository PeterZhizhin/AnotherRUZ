# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton
from datetime import datetime
import json


def get_weekday_name(date: datetime):
    weekday = date.weekday()
    if weekday == 0:
        return 'Понедельник'
    elif weekday == 1:
        return 'Вторник'
    elif weekday == 2:
        return 'Среда'
    elif weekday == 3:
        return 'Четверг'
    elif weekday == 4:
        return 'Пятница'
    elif weekday == 5:
        return 'Суббота'
    elif weekday == 6:
        return 'Воскресенье'


def get_inline_keyboard(keyboard):
    result = []
    for keyboard_line in keyboard:
        line = []
        for element in keyboard_line:
            line.append(InlineKeyboardButton(element[0],
                                             callback_data=element[1]))
        result.append(line)
    return result


date_format = '%d.%m.%Y'
time_format = '%H:%M'

continue_inline_tag = 'continue'

start_enter_message = """Добро пожаловать в бот РУЗ ВШЭ!
Этот бот позволяет вам легко получать самую актуальную информацию о расписаниях в университете.
Нажмите \"Продолжить\" чтобы произвести настройку.
В случае проблем — обращайтесь к админу @PeterZhizhin."""
start_enter_keyboard = get_inline_keyboard([[('Продолжить', continue_inline_tag)]])

enter_email_message = """Введите адрес почты на edu.hse.ru или на hse.ru
Например: vnpupkin@edu.hse.ru или teachermail@hse.ru"""

wrong_email_message = """Адрес должен быть @edu.hse.ru или @hse.ru. Попробуйте ещё раз."""

email_checking_message = "Проверка работоспособности почты. Это может занять некоторое время\n" \
                         "Проверяем наличие расписания на {}."
email_checking_dates = [(1, 'сегодня'), (7, 'неделю'), (31, 'месяц'), (5 * 30, 'пять месяцев')]

no_email_error = "Что-то пошло не так... " \
                 "Либо почта неправильная и её нет в базе РУЗ, " \
                 "либо на сервере расписаний ВШЭ неполадки. " \
                 "Проверьте почту и попробуйте ещё раз.\n" \
                 "Если есть подозрения, что вас нет в базе — обратитесь в учебный офис."
no_timetable = "Для почты {} нет расписания на целых пять месяцев! " \
               "Если почта неверна — введите её ещё раз. " \
               "Если нет — спросите учебный офис, почему у вас нет расписания на такой долгий срок"

email_correct_message = "Почта верна. Сейчас вы получите расписание."


def no_timetable_today_fun(date):
    return "Сегодня занятий нет. Ближайшее занятие {}.".format(date.strftime(date_format))


def go_date_fun(date):
    return json.dumps({'type': 'GoDate', 'to': date.strftime(date_format)},
                      separators=(',', ':'))


def no_timetable_keyboard_fun(date):
    return get_inline_keyboard(
        [[('Перейти на {}'.format(date.strftime(date_format)), go_date_fun(date))]])


no_timetable_at_all = "Для вас вообще нет расписания, даже на полгода вперёд. Обратитесь в учебный офис."
no_lessons_at_date = "*{} ({})*\nНет занятий."

timetable_base = """*{begin_lesson_time}-{end_lesson_time}*
{discipline}
{kind_of_work} в аудитории *{auditorium_number}*
{lecturer}"""

division_line = '\n――――――――――――――\n'


def format_date(date: datetime):
    return date.strftime(date_format)


today_string = 'Сегодня'
today_string_label = 'today'

refresh_string = 'Обновить'
refreshing_string = 'Обновление'
going_to_date = 'Переход на {}'

too_far_error = 'Ошибка. Дата {} слишком далеко, расписание получить невозможно.'

get_tomorrow_cmd = '/tmrw'
get_today_cmd = '/today'
get_settings_cmd = '/settings'
get_keyboard = '/keyboard'
get_tomorrow_markup = 'Расписание на завтра'
get_today_markup = 'Расписание на сегодня'
get_settings_markup = 'Настройки'

keyboard_message = 'Клавиатура в этом сообщении'
main_keyboard_markup = [[get_tomorrow_markup, get_today_markup],
                        [get_settings_markup]]

help_message = "У бота есть всего несколько команд, продублированных кнопками на клавиатуре," \
               "которую можно получить (если её у вас нет) при помощи команды {keyboard}.\n" \
               "Другие команды:\n" \
               "{today} — расписание на сегодня\n" \
               "{tomorrow} — расписание на завтра\n" \
               "{settings} — настройки бота\n" \
               "{keyboard} — клавиатура с командами".format(keyboard=get_keyboard, today=get_today_cmd,
                                                            tomorrow=get_tomorrow_cmd, settings=get_settings_cmd)
confirm_help_type = 'confirm_help'
i_understand_confirm = json.dumps({'type': confirm_help_type}, separators=(',', ':'))
help_understand_markup = get_inline_keyboard([[('Понятно', i_understand_confirm)]])

settings_main = "Ваша текущая почта: {}"
change_email_tag = 'change_email'
go_back_tag = 'go_main'
back = 'Назад'
settings_main_markup = get_inline_keyboard([[('Поменять почту', change_email_tag),
                                             (back, go_back_tag)]])

get_email_back_keyboard = get_inline_keyboard([['В главное меню', go_back_tag]])

free_auditoriums_keyboard_message = 'Свободные аудитории'

free_auditoriums_main_message = "*{} ({})*\n_{}_\nВыберите номер пары, на которую нужно найти аудиторию."

free_auditoriums_pair_format = 'Пара {} ({}-{})'

free_auditoriums_list_format = "*{} ()*\n" \
                               "_{}_\n" \
                               "Свободные аудитории на {} пару\n" \
                               "*{}*"

getting_free_auditoriums = "Получение свободных аудиторий. Это может занять некоторое время."
go_to_pairs_choose_keyboard_message = 'Назад к выбору пары'

error_during_getting_schedule = 'Произошла ошибка. Возвращаем в главное меню.'
