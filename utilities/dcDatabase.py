from datetime import datetime, timedelta
import sqlite3
import json
import os

class DB:
    def __init__(self, directory, filename):
        os.makedirs(directory, exist_ok=True)
        self.db_path = os.path.join(directory, filename)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
               CREATE TABLE IF NOT EXISTS guilds (
                   guild_id  INTEGER PRIMARY KEY,
                   forward_roles TEXT  DEFAULT '[]'
               )
               ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                   user_id INTEGER,
                   guild_id INTEGER,
                   date TEXT,
                   activity_points REAL DEFAULT 0,
                   PRIMARY KEY (user_id, guild_id, date)
                )
               ''')
            conn.commit()

    def add_forward_guild(self, guild_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)",
                (guild_id,)
            )
            conn.commit()

    def remove_forward_guild(self, guild_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
            conn.commit()

    def get_all_forward_guilds(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT guild_id FROM guilds")
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def get_forward_roles(self, guild_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT forward_roles FROM guilds WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return []

    def add_forward_role(self, guild_id, role_id):
        roles = self.get_forward_roles(guild_id)

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

    def remove_forward_role(self, guild_id, role_id):
        roles = self.get_forward_roles(guild_id)

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

    def _group_data_by_step(self, db_data, start_date_obj, end_date_obj, step):
        stats = {}
        current_date = start_date_obj

        while current_date <= end_date_obj:
            group_sum = 0.0
            group_label = current_date.strftime('%Y-%m-%d')

            for _ in range(step):
                if current_date > end_date_obj:
                    break

                date_str = current_date.strftime('%Y-%m-%d')
                group_sum += db_data.get(date_str, 0.0)
                current_date += timedelta(days=1)

            stats[group_label] = round(group_sum, 2)

        return stats

    def add_activity_points(self, user_id, guild_id, points, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_activity (user_id, guild_id, date, activity_points)
                VALUES (?, ?, ?, ?) ON CONFLICT(user_id, guild_id, date) DO
                UPDATE SET
                   activity_points = activity_points + excluded.activity_points
                ''', (user_id, guild_id, date, points))
            conn.commit()

    def get_activity_points(self, user_id, guild_id, days_back, end_days_back=0):
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        end_date = (datetime.now() - timedelta(days=end_days_back)).strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT SUM(activity_points)
                FROM user_activity
                WHERE user_id = ?
                 AND guild_id = ?
                 AND date BETWEEN ?
                 AND ?
                ''', (user_id, guild_id, start_date, end_date))

            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0.0

    def get_top_active_users(self, guild_id, days_back, limit=10):
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, SUM(activity_points) as total
                FROM user_activity
                WHERE guild_id = ? AND date >= ?
                GROUP BY user_id
                ORDER BY total DESC
                   LIMIT ?
                ''', (guild_id, start_date, limit))
            return cursor.fetchall()

    def get_user_activity_stats(self, name, user_id, guild_id, days_back, end_days_back=0, step=1):
        start_date_obj = datetime.now() - timedelta(days=days_back)
        end_date_obj = datetime.now() - timedelta(days=end_days_back)

        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT date, activity_points
                           FROM user_activity
                           WHERE user_id = ? AND guild_id = ? AND date BETWEEN ? AND ?
                           ORDER BY date ASC
                           ''', (user_id, guild_id, start_date_str, end_date_str))
            db_data = dict(cursor.fetchall())

        stats = self._group_data_by_step(db_data, start_date_obj, end_date_obj, step)
        return {"name": name, **stats}

    def get_group_activity_stats(self, name, user_ids, guild_id, days_back, end_days_back=0, step=1):
        start_date_obj = datetime.now() - timedelta(days=days_back)
        end_date_obj = datetime.now() - timedelta(days=end_days_back)
        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_str = end_date_obj.strftime('%Y-%m-%d')

        placeholders = ', '.join(['?'] * len(user_ids))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f'''
                SELECT date, SUM(activity_points) 
                FROM user_activity 
                WHERE guild_id = ? AND date BETWEEN ? AND ? AND user_id IN ({placeholders})
                GROUP BY date
                ORDER BY date ASC
            '''
            params = [guild_id, start_date_str, end_date_str] + list(user_ids)
            cursor.execute(query, params)
            db_data = dict(cursor.fetchall())

        stats = self._group_data_by_step(db_data, start_date_obj, end_date_obj, step)
        return {"name": name, **stats}