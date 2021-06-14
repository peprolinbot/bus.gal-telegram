import sqlite3
import busGal_api

#Creates a class for database
class Database:
    def __init__(self, dbFile):
        self.dbFile = dbFile

    def get_favorite_stops(self, userId):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId,)
        dbCursor.execute("SELECT stopId FROM favoriteStops WHERE telegramUserId=?", s)
        returnStops=[]
        for row in dbCursor.fetchall():
            returnStops.append(row[0])
        return returnStops

    def get_favorite_stops_objects(self, userId):
        stop_ids = self.get_favorite_stops(userId)
        return_stops = []
        online_stops = busGal_api.get_stops()
        for stop_id in stop_ids:
            for stop_online in online_stops:
                if stop_online.id == int(stop_id):
                    return_stops.append(stop_online)
        return return_stops

    def insert_new_favorite_stop(self, userId, stopId):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId, stopId,)
        dbCursor.execute("INSERT INTO favoriteStops VALUES(?,?)", s)
        db.commit()
    
    def delete_favorite_stop(self, userId, stopId):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId, stopId,)
        dbCursor.execute("DELETE FROM favoriteStops WHERE telegramuserId = ? AND stopId = ?", s)
        db.commit()


    def auto_insert_to_expedition(self, userId, arg):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId,)       
        dbCursor.execute("SELECT * FROM activeExpeditions WHERE telegramUserId=?", s)
        out=dbCursor.fetchall()
        if out == [] :
            s = (userId, arg,)
            dbCursor.execute("INSERT INTO activeExpeditions VALUES(?, ?, NULL, NULL)", s)
            columnName="originStopId"
        else:
            i=0    
            for column in out[0]:
                if column == None:
                    dbCursor.execute("PRAGMA table_info(activeExpeditions)")
                    columnName=dbCursor.fetchall()[i][1]
                    if not isinstance(arg, int) and columnName == "date":
                        spacerChar = ''.join([i for i in arg if not i.isdigit()])[0]
                        arg = arg.replace(spacerChar, "-")
                    s = (arg, userId,)
                    dbCursor.execute("UPDATE activeExpeditions SET " + columnName + " = ? WHERE telegramUserId = ?", s)
                    break
                i += 1
        
        db.commit()
        return columnName

    def remove_expedition(self, userId):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId,)       
        dbCursor.execute("DELETE FROM activeExpeditions WHERE telegramUserId=?", s)
        db.commit()

    def get_expedition_values(self, userId):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId,)       
        dbCursor.execute("SELECT * FROM activeExpeditions WHERE telegramUserId=?", s)
        out=dbCursor.fetchall()
        if out == []:
            return None
        returnValues = []
        for column in out[0]:
            if column != None:
                returnValues.append(column)
        returnValues.pop(0)
        return returnValues

    def set_state(self, user_id, state):
        possible_states = ["main_menu", "favorites_menu", "search_menu", "stop_menu"]
        if not state in possible_states:
            raise Exception(f"State msut be one of the following: {', '.join(possible_states)}")

        db = sqlite3.connect(self.dbFile)
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
        db = sqlite3.connect(self.dbFile)
        db_cursor = db.cursor()
        s = (user_id,)
        db_cursor.execute("SELECT state FROM states WHERE telegram_user_id=?", s)
        out = db_cursor.fetchall()[0][0]
        return out
    
    def delete_Everything_from_user(self, userId):
        db = sqlite3.connect(self.dbFile)
        dbCursor = db.cursor()
        s = (userId,)       
        dbCursor.execute("DELETE FROM activeExpeditions WHERE telegramUserId=?", s)
        dbCursor.execute("DELETE FROM favoriteStops WHERE telegramUserId=?", s)
        db.commit() 
