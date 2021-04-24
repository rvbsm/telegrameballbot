import psycopg2

"""	with psycopg2.connect(self.url) as self.conpg:
			self.conpg.autocommit = True
			with self.conpg.cursor() as self.curpg:"""

class DataBase:
	def __init__(self, db: dict):
		self.url = f"host={db['dbhost']} port={db['dbport']} dbname={db['dbname']} user={db['dbuser']} password={db['dbpass']} sslmode=verify-full sslrootcert=rds-combined-ca-bundle.pem"
		self.conpg = psycopg2.connect(self.url)
		self.conpg.autocommit = True
		self.curpg = self.conpg.cursor()


	def message(self, user_id: int):
		self.curpg.execute('''SELECT "user.id", "message.count" FROM "user" WHERE "user.id" = %s''', (user_id,))
		res = self.curpg.fetchall()
		for r in res:
			return r[0], r[1]

	def message_set(self, count: int, user_id: int):
		self.curpg.execute('''UPDATE "user" SET "message.count" = %s WHERE "user.id" = %s''', (count, user_id))
		return True


	def username(self, user_id: int):
		self.curpg.execute('''SELECT "name" FROM "user" WHERE "user.id" = %s''', (user_id,))
		result = self.curpg.fetchall()
		for i in result:
			return i[0]

	def username_set(self, username: str, user_id: int):
		self.curpg.execute('''UPDATE "user" SET "name" = %s WHERE "user.id" = %s''', (username, user_id))
		return True


	def words(self):
		self.curpg.execute('''SELECT * FROM "words"''')
		rows = self.curpg.fetchall()
		for r in rows:
			return[r[0] for r in rows]

	def word_add(self, word: str):
		self.curpg.execute('''INSERT INTO "words" ("word") VALUES (%s)''', (word,))
		return True

	def word_remove(self, word: str):
		self.curpg.execute('''DELETE FROM "words" WHERE "word" = %s''', (word,))
		return True


	def commands(self):
		self.curpg.execute('''SELECT "command" FROM "commands"''')
		rows = self.curpg.fetchall()
		for r in rows:
			return[r[0] for r in rows]

	def commands_text(self):
		self.curpg.execute('''SELECT "text" FROM "commands"''')
		rows = self.curpg.fetchall()
		for r in rows:
			return[r[0] for r in rows]

	def command_add(self, command: str, text: str):
		self.curpg.execute('''INSERT INTO "commands" ("command", "text") VALUES (%s, %s)''', (command, text))
		return True

	def command_remove(self, command: str):
		self.curpg.execute('''DELETE FROM "commands" WHERE "command" = %s''', (command,))
		return True


	def items(self):
		self.curpg.execute('''SELECT * FROM "shop"''')
		rows = self.curpg.fetchall()
		return rows

	def item_add(self, name: str, price: int, desc: str):
		self.curpg.execute('''INSERT INTO "shop" ("name", "price", "description") VALUES (%s, %s, %s)''', (name, price, desc))
		return True

	def item_remove(self, name: str):
		self.curpg.execute('''DELETE FROM "shop" WHERE "name" = %s''', (name,))
		return True


	def events(self):
		self.curpg.execute('''SELECT "name" FROM "events"''')
		rows = self.curpg.fetchall()
		for r in rows:
			return[r[0] for r in rows]

	def event_add(self, name: str):
		self.curpg.execute('''INSERT INTO "events" ("name") VALUES (%s)''', (name,))
		return True

	def event_remove(self, name: str):
		self.curpg.execute('''DELETE FROM "events" WHERE "name" = %s''', (name,))
		return True

	def dictionary(self):
		self.curpg.execute('''SELECT * FROM "dictionary"''')
		rows = self.curpg.fetchall()
		return rows

	def dictionary_words(self):
		self.curpg.execute('''SELECT "word" FROM "dictionary"''')
		rows = self.curpg.fetchall()
		for r in rows:
			return[r[0] for r in rows]

	def dictionary_count(self, word: str):
		self.curpg.execute('''SELECT "count" FROM "dictionary" WHERE "word" = %s''', (word,))
		result = self.curpg.fetchall()
		for r in result:
			return r[0]

	def dictionary_add(self, word: str, author: int):
		if word != '':
			self.curpg.execute('''INSERT INTO "dictionary" ("word", "count", "author") VALUES (%s, 1, %s)''', (word, author))
		return True

	def dictionary_set(self, word: str, count: int):
		self.curpg.execute('''UPDATE "dictionary" SET "count" = %s WHERE "word" = %s''', (count, word))
		return True

	def dictionary_remove(self, word: str):
		self.curpg.execute('''DELETE FROM "dictionary" WHERE "word" = %s''', (word,))
		return True

	def logs(self):
		self.curpg.execute('''SELECT * FROM "logs"''', ())
		rows = self.curpg.fetchall()
		for r in rows:
			return[r for r in rows]

	def log_add(self, message_id: int, user_id: int, percentage: int, word: str, similar: str):
		self.curpg.execute('''INSERT INTO "logs" ("date", "time", "message_id", "user.id", "percentage", "word", "similar") VALUES (CURRENT_DATE, LOCALTIME(0), %s, %s, %s, %s, %s)''', (message_id, user_id, percentage, word, similar))
		return True
