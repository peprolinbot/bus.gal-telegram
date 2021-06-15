import sqlite3
import busGal_api

#Creates a class for database
class Database:
    def __init__(self, db_file):
        self.db_file = db_file

    def get_favorite_stops(self, user_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)
        db_cursor.execute("SELECT stop_id FROM favorite_stops WHERE telegram_user_id=?", s)
        return_stops=[]
        for row in db_cursor.fetchall():
            return_stops.append(row[0])
        return return_stops

    def get_favorite_stops_objects(self, user_id):
        stop_ids = self.get_favorite_stops(user_id)
        return_stops = []
        online_stops = busGal_api.get_stops()
        for stop_id in stop_ids:
            for stop_online in online_stops:
                if stop_online.id == int(stop_id):
                    return_stops.append(stop_online)
        return return_stops

    def insert_new_favorite_stop(self, user_id, stop_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id, stop_id,)
        db_cursor.execute("INSERT INTO favorite_stops VALUES(?,?)", s)
        db.commit()
    
    def delete_favorite_stop(self, user_id, stop_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id, stop_id,)
        db_cursor.execute("DELETE FROM favorite_stops WHERE telegram_user_id = ? AND stop_id = ?", s)
        db.commit()


    def auto_insert_to_expedition(self, user_id, arg):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)       
        db_cursor.execute("SELECT * FROM active_expeditions WHERE telegram_user_id=?", s)
        out=db_cursor.fetchall()
        if out == [] :
            s = (user_id, arg,)
            db_cursor.execute("INSERT INTO active_expeditions VALUES(?, ?, NULL, NULL)", s)
            column_name="origin_stop_id"
        else:
            i=0    
            for column in out[0]:
                if column == None:
                    db_cursor.execute("PRAGMA table_info(active_expeditions)")
                    column_name=db_cursor.fetchall()[i][1]
                    if not isinstance(arg, int) and column_name == "date":
                        space_char = ''.join([i for i in arg if not i.isdigit()])[0]
                        arg = arg.replace(space_char, "-")
                    s = (arg, user_id,)
                    db_cursor.execute("UPDATE active_expeditions SET " + column_name + " = ? WHERE telegram_user_id = ?", s)
                    break
                i += 1
        
        db.commit()
        return column_name

    def remove_expedition(self, user_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)       
        db_cursor.execute("DELETE FROM active_expeditions WHERE telegram_user_id=?", s)
        db.commit()

    def get_expedition_values(self, user_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)       
        db_cursor.execute("SELECT * FROM active_expeditions WHERE telegram_user_id=?", s)
        out=db_cursor.fetchall()
        if out == []:
            return None
        return_values = []
        for column in out[0]:
            if column != None:
                return_values.append(column)
        return_values.pop(0)
        return return_values

    def set_state(self, user_id, state):
        possible_states = ["main_menu", "favorites_menu", "search_menu", "stop_menu"]
        if not state in possible_states:
            raise Exception(f"State msut be one of the following: {', '.join(possible_states)}")

        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)
        db_cursor.execute("SELECT * FROM states WHERE telegram_user_id=?", s)
        user_exists=bool(db_cursor.fetchall())
        if user_exists:
            s = (state, user_id,)
            db_cursor.execute("UPDATE states SET state = ? WHERE telegram_user_id = ?", s)
        else:
            s = (user_id, state,) 
            db_cursor.execute("INSERT INTO states VALUES(?,?)", s)
            
        db.commit()

    def get_state(self, user_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)
        db_cursor.execute("SELECT state FROM states WHERE telegram_user_id=?", s)
        out = db_cursor.fetchall()[0][0]
        return out
    
    def delete_Everything_from_user(self, user_id):
        db = sqlite3.connect(self.db_file)
        db_cursor = db.cursor()
        s = (user_id,)       
        db_cursor.execute("DELETE FROM active_expeditions WHERE telegram_user_id=?", s)
        db_cursor.execute("DELETE FROM favorite_stops WHERE telegram_user_id=?", s)
        db.commit() 
