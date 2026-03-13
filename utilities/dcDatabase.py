import sqlite3
import os
import json

class DB:
    def __init__(self, directory, filename):
        os.makedirs(directory, exist_ok=True)
        self.db_path = os.path.join(directory, filename)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
               CREATE TABLE IF NOT EXISTS guilds  (
                   guild_id  INTEGER PRIMARY KEY,
                   forward_roles TEXT  DEFAULT '[]'
               )
               ''')
            conn.commit()

    def add_guild(self, guild_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)",
                (guild_id,)
            )
            conn.commit()

    def remove_guild(self, guild_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
            conn.commit()

    def get_all_guilds(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT guild_id FROM guilds")
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def get_roles(self, guild_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT forward_roles FROM guilds WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return []

    def add_role(self, guild_id, role_id):
        roles = self.get_roles(guild_id)

        if role_id not in roles:
            roles.append(role_id)
            roles_json = json.dumps(roles)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE guilds SET forward_roles = ? WHERE guild_id = ?",
                    (roles_json, guild_id)
                )
                conn.commit()

    def remove_role(self, guild_id, role_id):
        roles = self.get_roles(guild_id)

        if role_id in roles:
            roles.remove(role_id)
            roles_json = json.dumps(roles)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE guilds SET forward_roles = ? WHERE guild_id = ?",
                    (roles_json, guild_id)
                )
                conn.commit()