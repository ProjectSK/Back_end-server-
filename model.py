#!/usr/bin/env python
import MySQLdb
import MySQLdb.cursors
import config

TABLE_CREATIONS = ['''CREATE TABLE IF NOT EXISTS user ( deviceId VARCHAR(100) NOT NULL PRIMARY KEY)''',
'''
CREATE TABLE IF NOT EXISTS appUsage ( deviceId VARCHAR(100) NOT NULL, startTime DATETIME NOT NULL, elapsedTime INT NOT NULL, packageName VARCHAR(100) NOT NULL, PRIMARY KEY (deviceId, startTime, packageName) )''',
'''
CREATE TABLE IF NOT EXISTS battery ( deviceId VARCHAR(100) NOT NULL, time DATETIME, capacity INT, level INT, scale INT, voltage INT, temperature FLOAT, healthType TEXT, plugType TEXT, PRIMARY KEY (deviceId, time))''',
'''
CREATE TABLE IF NOT EXISTS location (deviceId VARCHAR(100) NOT NULL, time DATETIME, lat FLOAT, lng FLOAT, PRIMARY KEY (deviceId, time))''',
'''
CREATE TABLE IF NOT EXISTS memory (deviceId VARCHAR(100) NOT NULL, time DATETIME, percentageUsage INT, totalMemory INT, freeMemory INT, PRIMARY KEY (deviceId, time))''',
'''
CREATE TABLE IF NOT EXISTS cpu (deviceId VARCHAR(100) NOT NULL, time DATETIME, user INT, system INT, idle INT, other INT, PRIMARY KEY (deviceId, time))
''']
def ensure_tables(db):
    for sql in TABLE_CREATIONS:
        c = db.cursor()
        c.execute(sql)
        db.commit()

def select_deviceId(cursor):
    cursor.execute("SELECT * FROM user LIMIT 10")
    row = cursor.fetchone()
    while row:
        yield row["deviceId"]
        row = cursor.fetchone()


def select_dict(cursor, deviceId, table, date_field, limit):
    cursor.execute("SELECT * FROM %s WHERE deviceId = '%s' ORDER BY %s DESC LIMIT %d"%(table, deviceId, date_field, limit))
    row = cursor.fetchone()
    while row:
        yield row
        row = cursor.fetchone()

def select_location(cursor, deviceId, limit):
    return select_dict(cursor, deviceId, "location", "time", limit)

def select_appUsage(cursor, deviceId, limit):
    return select_dict(cursor, deviceId, "appUsage", "packageName", limit)

def select_battery(cursor, deviceId, limit):
    return select_dict(cursor, deviceId, "battery", "time", limit)

def select_memory(cursor, deviceId, limit):
    return select_dict(cursor,deviceId, "memory", "time",limit)

def select_cpu(cursor, deviceId, limit):
    return select_dict(cursor,deviceId, "cpu", "time",limit)


def insert_deviceId(cursor, deviceId):
    cursor.execute("INSERT IGNORE INTO user VALUES (%s)", (deviceId, ))


def insert_appUsage(cursor, deviceId, usage):
    cursor.execute("INSERT INTO appUsage (deviceId, startTime, elapsedTime, packageName) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE deviceId = deviceId", (deviceId, usage["startTime"], usage["elapsedTime"], usage["packageName"]))

def insert_location(cursor, deviceId, loc):
    cursor.execute("INSERT INTO location (deviceId, time, lat, lng) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE deviceId = deviceId", ( deviceId, loc["time"], loc["latitude"], loc["longtitude"]))


def insert_battery(cursor, deviceId, battery):
    if "healthType" not in battery:
        print battery
    cursor.execute("INSERT INTO battery (deviceId, time, capacity, level, scale, voltage, temperature, healthType, plugType) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE deviceId = deviceId", (deviceId, battery["time"], battery["capacity"], battery["level"], battery["scale"], battery["voltage"], battery["temperature"], battery["healthType"], battery["plugType"]))


def insert_memory(cursor, deviceId, memory):
    cursor.execute("INSERT INTO memory (deviceId, time, percentageUsage, totalMemory, freeMemory) VALUES(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE deviceId = deviceId", (deviceId, memory["time"], memory["percentageOfMemoryUsage"], memory["totalMemory"], memory["freeMemory"]))

def insert_cpu(cursor, deviceId, cpu):
    cursor.execute("INSERT INTO cpu (deviceId, time, user, system, idle, other) VALUES(%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE deviceId = deviceId", (deviceId, cpu["time"], cpu["user"], cpu["system"], cpu["idle"], cpu["other"]))
    



if __name__ == '__main__':
    db = MySQLdb.connect(user=config.DATABASE_USERNAME, 
                         passwd=config.DATABASE_PASSWORD, 
                         db=config.DATABASE_NAME,
                         cursorclass=MySQLdb.cursors.DictCursor)
    ensure_tables(db)
    print list(select_deviceId(db.cursor()))
    db.close()
