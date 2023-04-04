from __future__ import print_function

import os.path
import pickle

###########################################################
import requests
import datetime
import telebot
from telebot import types
from decouple import config
###########################################################

API = config('API')

TOKEN = config('TOKEN2')
BOT = telebot.TeleBot(TOKEN)


cancel = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
cancel_button = types.KeyboardButton('cancel')
cancel.add(cancel_button)


keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
button_CURATOR = types.KeyboardButton('куратор')
button_SALES = types.KeyboardButton('sales')
button_EduTeam = types.KeyboardButton('eduteam')
button_INFO = types.KeyboardButton('info')
keyboard.add(button_SALES, button_CURATOR, button_INFO, button_EduTeam)

keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
button_day = types.KeyboardButton('day')
button_evening = types.KeyboardButton('evening')
keyboard1.add(button_day, button_evening, cancel_button)

curator_info_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
all_info_kb = types.KeyboardButton('общая информация')
info_by_groups_kb = types.KeyboardButton('по группам')
curator_info_kb.add(all_info_kb, info_by_groups_kb, cancel_button)

eduteam_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
lates = types.KeyboardButton('опоздание')
rating = types.KeyboardButton('рейтинг')
eduteam_kb.add(rating, lates, cancel_button)

position_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
curator_kb = types.KeyboardButton('куратор')
trecker_kb = types.KeyboardButton('трекер')
mentor_kb = types.KeyboardButton('ментор')
position_kb.add(curator_kb, trecker_kb, mentor_kb, cancel_button)



button_inf = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
button_inf.add(button_CURATOR, button_SALES, button_EduTeam, cancel_button )


class FormForKurators():
    departments = 'куратор'
    day_or_ev = None
    group = None
    comes_quantity = None
    lates_quantity = None
    kpi = None
    gone_away = None
    quantity_of_students = None

class FormForSales():
    departments = 'sales'
    number_quantity = None
    quantity_signup = None
    quantity_payment = None
    deadline = None
    quantity_old_dialogues = None
    quantity_new_dialogues = None
    quantity_of_entries_to_trial_lesson = None
    quantity_comes_to_trial_lesson = None
    quantity_of_calls_made_per_day = None

class Ratings():
    department = 'eduteam_ratings'
    position = None
    staff_choise = None
    weekly_rating = None

class Lates():
    department = 'eduteam_lates'
    quantity_of_lates = None

class Info():
    info_kb = None
    

@BOT.message_handler(commands=['start'])
def start(message):

    message2 = BOT.send_message(message.chat.id, "Привет", reply_markup=keyboard)
    BOT.register_next_step_handler(message2, check_kb)
    


@BOT.message_handler(content_types=['text'])
def check_kb(message):
    Info.info_kb = message

    if message.text.lower() == 'sales':
        number_quantity = BOT.send_message(message.chat.id, 'Количество номеров:', reply_markup=cancel)
        BOT.register_next_step_handler(number_quantity, number_quantity_today)

    elif message.text.lower() == 'куратор':
        message2 = BOT.send_message(message.chat.id, 'Выберите время суток', reply_markup = keyboard1)
        BOT.register_next_step_handler(message2,choose_day_or_ev )

    elif message.text.lower() == 'info':
        department = BOT.send_message(message.chat.id, 'Выберите отдел', reply_markup=button_inf)
        BOT.register_next_step_handler(department, department_choise)
    
    elif message.text.lower() == 'eduteam':
        message2 = BOT.send_message(message.chat.id, 'Выберите что хотите заполнить', reply_markup=eduteam_kb)
        BOT.register_next_step_handler(message2, check_edu_kb)

    else:
        BOT.clear_step_handler_by_chat_id(message.chat.id)
###########################################################################################

#-----------------------Проверка и отправка данных тимлида--------------------------------#
class Eduteam_info():
    info = None
