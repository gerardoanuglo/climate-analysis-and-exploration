#import modules
import pandas as pd
import numpy as np
import datetime as dt
#python SQL toolkit and Object Relational Mapper
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify

#Add database path and create engine
database_path = "/hawaii.sqlite"

engine = create_engine(f"sqlite://{database_path}")

#reflect an existing database into a new model
#use automap_base to reflect the database tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

#Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session 
session = Session(engine)

#Design of Climate App, as a Flask API
#Flask Setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    print("Server received request for 'Home' page...")
    return (
    f"Welcome to the Hawaii Climate Analysis API! <br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/temp/start<br/>"
    f"/api/v1.0/temp/start/end"
    )

#Precipitation api
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' api page...")
    
    #query using date as the key and prcp as the value.
    prcp_data = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date <= '2017-08-23').\
    filter(measurement.date >= '2016-08-23').\
    group_by(measurement.date).\
    order_by((measurement.date).desc())
    
    session.close()
    
    #Dict of results
    prcp_dict ={date: prcp for date, prcp in prcp_data}
    return jsonify(prcp_dict)

#Station API
@app.route("/api/v1.0/stations")
def all_stations():

    #Query a list of all stations
    station_activity = session.query(station.station).all()

    session.close()
    
    #create a JSON list of stations from the query
    stations_list = list(np.ravel(station_activity))
    return jsonify(stations=stations_list)


#temperatur API
@app.route("/api/v1.0/tobs")
def temperatures():

    #query the dates and temperature obersevations of the most active station for
    #the previous year of data, 'USC00519281'
    temperature_data = session.query(measurement.tobs, measurement.date).\
    filter(measurement.station == 'USC00519281').\
    filter(measurement.date  <= '2017-08-23').\
    filter(measurement.date >= '2016-08-23')

    session.close()

    #create a list of temperature observations for the previous year
    temp_list = list(np.ravel(temperature_data))
    #JSONIFY list
    return jsonify(temps = temp_list)

#start and end api
@app.route("/api/v1.0/<start>")
def start_record():
    #query max, min, and mean temperature beginning from the start day to present
    input_a = input("what day do you want to start at? yyyy-dd-mm")
    start_dt_records = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                        filter(measurement.date >= input_a).all()
    
    session.close()

     #create a list for temps summary statistics
    start_list = list(np.ravel(start_dt_records)
    #JSONIFY list
    return jsonify(temps = start_list)

#Ranged API
@app.route("/api/v1.0/<start>/<end>")
def start_end():
    #query max, min, and mean temperature beginning from the start day to the end date
    input_a = input("what day do you want to start at? yyyy-dd-mm")
    input_b = input("what day do you want to end at? yyyy-dd-mm")
    start_end_records = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                        filter(measurement.date >= input_a).all()
                        filter(measurement.date <= input_b).all()

    session.close()

    #create list of temp summary statistics
    start_end_list = list(np.ravel(start_end_records)
    #JSONIFY list
    return jsonify(temps = start_end_list)

if __name__ == "__main__":
    app.run()
