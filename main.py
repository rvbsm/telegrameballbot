from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher.filters import IsReplyFilter
from aiogram.utils.executor import start_webhook
import asyncio, logging, psycopg2, os
from random import choice, randint
from fuzzywuzzy import process
import conf
from pgdb import DataBase

YES_LIST = ["да, делай", "ДАВАЙ, ВПЕРЁЁД", "да🗿", "допустим да", "давай да", "да...?"]
NO_LIST = ["больная что-ли? Нет, конечно", "я думаю нет", "нет🗿", "не, не надо", "ацтань, нет", "не нужно", "не", "прости, но нет"]

table = "<b>Е-БАЛЛЫ:</b>\n\n"
cmd = """<b>Допуступные всем (*тык* for copy):</b>
<code>!set</code> &lt;команда&gt; &lt;текст при вызове команды&gt;
<code>!шанс</code> &lt;событие&gt;
<code>!помощь</code>
<code>!задания</code>
<code>!количество</code>
<code>!ивенты</code>
<code>!даилинет</code>

<b>Пользовательские:</b>"""

chat = [-1001400136881]
users = [529598217, 932736973, 636619912, 555328241, 200635302]
bot = Bot(token=conf.API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["табло"], commands_prefix=['!'], is_reply=True)
async def table_command_reply(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if message.reply_to_message["from"]["is_bot"]:
		pg.message_set(message.reply_to_message.message_id, 1708019201)

@dp.message_handler(commands=["табло"], commands_prefix=['!'])
async def table_command(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ttable = table
	ulist = list()
	pg.message_set(message.message_id+1, 1708019201)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username(f[0])} — {f[1]}\n"
	await message.answer(text=ttable, parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["дать"], commands_prefix=['!'], is_reply=True)
async def point_add(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ulist = list()
	ttable = table
	text = message.text.split()
	items = pg.items()
	oldm = pg.message(message.reply_to_message["from"]["id"])[1] + 1
	if len(text) > 1:
		try:
			n = int(text[1])
		except:
			return 0
	else:
		n = 1
	nlist = list(range(oldm, oldm+n))
	pg.message_set(pg.message(message.reply_to_message["from"]["id"])[1]+n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username(f[0])} — {f[1]}\n"
		if message.reply_to_message["from"]["id"] == f[0]:
			for t in items:
					if t[1] in nlist:
						await bot.send_message(chat_id=chat[0], text=f"{pg.username(f[0])} <b>Вам выпало задание</b> «{t[0]}»:\n<i>{t[2]}</i>", parse_mode="HTML")
	await bot.edit_message_text(chat_id=chat[0], text=ttable, message_id=pg.message(1708019201)[1], parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["забрать"], commands_prefix=['!'], is_reply=True)
async def point_remove(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ttable = table
	ulist = list()
	text = message.text.split()
	if len(text) > 1:
		try:
			n = int(text[1])
		except:
			return 0
	else:
		n = 1
	pg.message_set(pg.message(message.reply_to_message["from"]["id"])[1]-n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=chat[0], text=ttable, message_id=pg.message(1708019201)[1], parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["добавить"], commands_prefix=['!'])
async def wb_update_add(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1:]
	for w in word:
		if w not in BW:
			pg.word_add(w)
			BW = pg.words()
			await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Добавлено:\n" + w)

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["убрать"], commands_prefix=['!'])
async def wb_update_remove(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1:]
	for w in word:
		if w in BW:
			pg.word_remove(w)
			BW = pg.words()
			await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Убрано:\n" + w)

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["создатьпредмет"], commands_prefix=['!'])
async def item_add(message: types.Message):
	text = message.text.split()
	if len(text) < 3:
		return 0
	textt = str()
	for t in text[3:]:
		textt += t + ' '
	pg.item_add(text[1], text[2], textt)
	await message.answer(text=f"<b>🆕Новое задание:</b> «<code>{text[1]}</code>»", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["удалитьпредмет"], commands_prefix=['!'])
async def item_remove(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.item_remove(text[1])
	await message.answer(text=f"<b>🗑Удалено задание:</b> «<code>{text[1]}</code>»", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == users[4], commands=["описание"], commands_prefix=['!'])
async def items_description(message: types.Message):
	tlist = sorted(pg.items(), key=lambda x: x[1])
	text = "<b>Описание заданий:</b>\n\n"
	for t in tlist:
		text += f"{t[1]} <b>{t[0]}</b> — <i>{t[2]}</i>\n"
	await message.answer(text=text, parse_mode="HTML")

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
	await message.answer(text=f"Добавлена команда <code>!{text[1]}</code>", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users, commands=["unset"], commands_prefix=['!'])
async def usercommand_remove(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.command_remove(text[1])
	global CL
	CL = pg.commands()
	await message.answer(text=f"Убрана команда <code>!{text[1]}</code>", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users, commands=["количество"], commands_prefix=['!'])
async def wb_count(message: types.Message):
	text = f"{pg.username(message.from_user.id)} Количество мата в БД: {len(BW)}🙂"
	await message.answer(text=text)

@dp.message_handler(lambda message: message.from_user.id in users, commands=["создатьивент"], commands_prefix=['!'])
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

@dp.message_handler(lambda message: message.from_user.id in users, commands=["удалитьивент"], commands_prefix=['!'])
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

@dp.message_handler(lambda message: message.from_user.id in users, commands=["ивенты"], commands_prefix=['!'])
async def events_command(message: types.Message):
	text = "<b>Ивенты:</b>\n"
	events = pg.events()
	if events != None:
		for e in events:
			text += "\n<i>" + e + "</i>"
	await message.answer(text=text, parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users, commands=["команды", "помощь"], commands_prefix=['!'])
async def help_command(message: types.Message):
	cmds = cmd
	for c in CL:
		cmds += f"\n<code>!{c}</code>"
	await message.answer(text=f"{pg.username(message.from_user.id)}\n{cmds}", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users, commands=["даилинет"], commands_prefix=['!'])
async def yesorno_command(message: types.Message):
	ran = randint(1, 6)
	if ran in (1, 3, 5):
		text = choice(YES_LIST)
	elif ran in (2, 4, 6):
		text = choice(NO_LIST)
	await message.answer(text=f"{pg.username(message.from_user.id)} {text}")

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

@dp.message_handler(lambda message: message.from_user.id in users and message.text[0] == '!')
async def usercommands(message: types.Message):
	cmd = message.text[1:].split()
	if cmd[0] in CL:
		text = pg.commands_text()[pg.commands().index(cmd[0])]
		await message.answer(text=f"{pg.username(message.from_user.id)} {text}", disable_web_page_preview=True)

@dp.message_handler(lambda message: message.from_user.id in users)
async def filter(message: types.Message):
	if message.from_user.username == None:
		pg.username_set(message.from_user.first_name, message.from_user.id)
	else:
		pg.username_set('@'+message.from_user.username, message.from_user.id)
	n = 0
	textt = str()
	seen = set()
	ulist = nlist = uniq = list()
	prnt = False
	ttable = table
	text = message.text.split()
	oldm = pg.message(message.from_user.id)[1]
	items = pg.items()
	for l in text:
		textt += ''.join(t for t in l if t.isalpha()) + ' '
	for x in textt.split():
		if x not in seen:
			uniq.append(x)
			seen.add(x)
	for t in uniq:
		ratio = process.extract(t.lower(), BW)
		for r in ratio:
			print(message.from_user.first_name, r[0], r[1])
			if r[1] > 92:
				n += 1
				nlist.append(oldm+n)
			else:
				pass
	if n == 0:
		return 0
	pg.message_set(pg.message(message.from_user.id)[1]+n, message.from_user.id)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username(f[0])} — {f[1]}\n"
		if message.from_user.id == f[0]:
			for t in items:
				if t[1] in nlist:
					await bot.send_message(chat_id=chat[0], text=f"{pg.username(f[0])} <b>Вам выпало задание</b> «{t[0]}»:\n<i>{t[2]}</i>", parse_mode="HTML")
	await bot.edit_message_text(chat_id=chat[0], text=ttable, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

	# ~0,43% chance
	ranlen = range(64)
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

@dp.message_handler(lambda message: message.from_user.id not in users, content_types=types.message.ContentType.ANY)
async def messages(message: types.Message):
	link_markup = types.inline_keyboard.InlineKeyboardMarkup(row_width=2)
	author_button = types.inline_keyboard.InlineKeyboardButton(text="Связаться с автором", url="https://t.me/rvbsm")
	# _button = types.inline_keyboard.InlineKeyboardButton(text="", url="")
	link_markup.add(author_button)
	await message.answer(text="<b>Полезные ссылки:</b>", parse_mode="HTML", reply_markup=link_markup)

async def db_update():
	while True:
		global pg, BW, CL
		pg = DataBase(conf.DATABASE)
		BW = pg.words()
		CL = pg.commands()
		logging.info("DB Updated")
		await asyncio.sleep(240)

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	loop = asyncio.get_event_loop()
	loop.create_task(db_update())
	executor.start_polling(dispatcher=dp, loop=loop)