def check_edu_kb(message):
    Eduteam_info.info = message
    if message.text.lower() == 'опоздание':
        lates = BOT.send_message(message.chat.id, 'Введите количество опозданий', reply_markup = cancel)
        BOT.register_next_step_handler(lates, send_data_lates)
    elif message.text.lower() == 'рейтинг':
        position_ = BOT.send_message(message.chat.id, 'Выберите позицию', reply_markup=position_kb)
        BOT.register_next_step_handler(position_ , position_staff)
    else:
        start(message)

def position_staff(message):
    Ratings.position = message.text
    data = {
				'position':message.text.lower(),
				'username':'bot'
			}
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    if message.text.lower() == 'cancel':
        start(message)
    else:
        res = requests.get(f'{API}/get_staff/', headers=headers, data=data)
        if message.text.lower() == 'куратор':
            try:
                staffs = res.json().get('data')
    
                staff_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                for i in staffs:
                    i = ' '.join(i)
                    button  = types.KeyboardButton(str(i))
                    staff_kb.add(button)
                staff = BOT.send_message(message.chat.id, 'Выберите сотрудника',reply_markup=staff_kb ) 
                BOT.register_next_step_handler(staff, staff_ratings)
            except:
                nomessage = BOT.send_message(message.chat.id, 'База пуста', reply_markup=cancel)
                BOT.register_next_step_handler(nomessage, start)

        elif message.text.lower() == 'трекер' or 'ментор':

            try:
                staffs = sum(res.json().get('data'), [])
    
                staff_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                for i in staffs:
                    i = ' '.join(i)
        
                    button  = types.KeyboardButton(str(i))
                    staff_kb.add(button)
                staff = BOT.send_message(message.chat.id, 'Выберите сотрудника',reply_markup=staff_kb ) 
                BOT.register_next_step_handler(staff, staff_ratings)
            except:
                nomessage = BOT.send_message(message.chat.id, 'База пуста', reply_markup=cancel)
                BOT.register_next_step_handler(nomessage, start)

def staff_ratings(message):
    Ratings.staff_choise = message.text
    ratings = BOT.send_message(message.chat.id, 'Введите рейтинг сотрудника')
    BOT.register_next_step_handler(ratings, send_data_ratings)


def send_data_ratings(message):
    Ratings.weekly_rating = message.text
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    data = {
        'departments':'eduteam_ratings',
        'position':Ratings.position,
        'staff_choise':Ratings.staff_choise,
        'weekly_rating':Ratings.weekly_rating,
    }
    BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHXEdjyoxL9F5bHFdyiVM3NGYCKwR5NQAC7hQAAuNVUEk4S4qtAhNhvC0E')
    BOT.send_message(message.chat.id, 'Спасибо за информацию')
    res = requests.post(f'{API}/set_info/', headers=headers, data=data)
    rating_info_to_sheets()
    message = Eduteam_info.info
    check_edu_kb(message)

def send_data_lates(message):
    if message.text.lower() == 'cancel':
        start(message)
    else:
        Lates.quantity_of_lates = message.text
        responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
        auth = responce.json().get('access')
        headers = {'Authorization':f'Bearer {auth}'}
        data = {'departments': 'eduteam_lates',
        'quantity_of_lates':Lates.quantity_of_lates,
        }
        BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHXEdjyoxL9F5bHFdyiVM3NGYCKwR5NQAC7hQAAuNVUEk4S4qtAhNhvC0E')
        BOT.send_message(message.chat.id, 'Спасибо за информацию', reply_markup=cancel)
        res = requests.post(f'{API}/set_info/', headers=headers, data=data)
        lates_info_to_sheets()
        start(message)



###########################################################################################
#------------------НИЖЕ ПРОВЕРКА И ОТПРАВКА ДАННЫХ SALES----------------------------------#
def number_quantity_today(message):
    if message.text.lower() == 'cancel':
        start(message)
    else:
        FormForSales.number_quantity = message.text
        quantity_signup = BOT.send_message(message.chat.id,'Количество записей по факту:')
        BOT.register_next_step_handler(quantity_signup, quantity_signup_today)

