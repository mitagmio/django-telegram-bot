from ast import Pass, Str
from ctypes import Union
import datetime
from email.policy import default
import time
from turtle import update

from django.utils import timezone
from telegram import Bot, ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text, static_state
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User, Cities, Pairs, Periods, Terms, Order, Suggestion, P2p, MerchantsCities
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.tasks import broadcast_message
from dtb.settings import BINANCE_API, BINANCE_SECRET

# Начало диалога
def command_start(update: Update, context: CallbackContext):
	u, _ = User.get_user_and_created(update, context)
	state = u.state
	message = get_message_bot(update)
	print(state)
	if state == static_state.S_ACCEPTED_ORDER:
		cmd_accepted_order_show(update, context)
		return
	if state == static_state.S_ACCEPTED_EXCHANGE:
		cmd_accepted_exchange_show(update, context)
		return
	del_mes(update, context, True)
	text = "\n"
	if check_username(update, context, text): # Если пользователь без username мы предлагаем ему заполнить свой профиль.
		btn_menu = InlineKeyboardButton(text='📋 Меню', callback_data='Меню')
		markup = InlineKeyboardMarkup([
      			[btn_menu]
         ])
		#print(bot.get_chat_member(352482305))
		id = context.bot.send_message(message.chat.id, static_text.START_USER.format(text, message.chat.id), reply_markup=markup, parse_mode="HTML") #отправляет приветствие и кнопку
		User.set_message_id(update, context, id.message_id)

    # if created:
    #     text = static_text.start_created.format(first_name=u.first_name)
    # else:
    #     text = static_text.start_not_created.format(first_name=u.first_name)

    # update.message.reply_text(text=text, reply_markup=make_keyboard_for_start_command())

## Принимаем любой текст и проверяем состояние пользователя
def message_handler_func(update: Update, context: CallbackContext):
    state = User.get_user_state(update, context)
    if state in State_Dict:
        func_menu = State_Dict[state]
        func_menu(update, context)
    elif update.message.text in Menu_Dict: #button_message проверяем текст на соответствие любой кнопке
        func_menu = Menu_Dict[update.message.text]
        func_menu(update, context)
    else:
        del_mes(update, context)

def callback_inline(update: Update, context: CallbackContext):
	# Если сообщение из чата с ботом
	# print('callback_inline', update)
	call_list = ['Город', 'Пара', 'Период', 'ТИП_Пары', 'Город_обменника',
              'Предложить', 'Выбираю_предложение','Клиент_подтвердил_сделку','Клиент_отменил_сделку'
    ]
	call = update.callback_query
	if call.message:
		call_func = call.data.split(' ')
		# print(call_func)
		if len(call_func) > 1:
			if call_func[0] in call_list:
					func_menu = Menu_Dict[call_func[0]]
					func_menu(update, context, call_func[1])	
		else:		
			func_menu = Menu_Dict[call.data]
			func_menu(update, context)
	# Если сообщение из инлайн-режима
	#elif call.inline_message_id:
	#	func_menu = Menu_Dict[call.data]
	#	func_menu(call, context)

# Удаляем записи для отображения только одной
def del_mes(update: Update, context: CallbackContext, bot_msg: bool=False): #функция удаляющая предыдущие сообщения бота (делает эффект обновления меню при нажатии кнопки) и человека по States.S_MENU(всегда, если его статус=1)
	message = get_message_bot(update)
	try:
		context.bot.delete_message(message.chat.id, message.message_id)
	except:
		pass
	if bot_msg:
		# time.sleep(0.1)
		try:
			context.bot.delete_message(message.chat.id, int(message.message_id)-1)
		except:
			pass
		# time.sleep(0.1)
		try:
			context.bot.delete_message(message.chat.id, int(message.message_id)-2)
		except:
			pass
		# time.sleep(0.1)
		try:
			context.bot.delete_message(message.chat.id, int(message.message_id)-3)
		except:
			pass
		# time.sleep(0.1)
		try:
			context.bot.delete_message(message.chat.id, int(message.message_id)-4)
		except:
			pass
		# time.sleep(0.1)
		try:
			context.bot.delete_message(message.chat.id, int(message.message_id)-5)
		except:
			pass
		# time.sleep(0.1)
		try:
			context.bot.delete_message(message.chat.id, int(message.message_id)-6)
		except:
			pass

# Распаковываем message
def get_message_bot(update):
	if hasattr(update, 'message') and update.message != None:
		message = update.message
	if hasattr(update, 'callback_query') and update.callback_query != None:
		message = update.callback_query.message
	return message

# Проверяем является ли float
def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

#Проверка на username
def check_username(update: Update, context: CallbackContext, text = '\n'):
	message = get_message_bot(update)
	if not hasattr(message.chat, 'username') or message.chat.username == '' or message.chat.username == None:
		btn_menu = InlineKeyboardButton(text='🎉 Старт', callback_data='Старт')
		markup = InlineKeyboardMarkup([
				[btn_menu]
		])
		id = context.bot.send_message(message.chat.id, static_text.NOT_USER_NAME.format(text, message.chat.id), reply_markup=markup) #отправляет приветствие и кнопку
		User.set_message_id(update, context, id.message_id)
		return False
	return True

