#!/usr/bin/env python

#main code for server.
#
#do actual visualization and get calls for getting info from client
#
#

import MySQLdb
import MySQLdb.cursors
import model
import config
import json

from flask import Flask, request, render_template, redirect, url_for, abort, session

app = Flask(__name__)
db = MySQLdb.connect(user=config.DATABASE_USERNAME, 
        passwd=config.DATABASE_PASSWORD, 
        db=config.DATABASE_NAME, 
        cursorclass=MySQLdb.cursors.DictCursor)


@app.route("/")
def index():
    result = []
    result.append("<div id='idlist'>");
    result.append("<h2> List of registered deviceIds </h2>");
    for devid in model.select_deviceId(db.cursor()):
        result.append("<p>")
        result.append("<h3>")
        result.append(devid)
        result.append("</h3>")
        for infoname in ["appUsage", "battery", "cpu", "data", "location", "memory"]:
            result.append("<a href='http://52.11.1.59:8080/");
            result.append(infoname);
            result.append("/");
            result.append(devid);
            result.append("' target='_blank'>");
            result.append(infoname);
            result.append("</a>");
            result.append("&nbsp; ");
        result.append("</p>");
    return "".join(result)



#get info from client apps
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

#function for each data

@app.route("/location", methods=["POST"])
def post_location():
    return do_post(model.insert_location)

@app.route("/appUsage", methods=["POST"])
def post_appUsage():
    return do_post(model.insert_appUsage)

@app.route('/battery', methods=["POST"])
def post_battery():
    return do_post(model.insert_battery)

@app.route('/memory', methods=["POST"])
def post_memory():
    return do_post(model.insert_memory)

@app.route('/cpu', methods=["POST"])
def post_cpu():
    return do_post(model.insert_cpu)

@app.route('/data', methods=["POST"])
def post_data():
    return do_post(model.insert_data)




#draw table of each data
def show_columns(selector, deviceId, limit, mand_cols):
    c = db.cursor()
    result = []
    result.append("<div class='container'>");
    result.append("<table class='table table-striped'>")
    result.append('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css"> <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">')
    result.append("<thead><tr>")
    for col in mand_cols:
        result.append("<th>")
        result.append(col)
        result.append("</th>")
    result.append("</tr></thead>")
    for record in selector(c, deviceId, limit):
        result.append("<tr>")
        for col in mand_cols:
            result.append("<td>")
            result.append(str(record[col]))
            result.append("</td>")
        result.append("</tr>")
    result.append("</table>")
    result.append("</div>")
    return "".join(result)


#functinos for drawing visualization(graph + table) each function has grph visualization part

@app.route("/location/<deviceId>", methods=["GET"])
def show_locations(deviceId):
    c=db.cursor()
    result=[]
    limit=20
    for record in model.select_location(c,deviceId,limit):
        data={}
        data["time"]=record["time"]
        data["lat"]=record["lat"]
        data["lng"]=record["lng"]
        result.append((data))
    return render_template("Location.html",Latlngs=result) + show_columns(model.select_location, deviceId, limit, ["time", "lat", "lng"])

@app.route("/battery/<deviceId>", methods=["GET"])
def show_battery(deviceId):
    c=db.cursor()
    retVal={}
    result=[]
    limit = 20
    for record in model.select_battery(c,deviceId,limit):
        data={}
        data["date"]=str(record["time"])
        for info in ["capacity", "temperature"]:
            data[info]=str(record[info])
        result.append((data))
    retVal["yaxisDesc"]="Percentage (%) || Temperature (C)"
    retVal["data"]=result
    return render_template("battery.html",info=retVal)  +  show_columns(model.select_battery, deviceId, limit, ["time", "capacity", "level", "scale", "voltage", "temperature", "healthType", "plugType"])

@app.route("/appUsage/<deviceId>", methods=["GET"])
def show_appUsage(deviceId):
    c=db.cursor()
    retVal={}
    result=[]
    limit=20
    for record in model.select_appUsage(c,deviceId,limit):
        data={}
        data["name"]=str(record["packageName"])
        for info in ["startTime", "elapsedTime"]:
            data[info]=str(record[info])
        result.append((data))
    retVal["yaxisDesc"]="PackageName"
    retVal["data"]=result
    return render_template("appUsage.html",info=retVal)+show_columns(model.select_appUsage, deviceId, limit, ["packageName", "startTime", "elapsedTime"])

@app.route("/memory/<deviceId>", methods=["GET"])
def show_memory(deviceId):
    c=db.cursor()
    retVal={}
    result=[]
    limit=20
    for record in model.select_memory(c,deviceId,limit):
        data={}
        data["date"]=str(record["time"])
        data["percentageUsage"]=str(record["percentageUsage"])
        result.append((data))
    retVal["yaxisDesc"]="Percentage(%)"
    retVal["data"]=result
    return render_template("memory.html",info=retVal)+show_columns(model.select_memory, deviceId, limit, ["time", "percentageUsage", "totalMemory", "freeMemory"])


@app.route("/cpu/<deviceId>", methods=["GET"])
def show_cpu(deviceId):
    c=db.cursor()
    retVal={}
    result=[]
    limit=20
    for record in model.select_cpu(c,deviceId,limit):
        data={}
        data["date"]=str(record["time"])
        for info in ["user", "system", "idle", "other"]:
            data[info]=str(record[info])
        result.append((data))
    retVal["yaxisDesc"]="Percentage(%)"
    retVal["data"]=result
    return render_template("cpu.html",info=retVal)+show_columns(model.select_cpu, deviceId, limit, ["time","user","system","idle","other"]);

@app.route("/data/<deviceId>", methods=["GET"])
def show_data(deviceId):
    c=db.cursor()
    retVal={}
    result=[]
    limit=20
    for record in model.select_data(c,deviceId,limit):
        data={}
        data["date"]=str(record["time"])
        for info in ["transdata", "recdata"]:
            data[info]=str(record[info])
        result.append((data))
    retVal["yaxisDesc"]="DATA"
    retVal["data"]=result
    return render_template("data.html",info=retVal)+show_columns(model.select_data, deviceId, limit, ["time","transdata","recdata","elapsedTime"]);


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
