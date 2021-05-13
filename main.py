# -*- coding: utf-8 -*-
from aiogram import Dispatcher, Bot, executor, types # Aiogram
from aiogram.utils.executor import start_webhook # Webhook
from aiogram.types import PollAnswer # PollAnswers
from aiogram.dispatcher.filters.state import State, StatesGroup # States
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pgdb import DataBase # Postgresql database
from random import choice, randint # Pseudo-random
from fuzzywuzzy import process # Comparison and similarity
from datetime import datetime # Datetime
from math import ceil # Round up
import asyncio, logging, os, codecs, re, gspread # other libs
import message_texts as txt # Messages
import conf # Configuration

"""
ПЛАНЫ:

Прогнозы
Отвечать на 'бот'
? Квесты
? Для общего пользования
"""

client = gspread.authorize(conf.creds) # Authorization to Google Sheets API
sheet = client.open(conf.GSHEETNAME) # Opening sheet
bot = Bot(token=conf.API_TOKEN) # Bot
dp = Dispatcher(bot, storage=MemoryStorage()) # Dispatcher

class Forecast(StatesGroup):
	Bet = State()

def get_arguments(text):
	return text.split()[1:]

# Reply to message from bot and pin in for table
# reply: !табло
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["табло"], commands_prefix=['!'], is_reply=True)
async def table_reply(message: types.Message):
	if message.reply_to_message["from"]["is_bot"]:
		pg.message_set(message.reply_to_message.message_id, 1708019201)
		await message.answer(text=f"Таблица установлена <a href='t.me/c/{chat[0]}/{message.reply_to_message.message_id}'тут</a>", parse_mode="HTML")
	else:
		await message.answer(text="Ответьте на сообщение от бота или отправьте сообщение не ответом, я не умею изменять сообщения пользователей😖")

# Send table
# !табло
@dp.message_handler(commands=["табло"], commands_prefix=['!'])
async def table_command(message: types.Message):
	ulist = list()
	table = txt.TABLE_MESSAGE
	await message.answer(text=table, parse_mode="HTML")
	pg.message_set(message.message_id+1, 1708019201)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		table += f"{pg.username(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=chat[0], text=table, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

# Add n-points to user
# reply: !дать 4
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["дать"], commands_prefix=['!'], is_reply=True)
async def point_add(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ulist = list()
	table = txt.TABLE_MESSAGE
	mtext = get_arguments(message.text)
	items = pg.items()
	oldm = pg.message(message.reply_to_message["from"]["id"])[1] + 1
	if mtext[0].isdigit():
		n = int(mtext[0])
	else:
		n = 1
	nlist = list(range(oldm, oldm+n))
	pg.message_set(pg.message(message.reply_to_message["from"]["id"])[1]+n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		table += f"{pg.username(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=chat[0], text=table, message_id=pg.message(1708019201)[1], parse_mode="HTML")

# Take n-points from user
# reply: !забрать 4
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["забрать"], commands_prefix=['!'], is_reply=True)
async def point_remove(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ulist = list()
	table = txt.TABLE_MESSAGE
	mtext = get_arguments(message.text)
	if mtext[0].isdigit():
		n = int(mtext[0])
	else:
		n = 1
	pg.message_set(pg.message(message.reply_to_message["from"]["id"])[1]-n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		table += f"{pg.username(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=chat[0], text=table, message_id=pg.message(1708019201)[1], parse_mode="HTML")

# Add new words to database with ban words
# !добавитьмат блять пиздец
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["добавитьмат"], commands_prefix=['!'])
async def banword_add(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	mtext = get_arguments(message.text)
	if len(mtext) < 1:
		return
	for w in mtext:
		for l in w:
			if w not in BW:
				if not l.isalpha():
					break
				pg.word_add(w)
				BW = pg.words()
				await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Добавлено:\n" + w)
				break

# Take away words from database with ban words
# !убратьмат блять пиздец
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["убратьмат"], commands_prefix=['!'])
async def wb_remove(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	mtext = get_arguments(message.text)
	if len(mtext) < 1:
		return
	for w in mtext:
		if w in BW:
			pg.word_remove(w)
			BW = pg.words()
			await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Убрано:\n" + w)

# Add item
# !добавитьпредмет Задание 821 Описание задания
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["добавитьпредмет"], commands_prefix=['!'])
async def item_add(message: types.Message):
	mtext = get_arguments(message.text)
	if len(mtext) < 2:
		return
	desc = ' '.join(map(str, mtext[2:]))
	pg.item_add(mtext[0], mtext[1], desc)
	await bot.send_message(chat_id=chat[0], text=f"<b>🆕Новое задание:</b> «<code>{mtext[0]}</code>»", parse_mode="HTML")

# Remove item
# !убратьпредмет Задание
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["убратьпредмет"], commands_prefix=['!'])
async def item_remove(message: types.Message):
	mtext = get_arguments(message.text)
	if len(text) < 1:
		return
	pg.item_remove(mtext[1])
	await message.answer(text=f"<b>🗑Удалено задание:</b> «<code>{mtext[0]}</code>»", parse_mode="HTML")

# Description for all items
# !описание
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["описание"], commands_prefix=['!'])
async def item_description(message: types.Message):
	tlist = sorted(pg.items(), key=lambda x: x[1])
	desc_text = "<b>Описание заданий:</b>\n\n"
	for t in tlist:
		desc_text += f"{t[1]} <b>{t[0]}</b> — <i>{t[2]}</i>\n"
	await message.answer(text=desc_text, parse_mode="HTML")