# Меню
def cmd_menu(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	if check_username(update, context):
		message = get_message_bot(update)
		User.set_user_state(update, context, static_state.S_MENU)# помечаем состояние пользователя.
		buttons = []
		btn_help = InlineKeyboardButton(text='🆘 Помощь', callback_data='Help')
		btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Старт')
		btn_main = InlineKeyboardButton(text='⏮ В начало', callback_data='Старт')
		btn_client = InlineKeyboardButton(text='🧍‍♂️ Заказать наличку', callback_data='Меню_Клиент')
		btn_shop = InlineKeyboardButton(text='💸 Я Обменник', callback_data='Обменник')
		buttons.append([btn_client, btn_shop])
		u = User.get_user(update, context)
		if u.is_admin:
			btn_admin = InlineKeyboardButton(text='📝 Администрирование', callback_data="Администрирование")
			buttons.append([btn_admin])
		buttons.append([btn_help])
		buttons.append([btn_main, btn_back])
		markup = InlineKeyboardMarkup(buttons)
		id = context.bot.send_message(message.chat.id, "Выбери свою роль для проведения сделки:", reply_markup=markup, parse_mode="HTML")
		User.set_message_id(update, context, id.message_id)

# Меню клиента ## user_story
def start_client(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	u = User.get_user(update, context)
	if check_username(update, context):
		if u.orders_client == 'None':
			cmd_client(update, context)
			return
		message = get_message_bot(update)
		User.set_user_state(update, context, static_state.S_MENU)# помечаем состояние пользователя.
		buttons = []
		btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню')
		btn_client = InlineKeyboardButton(text='💸 Новый заказ', callback_data='Клиент')
		btn_shop = InlineKeyboardButton(text='📝 Мои заказы', callback_data='Заказы_Клиент')
		buttons.append([btn_client, btn_shop])
		buttons.append([btn_back])
		markup = InlineKeyboardMarkup(buttons)
		id = context.bot.send_message(message.chat.id, "Выбери нужный пункт:", reply_markup=markup, parse_mode="HTML")
		User.set_message_id(update, context, id.message_id)

# новый заказ "Клиент" - Город
def cmd_client(update: Update, context: CallbackContext):
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_orders_client(update, context, "yes")	
	User.set_user_state(update, context, static_state.S_MENU)# помечаем состояние пользователя.
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')
	cities = Cities.get_obj()
	if len(cities)>= 1: # Проверяем есть ли в списке города
		count = 0
		for element in cities: # перебираем весь список если четное количество, то пишем по 2 в ряд.
			count += 1
			merchants_id = list(MerchantsCities.objects.filter(city_id=element['id']).values_list('merchant_id', flat=True))
			merchants = len(list(User.objects.filter(user_id__in=merchants_id, merchant_status='online')))
			if len(cities) == count and len(cities) % 2 != 0: # если последний элемент не четный помещаем в одну строку
				city = InlineKeyboardButton(element['ru_name']+'    '+str(merchants), callback_data='Город '+element['ru_name'])
				buttons.append([city])
				break
			if count % 2!= 0:
				city_a = InlineKeyboardButton(element['ru_name']+'    '+str(merchants), callback_data='Город '+element['ru_name']) 
			else:
				city_b = InlineKeyboardButton(element['ru_name']+'    '+str(merchants), callback_data='Город '+element['ru_name']) 	
				buttons.append([city_a, city_b])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "<b>Рядом с городом отображается число обменников онлайн, которые получат Вашу заявку и смогут предложить лучшую сделку.\n\nВЫБЕРИ ГОРОД, В КОТОРОМ ХОЧЕШЬ ПРОИЗВЕСТИ ОБМЕН:</b>", reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Выбран город и выводим меню выбора пары обмена
# Сюда попадаем через колбек с передачей параметра город
# Выбираем направление обмена, тип пары
def cmd_type_pair(update: Update, context: CallbackContext, city: Str = 'None'):
	message = get_message_bot(update)
	if city == 'None':
		cmd_client(update, context)
		return
	del_mes(update, context, True)
	User.set_city(update, context, city) #записываем город в словарь пользователя, потом заберем и очистим поле.
	User.set_user_state(update, context, static_state.S_MENU)# помечаем состояние пользователя.
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')
	pair_a = InlineKeyboardButton('🇺🇸 USD (наличка)', callback_data='ТИП_Пары '+'USD')
	pair_b = InlineKeyboardButton('🇱🇰 LKR (наличка)', callback_data='ТИП_Пары '+'LKR')
	buttons.append([pair_a, pair_b])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Черновик заказа на обмен\n\nВыбран город <code>{}</code>\n\n<b>ВЫБЕРИ ВАЛЮТУ ДЛЯ ПОЛУЧЕНИЯ:</b>\n\n".format(city), reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Выбран тип пары
# Сюда попадаем через колбек с передачей параметра тип пары
# Выбираем направление обмена
def user_type_pair(update: Update, context: CallbackContext, type_pair: Str = 'None'):
	u, _ = User.get_user_and_created(update, context)
	message = get_message_bot(update)
	if type_pair == 'None':
		cmd_type_pair(update, context, u.city)
		return 
	del_mes(update, context, True)
	User.set_type_pair(update, context, type_pair) #записываем город в словарь пользователя, потом заберем и очистим поле.
	User.set_user_state(update, context, static_state.S_MENU)# помечаем состояние пользователя.
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')
	pairs = Pairs.get_obj()
	if len(pairs)>= 1: # Проверяем есть ли в списке города
		for element in pairs: # перебираем весь список если четное количество, то пишем по 2 в ряд.
			if element['pair'].split('/')[1] == type_pair:
				pair = InlineKeyboardButton(element['ru_pair'], callback_data='Пара '+element['pair'])
				buttons.append([pair])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Черновик заказа на обмен\n\nВыбран город <code>{}</code>\n\n<b>ВЫБЕРИ ПАРУ ДЛЯ ОБМЕНА:</b>\n\n".format(u.city), reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Выбрана пара и выводим вопрос сколько денег хочет обменять на Рупии в выбранной паре.
# Сюда попадаем через колбек с передачей параметра пара
def cmd_pair(update: Update, context: CallbackContext, pair: Str = 'None'):
	message = get_message_bot(update)	
	if pair == None:
		return user_type_pair(update, context, u.type_pair)
	del_mes(update, context, True)
	User.set_pair(update, context, pair) #записываем пару в словарь пользователя, потом заберем и очистим поле.
	User.set_user_state(update, context, static_state.S_ENTERED_PAIR)# помечаем состояние пользователя.
	u, _ = User.get_user_and_created(update, context)
	pair = Pairs.get_dict()[u.pair]
	city = u.city
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Черновик заказа на обмен\n\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\n\n<b>ВВЕДИТЕ СУММУ ЦИФРОЙ ДЛЯ ОБМЕНА:</b>\n\n".format(city, pair), reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Уточняем период сделки после ввода суммы
# в хендлер попадаем сравнивая состояние пользователя
def cmd_periods(update: Update, context: CallbackContext, summ: float = 0.0):
	u, _ = User.get_user_and_created(update, context)
	message = get_message_bot(update)
	if summ == 0.0:
		summ = message.text
	if isfloat(summ):
		del_mes(update, context, True)
		User.set_user_state(update, context, static_state.S_MENU)
		User.set_summ(update, context, summ)
		city = u.city
		pair = Pairs.get_dict()[u.pair]
		buttons = []
		btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Клиент')
		periods = Periods.get_obj()
		for element in periods:
			period = InlineKeyboardButton('⏳ '+element['ru_period'], callback_data='Период '+element['period'])
			buttons.append([period])
		buttons.append([btn_back])
		markup = InlineKeyboardMarkup(buttons)
		id = context.bot.send_message(message.chat.id, "Черновик заказа на обмен\n\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма <code>{}</code> {}\n\n<b>КАК БЫСТРО ВАМ НУЖЕН КЭШ?</b> ⏳".format(city, pair, summ, pair.split(' =>  ')[0]), reply_markup=markup, parse_mode="HTML")
		User.set_message_id(update, context, id.message_id)
	else:
		pair = u.pair
		cmd_pair(update, context, pair)

# Выбран период и выводим вопрос подтверждения заказа на обмен.
# Сюда попадаем через колбек с передачей параметра период
def cmd_accept_order(update: Update, context: CallbackContext, period: str = 'None'):
	u, _ = User.get_user_and_created(update, context)
	message = get_message_bot(update)
	if period == 'None':
		return cmd_periods(update, context, u.summ)
	del_mes(update, context, True)
	User.set_period(update, context, period) #записываем период в словарь пользователя, потом заберем и очистим поле.
	User.set_user_state(update, context, static_state.S_MENU)
	period = Periods.get_dict()[period]
	city = u.city
	pair = Pairs.get_dict()[u.pair]
	summ = u.summ
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Клиент')
	btn_yes = InlineKeyboardButton(text='✅ Все верно', callback_data='Заявка_подтверждена')
	btn_no = InlineKeyboardButton(text='❌ Нет', callback_data='Заявка_отклонена')
	buttons.append([btn_yes, btn_no])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Черновик заказа на обмен\n\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма <code>{}</code> {}\nКэш нужен <code>{}</code>\n\n<b>ПОДТВЕРДИТЕ ЗАЯВКУ НА ОБМЕН, ВСЕ ВЕРНО?</b>".format(city, pair, summ, pair.split(' =>  ')[0], period), reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)


def cmd_accepted_order_show(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	city = u.city
	pair = Pairs.get_dict()[u.pair]
	summ = u.summ
	period = Periods.get_dict()[u.period]
	id = context.bot.send_message(message.chat.id, "<b>ВАШ ЗАКАЗ\n\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>\n\n<b>Пожалуйста ожидайте один час, за это время обменники сделают свои предложения по вашему заказу.</b>".format(city, pair, pair.split('/')[0], summ, period), parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# клиент подтвердил заказ на обмен
def cmd_accepted_order(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	city = u.city
	pair = Pairs.get_dict()[u.pair]
	summ = u.summ
	period = Periods.get_dict()[u.period]
	timestamp = int(datetime.datetime.today().timestamp())
	timestamp_execut = timestamp + (60*60*1)
	date_time_execut = datetime.datetime.fromtimestamp(timestamp_execut  + (60*60*5.5))
	p2p_last = P2p.objects.latest('timestamp').__dict__
	p2p_last['usdt'] = 1
	pair_dict = Pairs.get_convert_dict()
	exchange_rate = p2p_last[pair_dict[u.pair]]
	order_fee = round ((float(summ) / float(exchange_rate)) * float(Terms.get_dict()['size_fee']), 2)
	o, created = Order.objects.update_or_create(timestamp_execut=timestamp_execut, defaults={
		'client_id' 		: u,
		'city' 	  			: u.city,
		'pair' 	  			: u.pair,
		'summ'				: u.summ,
		'period' 	  		: u.period,
		'date_time_execut'	: date_time_execut,
		'order_fee' 		: order_fee,
		'status' 	  		: 'active'
	})
	if created:
		s = Cities.objects.get(ru_name=u.city)
		user_ids = list(s.city_merchant_ids_set.all().values_list('merchant_id', flat=True)) # Список мерчантов представленных в городе
		ids = list(User.objects.filter(user_id__in=user_ids, merchant_status='online').values_list('user_id', flat=True)) # Проверяем статус мерчантов = 'online'
		bts = [
			[{ 'text':'💵 Сделать предложение', 'callback_data':'Предложить '+ str(o.id) }],
			[{ 'text':'🪁 Пропустить', 'callback_data':'Удалить' }]
		]
		percent = round(u.count_client_order_success / u.count_client_order * 100, 2)
		# send in async mode via celery
		broadcast_message.delay(
			user_ids=ids,
			text="<b>НОВЫЙ ОРДЕР\nУспешно выполнено \\ всего заявок: <code>{} \\ {}   {}%</code>\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code>\n\n Комиссия за сделку <code>{}</code> USDT</b>".format(u.count_client_order_success, u.count_client_order, percent, city, pair, pair.split('/')[0], summ, period, order_fee),
			entities=update.callback_query.message.to_dict().get('entities'),
			reply_markup=bts
		)
		User.set_user_state(update, context, static_state.S_ACCEPTED_ORDER)
		id = context.bot.send_message(message.chat.id, "<b>АКТИВНЫЙ ОРДЕР\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>\n\nВ течении часа мы соберем все предложения от всех обменников, работающих в вашем городе и предоставим вам информацию о их тарифах и предложениях, ожидайте.".format(city, pair, pair.split('/')[0], summ, period), parse_mode="HTML")
		User.set_message_id(update, context, id.message_id)
		return
	cmd_accept_order(update, context, u.period)	



# клиент отменил заказ на обмен
def cmd_canceled_order(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	u.city = 'None'
	u.type_pair = 'None'
	u.pair = 'None'
	u.summ = 0.0
	u.period = 'None'
	u.save()
	start_client(update, context)
	# u = User.get_user(update, context)
	# u.city = 'None'
	# u.type_pair = 'None'
	# u.pair = 'None'
	# u.summ = 0.0
	# u.period = 'None'
	# u.save()

# заказы клиента
def client_orders(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	for i in u.client_id_order_set.filter(status__in=['exchanged_succesfull', 'exchange']).order_by('timestamp_execut').reverse()[:5]:
		pair = Pairs.get_dict()[i.pair]
		period = Periods.get_dict()[i.period]
		time.sleep(0.2)
		context.bot.send_message(message.chat.id, "<b>ОРДЕР {}\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code> \n СТАТУС {}</b>\n\n".format(i.merchant_executor_id, i.city, pair, pair.split(' =>  ')[0], i.summ, period, i.status), parse_mode="HTML")
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Отображаем последние 5 выполненных заказов", reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# подтвердить и выбрать исполнителя
def cmd_accepted_merchant_executer(update: Update, context: CallbackContext, orderid_merchantid: str):
	orderid_merchantid = orderid_merchantid.split('_')
	orderid = orderid_merchantid[0]
	merchantid = orderid_merchantid[1]
	m =  User.objects.get(user_id=merchantid)
	message = get_message_bot(update)
	u = User.get_user(update, context)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_ACCEPTED_EXCHANGE)
	o = Order.objects.get(id=orderid)
	o.merchant_executor_id = m
	o.status = 'exchange'
	o.save()
	m = User.objects.get(user_id=merchantid)
	pair = Pairs.get_dict()[o.pair]
	period = Periods.get_dict()[o.period]
	s = Suggestion.objects.get(order_id=orderid, merchant_executor_id=merchantid)
	text = "<b>Выбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>".format(o.city, pair, pair.split(' =>  ')[0], o.summ, period)
	text_fee = "\n\nКомиссия за сделку <i><b>{} USDT</b></i>".format(o.order_fee)
	pay_summ = "{} {}".format(s.summ, pair.split(' =>  ')[1])
	id = context.bot.send_message(message.chat.id, "<b>АКТИВНЫЙ ОРДЕР</b>\n\n"+text+"\nВАМ ЗАПЛАТЯТ "+pay_summ+"\n\n<b>СВЯЖИТЕСЬ С ОБМЕННИКОМ {}, ДОГОВОРИТЕСЬ О ДЕТАЛЯХ ВАШЕЙ ВСТРЕЧИ</b>".format(m), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='✅ Сделка состоялась', callback_data='Клиент_подтвердил_сделку '+orderid)],[InlineKeyboardButton(text='❌ Сделка не состоялась', callback_data='Клиент_отменил_сделку '+orderid)]]), parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)
	time.sleep(0.2)
	client_name = "Клиент {}\n".format(u)
	id_m = context.bot.send_message(merchantid, "КЛИЕНТ ВЫБРАЛ ВАШЕ ПРЕДЛОДЕНИЕ\n\n"+client_name+text+text_fee+"\nВЫ ЗАПЛАТИТЕ КЛИЕНТУ "+pay_summ, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')]]), parse_mode="HTML")
	m.message_id = id_m.message_id
	m.save()

def cmd_accepted_exchange_show(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	o = u.client_id_order_set.get(status='exchange')
	m = o.merchant_executor_id
	pair = Pairs.get_dict()[o.pair]
	period = Periods.get_dict()[o.period]
	text = "<b>Выбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>".format(o.city, pair, pair.split(' =>  ')[0], o.summ, period)
	s = Suggestion.objects.get(order_id=o.id, merchant_executor_id=m.user_id)
	pay_summ = "{} {}".format(s.summ, pair.split(' =>  ')[1])
	id = context.bot.send_message(message.chat.id, "<b>АКТИВНЫЙ ОРДЕР</b>\n\n"+text+"\nВАМ ЗАПЛАТЯТ "+pay_summ+"\n\n<b>СВЯЖИТЕСЬ С ОБМЕННИКОМ {}, ДОГОВОРИТЕСЬ О ДЕТАЛЯХ ВАШЕЙ ВСТРЕЧИ</b>".format(m), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='✅ Сделка состоялась', callback_data='Клиент_подтвердил_сделку '+str(o.id))],[InlineKeyboardButton(text='❌ Сделка не состоялась', callback_data='Клиент_отменил_сделку '+str(o.id))]]), parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)


   
