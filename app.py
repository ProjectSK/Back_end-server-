#!/usr/bin/env python
import MySQLdb
import MySQLdb.cursors
import model
import config

from flask import Flask, request

app = Flask(__name__)
db = MySQLdb.connect(user=config.DATABASE_USERNAME, 
                     passwd=config.DATABASE_PASSWORD, 
                     db=config.DATABASE_NAME, 
                     cursorclass=MySQLdb.cursors.DictCursor)


@app.route("/")
def index():
    return "<h2> List of Device Ids </h2>" + "".join(["<h3>%s</h3>"%x for x in model.select_deviceId(db.cursor())])


def do_post(inserter):
    deviceId = request.json["deviceId"]
    data = request.json["data"]
    model.insert_deviceId(db.cursor(), deviceId)
    db.commit()

    c = db.cursor()
    for loc in data:
        inserter(c, deviceId, loc)
    db.commit()

    return "OK"

@app.route("/location", methods=["POST"])
def post_location():
    return do_post(model.insert_location)

@app.route("/appUsage", methods=["POST"])
def post_appUsage():
    return do_post(model.insert_appUsage)

@app.route('/battery', methods=["POST"])
def post_battery():
    return do_post(model.insert_battery)


def show_columns(selector, deviceId, limit, mand_cols):
    c = db.cursor()
    result = []
    for record in selector(c, deviceId, limit):
        for col in mand_cols:
            result.append(str(record[col]))
            result.append(" ")
        result.append("\n")
    return "".join(result)


@app.route("/location/<deviceId>", methods=["GET"])
def show_locations(deviceId):
    return show_columns(model.select_location, deviceId, 20, ["time", "lat", "lng"])

@app.route("/battery/<deviceId>", methods=["GET"])
def show_battery(deviceId):
    return show_columns(model.select_battery, deviceId, 20, ["time", "capacity", "level", "scale", "voltage", "temperature", "healthType", "plugType"])

@app.route("/appUsage/<deviceId>", methods=["GET"])
def show_appUsage(deviceId):
    return show_columns(model.select_appUsage, deviceId, 20, ["packageName", "startTime", "elapsedTime"])


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=8080, debug=True)