def quantity_signup_today(message):
    FormForSales.quantity_signup = message.text
    quantity_payment = BOT.send_message(message.chat.id, 'Количество оплат по факту:')
    BOT.register_next_step_handler(quantity_payment, quantity_payment_today)

def quantity_payment_today(message):
    FormForSales.quantity_payment = message.text
    deadline = BOT.send_message(message.chat.id, 'Сколько дней осталось до запуска:')
    BOT.register_next_step_handler(deadline, before_the_deadline)

def before_the_deadline(message):
    FormForSales.deadline = message.text
    quantity_old_dialogues = BOT.send_message(message.chat.id, 'Количество старых диалогов:')
    BOT.register_next_step_handler(quantity_old_dialogues, quantity_old_dialogues_all)

def quantity_old_dialogues_all(message):
    FormForSales.quantity_old_dialogues = message.text
    quantity_new_dialogues = BOT.send_message(message.chat.id, 'Количество новых диалогов:')
    BOT.register_next_step_handler(quantity_new_dialogues, quantity_new_dialogues_all)

def quantity_new_dialogues_all(message):
    FormForSales.quantity_new_dialogues = message.text
    quantity_of_entries_to_trial_lesson = BOT.send_message(message.chat.id, 'Количество записей на пробный урок:')
    BOT.register_next_step_handler(quantity_of_entries_to_trial_lesson,quantity_of_entries_to_trial_lesson_all )

def quantity_of_entries_to_trial_lesson_all(message):
    FormForSales.quantity_of_entries_to_trial_lesson = message.text
    quantity_comes_to_trial_lesson = BOT.send_message(message.chat.id, 'Количество пришедших на пробный:')
    BOT.register_next_step_handler(quantity_comes_to_trial_lesson, quantity_comes_to_trial_lesson_today)

def quantity_comes_to_trial_lesson_today(message):
    FormForSales.quantity_comes_to_trial_lesson = message.text
    quantity_of_calls_made_per_day = BOT.send_message(message.chat.id, 'Количество звонков, сделанные за день:')
    BOT.register_next_step_handler(quantity_of_calls_made_per_day, send_data_sales)


def send_data_sales(message):
    
    FormForSales.quantity_of_calls_made_per_day = message.text
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    data = {
        'departments': FormForSales.departments,
        'number_quantity' : FormForSales.number_quantity,
        'quantity_signup' : FormForSales.quantity_signup,
        'quantity_payment' : FormForSales.quantity_payment,
        'deadline' : FormForSales.deadline,
        'quantity_old_dialogues' : FormForSales.quantity_old_dialogues,
        'quantity_new_dialogues' : FormForSales.quantity_new_dialogues,
        'quantity_of_entries_to_trial_lesson' : FormForSales.quantity_of_entries_to_trial_lesson,
        'quantity_comes_to_trial_lesson' : FormForSales.quantity_comes_to_trial_lesson,
        'quantity_of_calls_made_per_day' : FormForSales.quantity_of_calls_made_per_day,
    }
    BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHXEdjyoxL9F5bHFdyiVM3NGYCKwR5NQAC7hQAAuNVUEk4S4qtAhNhvC0E')
    BOT.send_message(message.chat.id, 'Спасибо за информацию', reply_markup=cancel)
    sales_info_to_sheets()
    res = requests.post(f'{API}/set_info/', headers=headers, data=data)
    
    start(message)

    
