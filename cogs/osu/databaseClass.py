import mysql.connector
# from pbwrap import Pastebin
from decouple import config
import asyncio
import os

class DatabaseClass():
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="bot",
            passwd=config('DBPASS'),
            database="Kogomi"
        )
        self.cursor = self.db.cursor()

    # def fetch_pb(self):
    #     pb = Pastebin('')
    #     pb.authenticate(os.environ['DEFAULTUSER'],os.environ['PBINKEY'])
    #     return pb

    async def refresh(self):
        print("Refreshing DB...")
        self.db.close()
        self.cursor.close()
        self.db = mysql.connector.connect(
            host="localhost",
            user="bot",
            passwd=config('DBPASS'),
            database="Kogomi"
        )
        self.cursor = self.db.cursor()
        print("Complete.")

    def fetch_osuname(self, discid:int):
        sql = f"SELECT osuname FROM users WHERE discid = '{discid}'"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if len(res) == 0:
            return False
        return res[0][0]

    def fetch_osuid(self, discid):
        sql = f"SELECT osuid FROM users WHERE discid = '{discid}'"
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        if len(res) == 0:
            return False
        return res[0][0]

    def change_osuid(self, discid, osuid, osuname):
        try:
            if not self.create_user(discid, osuid, osuname):
                sql = f"UPDATE users SET osuid = '{osuid}', osuname = '{osuname}' WHERE discid = '{discid}'"
                self.cursor.execute(sql)
                self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def change_osuname(self, discid, osuname):
        try:
            sql = f"UPDATE users SET osuname = '{osuname}' WHERE discid = '{discid}'"
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def create_user(self, discid, osuid = None, osuname = None, loluser = None, lolregion = None):
        self.cursor.execute(f"SELECT * FROM users WHERE discid = '{discid}'")
        res = self.cursor.fetchall()
        if len(res) == 0:
            sql = "INSERT INTO users (discid, osuid, osuname, loluser, lolregion) VALUES (%s, %s, %s, %s, %s)"
            val = (discid, osuid, osuname, loluser, lolregion)
            self.cursor.execute(sql, val)
            self.db.commit()
            return True
        return False