# Last logs
# !логи 23
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["логи"], commands_prefix=['!'])
async def logs_command(message: types.Message):
	try:
		n = int(get_arguments(message.text)[0])
	except:
		n = 25
	if n > 50:
		return
	logs = sorted(pg.logs(), key=lambda x: x[2], reverse=True)
	logs_text = f"<b>Последние {n} бан-вордов:</b>"
	for l in logs[0:n]:
		logs_text += f"\n<a href='t.me/c/1400136881/{l[2]}'>{l[0]} {l[1]} {pg.username(l[3])} — {l[5]}</a>"
	await message.answer(text=logs_text, parse_mode="HTML")

# Send message from bot to chat
# !сообщение Привет, я Бот!
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["сообщение"], commands_prefix=['!'])
async def sendmessage_command(message: types.Message):
	mtext = get_arguments(message.text)
	if len(mtext) < 1:
		return
	msg_text = ' '.join(map(str, mtext))
	await bot.send_message(chat_id=chat[0], text=msg_text)

# Add film to Google Sheets
# !добавитьфильм https://www.kinopoisk.ru/film/12198/ 8.3 триллер/детектив Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["добавитьфильм"], commands_prefix=['!'])
async def film_add(message: types.Message):
	sheet_instance = sheet.get_worksheet(0)
	row = sheet_instance.row_count
	mtext = get_arguments(message.text)
	kp_link = mtext[0]
	kp = mtext[1]
	genre = mtext[2]
	name = ' '.join(map(str, mtext[3:]))
	sheet_instance.insert_row(index=row, values=['badyep', name.strip(), genre, kp])
	sheet_instance.update(f'D{row}', f'=HYPERLINK("{kp_link}", {kp})', raw=False)
	sheet_instance.update(f'E{row}', f'=IFERROR(ROUND(AVERAGE(H{row}:L{row}), 1), "—")', raw=False)
	await message.answer(text=f"Добавлен новый фильм в таблицу: «{name}»")

# Admin commands
# !админкоманды
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["админкоманды", "админпомощь"], commands_prefix=['!'])
async def admin_help_command(message: types.Message):
	cmd = txt.CMD_ADMIN_MESSAGE
	await message.answer(text=f"{pg.username(message.from_user.id)} Админ команды:{cmd}", parse_mode="HTML")