###########################################################################################
#--------------------НИЖЕ ПРОВЕРКА И ОТПРАВКА ДАННЫХ КУРАТОРОВ----------------------------#
@BOT.message_handler(content_types=['text'])
def choose_day_or_ev(message):

    data = {
				'day_or_ev':message.text.lower(),
				'username':'bot'
			}
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    if message.text.lower() == 'day':
        
        res = requests.get(f'{API}/group_day_and_ev/', headers=headers, data=data)

        day_group = sum(res.json().get('day_group'), [])
        
        FormForKurators.day_or_ev = message.text
        keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for i in day_group:
            
            button  = types.KeyboardButton(str(i))
            keyboard2.add(button)
        group = BOT.send_message(message.chat.id, 'GROUP:', reply_markup=keyboard2)
        BOT.register_next_step_handler(group, quantity_of_students)
        
    elif message.text.lower() == 'evening':
        res = requests.get(f'{API}/group_day_and_ev/', headers=headers, data=data)
        ev_group = sum(res.json().get('ev_group'), [])
        FormForKurators.day_or_ev = message.text
        keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        for i in ev_group:
            button  = types.KeyboardButton(str(i))
            keyboard2.add(button)
        group = BOT.send_message(message.chat.id, 'GROUP:', reply_markup=keyboard2)
        BOT.register_next_step_handler(group, quantity_of_students)
    else:
        start(message)

def quantity_of_students(message):
    FormForKurators.group = message.text
    message2 = BOT.send_message(message.chat.id, 'Количество студентов в группе:')
    BOT.register_next_step_handler(message2, comes_quantity_group)

def comes_quantity_group(message):
    FormForKurators.quantity_of_students = message.text
    message2 = BOT.send_message(message.chat.id, 'Количество посещений в группе:')
    BOT.register_next_step_handler(message2, late_quantity_group)

def late_quantity_group(message):
    message2 = BOT.send_message(message.chat.id, 'Количество опозданий в группе:')
    FormForKurators.comes_quantity = message.text
    BOT.register_next_step_handler(message2, gone_away_from_group)

def gone_away_from_group(message):
    FormForKurators.lates_quantity = message.text
    gone_away = BOT.send_message(message.chat.id, 'Количество сливов в группе')
    BOT.register_next_step_handler(gone_away, send_data_kurators)



def send_data_kurators(message):
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    
    
    FormForKurators.gone_away = message.text
    data = {
        'departments': 'куратор',
        'day_or_ev' : FormForKurators.day_or_ev,
        'group' : FormForKurators.group,
        'quantity_of_students': FormForKurators.quantity_of_students,
        'comes_quantity' : FormForKurators.comes_quantity,
        'lates_quantity' : FormForKurators.lates_quantity,
        'gone_away' : FormForKurators.gone_away,
    }
    BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHXEdjyoxL9F5bHFdyiVM3NGYCKwR5NQAC7hQAAuNVUEk4S4qtAhNhvC0E')
    BOT.send_message(message.chat.id, 'Спасибо за информацию')
    res = requests.post(f'{API}/set_info/', headers=headers, data=data)
    curators_info_to_sheets()
    message = Info.info_kb
    check_kb(message)

####################################################################################


