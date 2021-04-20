import psycopg2

class DataBase:
	def __init__(self):
		self.dhost = "rvbsm-postgre.ct4bvuutiewe.eu-west-1.rds.amazonaws.com"
		self.dname = "fivelyceumbot_postgre"
		self.dusr = "master"
		self.dpwd = "22rusbesm22"
		self.dport = "5432"
		self.conpg = psycopg2.connect(user=self.dusr, password=self.dpwd, host=self.dhost, port=self.dport, dbname=self.dname, sslrootcert="rds-combined-ca-bundle.pem", sslmode="verify-full")
		self.conpg.autocommit = True
		self.curpg = self.conpg.cursor()

	def message(self, uid):
		self.curpg.execute('''SELECT "user.id", "message.count" FROM "user" WHERE "user.id" = %s''', (uid,))
		res = self.curpg.fetchall()
		for r in res:
			return r[0], r[1]
			
	def message_edit(self, count, uid):
		self.curpg.execute('''UPDATE "user" SET "message.count" = %s WHERE "user.id" = %s''', (count, uid))

	def username_export(self, user_id: int):
		self.curpg.execute('''SELECT "name" FROM "user" WHERE "user.id" = %s''', (user_id,))
		result = self.curpg.fetchall()
		for i in result:
			return i[0]

	def username_import(self, username, user_id: int):
		self.curpg.execute('''UPDATE "user" SET "name" = %s WHERE "user.id" = %s''', (username, user_id))

	def word_import(self, word):
		self.curpg.execute('''INSERT INTO "words" ("word") VALUES (%s)''', (word,))

	def word_remove(self, word):
		self.curpg.execute('''DELETE FROM "words" WHERE "word" = %s''', (word,))

	def words(self):
		self.curpg.execute('''SELECT * FROM "words"''')
		rows = self.curpg.fetchall()
		for r in rows:
			return[r[0] for r in rows]

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

	def command_import(self, command, text: str):
		self.curpg.execute('''INSERT INTO "commands" ("command", "text") VALUES (%s, %s)''', (command, text))

	def command_remove(self, command):
		self.curpg.execute('''DELETE FROM "commands" WHERE "command" = %s''', (command,))

	def tovar_import(self, name, price, desc):
		self.curpg.execute('''INSERT INTO "shop" ("name", "price", "description") VALUES (%s, %s, %s)''', (name, price, desc))

	def tovar_remove(self, name):
		self.curpg.execute('''DELETE FROM "shop" WHERE "name" = %s''', (name,))

	def tovars(self):
		self.curpg.execute('''SELECT * FROM "shop"''')
		rows = self.curpg.fetchall()
		return rows