# Set film as watched
# !просмотрено Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["просмотрено"], commands_prefix=['!'])
async def watched_command(message: types.Message):
	sheet_instance = sheet.get_worksheet(0)
	req = sheet_instance.get_all_records()
	film_markup = types.InlineKeyboardMarkup(row_width=4)
	film = set()
	fsearch = list()
	user_id = message.from_user.id
	for r in req:
		if r['status'] == "badyep":
			film.add(r["name"])
	mtext = get_arguments(message.text)
	name = ' '.join(map(str, mtext))
	ratio = process.extract(name, film)
	for r in ratio:
		if r[1] > 75:
			fsearch.append(r[0])
	if len(fsearch) > 1:
		for f in sorted(fsearch, key=lambda x: x[-5:]):
			print(f"watched-{f}-{user_id}")
			film_button = types.InlineKeyboardButton(text=f, callback_data=f"watched-{f}-{user_id}")
			film_markup.add(film_button)
		await message.answer(text="Нашёл несколько фильмов:", reply_markup=film_markup)
	elif len(fsearch) < 2:
		try:
			frow = sheet_instance.find(query=name, in_column=2).row
			sheet_instance.update(f"A{frow}", "yep")
			sheet_instance.update(f"F{frow}", datetime.now().strftime("%d.%m.%Y"))
			await message.answer("Как вам фильм, понравился?")
		except gspread.exceptions.CellNotFound as e:
			await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")

# Set rating from user to film
# reply: !оценка 10 Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["оценка"], commands_prefix=['!'], is_reply=True)
async def admin_rate_command(message: types.Message):
	sheet_instance = sheet.get_worksheet(0)
	req = sheet_instance.get_all_records()
	film_markup = types.InlineKeyboardMarkup(row_width=4)
	film = set()
	fsearch = list()
	for r in req:
		if r['status'] == "yep":
			film.add(r["name"])
	user_id = message.reply_to_message["from"]["id"]
	mtext = get_arguments(message.text)
	urate = mtext[0]
	if not urate.isdigit():
		await message.answer("Оценка должна быть числом")
		return
	ucol = sheet_instance.find(query=str(user_id), in_row=1).col
	name = ' '.join(map(str, mtext[1:]))
	ratio = process.extract(name, film)
	for r in ratio:
		if r[1] > 75:
			fsearch.append(r[0])
	if len(fsearch) > 1:
		for f in sorted(fsearch, key=lambda x: x[-5:]):
			film_button = types.InlineKeyboardButton(text=f, callback_data=f"{urate}-{f}-{user_id}")
			film_markup.add(film_button)
		await message.answer(text="Нашёл несколько фильмов:", reply_markup=film_markup)
	elif len(fsearch) < 2:
		if len(fsearch) == 0:
			await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")
			return
		try:
			frow = sheet_instance.find(query=fsearch[0], in_column=2).row
			sheet_instance.update_cell(row=frow, col=ucol, value=urate)
			await message.answer(f"Поставлена оценка {urate} фильму {fsearch[0]} от {pg.username(user_id)}")
		except gspread.exceptions.CellNotFound as e:
			await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")

# Send poll with forecast
# !прогноз Кто победит? Синие Красные
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["прогноз"], commands_prefix=['!'])
async def poll(message: types.Message):
	mtext = get_arguments(message.text)
	question = ' '.join(map(str, mtext[:-2]))
	options = mtext[-2:]
	if not question or len(options) != 2:
		await message.answer("Вы забыли аргументы\nПример: <code>!прогноз Кто победит? Синие Красные</code>", parse_mode="HTML")
		return
	await message.answer(text=txt.FORECAST_MESSAGE.format(0, 0, 0, 0, 0, 0), parse_mode="HTML")
	for u in users:
		pg.bet_set(u, 0)
		pg.poll_answer_set(u, 2)
	pg.poll_answer_set(1708019201, message.message_id + 1)
	await bot.send_poll(chat_id=message.chat.id, question=question, options=options, is_anonymous=False, open_period=300)