def department_choise(message):
    if message.text.lower() == 'sales':
        BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHxwtj7w6Ql2Fj01jQBXTuyJ-0WcraFAACYhUAAiKjwUn70vs57W5Ifi4E')
        responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
        auth = responce.json().get('access')
        headers = {'Authorization':f'Bearer {auth}'}
        data1 = {
				'departments':message.text.lower(),
				'username':'bot'
			}
        res = requests.get(f'{API}/get_info/', headers=headers, data=data1)
        if res.status_code > 400:
            BOT.send_message(message.chat.id, 'сооори')
            return
        try:
            result = (res.json()[0])
        
            BOT.send_message(message.chat.id, text=f'''DATE:   {result.get('create_at')}
Количество номеров:   {result.get('number_quantity')}
Количество звонко, сделанные за день:   {result.get('quantity_of_calls_made_per_day')}
Количество записей по факту:   {result.get('quantity_signup')}
Количество оплат по факту:   {result.get('quantity_payment')}
Сколько дней осталось до запуска:   {result.get('deadline')}
Количество старых диалогов:   {result.get('quantity_old_dialogues')}
Количество новых диалогов:   {result.get('quantity_new_dialogues')}
Количество записей на пробный урок:   {result.get('quantity_of_entries_to_trial_lesson')}
Количество записей на пробный урок:   {result.get('quantity_of_entries_to_trial_lesson')}
Количество пришедших на пробный:   {result.get('quantity_comes_to_trial_lesson')}
''')
            message = Info.info_kb
            check_kb(message)
        except (requests.exceptions.JSONDecodeError, IndexError):
            BOT.send_message(message.chat.id, 'Сегодня не вводили данные')
            message = Info.info_kb
            check_kb(message)

    elif message.text.lower() == 'куратор':
        
        message2 = BOT.send_message(message.chat.id, 'какую инфу желаете получить?',reply_markup=curator_info_kb )
        BOT.register_next_step_handler(message2, get_info_curators)
    elif message.text.lower() == 'eduteam':
        message2 = BOT.send_message(message.chat.id, 'какую инфу желаете получить?', reply_markup=eduteam_kb)
        BOT.register_next_step_handler(message2, get_info_eduteam)
    else:
        start(message)

        

def get_info_eduteam(message):
    info = message.text
    BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHxwtj7w6Ql2Fj01jQBXTuyJ-0WcraFAACYhUAAiKjwUn70vs57W5Ifi4E')
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    data1 = {
				'departments':'eduteam',
				'username':'bot',
                'info':info,
			}
    res = requests.get(f'{API}/get_info/', headers=headers, data=data1)
    
    
    if info == 'рейтинг':
        res = res.json()
        try:
            for i in range(len(res)):
                result = (res[i])
                
            
                BOT.send_message(message.chat.id, text=f'''DATE:   {result.get('create_at')}
Позиция:  {result.get('position')}
Имя сотрудника:  {result.get('staff_choise')}
Рейтинг:   {result.get('weekly_rating')}
''')
            message = Info.info_kb
            check_kb(message)
        except(requests.exceptions.JSONDecodeError, IndexError):
            BOT.send_message(message.chat.id, 'Сегодня не вводили данные')
            message = Info.info_kb
            check_kb(message)
    elif info == 'опоздание':
        res = res.json()
        try:
            for i in range(len(res)):
                result = (res[i])
                
            
                BOT.send_message(message.chat.id, text=f'''DATE:   {result.get('create_at')}
Опоздавшие : {result.get('quantity_of_lates')}
''')        
            message = Info.info_kb
            check_kb(message)
        except(requests.exceptions.JSONDecodeError, IndexError):
            BOT.send_message(message.chat.id, 'Сегодня не вводили данные')
            message = Info.info_kb
            check_kb(message)
    else:
        start(message)


def get_info_curators(message):
    BOT.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHxwtj7w6Ql2Fj01jQBXTuyJ-0WcraFAACYhUAAiKjwUn70vs57W5Ifi4E')
   
    if message.text.lower() =='cancel':
        start(message)
    
    elif message.text.lower() == 'по группам':
        responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
        auth = responce.json().get('access')
        headers = {'Authorization':f'Bearer {auth}'}
        data1 = {
				'departments':'куратор',
				'username':'bot'
			}
        res = requests.get(f'{API}/get_info/', headers=headers, data=data1)
        try:
            for i in range(len(res.json())):
                result = (res.json()[i])
            
                BOT.send_message(message.chat.id, text=f'''DATE:   {result.get('create_at')}
Группа : {result.get('group')}
Количество студентов в группе: {result.get('quantity_of_students')}
Количество посещений в группе:   {result.get('comes_quantity')}
Количество опозданий в группе:   {result.get('lates_quantity')}
Количество сливов в группе:   {result.get('gone_away')}
''')
            message = Info.info_kb
            check_kb(message)

        except(requests.exceptions.JSONDecodeError, IndexError):
            BOT.send_message(message.chat.id, 'Сегодня не вводили данные')
            message = Info.info_kb
            check_kb(message)

    elif message.text.lower() == 'общая информация':
        count_of_students(message)


