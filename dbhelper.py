import sqlite3
from models import Deal

class DBHelper:
    def __init__(self):
        self.dbname = "amzdeals.db"
        self.conn = None
        self.get_db_connection()
    
    def get_db_connection(self):
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.dbname, check_same_thread=False)
            except Error as e:
                print(e)
        return self.conn

    def create_deals_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS deals (
                id integer PRIMARY KEY,
                offer_title text,
                title text UNIQUE,
                deal_price text,
                mrp text,
                off_percent text,
                rating text,
                claim_percent text,
                time_end text,
                url text,
                off_percent_int integer,
                review_count integer,
                updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(review_count)
                );'''
        self.conn.execute(sql)
        self.conn.commit()
    
    def create_test_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS test (
                id integer PRIMARY KEY,
                mid text,
                message text
                );'''
        self.conn.execute(sql)
        self.conn.commit()
    
    def create_search_history_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS search_history (
                chat_id text PRIMARY KEY,
                offset integer,
                updated DATETIME DEFAULT CURRENT_TIMESTAMP
                );'''
        self.conn.execute(sql)
        self.conn.commit()
    
    def get_search_history(self, chat_id,):

        sql = "SELECT * FROM search_history WHERE chat_id='"+ str(chat_id) +"';"
        cur = self.conn.execute(sql)

        rows = cur.fetchall()
        print(f'Count of chat_id results= {len(rows)}')
        return rows
    
    def insert_or_update_search_history(self, chat_id,offset):

        history = self.get_search_history(chat_id)

        n_history = len(history)
        print(f'insert_or_update_search_history::Count of chat_id results= {n_history}')

        if n_history>0:
            sql = "UPDATE search_history SET offset=" + str(offset) + " WHERE chat_id='"+ str(chat_id) +"';"
            cur = self.conn.execute(sql)
        else:
            sql = 'INSERT INTO search_history(chat_id,offset) VALUES(?,?)'
            data = (chat_id, offset)
            cur = self.conn.execute(sql, data)
        self.conn.commit()

        return cur.lastrowid
    
    def delete_test_table(self):
        sql = '''DROP table IF EXISTS test;'''

        self.conn.execute(sql)
        self.conn.commit()
    
    def delete_deals_table(self):
        sql = '''DROP table IF EXISTS deals;'''

        self.conn.execute(sql)
        self.conn.commit()
    
    def insert_test_data(self, item):
        # sql = ''' INSERT INTO tasks(name,priority,status_id,project_id,begin_date,end_date)
        #       VALUES(?,?,?,?,?,?) '''
        sql = '''INSERT INTO test(mid, message) 
                VALUES (?,?)'''
        data = (item.id, item.message)
        cur = self.conn.execute(sql, data)
        self.conn.commit()

        return cur.lastrowid

    def insert_deals_data(self, deal):
        # sql = ''' INSERT INTO tasks(name,priority,status_id,project_id,begin_date,end_date)
        #       VALUES(?,?,?,?,?,?) '''
        sql = '''INSERT INTO deals(offer_title, title, deal_price, mrp, off_percent, rating, review_count, off_percent_int, claim_percent, time_end, url) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
        
        data = (deal.offer_title, deal.title, deal.deal_price, 
                deal.mrp, deal.off_percent, deal.rating, deal.review_count, deal.off_percent_int, deal.claim_percent, deal.time_end, deal.url)
        try:
            cur = self.conn.execute(sql, data)
            self.conn.commit()

            return cur.lastrowid
        except:
            return -1

    def get_deals_data(self, limit=5, offset=0):
        # sql = '''SELECT * FROM deals LIMIT 5;'''
        sql = 'SELECT * FROM deals order by review_count desc LIMIT '+str(limit) +' OFFSET '+ str(offset) +';'

        cur = self.conn.execute(sql)

        rows = cur.fetchall()

        deals = []

        for row in rows:
            deal = Deal()
            deal.offer_title = row[1]
            deal.title = row[2]
            deal.deal_price = row[3]
            deal.mrp = row[4]
            deal.off_percent = row[5]
            deal.rating = row[6]
            deal.review_count = row[6]
            deal.off_percent_int = row[6]
            deal.claim_percent = row[7]
            deal.time_end = row[8]
            deal.url = row[9]
            deal.updated = row[10]
            deals.append(deal)
        
        return deals
        
