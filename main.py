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
# СОРТИРОВКА

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

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["мат"], commands_prefix=['!'], is_reply=True)
async def add_point(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ttable = table
	ulist = list()
	try:
		if message.text[4:] == '':
			n = 1
		else:
			n = int(message.text[4:])
	except:
		return 0
	pg.message_edit(pg.message(message.reply_to_message["from"]["id"])[1]+n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=message.chat.id, text=ttable, message_id=pg.message(1708019201)[1], parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["немат"], commands_prefix=['!'], is_reply=True)
async def remove_point(message: types.Message):
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	ttable = table
	ulist = list()
	try:
		if message.text[6:] == '':
			n = 1
		else:
			n = int(message.text[6:])
	except:
		return 0
	pg.message_edit(pg.message(message.reply_to_message["from"]["id"])[1]-n, message.reply_to_message["from"]["id"])
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=message.chat.id, text=ttable, message_id=pg.message(1708019201)[1], parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["плюс"], commands_prefix=['!'])
async def new_mat(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1]
	if word not in BW:
		pg.word_import(word)	
		BW = pg.words()
		await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Добавлено:\n" + word)

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=["минус"], commands_prefix=['!'])
async def remove_mat(message: types.Message):
	global BW
	await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	if len(message.text.split()) < 2:
		return 0
	word = message.text.split()[1]
	if word in BW:
		pg.word_remove(word)
		BW = pg.words()
		await bot.send_message(chat_id=message.from_user.id, text="Обновлён список запрещёнки. Убрано:\n" + word)

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=['set'], commands_prefix=['!'])
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

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=['unset'], commands_prefix=['!'])
async def remove_com(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	pg.command_remove(text[1])
	global CL
	CL = pg.commands()
	await message.answer(text=f"Убрана команда !{text[1]}")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=['товар'], commands_prefix=['!'])
async def add_tovar(message: types.Message):
	text = message.text.split()
	if len(text) < 3:
		return 0
	textt = str()
	for t in text[2:]:
		textt += t + ' '
	pg.tovar_import(textt.strip(), text[1])
	await message.answer(text=f"Новый товар {textt}")

@dp.message_handler(lambda message: message.from_user.id == 200635302, commands=['удалить'], commands_prefix=['!'])
async def remove_tovar(message: types.Message):
	text = message.text.split()
	if len(text) < 2:
		return 0
	textt = str()
	for t in text[1:]:
		textt += t + ' '
	pg.tovar_remove(textt.strip())
	await message.answer(text=f"Убран товар {textt}")

@dp.message_handler(commands=['товары'], commands_prefix=['!'])
async def tovary(message: types.Message):
	await message.answer(text=pg.tovars(), parse_mode="HTML")

@dp.message_handler(lambda message: message.text[0] == '!')
async def command_com(message: types.Message):
	command = message.text[1:].split()
	if command in CL:
		text = pg.commands_text()[pg.commands().index(message.text[0])]
		await message.answer(text=f"@{pg.username_export(message.from_user.id)} {text}")
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
					print(t.lower(), r[1])
				else:
					print(t.lower(), r[1])
		if n == 0:
			return 0
		pg.message_edit(pg.message(message.from_user.id)[1]+n, message.from_user.id)
		for u in users:
			ulist.append(pg.message(u))
		ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
		for f in ulist:
			ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
		await bot.edit_message_text(chat_id=message.chat.id, text=ttable, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

@dp.message_handler()
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
				print(t.lower(), "is", r[1])
			else:
				print("Nope", r[1])
	if n == 0:
		return 0
	pg.message_edit(pg.message(message.from_user.id)[1]+n, message.from_user.id)
	for u in users:
		ulist.append(pg.message(u))
	ulist = sorted(ulist, key=lambda x: x[1], reverse=True)
	for f in ulist:
		ttable += f"{pg.username_export(f[0])} — {f[1]}\n"
	await bot.edit_message_text(chat_id=message.chat.id, text=ttable, message_id=int(pg.message(1708019201)[1]), parse_mode="HTML")

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