def cmd_finnaly_accepted_order(update: Update, context: CallbackContext, orderid: str):
	del_mes(update, context, True)
	message = get_message_bot(update)
	u = User.get_user(update, context)
	o = Order.objects.get(id=orderid)
	o.status = 'exchanged_succesfull'
	o.save()
	m = o.merchant_executor_id
	cmo = m.count_merchant_order
	m.count_merchant_order = cmo + 1
	cmos = m.count_merchant_order_success
	m.count_merchant_order_success = cmos + 1
	m.save()
	cuo = u.count_client_order
	u.count_client_order = cuo + 1
	cuos = u.count_client_order_success
	u.count_client_order_success = cuos + 1	
	id = context.bot.send_message(message.chat.id, "Поздравляем с завершенным обменом!!!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')]]), parse_mode="HTML")
	u.message_id = id.message_id
	u.save()

def cmd_finnaly_rejected_order(update: Update, context: CallbackContext, orderid: str):
	del_mes(update, context, True)
	message = get_message_bot(update)
	u = User.get_user(update, context)
	o = Order.objects.get(id=orderid)
	o.status = 'exchanged_rejected'
	o.save()
	m = o.merchant_executor_id
	cmo = m.count_merchant_order
	m.count_merchant_order = cmo + 1
	m.save()
	cuo = u.count_client_order
	u.count_client_order = cuo + 1
	id = context.bot.send_message(message.chat.id, "Сделка не состоялась.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='⏪ Назад', callback_data='Меню_Клиент')]]), parse_mode="HTML")
	u.message_id = id.message_id
	u.save()

#####################################
#####################################
#####################################


# История обменника ## merchant_story
def cmd_merchant(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	if u.merchant_client != 'None' and  u.merchant_client != 'under_consideration':
		cmd_menu_merchant(update, context)
		return
	if u.merchant_client == 'under_consideration':
		merchant_terms_of_use_agreed(update, context)
		return
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню')
	btn_yes = InlineKeyboardButton(text='✅ Согласен', callback_data='Правила_согласованны')
	btn_no = InlineKeyboardButton(text='❌ Нет', callback_data='Меню')
	buttons.append([btn_yes, btn_no])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Мы рады приветствовать Вас в нашей программе по предоставлению заявок на обнал на острове Шри-Ланка. Пожалуйста, ознакомьтесь с условиями.\n\n{}\n\n<b>ВЫ СОГЛАСНЫ С УСЛОВИЯМИ?</b>".format(Terms.get_dict()['terms_of_use_merchant']), reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# подписываем пользовательское соглашение обменника
def merchant_terms_of_use_agreed(update: Update, context: CallbackContext):
	User.set_merchant_client(update, context, 'True') #under_consideration Поменять если хотим сделать блокировку.
	message = get_message_bot(update)
	u = User.get_user(update, context)
	if u.merchant_client == 'under_consideration':
		del_mes(update, context, True)
		text = 'Вы собираетесь стать обменником.\n\n!!! СВЯЖИТЕСЬ  С  @sri_seacher  ДЛЯ ПРОХОЖДЕНИЯ ПРОВЕРКИ ЛИЧНОСТИ !!!'
		buttons = []
		btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню')
		buttons.append([btn_back])
		markup = InlineKeyboardMarkup(buttons)
		id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
		User.set_message_id(update, context, id.message_id)
		return
	cmd_menu_merchant(update, context)

# получаем курсы из базы.
def merchant_course(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	message = get_message_bot(update)
	User.set_user_state(update, context, static_state.S_MENU)
	p2p_last = P2p.objects.latest('timestamp').__dict__
	text = '<b><i>Курсы валют обновляются раз в час с </i>P2P Binance<i>\nи служат для ориентира пользователей:</i></b>\n\n<code>{}</code> RUB/USDT  (Российский рубль)\nUSDT/ <code>{}</code> LKR  (Шри-ланкийская рупия)\n<code>{}</code> UAH/USDT  (Украинская Гривна)\n<code>{}</code> EUR/USDT    (Евро)\n<code>{}</code> USD/USDT    (Доллар)\n\n'.format(p2p_last['rub_tinkoff_usdt'], p2p_last['usdt_lkr'], p2p_last['uah_usdt'], p2p_last['eur_revolut_usdt'], p2p_last['usd_tinkoff_usdt'])
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)


# Меню обменника
def cmd_menu_merchant(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	if u.merchant_client == 'None':
		cmd_merchant(update, context)
		return
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню')
	btn_course = InlineKeyboardButton(text='📉📈 Текущий курс валют', callback_data='Курс_валют')
	btn_actual_orders_merchant = InlineKeyboardButton(text='📥 Актуальные заявки', callback_data='Актуальные_заявки')
	btn_orders = InlineKeyboardButton(text='📨 Мои заказы', callback_data='Заказы_Мерчант')
	btn_orders_suggestion = InlineKeyboardButton(text='🧧🧾 Мои предложения', callback_data='Мои_предложения')
	btn_orders_completed = InlineKeyboardButton(text='✅🧾 Выполненные заказы', callback_data='Выполненные_заказы')
	merchant_status = u.merchant_status
	if merchant_status == 'None' or merchant_status == 'pause':
		merchant_status_ru = '🛋 Статус: Пауза'
		callback = 'Смена_статуса'
	if merchant_status == 'online':
		merchant_status_ru = '♻️ Статус: Онлайн'
		callback = 'Смена_статуса'
	if merchant_status == 'dolg':
		merchant_status_ru = '‼️ Статус: Долг'
		callback = 'pass'
	btn_status = InlineKeyboardButton(text=merchant_status_ru, callback_data=callback)
	btn_settings = InlineKeyboardButton(text='⚙️ Управление', callback_data='Управление')
	buttons.append([btn_settings, btn_status])
	buttons.append([btn_course])
	buttons.append([btn_actual_orders_merchant])
	buttons.append([btn_orders])
	buttons.append([btn_orders_suggestion])
	buttons.append([btn_orders_completed])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "МЕНЮ ОБМЕННИКА:\n\n <b>♻️ Статус: Онлайн</b> - вы получаете новые заявки на обмен и можете делать свои предложения.\nКлиенты видят вас в списке городов.\n\n<b>🛋 Статус: Пауза</b> - Вы не получаете новых предложений, для пользователей вы не видны в городах.\n Но вы все еще можете взять активную заявку согласно своих городов присутствия.\n\n<b>‼️ Статус: Долг</b> - Вам необходимо погасить задолженность, свяжитесь с @sri_seacher", reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Меняем статус
def merchant_change_status(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	merchant_status = u.merchant_status
	if merchant_status == 'None' or merchant_status == 'pause':
		u.merchant_status = 'online'
	if merchant_status == 'online':
		u.merchant_status = 'pause'
	u.save()
	cmd_menu_merchant(update, context)

# Меню управления обменника.
def merchant_settings(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	message = get_message_bot(update)
	User.set_user_state(update, context, static_state.S_MENU)
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	btn_yes = InlineKeyboardButton(text='💵 Мои долги', callback_data='Мои_долги')
	btn_no = InlineKeyboardButton(text='🏘 Мои города', callback_data='Мои_города')
	buttons.append([btn_yes, btn_no])
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Управление обменника", reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Мои города
def merchant_cities(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	u = User.get_user(update, context)
	message = get_message_bot(update)
	User.set_user_state(update, context, static_state.S_MENU)
	merchant_city = [ k['city_id'] for k in list(u.merchant_id_cities_set.all().values('city_id')) ] # получаем id всех записей городов присутствия обменника
	merchant_cities = Cities.objects.filter(id__in=merchant_city) # Фильтруем список городов
	cities = Cities.objects.all().order_by('ru_name')
	cities_checked = { obj.ru_name : 'checked' for obj in merchant_cities } # Список отмеченных городов присутсвия 
	cities_unchecked = { obj.ru_name : 'unchecked' for obj in cities } # Все возможные города
	buttons = []
	cities_unchecked.update(cities_checked) # обновляем словарь городами присутсвия и получаем готовый словарь отмеченных и не отмеченных городов
	if len(cities_unchecked)>= 1: # Проверяем есть ли в списке города
		count = 0
		for k in cities_unchecked: # перебираем весь список
			if cities_unchecked[k] == 'checked':
				box = ' ✅'
			if cities_unchecked[k] == 'unchecked':
				box = ' ⏹'
			count += 1
			if len(cities_unchecked) == count and len(cities_unchecked) % 2 != 0: # если последний элемент не четный, то помещаем в одну строку
				city = InlineKeyboardButton(k + box, callback_data='Город_обменника '+k)
				buttons.append([city])
				break
			if count % 2!= 0: # если четное количество, то пишем по 2 в ряд
				city_a = InlineKeyboardButton(k + box, callback_data='Город_обменника '+k) 
			else:
				city_b = InlineKeyboardButton(k + box, callback_data='Город_обменника '+k) 	
				buttons.append([city_a, city_b])
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Отметь города в которых будешь производить объмен:", reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# помечаем город на который нажал пользователь
def change_merchat_city(update: Update, context: CallbackContext, city_merchant: str):
	u = User.get_user(update, context)
	c = Cities.objects.get(ru_name=city_merchant)
	try:
		check_city = MerchantsCities.objects.get(merchant_id=u, city_id=c)
		check_city.delete()
	except:
		MerchantsCities.objects.create(merchant_id=u, city_id=c)		
	merchant_cities(update, context)


# Актуальные заявки
def actual_orders(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	cities_id = list(u.merchant_id_cities_set.all().values_list('city_id_id', flat=True))
	cities = list(Cities.objects.filter(id__in=cities_id).values_list('ru_name', flat=True))
	suggestions = list(u.merchant_executor_id_suggestion_set.all().values_list('order_id', flat=True))
	orders = Order.objects.filter(city__in=cities, status__in=['active', 'mailing'], timestamp_execut__gte=time.time()).exclude(id__in=suggestions).order_by('timestamp_execut')[:5]
	text = 'Активных заявок в ваших городах пока нет'
	if u.merchant_status in ['dolg']:
		text = 'У вас не погашен долг, обратитесь в тех. поддержку.\n\nТехническая поддержка: @sri_seacher'
	try:
		if len(orders) >=1 and u.merchant_status not in ['dolg']:
			for i in orders:
				pair = Pairs.get_dict()[i.pair]
				period = Periods.get_dict()[i.period]
				ts = int(i.timestamp_execut) + (60*60*5.5)
				dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
				bts = InlineKeyboardMarkup([
					[InlineKeyboardButton(text='💵 Сделать предложение', callback_data='Предложить '+ str(i.id))]
				])
				context.bot.send_message(message.chat.id, "<b>АКТУАЛЬНЫЙ ОРДЕР\n\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>\n\nАтуально до <b>{}</b>\nКомиссия за сделку <i><b>{} USDT</b></i>".format(i.city, pair, pair.split(' =>  ')[0], i.summ, period, dt, i.order_fee), reply_markup=bts, parse_mode="HTML")
				time.sleep(0.2)
			text = '<b>СДЕЛАЙТЕ ПРЕДЛОЖЕНИЕ ПО ИНТЕРЕСНОЙ ВАМ ЗАЯВКЕ</b>'
	except:
		pass
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)


# Мои долги
def merchant_debts(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	orders = u.merchant_executor_id_order_set.filter(status='exchanged_succesfull', status_fee='not_paid').order_by('timestamp_execut').reverse()[:5]
	text = 'Долгов нет'
	if len(orders) >=1:
		summ_debt = 0
		for i in orders:
			pair = Pairs.get_dict()[i.pair]
			period = Periods.get_dict()[i.period]
			summ_debt += i.order_fee
			time.sleep(0.2)
			context.bot.send_message(message.chat.id, "<b>ВЫПОЛНЕННЫЙ ОРДЕР\nКлиент {}\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>\n\nКомиссия за сделку <i><b>{} USDT</b></i>".format(i.client_id, i.city, pair, pair.split(' =>  ')[0], i.summ, period, i.order_fee), parse_mode="HTML")
		text = '<b>Сумма долга {} USDT</b>\nПосле оплаты долга Вы сможете продолжить принимать заказы.\n\nТехническая поддержка: @sri_seacher'.format(summ_debt)
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)


# Мои заказы
def merchant_orders(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	orders = u.merchant_executor_id_order_set.filter(status='exchange', timestamp_execut__lte=time.time()).order_by('timestamp_execut').reverse()[:5]
	text = 'Ордеров нет'
	try:
		if len(orders) >=1:
			text = 'Вернуться'
			for i in orders:
				pair = Pairs.get_dict()[i.pair]
				period = Periods.get_dict()[i.period]
				time.sleep(0.2)
				context.bot.send_message(message.chat.id, "<b>ОРДЕР В РАБОТЕ\nКлиент {}\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>\n\n".format(i.client_id, i.city, pair, pair.split(' =>  ')[0], i.summ, period), parse_mode="HTML")
	except:
		pass
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Мои выполненные заказы
def merchant_orders_completed(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	orders = u.merchant_executor_id_order_set.filter(status='exchanged_succesfull').order_by('timestamp_execut').reverse()[:5]
	text = 'Ордеров нет'
	if len(orders) >=1:
		text = 'Вернуться'
		for i in orders:
			pair = Pairs.get_dict()[i.pair]
			period = Periods.get_dict()[i.period]
			time.sleep(0.2)
			context.bot.send_message(message.chat.id, "<b>ВЫПОЛНЕННЫЙ ОРДЕР\nКлиент {}\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code></b>\n\n".format(i.client_id, i.city, pair, pair.split(' =>  ')[0], i.summ, period), parse_mode="HTML")
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Мои предложения
def merchant_suggestions(update: Update, context: CallbackContext):
	u = User.get_user(update, context)
	message = get_message_bot(update)
	del_mes(update, context, True)
	User.set_user_state(update, context, static_state.S_MENU)
	suggestions = list(u.merchant_executor_id_suggestion_set.all().values_list('order_id', flat=True))
	orders = Order.objects.filter(id__in=suggestions, status__in=['active', 'mailing'])[:5]
	text = 'Ордеров нет'
	try:
		if len(orders) >=1:
			text = 'Вернуться'
			for i in orders:
				pair = Pairs.get_dict()[i.pair]
				period = Periods.get_dict()[i.period]
				sug_text=''
				s = Order.objects.get(id=i.id)
				ts = int(i.timestamp_execut) + (60*60*5.5)
				dt = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
				for sug in s.order_id_suggestion_set.all():
					sug_text += str(sug.summ)+' '+str(pair.split(' =>  ')[1])
					if u == sug.merchant_executor_id:
						sug_text += ' ВАШЕ предложение'
					sug_text +='\n'
				bts = InlineKeyboardMarkup([
					[InlineKeyboardButton(text='💵 Изменить предложение', callback_data='Предложить '+ str(i.id))]
				])
				context.bot.send_message(message.chat.id, "<b>ЗАЯВКА В ПРОЦЕССЕ ПОДБОРА ИСПОЛНИТЕЛЯ:\n\nУспешно выполнено \\ всего заявок: <code>{} \\ {}   {}%</code>\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code>\n\nАтуально до <b>{}</b>\n\nПредложения:\n{}</b>".format(i.client_id.count_client_order_success, i.client_id.count_client_order, round(i.client_id.count_client_order_success / i.client_id.count_client_order * 100, 2), i.city, pair, pair.split(' =>  ')[0], i.summ, period, dt, sug_text), reply_markup=bts, parse_mode="HTML")
				time.sleep(0.2)
	except:
		pass
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Обменник')
	buttons.append([btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
	User.set_message_id(update, context, id.message_id)

# Предложить сумму на обмен
def merchant_suggestion(update: Update, context: CallbackContext, order_id: str = 'None'):
	message = get_message_bot(update)
	User.set_user_state(update, context, static_state.S_ENTERED_SUMM_SUGGESTION)
	o = Order.objects.get(id=int(order_id))
	try:
		city = o.city
		pair = Pairs.get_dict()[o.pair]
		summ = o.summ
		period = Periods.get_dict()[o.period]
		order_fee = o.order_fee
		User.set_merchant_client(update, context, order_id)
		User.set_message_id(update, context, message.message_id)
		text = "<b>ЗАЯВКА НА ОБМЕН\n\nВыбран город <code>{}</code>\nВыбрана пара\n<code>{}</code>\nСумма {} <code>{}</code>\nКэш нужен <code>{}</code>\n\n Комиссия за сделку <code>{}</code> USDT\n\n\n ВВЕДИТЕ СУММУ ЦИФРОЙ В {}</b>".format(city, pair, pair.split(' => ')[0], summ, period, order_fee, pair.split(' => ')[1])
		buttons = []
		btn_back = InlineKeyboardButton(text='Отказаться', callback_data='Отказаться')
		buttons.append([btn_back])
		markup = InlineKeyboardMarkup(buttons)
		context.bot.edit_message_text(chat_id=message.chat.id, text=text, message_id=message.message_id, reply_markup=markup, parse_mode="HTML")
	except:
		#merchant_suggestion_cancel(update, context)
		pass

# Отказаться от предложения суммы
def merchant_suggestion_cancel(update: Update, context: CallbackContext):
    User.set_user_state(update, context, static_state.S_MENU)
    del_mes(update, context)

# Записываем сумму
def merchant_suggestion_summ(update: Update, context: CallbackContext):
	del_mes(update, context)
	u = User.get_user(update, context)
	message = get_message_bot(update)
	order_id = u.merchant_client
	summ = message.text
	if isfloat(summ):
		o = Order.objects.get(id=int(order_id))
		User.set_user_state(update, context, static_state.S_MENU)
		s, created = Suggestion.objects.update_or_create(order_id=o, merchant_executor_id=u, defaults={
      		'summ':summ
        })
		o.status = 'mailing'
		o.save()
	context.bot.delete_message(message.chat.id, u.message_id)





###################################
###################################
def cmd_help(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	message = get_message_bot(update)
	buttons = []
	btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню')
	btn_main = InlineKeyboardButton(text='⏮ В начало', callback_data='Старт')
	buttons.append([btn_main, btn_back])
	markup = InlineKeyboardMarkup(buttons)
	id = context.bot.send_message(message.chat.id, "Помощь", reply_markup=markup)
	User.set_message_id(update, context, id.message_id)

def cmd_admin(update: Update, context: CallbackContext):
	del_mes(update, context, True)
	u = User.get_user(update, context)
	if u.is_admin:
		message = get_message_bot(update)
		buttons = []
		btn_back = InlineKeyboardButton(text='⏪ Назад', callback_data='Меню')
		btn_main = InlineKeyboardButton(text='⏮ В начало', callback_data='Старт')
		buttons.append([btn_main, btn_back])
		markup = InlineKeyboardMarkup(buttons)
		id = context.bot.send_message(message.chat.id, "📝 Администрирование:\nвыбери необходимый пункт для дальнейших действий\n\n<code>{}</code>".format(P2p.pay_trade_history()), reply_markup=markup, parse_mode="HTML")
		User.set_message_id(update, context, id.message_id)
	else:
		command_start(update, context)

def cmd_pass():
	pass

#словарь функций Меню по состоянию
State_Dict = {
    static_state.S_MENU : del_mes, # Когда выбрано Меню, мы можем только нажимать кнопки. Любой текст удаляется
    static_state.S_ENTERED_PAIR : cmd_periods,
    static_state.S_ENTERED_SUMM_SUGGESTION : merchant_suggestion_summ, # Обменник предлагает сумму для обмена
    static_state.S_ACCEPTED_ORDER : del_mes, # Ожидаем когда пройдет час, чтоб сменился статус, до этого удаляем все сообщения
    static_state.S_ACCEPTED_EXCHANGE : del_mes,
}

#словарь функций Меню
Menu_Dict = {
	'Старт': command_start,
	'Меню': cmd_menu,
	'Администрирование': cmd_admin,
	'Меню_Клиент' : start_client,
	'Заказы_Клиент': client_orders,
	'Клиент': cmd_client,
	'Город' : cmd_type_pair,
	'ТИП_Пары' : user_type_pair,
	'Пара' : cmd_pair,
	'Период' : cmd_accept_order,
	'Заявка_подтверждена': cmd_accepted_order,
	'Заявка_отклонена' : cmd_canceled_order,
	'Выбираю_предложение' : cmd_accepted_merchant_executer,
	'Обменник': cmd_merchant,
	'Правила_согласованны': merchant_terms_of_use_agreed,
	'Управление' : merchant_settings,
	'Смена_статуса' : merchant_change_status,
	'Мои_города' : merchant_cities,
	'Мои_долги' : merchant_debts,
	'Город_обменника' : change_merchat_city,
	'Выполненные_заказы': merchant_orders_completed,
	'Актуальные_заявки': actual_orders,
	'Заказы_Мерчант': merchant_orders,
	'Удалить': del_mes,
	'Предложить' : merchant_suggestion,
	'Отказаться' : merchant_suggestion_cancel,
	'Мои_предложения': merchant_suggestions,
	'Курс_валют': merchant_course,
	'pass': cmd_pass,
	'Клиент_подтвердил_сделку': cmd_finnaly_accepted_order,
	'Клиент_отменил_сделку': cmd_finnaly_rejected_order,
	'Help': cmd_help,
}


def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )