# -*- coding: utf-8 -*-
from aiogram import Dispatcher, Bot, executor, types # Aiogram
from aiogram.utils.executor import start_webhook # Webhook
from pgdb import DataBase # Postgresql database
from random import choice, randint # Pseudo-random
from fuzzywuzzy import process # Comparison and similarity
from datetime import datetime # Datetime
import asyncio, logging, os, codecs, re, gspread # other libs
import message_texts as txt # Messages
import conf # Configuration

client = gspread.authorize(conf.creds) # Authorization to Google Sheets API
sheet = client.open(conf.GSHEETNAME) # Opening sheet
sheet_instance = sheet.get_worksheet(0) # Working w/ sheet
bot = Bot(token=conf.API_TOKEN) # Bot
dp = Dispatcher(bot) # Dispatcher

# Reply to message from bot and pin in for table
# reply: !табло
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["табло"], commands_prefix=['!'], is_reply=True)
async def table_reply(message: types.Message):
	try:
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	except:
		pass
	if message.reply_to_message["from"]["is_bot"]:
		pg.message_set(message.reply_to_message.message_id, 1708019201)
		await message.answer(text=f"Таблица установлена <a href='t.me/c/{chat[0]}/{message.reply_to_message.message_id}'тут</a>", parse_mode="HTML")
	else:
		await message.answer(text="Ответьте на сообщение от бота, я не умею изменять сообщения пользователей😖")

# Send table
# !табло
@dp.message_handler(commands=["табло"], commands_prefix=['!'])
async def table_command(message: types.Message):
	try:
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	except:
		pass
	ulist = list()
	table = txt.TABLE_MESSAGE
	pg.message_set(message.message_id+1, 1708019201)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		table += f"{pg.username(f[0])} — {f[1]}\n"
	await message.answer(text=table, parse_mode="HTML")

# Add n-points to user
# reply: !дать 4
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["дать"], commands_prefix=['!'], is_reply=True)
async def point_add(message: types.Message):
	try:
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	except:
		pass
	ulist = list()
	table = txt.TABLE_MESSAGE
	mtext = message.text.split()
	items = pg.items()
	oldm = pg.message(message.reply_to_message["from"]["id"])[1] + 1
	if len(mtext) > 1 and mtext[1].isdigit():
		n = int(mtext[1])
	else:
		n = 1
	nlist = list(range(oldm, oldm+n))
	pg.message_set(pg.message(message.reply_to_message["from"]["id"])[1]+n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		table += f"{pg.username(f[0])} — {f[1]}\n"
		if message.reply_to_message["from"]["id"] == f[0]:
			for t in items:
					if t[1] in nlist:
						await bot.send_message(chat_id=chat[0], text=f"{pg.username(f[0])} <b>Вам выпало задание</b> «{t[0]}»:\n<i>{t[2]}</i>", parse_mode="HTML")
	await bot.edit_message_text(chat_id=chat[0], text=table, message_id=pg.message(1708019201)[1], parse_mode="HTML")

# Take n-points from user
# reply: !забрать 4
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["забрать"], commands_prefix=['!'], is_reply=True)
async def point_remove(message: types.Message):
	try:
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	except:
		pass
	ulist = list()
	table = txt.TABLE_MESSAGE
	mtext = message.text.split()
	if len(mtext) > 1 and mtext[1].isdigit():
		n = int(mtext[1])
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
	try:
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	except:
		pass
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1:]
	for w in word:
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
	try:
		await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	except:
		pass
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1:]
	for w in word:
		if w in BW:
			pg.word_remove(w)
			BW = pg.words()
			await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Убрано:\n" + w)

# Add item
# !добавитьпредмет Задание 821 Описание задания
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["добавитьпредмет"], commands_prefix=['!'])
async def item_add(message: types.Message):
	text = message.text.split()
	if len(text) < 3:
		return 0
	textt = str()
	for t in text[3:]:
		textt += t + ' '
	pg.item_add(text[1], text[2], textt)
	await bot.send_message(chat_id=chat[0], text=f"<b>🆕Новое задание:</b> «<code>{text[1]}</code>»", parse_mode="HTML")

# Remove item
# !убратьпредмет Задание
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["убратьпредмет"], commands_prefix=['!'])
async def item_remove(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.item_remove(text[1])
	await message.answer(text=f"<b>🗑Удалено задание:</b> «<code>{text[1]}</code>»", parse_mode="HTML")

# Description for all items
# !описание
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["описание"], commands_prefix=['!'])
async def item_description(message: types.Message):
	tlist = sorted(pg.items(), key=lambda x: x[1])
	text = "<b>Описание заданий:</b>\n\n"
	for t in tlist:
		text += f"{t[1]} <b>{t[0]}</b> — <i>{t[2]}</i>\n"
	await message.answer(text=text, parse_mode="HTML")

# Last logs
# !логи 23
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["логи"], commands_prefix=['!'])
async def logs_command(message: types.Message):
	try:
		n = int(message.text.split()[1])
	except:
		n = 25
	if n > 50:
		return 0
	logs = sorted(pg.logs(), key=lambda x: x[2], reverse=True)

	logs_text = f"<b>Последние {n} бан-вордов:</b>"
	for l in logs[0:n]:
		logs_text += f"\n<a href='t.me/c/1400136881/{l[2]}'>{l[0]} {l[1]} {pg.username(l[3])} — {l[5]}</a>"
	await message.answer(text=logs_text, parse_mode="HTML")

# Send message from bot tp chat
# !сообщение Привет, я Бот!
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["сообщение"], commands_prefix=['!'])
async def sendmessage_command(message: types.Message):
	text = message.text.split()[1:]
	msg_text = str()
	if len(text) < 1:
		return
	for t in text:
		msg_text += f"{t} "
	await bot.send_message(chat_id=chat[0], text=msg_text)

# Add film to Google Sheets
# !добавитьфильм https://www.kinopoisk.ru/film/12198/ 8.3 Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["добавитьфильм"], commands_prefix=['!'])
async def film_add(message: types.Message):
	name = str()
	mtext = message.text.split()[1:]
	row = sheet_instance.row_count
	kp_link = mtext[0]
	kp = mtext[1]
	for w in mtext[2:]:
		name += w + " "
	sheet_instance.insert_row(index=row, values=['badyep', name.strip(), kp])
	sheet_instance.update(f'C{row}', f'=HYPERLINK("{kp_link}", {kp})', raw=False)
	sheet_instance.update(f'D{row}', f'=IFERROR(ROUND(AVERAGE(G{row}:K{row}), 1), "—")', raw=False)
	await message.answer(text=f"Добавлен новый фильм в таблицу: {name}")

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
	film = list()
	name = str()
	req = sheet_instance.get_all_records()
	for r in req[5:]:
		if r['status'] != "yep":
			film.append(r["name"])
	message = message.text.split()
	for m in message[1:]:
		name += m + " "
	name = name.strip()
	ratio = process.extract(name, film)
	for r in ratio:
		if r[1] > 90:
			name = r[0]
			break
	try:
		frow = sheet_instance.find(query=name, in_column=2).row
		sheet_instance.update(f"A{frow}", "yep")
	except gspread.exceptions.CellNotFound as e:
		await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")

# Set rating from user to film
# reply: !оценка 10 Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in admin_users, commands=["оценка"], commands_prefix=['!'], is_reply=True)
async def rate_command(message: types.Message):
	film = list()
	name = str()
	req = sheet_instance.get_all_records()
	for r in req[5:]:
		if r['status'] != "yep":
			film.append(r["name"])
	user_id = message.reply_to_message["from"]["id"]
	message = message.text.split()
	urate = message[1]
	ucol = sheet_instance.find(query=str(user_id), in_row=1).col
	for m in message[2:]:
		name += m + " "
	name = name.strip()
	ratio = process.extract(name, film)
	for r in ratio:
		if r[1] > 90:
			name = r[0]
			break
	try:
		frow = sheet_instance.find(query=name, in_column=2).row
		sheet_instance.update_cell(row=frow, col=ucol, value=urate)
		await message.answer(f"Поставлена оценка {urate} фильму {name} от {pg.username(user_id)}")
	except gspread.exceptions.CellNotFound as e:
		await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["админ"], commands_prefix=['!'], is_reply=True)
async def promote_command(message: types.Message):
	await bot.promote_chat_member(
		chat_id=chat[0], 
		user_id=message.from_user.id, 
		can_manage_chat=True, 
		can_change_info=True, 
		can_delete_messages=True, 
		can_manage_voice_chats=True, 
		can_invite_users=True, 
		can_restrict_members=True, 
		can_pin_messages=True, 
		can_promote_members=True)
	await bot.set_chat_administrator_custom_title(chat_id=chat[0], user_id=message.from_user.id, custom_title=message.get_args())

# Add user-command
# !set привет Привет, человек
@dp.message_handler(lambda message: message.from_user.id in users, commands=["set"], commands_prefix=['!'])
async def usercommand_add(message: types.Message):
	text = message.text.split()
	if len(text) < 3:
		return 0
	textt = str()
	for t in text[2:]:
		textt += t + ' '
	pg.command_add(text[1], textt)
	global CL
	CL = pg.commands()
	await bot.send_message(chat_id=chat[0], text=f"🆕Новая команда <code>!{text[1]}</code>", parse_mode="HTML")

# Remove user-command
# !unset привет
@dp.message_handler(lambda message: message.from_user.id in users, commands=["unset"], commands_prefix=['!'])
async def usercommand_remove(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.command_remove(text[1])
	global CL
	CL = pg.commands()
	await bot.send_message(chat_id=chat[0], text=f"🗑Удалена команда <code>!{text[1]}</code>", parse_mode="HTML")

# Lenght of Ban Word database
# !количество
@dp.message_handler(lambda message: message.from_user.id in users, commands=["количество"], commands_prefix=['!'])
async def wb_count(message: types.Message):
	text = f"{pg.username(message.from_user.id)} Количество мата в БД: {len(BW)}🙂"
	await message.answer(text=text)

# Add event
# !добавитьивент Ивент
@dp.message_handler(lambda message: message.from_user.id in users, commands=["добавитьивент"], commands_prefix=['!'])
async def event_add(message: types.Message):
	text = message.text.split()
	textt = str()
	events = pg.events()
	if events == None:
		events = list()
	for t in text[1:]:
		textt += t + ' '
	if textt.strip() not in events:
		pg.event_add(textt.strip())
		await message.answer(text=f"🆕<b>Создан новый ивент:</b>\n«<code>{textt.strip()}</code>»", parse_mode="HTML")

# Remove event
# !убратьивент Ивент
@dp.message_handler(lambda message: message.from_user.id in users, commands=["убратьивент"], commands_prefix=['!'])
async def event_remove(message: types.Message):
	text = message.text.split()
	textt = str()
	events = pg.events()
	if events == None:
		events = list()
	for t in text[1:]:
		textt += t + ' '
	if textt.strip() in events:
		pg.event_remove(textt.strip())
		await message.answer(text=f"🆕<b>Удалён ивент:</b>\n«<code>{textt.strip()}</code>»", parse_mode="HTML")

# Next items for user
# !задания
@dp.message_handler(lambda message: message.from_user.id in users, commands=["задания", "квесты", "наказания"], commands_prefix=['!'])
async def items_command(message: types.Message):
	a = "<b>Грядущие задания:</b> \n\n"
	tlist = sorted(pg.items(), key=lambda x: x[1])
	for t in tlist:
		if pg.message(message.from_user.id)[1] > int(t[1]):
			pass
		else:
			a += f"{t[1]} — <code>{t[0]}</code>\n"
	await message.answer(text=f"{pg.username(message.from_user.id)} {a}", parse_mode="HTML")

# All events
# !ивенты
@dp.message_handler(lambda message: message.from_user.id in users, commands=["ивенты"], commands_prefix=['!'])
async def events_command(message: types.Message):
	text = "<b>Ивенты:</b>\n"
	events = pg.events()
	if events != None:
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
	if ran in (1, 3, 5):
		text = choice(txt.YES_LIST)
	elif ran in (2, 4, 6):
		text = choice(txt.NO_LIST)
	await message.answer(text=f"{pg.username(message.from_user.id)} {text}")

# Chance of event
# !шанс Событие
@dp.message_handler(lambda message: message.from_user.id in users, commands=["шанс"], commands_prefix=['!'])
async def chance_command(message: types.Message):
	text = str()
	mtext = message.text.split()
	if len(mtext) < 2:
		return 0
	for t in mtext[1:]:
		text += t + ' '
	chance_text = f"{pg.username(message.from_user.id)} шанс того, что {text}{randint(0, 100)}%"
	await message.answer(text=chance_text)

# Top of used words
# !словарь 13
@dp.message_handler(lambda message: message.from_user.id in users, commands=["словарь"], commands_prefix=['!'])
async def dictionary_command(message: types.Message):
	try:
		top = int(message.text.split()[1])
	except:
		top = 10
	if top > 25:
		return 0
	dictl = sorted(pg.dictionary(), key=lambda x: x[1], reverse=True)
	dictionary_text = f"<b>Топ-{top} слов:</b>"
	for d in dictl[0:top]:
		dictionary_text += f"\n{dictl.index(d)+1}. <i>{d[0]}</i> — {d[1]}"
	await message.answer(text=dictionary_text, parse_mode="HTML")

# Poll with non-watched films
# !смотрим
@dp.message_handler(lambda message: message.from_user.id in users, commands=["смотрим"], commands_prefix=['!'])
async def watchlist_command(message: types.Message):
	film = list()
	req = sheet_instance.get_all_records()
	for r in req:
		if r['status'] == "badyep":
			film.append(f"{r['name']} (КП: {r['kp']})")
	await bot.send_poll(chat_id=message.chat.id, question=txt.FILM_POLL, options=film, allows_multiple_answers=True, is_anonymous=False)

# Set rating to film
# !оценка 6 Игра (1997)
@dp.message_handler(lambda message: message.from_user.id in users, commands=["оценка"], commands_prefix=['!'])
async def rate_command(message: types.Message):
	film = list()
	name = str()
	req = sheet_instance.get_all_records()
	for r in req[5:]:
		if r['status'] != "yep":
			film.append(r["name"])
	user_id = message.from_user.id
	mtext = message.text.split()
	urate = mtext[1]
	ucol = sheet_instance.find(query=str(user_id), in_row=1).col
	for m in mtext[2:]:
		name += m + " "
	name = name.strip()
	ratio = process.extract(name, film)
	for r in ratio:
		if r[1] > 90:
			name = r[0]
			break
	try:
		frow = sheet_instance.find(query=name, in_column=2).row
		sheet_instance.update_cell(row=frow, col=ucol, value=urate)
		await message.answer(f"Поставлена оценка {urate} фильму {name} от {pg.username(user_id)}")
	except gspread.exceptions.CellNotFound as e:
		await message.answer("Не нашёл такой фильм в табличке, попробуй указать год")

# Self mute
# !табуретка 10000
@dp.message_handler(lambda message: message.from_user.id in users, commands=["табуретка"], commands_prefix=['!'])
async def selfmute_command(message: types.Message):
	now = int(datetime.now().timestamp())
	if len(message.text.split()) > 1 and message.text.split()[1].isdigit():
		args = int(message.text.split()[1])
		fdate = now + args
	if message.from_user.id not in admin_users:
		await bot.restrict_chat_member(chat_id=chat[0], user_id=message.from_user.id, can_send_messages=False, until_date=fdate)
		await message.answer(text=f"{pg.username(message.from_user.id)} был замучен на {args} секунд")

# Usercomands
# Example: !команда
@dp.message_handler(lambda message: message.from_user.id in users and message.text[0] == '!')
async def usercommands(message: types.Message):
	cmd = message.text[1:].split()
	if cmd[0] in CL:
		text = pg.commands_text()[pg.commands().index(cmd[0])]
		await message.answer(text=f"{pg.username(message.from_user.id)} {text}", parse_mode="HTML", disable_web_page_preview=True)

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
			if message.from_user.id == f[0]:
				for t in items:
					if t[1] in nlist:
						pass
						await bot.send_message(chat_id=chat[0], text=f"{pg.username(f[0])} <b>Вам выпало задание</b> «{t[0]}»:\n<i>{t[2]}</i>", parse_mode="HTML")
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
			if message.from_user.id == f[0]:
				for t in items:
					if t[1] in nlist:
						pass
						await bot.send_message(chat_id=chat[0], text=f"{pg.username(f[0])} <b>Вам выпало задание</b> «{t[0]}»:\n<i>{t[2]}</i>", parse_mode="HTML")
		await bot.edit_message_text(chat_id=chat[0], text=table, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

# Messages for users who are not in users list
@dp.message_handler(lambda message: message.from_user.id not in users, content_types=types.message.ContentType.ANY)
async def messages(message: types.Message):
	await bot.send_message(chat_id=users[4], text=message.from_user.id)
	link_markup = types.inline_keyboard.InlineKeyboardMarkup(row_width=2)
	author_button = types.inline_keyboard.InlineKeyboardButton(text="Связаться с автором", url="https://t.me/rvbsm")
	# _button = types.inline_keyboard.InlineKeyboardButton(text="", url="")
	link_markup.add(author_button)
	#await message.answer(text="<b>Полезные ссылки:</b>", parse_mode="HTML", reply_markup=link_markup)

# Database connecting
async def db_update():
	while True:
		global pg, BW, CL, admin_users
		pg = DataBase(conf.DATABASE)
		BW = pg.words()
		CL = pg.commands()
		await asyncio.sleep(180)
		admin_users = await bot.get_chat_administrators(chat[0])

# Set vars
async def on_startup(dp):
	global chat, users, admin_users
	chat = [-1001400136881]
	users = [529598217, 932736973, 636619912, 555328241, 200635302]
	admin_users = await bot.get_chat_administrators(chat[0])
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