def count_of_students(message):
    responce = requests.post(f'{API}/login/',{'username':'bot', 'password':'12345678asdfghjk'})
    auth = responce.json().get('access')
    headers = {'Authorization':f'Bearer {auth}'}
    data1 = {
				'departments':'куратор',
				'username':'bot'
			}
    res = requests.get(f'{API}/get_info/', headers=headers, data=data1)
    try:
        quantity_of_students = 0
        quantity_of_late = 0
        quantity_of_come = 0
        for i in range(len(res.json())):
            result = (res.json()[i])
            quantity_of_students += result.get('quantity_of_students')
            quantity_of_late +=result.get('lates_quantity')
            quantity_of_come +=result.get('comes_quantity')
        BOT.send_message(message.chat.id, text=f'''Общее количество студентов в группах: {quantity_of_students}
Общее количество посещений: {quantity_of_come}
Общее количество опозданий: {quantity_of_late}
        ''')
        message = Info.info_kb
        check_kb(message)

    except(requests.exceptions.JSONDecodeError):
        BOT.send_message(message.chat.id, text='Сегодня не вводили данные')
        message = Info.info_kb
        check_kb(message)


#####################################################################################
def curators_info_to_sheets():
    GoogleURL = config('CURATORS_URL')

    urlResponse = GoogleURL+'/formResponse'
    urlReferer = GoogleURL+'/viewform'

    form_data = {
        'entry.960500620': FormForKurators.day_or_ev,
        'entry.1829161847': FormForKurators.group,
        'entry.150974716': FormForKurators.quantity_of_students,
        'entry.286887983' : FormForKurators.comes_quantity,
        'entry.619172007' : FormForKurators.lates_quantity,
        'entry.387536842' : FormForKurators.gone_away
             
                       }
    user_agent = {'Referer':urlReferer,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = requests.post(urlResponse, data=form_data, headers=user_agent) 


def sales_info_to_sheets():
    GoogleURL = config('SALES_URL')

    urlResponse = GoogleURL+'/formResponse'
    urlReferer = GoogleURL+'/viewform'

    form_data = {'entry.1517062231': FormForSales.deadline,
             'entry.1137459076': FormForSales.number_quantity,
             'entry.796396701' : FormForSales.quantity_signup,
             'entry.257639982' : FormForSales.quantity_payment,
             'entry.21934598' : FormForSales.quantity_old_dialogues,
             'entry.1318496928' : FormForSales.quantity_new_dialogues,
             'entry.2014728782' : FormForSales.quantity_of_calls_made_per_day,
             'entry.1674020269' : FormForSales.quantity_of_entries_to_trial_lesson, 
             'entry.561366031' : FormForSales.quantity_comes_to_trial_lesson,
                       }
    user_agent = {'Referer':urlReferer,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = requests.post(urlResponse, data=form_data, headers=user_agent) 

def rating_info_to_sheets():
    GoogleURL = config('RATING_URL')

    urlResponse = GoogleURL+'/formResponse'
    urlReferer = GoogleURL+'/viewform'

    form_data = {
            'entry.1166912595' : Ratings.position,
            'entry.565028048' : Ratings.staff_choise,
            'entry.1246600929' : Ratings.weekly_rating,
               }
    user_agent = {'Referer':urlReferer,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = requests.post(urlResponse, data=form_data, headers=user_agent) 

def lates_info_to_sheets():
    GoogleURL = config('LATES_URL')

    urlResponse = GoogleURL+'/formResponse'
    urlReferer = GoogleURL+'/viewform'

    form_data = {
        'entry.588093668': Lates.quantity_of_lates,     
                }
    user_agent = {'Referer':urlReferer,'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36"}
    r = requests.post(urlResponse, data=form_data, headers=user_agent) 







BOT.polling(none_stop=True)



