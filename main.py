from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher.filters import IsReplyFilter
from aiogram.utils.executor import start_webhook
import asyncio, logging, psycopg2, os
from fuzzywuzzy import process
import conf
from pgdb import DataBase

table = """
<b>Е-БАЛЛЫ</b>

"""

chat = [-1001400136881]
users = [529598217, 932736973, 636619912, 555328241, 200635302]

bot = Bot(token=conf.API_TOKEN)
dp = Dispatcher(bot)
pg = DataBase()
BW = pg.words()
CL = pg.commands()

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["табло"], commands_prefix=['!'], is_reply=True)
async def table_ch(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if message.reply_to_message["from"]["is_bot"]:
		pg.message_edit(message.reply_to_message.message_id, 1708019201)

@dp.message_handler(commands=["табло"], commands_prefix=['!'])
async def table_com(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ttable = table
	ulist = list()
	pg.message_edit(message.message_id+1, 1708019201)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
	await message.answer(text=ttable, parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["плюс"], commands_prefix=['!'], is_reply=True)
async def add_point(message: types.Message):
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
	pg.message_edit(pg.message(message.reply_to_message["from"]["id"])[1]+n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=-1001400136881, text=ttable, message_id=pg.message(1708019201)[1], parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["минус"], commands_prefix=['!'], is_reply=True)
async def remove_point(message: types.Message):
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
	pg.message_edit(pg.message(message.reply_to_message["from"]["id"])[1]-n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=-1001400136881, text=ttable, message_id=pg.message(1708019201)[1], parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["добавить"], commands_prefix=['!'])
async def new_mat(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1:]
	for w in word:
		if w not in BW:
			pg.word_import(w)
			BW = pg.words()
			await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Добавлено:\n" + w)

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["убрать"], commands_prefix=['!'])
async def remove_mat(message: types.Message):
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

@dp.message_handler(commands=["количество"], commands_prefix=['!'])
async def count_mat(message: types.Message):
	await message.answer(text=f"Количество мата в БД: {len(BW)}🙂")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["set"], commands_prefix=['!'])
async def add_com(message: types.Message):
	text = message.text.split()
	if len(text) < 3:
		return 0
	textt = str()
	for t in text[2:]:
		textt += t + ' '
	pg.command_import(text[1], textt)
	global CL
	CL = pg.commands()
	await message.answer(text=f"Добавлена команда !{text[1]}")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["unset"], commands_prefix=['!'])
async def remove_com(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.command_remove(text[1])
	global CL
	CL = pg.commands()
	await message.answer(text=f"Убрана команда !{text[1]}")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["создать"], commands_prefix=['!'])
async def add_tovar(message: types.Message):
	text = message.text.split()
	if len(text) < 3:
		return 0
	textt = str()
	for t in text[3:]:
		textt += t + ' '
	pg.tovar_import(text[1], text[2], textt)
	await message.answer(text=f"<b>🆕Новое задание:</b> «<code>{text[1]}</code>»", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["удалить"], commands_prefix=['!'])