@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["красные", "синие"], commands_prefix=['!'])
async def results(message: types.Message):
	mtext = message.text[1:]
	table = txt.TABLE_MESSAGE
	blueList = set()
	redList = set()
	ulist = list()
	blueAll = redAll = 0
	await message.answer(f"Победили {mtext}, поздравляю, разбирайте Е-баллы")
	for u in users:
		if pg.poll_answer(u) == 0:
			blueList.add(u)
		elif pg.poll_answer(u) == 1:
			redList.add(u)
	for b in blueList:
		blueAll += int(pg.bet(b))
	for r in redList:
		redAll += int(pg.bet(r))
	if bluePerc != 0:
		blueCoef = round(1+redPerc/bluePerc, 2)
	if redPerc != 0:
		redCoef = round(1+bluePerc/redPerc, 2)
	if message.text[1:] == "красные":
		for b in blueList:
			pg.message_set(pg.message(b)+pg.bet(b)*blueCoef, r)
	elif message.text[1:] == "синие":
		for r in redList:
			pg.message_set(pg.message(r)+pg.bet(r)*redCoef, r)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		table += f"{pg.username(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=chat[0], text=table, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

# Get bet from user
# 300
@dp.message_handler(lambda message: message.from_user.id in users, state=Forecast.Bet)
async def bet_message(message: types.Message, state: FSMContext):
	mtext = message.text.split()
	table = txt.TABLE_MESSAGE
	blueList = set()
	redList = set()
	ulist = list()
	blueAll = redAll = 0
	if mtext[0].isdigit():
		if int(mtext[0]) < pg.message(message.from_user.id)[1]:
			pg.bet_set(message.from_user.id, mtext[0])
			pg.message_set(pg.message(message.from_user.id)[1] - int(mtext[0]), message.from_user.id)
			await message.answer(f"Поздравляю, вы поставили {mtext[0]} Е-баллов!")
			for u in users:
				ulist.append(pg.message(u))
			ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
			for f in ulist:
				table += f"{pg.username(f[0])} — {f[1]}\n"
			await bot.edit_message_text(chat_id=chat[0], text=table, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")
			for u in users:
				if pg.poll_answer(u) == 0:
					blueList.add(u)
				elif pg.poll_answer(u) == 1:
					redList.add(u)
			for b in blueList:
				blueAll += int(pg.bet(b))
			for r in redList:
				redAll += int(pg.bet(r))
			bluePerc = blueAll/(redAll+blueAll)
			redPerc = redAll/(redAll+blueAll)
			if blueAll != 0:
				blueCoef = round(1+redPerc/bluePerc, 2)
			else:
				blueCoef = 0
			if redAll != 0:
				redCoef = round(1+bluePerc/redPerc, 2)
			else:
				redCoef = 0
			await bot.edit_message_text(chat_id=chat[0], message_id=pg.poll_answer(1708019201), text=txt.FORECAST_MESSAGE.format(blueAll, redAll, blueCoef, redCoef), parse_mode="HTML")
			await state.finish()
		else:
			await message.answer("У Вас нет столько баллов🙂")
	elif message.chat.id in chat:
		await message.answer(f"{pg.username(message.from_user.id)} ответь боту в личке, а то щас всё пойдёт по одному месту😣")
	else:
		await message.answer("Ставка должна быть числом😉")

# Add user-command
# !set привет Привет, человек
@dp.message_handler(lambda message: message.from_user.id in users, commands=["set"], commands_prefix=['!'])
async def usercommand_add(message: types.Message):
	global CL
	mtext = get_arguments(message.text)
	if len(mtext) < 2:
		return
	text = ' '.join(map(str, mtext[1:]))
	pg.command_add(mtext[0], text)
	CL = pg.commands()
	await bot.send_message(chat_id=chat[0], text=f"🆕Новая команда <code>!{mtext[0]}</code>", parse_mode="HTML")

# Remove user-command
# !unset привет
@dp.message_handler(lambda message: message.from_user.id in users, commands=["unset"], commands_prefix=['!'])
async def usercommand_remove(message: types.Message):
	global CL
	mtext = get_arguments(message.text)
	if len(mtext) < 1:
		return
	pg.command_remove(mtext[0])
	CL = pg.commands()
	await bot.send_message(chat_id=chat[0], text=f"🗑Удалена команда <code>!{mtext[0]}</code>", parse_mode="HTML")

# Lenght of Ban Word database
# !количество
@dp.message_handler(lambda message: message.from_user.id in users, commands=["количество"], commands_prefix=['!'])
async def wb_count(message: types.Message):
	counter = f"{pg.username(message.from_user.id)} Количество мата в БД: {len(BW)}🙂"
	await message.answer(text=counter)

# Add event
# !добавитьивент Ивент
@dp.message_handler(lambda message: message.from_user.id in users, commands=["добавитьивент"], commands_prefix=['!'])
async def event_add(message: types.Message):
	mtext = get_arguments(message.text)
	events = pg.events()
	event = ' '.join(map(str, mtext))
	if event not in events:
		pg.event_add(event)
		await message.answer(text=f"🆕<b>Создан новый ивент:</b>\n«<code>{event}</code>»", parse_mode="HTML")

# Remove event
# !убратьивент Ивент
@dp.message_handler(lambda message: message.from_user.id in users, commands=["убратьивент"], commands_prefix=['!'])
async def event_remove(message: types.Message):
	mtext = get_arguments(message.text)
	events = pg.events()
	event = ' '.join(map(str, mtext))
	if event in events:
		pg.event_remove(event)
		await message.answer(text=f"🆕<b>Удалён ивент:</b>\n«<code>{event}</code>»", parse_mode="HTML")

# Next items for user
# !задания
@dp.message_handler(lambda message: message.from_user.id in users, commands=["задания", "квесты", "наказания"], commands_prefix=['!'])
async def items_command(message: types.Message):
	items = "<b>Грядущие задания:</b> \n\n"
	tlist = sorted(pg.items(), key=lambda x: x[1])
	for t in tlist:
		if pg.message(message.from_user.id)[1] > int(t[1]):
			pass
		else:
			items += f"{t[1]} — <code>{t[0]}</code>\n"
	await message.answer(text=f"{pg.username(message.from_user.id)} {items}", parse_mode="HTML")

# All events
# !ивенты
@dp.message_handler(lambda message: message.from_user.id in users, commands=["ивенты"], commands_prefix=['!'])
async def events_command(message: types.Message):
	text = "<b>Ивенты:</b>\n"
	events = pg.events()
	for e in events:
		text += "\n<i>" + e + "</i>"
	await message.answer(text=text, parse_mode="HTML")

# All commands
# !команды
@dp.message_handler(lambda message: message.from_user.id in users, commands=["команды", "помощь"], commands_prefix=['!'])
async def help_command(message: types.Message):
	cmd = txt.CMD_MESSAGE
	for c in CL:
		cmd += f"\n<code>!{c}</code>"
	await message.answer(text=f"{pg.username(message.from_user.id)}{cmd}", parse_mode="HTML")

# Yes or No
# !даилинет
@dp.message_handler(lambda message: message.from_user.id in users, commands=["даилинет"], commands_prefix=['!'])
async def yesorno_command(message: types.Message):
	ran = randint(1, 6)
	if ran % 2 == 1:
		text = choice(txt.YES_LIST)
	elif ran % 2 == 0:
		text = choice(txt.NO_LIST)
	await message.reply(text=text)

# Chance of event
# !шанс Событие
@dp.message_handler(lambda message: message.from_user.id in users, commands=["шанс"], commands_prefix=['!'])
async def chance_command(message: types.Message):
	mtext = get_arguments(message.text)
	if len(mtext) < 2:
		return
	text = ' '.join(map(str, mtext))
	chance_text = f"Шанс того, что {text} {randint(0, 100)}%"
	await message.reply(text=chance_text)

# Top of used words
# !словарь 13
@dp.message_handler(lambda message: message.from_user.id in users, commands=["словарь"], commands_prefix=['!'])
async def dictionary_command(message: types.Message):
	try:
		top = int(message.text.split()[1])
	except:
		top = 10
	if top > 25:
		return
	dictl = sorted(pg.dictionary(), key=lambda x: x[1], reverse=True)
	dictionary_text = f"<b>Топ-{top} слов:</b>"
	for d in dictl[0:top]:
		dictionary_text += f"\n{dictl.index(d)+1}. <i>{d[0]}</i> — {d[1]}"
	await message.answer(text=dictionary_text, parse_mode="HTML")

# Poll with non-watched films
# !смотрим
@dp.message_handler(lambda message: message.from_user.id in users, commands=["смотрим"], commands_prefix=['!'])
async def watchlist_command(message: types.Message):
	sheet_instance = sheet.get_worksheet(0)
	film = list()
	date = int(datetime.now().timestamp()) + 300
	req = sheet_instance.get_all_records()
	for r in req:
		if r['status'] == "badyep" and len(film) < 11:
			film.append(f"{r['name']} {r['genre']} (КП: {r['kp']})")
	await message.answer(text=pg.commands_text()[pg.commands().index('ахуй')], parse_mode="HTML")
	await bot.send_poll(chat_id=message.chat.id, question=txt.FILM_POLL, options=film, allows_multiple_answers=True, is_anonymous=False, close_date=date)

# Set rating to film
# !оценка 6 Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in users, commands=["оценка"], commands_prefix=['!'])
async def rate_command(message: types.Message):
	sheet_instance = sheet.get_worksheet(0)
	req = sheet_instance.get_all_records()
	film_markup = types.InlineKeyboardMarkup(row_width=4)
	film = set()
	fsearch = list()
	for r in req[5:]:
		if r['status'] == "yep":
			film.add(r["name"])
	user_id = message.from_user.id
	mtext = get_arguments(message.text)
	urate = mtext[0]
	if not urate.isdigit():
		await message.answer("Оценка должна быть числом")
		return
	ucol = sheet_instance.find(query=str(user_id), in_row=1).col
	name = ' '.join(map(str, mtext[1:]))
	ratio = process.extract(name, film)
	for r in ratio:
		if r[1] > 75:
			fsearch.append(r[0])
	if len(fsearch) > 1:
		for f in sorted(fsearch, key=lambda x: x[-5:]):
			print(f"{urate}-{f}-{user_id}")
			film_button = types.InlineKeyboardButton(text=f, callback_data=f"{urate}-{f}-{user_id}")
			film_markup.add(film_button)
		await message.answer(text="Нашёл несколько фильмов:", reply_markup=film_markup)
	elif len(fsearch) < 2:
		if len(fsearch) == 0:
			await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")
			return
		try:
			frow = sheet_instance.find(query=fsearch[0], in_column=2).row
			sheet_instance.update_cell(row=frow, col=ucol, value=urate)
			await message.answer(f"Поставлена оценка {urate} фильму {fsearch[0]} от {pg.username(user_id)}")
		except gspread.exceptions.CellNotFound as e:
			await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")

# Self mute
# !табуретка 10000
@dp.message_handler(lambda message: message.from_user.id in users, commands=["табуретка"], commands_prefix=['!'])
async def selfmute_command(message: types.Message):
	now = int(datetime.now().timestamp())
	mtext = get_arguments(message.text)
	if len(mtext) == 1 and mtext[0].isdigit():
		args = int(message.text.split()[1])
		args = ceil(args / 60) * 60
		fdate = now + args
	else:
		args = 60
		fdate = now + 60
	if message.from_user.id not in admin_users:
		await bot.restrict_chat_member(chat_id=chat[0], user_id=message.from_user.id, can_send_messages=False, until_date=fdate)
	await message.answer(text=f"{pg.username(message.from_user.id)} был замучен на {args/60} минут")

# Usercomands
# Example: !команда
@dp.message_handler(lambda message: message.from_user.id in users and message.text[0] == '!')
async def usercommands(message: types.Message):
	cmd = message.text[1:].split()
	if cmd[0] in CL:
		text = pg.commands_text()[pg.commands().index(cmd[0])]
		await message.reply(text=text, parse_mode="HTML", disable_web_page_preview=True)

# Ban-word Filter
@dp.message_handler(lambda message: message.from_user.id in users)
async def filter(message: types.Message):
	if message.from_user.username == None:
		pg.username_set(message.from_user.first_name, message.from_user.id)
	else:
		pg.username_set('@'+message.from_user.username, message.from_user.id)
	n = int()
	ulist = list()
	nlist = set()
	outw = str()
	outl = set()
	prnt = False
	table = txt.TABLE_MESSAGE
	mtext = message.text.lower()
	oldm = pg.message(message.from_user.id)[1]
	text = " ".join(re.findall("[а-яА-ЯёЁa-zA-Z]+", mtext))
	items = pg.items()
	dw = pg.dictionary_words()
	for w in text.split():
		lastl = str()
		outw = str()
		for l in w:
			if l != lastl:
				outw += l
				lastl = l
		outl.add(outw)
	bt = 0
	try:
		for t in outl:
			if t in txt.BOT_LIST:
				with open(f"gif/{randint(1, 3)}.gif", "rb") as gif:
					await message.reply_video(gif, caption="ни грути. цём")
					gif.close()
			if t != None:
				if t in dw and len(t) > 1:
					pg.dictionary_set(t, pg.dictionary_count(t)+1)
				elif t not in dw and len(t) > 1:
					pg.dictionary_add(t, message.from_user.id)
				ratio = process.extract(t, BW)
				for r in ratio:
					if r[1] > 93:
						n += 1
						nlist.add(oldm+n)
						pg.log_add(message.message_id, message.from_user.id, r[1], t, r[0])
						break
	except Exception as e:
		pg.log_add(message.message_id, message.from_user.id, 0, str(e), str(e))
	if n != 0:
		pg.message_set(pg.message(message.from_user.id)[1]+n, message.from_user.id)
		await asyncio.sleep(1)
		for u in users:
			ulist.append(pg.message(u))
		ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
		for f in ulist:
			table += f"{pg.username(f[0])} — {f[1]}\n"
		await bot.edit_message_text(chat_id=chat[0], text=table, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

	# ~0,13% chance
	ranlen = range(128)
	ranch = choice(ranlen)
	ranch2 = choice(ranlen)
	if ranch < ranch2:
		ran = randint(ranch, ranch2)
	elif ranch > ranch2:
		ran = randint(ranch2, ranch)
	elif ranch == ranch2:
		ran = ranch	
	prnt = ran**2 == ranch**ranch2
	if prnt == True:
		text = choice(pg.events())
		await bot.send_message(chat_id=chat[0], text=f"{pg.username(message.from_user.id)} <b>Вам выпал ивент:</b>\n\n{text}", parse_mode="HTML")

# Edited message ban-word filter
@dp.edited_message_handler(lambda message: message.from_user.id in users)
async def edited_message_filter(message: types.Message):
	if message.from_user.username == None:
		pg.username_set(message.from_user.first_name, message.from_user.id)
	else:
		pg.username_set('@'+message.from_user.username, message.from_user.id)
	n = int()
	ulist = list()
	nlist = set()
	outw = str()
	outl = set()
	table = txt.TABLE_MESSAGE
	mtext = message.text.lower()
	oldm = pg.message(message.from_user.id)[1]
	text = " ".join(re.findall("[а-яА-ЯёЁa-zA-Z]+", mtext))
	items = pg.items()
	dw = pg.dictionary_words()
	for w in text.split():
		lastl = str()
		outw = str()
		for l in w:
			if l != lastl:
				outw += l
				lastl = l
		outl.add(outw)
	try:
		for t in outl:
			if t != None:
				if t in dw and len(t) > 1:
					pg.dictionary_set(t, pg.dictionary_count(t)+1)
				elif t not in dw and len(t) > 1:
					pg.dictionary_add(t, message.from_user.id)
				ratio = process.extract(t, BW)
				for r in ratio:
					if r[1] > 93:
						n += 1
						nlist.add(oldm+n)
						pg.log_add(message.message_id, message.from_user.id, r[1], t, r[0])
						break
	except Exception as e:
		pg.log_add(message.message_id, message.from_user.id, 0, e, str())
	if n != 0:
		await asyncio.sleep(1)
		pg.message_set(pg.message(message.from_user.id)[1]+n, message.from_user.id)
		for u in users:
			ulist.append(pg.message(u))
		ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
		for f in ulist:
			table += f"{pg.username(f[0])} — {f[1]}\n"
		await bot.edit_message_text(chat_id=chat[0], text=table, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

@dp.message_handler(content_types=types.message.ContentType.LEFT_CHAT_MEMBER)
async def left_member(message: types.Message):
	await message.answer("Верните эту придурошную обратно")

# Messages for users who are not in users list
@dp.message_handler(lambda message: message.from_user.id not in users, content_types=types.message.ContentType.ANY)
async def messages(message: types.Message):
	await bot.send_message(chat_id=admin_users[0], text=message.from_user.id)
	link_markup = types.inline_keyboard.InlineKeyboardMarkup(row_width=2)
	author_button = types.inline_keyboard.InlineKeyboardButton(text="Связаться с автором", url="https://t.me/rvbsm")
	# _button = types.inline_keyboard.InlineKeyboardButton(text="", url="")
	link_markup.add(author_button)
	#await message.answer(text="<b>Полезные ссылки:</b>", parse_mode="HTML", reply_markup=link_markup)

@dp.callback_query_handler(lambda call: call.from_user.id in users)
async def film_callback(call: types.callback_query):
	sheet_instance = sheet.get_worksheet(0)
	callback = call.data.split('-')
	user_id = int(callback[2])
	if user_id == call.from_user.id or user_id in admin_users:
		if callback[0].isdigit():	
			
			ucol = sheet_instance.find(query=str(user_id), in_row=1).col
			urate = callback[0]
			ufilm = callback[1]
			frow = sheet_instance.find(query=ufilm, in_column=2).row
			sheet_instance.update_cell(row=frow, col=ucol, value=urate)
			await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поставлена оценка {urate} фильму {ufilm} от {pg.username(user_id)}")

		elif callback[0] == "watched":
			frow = sheet_instance.find(query=callback[1], in_column=2).row
			sheet_instance.update(f"A{frow}", "yep")
			sheet_instance.update(f"F{frow}", datetime.now().strftime("%d.%m.%Y"))
			await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Как вам фильм, понравился?")
	else:
		await call.answer(text=f"Ты не {pg.username(user_id)}")

@dp.poll_answer_handler(lambda poll_answer: poll_answer.user.id in users)
async def forecast_answer(poll_answer: types.PollAnswer):
	if len(poll_answer.option_ids) == 1:
		pg.poll_answer_set(poll_answer.user.id, poll_answer.option_ids[0])
		await Forecast.Bet.set()
		await bot.send_message(chat_id=poll_answer.user.id, text="Сколько баллов ставишь?")

# Database connecting
async def db_update():
	while True:
		global pg, BW, CL
		pg = DataBase(conf.DATABASE)
		BW = pg.words()
		CL = pg.commands()
		await asyncio.sleep(180)

# Set vars
async def on_startup(dp):
	global chat, users, admin_users
	chat = [-1001400136881]
	users = [529598217, 932736973, 636619912, 555328241, 200635302]
	admin_users = [200635302, 932736973]
	await bot.delete_webhook(drop_pending_updates=True)
	await bot.set_webhook(conf.WEBHOOK_URL, drop_pending_updates=True)

# Starting
if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	loop = asyncio.get_event_loop()
	loop.create_task(db_update())
	start_webhook(
		dispatcher=dp, 
		loop=loop,
		webhook_path=conf.WEBHOOK_PATH, 
		skip_updates=True, 
		on_startup=on_startup,
		host=conf.WEBAPP_HOST, 
		port=conf.WEBAPP_PORT
	)