async def remove_tovar(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.tovar_remove(text[1])
	await message.answer(text=f"<b>🗑Удалено задание:</b> «<code>{text[1]}</code>»", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["описание"], commands_prefix=['!'])
async def description_tovar(message: types.Message):
	tlist = sorted(pg.tovars(), key=lambda x: x[1])
	text = "<b>Описание заданий:</b>\n\n"
	for t in tlist:
		text += f"{t[1]} <b>{t[0]}</b> — <i>{t[2]}</i>\n"
	await message.answer(text=text, parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users or message.chat.id in chat, commands=['задания', "квесты", "наказания"], commands_prefix=['!'])
async def tovary(message: types.Message):
	a = "<b>Грядущие задания:</b> \n\n"
	tlist = sorted(pg.tovars(), key=lambda x: x[1])
	for t in tlist:
		if pg.message(message.from_user.id)[1] > int(t[1]):
			a += f"<s>{t[1]} — <code>{t[0]}</code></s>\n"
		else:
			a += f"{t[1]} — <code>{t[0]}</code>\n"
	await message.answer(text=f"{pg.username_export(message.from_user.id)} {a}", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users, commands=["команды", "помощь"], commands_prefix=['!'])
async def help_command(message: types.Message):
	cmds = "!табло\n!плюс / !минус {количество}\n!добавить / !убрать &lt;матслово&gt;\n!set / !unset &lt;команда&gt; {текст}\n!создать / !удалить &lt;название&gt; {цена} {описание}\n\nДопуступные всем:\n<code>!задания</code>\n<code>!количество</code>\n<code>!описание</code>\n<code>!помощь</code>"
	for c in CL:
		cmds += f"\n<code>!{c}</code>"
	await message.answer(text=f"{pg.username_export(message.from_user.id)}\n{cmds}", parse_mode="HTML")

@dp.message_handler(lambda message: message.text[0] == '!' and (message.from_user.id in users or message.chat.id in chat))
async def command_com(message: types.Message):
	cmd = message.text[1:].split()
	if cmd[0] in CL:
		text = pg.commands_text()[pg.commands().index(cmd[0])]
		await message.answer(text=f"{pg.username_export(message.from_user.id)} {text}")
	else:
		n = 0
		ttable = table
		text = message.text.split()
		textt = str()
		ulist = list()
		for l in text:
			textt += ''.join(t for t in l if t.isalpha()) + ' '
		seen = set()
		uniq = list()
		for x in textt.split():
			if x not in seen:
				uniq.append(x)
				seen.add(x)
		for t in uniq:
			ratio = process.extract(t.lower(), BW)
			for r in ratio:
				if r[1] > 92:
					n += 1
					print(pg.username_export(message.from_user.id), t.lower(), r[1])
				else:
					pass
		if n == 0:
			return 0
		pg.message_edit(pg.message(message.from_user.id)[1]+n, message.from_user.id)
		for u in users:
			ulist.append(pg.message(u))
		ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
		for f in ulist:
			ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
		await bot.edit_message_text(chat_id=-1001400136881, text=ttable, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in users or message.chat.id in chat)
async def filter(message: types.Message):
	if message.from_user.username == None:
		pg.username_import(message.from_user.first_name, message.from_user.id)
	else:
		pg.username_import('@'+message.from_user.username, message.from_user.id)
	n = 0
	ttable = table
	text = message.text.split()
	textt = str()
	ulist = list()
	for l in text:
		textt += ''.join(t for t in l if t.isalpha()) + ' '
	seen = set()
	uniq = list()
	for x in textt.split():
		if x not in seen:
			uniq.append(x)
			seen.add(x)
	for t in uniq:
		ratio = process.extract(t.lower(), BW)
		for r in ratio:
			if r[1] > 92:
				n += 1
				print(pg.username_export(message.from_user.id), t.lower(), r[1])
			else:
				pass
	if n == 0:
		return 0
	pg.message_edit(pg.message(message.from_user.id)[1]+n, message.from_user.id)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
		for t in pg.tovars():
			if f[1] == t[1]:
				await message.answer(text=f"{pg.username_export(f[0])} <b>Вам выпало задание</b> «{t[0]}»:\n<i>{t[2]}</i>", parse_mode="HTML")
	await bot.edit_message_text(chat_id=-1001400136881, text=ttable, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

@dp.message_handler()
async def message(message: types.Message):
	await message.answer(text="Свяжитесь с @rvbsm")

async def db_update():
	await asyncio.sleep(240)
	while True:
		global pg, BW, CL
		pg = DataBase()
		BW = pg.words()
		CL = pg.commands()
		await asyncio.sleep(240)

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	loop = asyncio.get_event_loop()
	loop.create_task(db_update())
	executor.start_polling(dispatcher=dp, loop=loop)