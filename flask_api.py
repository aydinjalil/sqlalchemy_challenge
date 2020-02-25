# Dependencies

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import create_engine, func, inspect, distinct, and_

from datetime import datetime
from dateutil.relativedelta import relativedelta

# Reflect tables into SQLAlchemy ORM

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)


Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask app


db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

from flask import Flask, jsonify

app = Flask(__name__)



last_date_str = db_session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
twelve_months = relativedelta(months=-12)
relative_date = last_date + twelve_months

@app.route("/")
def home():
    return (
        f"Welcome to HAWAII API<br/><br/>"
        f"To access information about the weather and our stations please follow the links below:<br/><br/>"
        f"/api/v1.0/precipitation ---- returns a JSON list of precipitation data for the dates between 8/23/16 and 8/23/17.<br/><br/>"
        f"/api/v1.0/stations ---- returns a JSON list of the weather stations.<br/><br/>"
        f"/api/v1.0/tobs ---- returns a JSON list of temperature observations for each station between the start and end dates.<br/><br/>"
        f"/api/v1.0/start ---- returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.<br/><br/>Use single date in format Y-m-d(i.e 2017-01-01) to access weather stats from given date to the end date of the dataset<br/><br/>"
        f"/api/v1.0/start/end` ---- returns a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.<br/><br/>Use two dates in format Y-m-d (i.e. 2016-05-01/2017-01-01) to access the weather stats for the given range<br/><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #session = Session(engine)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


    data_query = db_session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= relative_date).order_by(Measurement.date).all()
    prcp_list = []
    for data in data_query:
        row_dict = {}
        row_dict["Date"] = data.date
        row_dict["Precipitation"] = data.prcp
        prcp_list.append(row_dict)
    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    #session = Session(engine)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    stations_query = db_session.query(Station).all()
    all_stations = []
    for stations in stations_query:
        stations_dict = {}
        stations_dict["Station"] = stations.station
        stations_dict["Station Name"] = stations.name
        stations_dict["Latitude"] = stations.latitude
        stations_dict["Longitude"] = stations.longitude
        stations_dict["Elevation"] = stations.elevation
        all_stations.append(stations_dict)
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    #session = Session(engine)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    last_date_str = db_session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
    twelve_months = relativedelta(months=-12)
    relative_date = last_date + twelve_months

    last_twelve_of_most_active_station = db_session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date > relative_date).all()
    return jsonify(last_twelve_of_most_active_station)
    #session.Close()


@app.route("/api/v1.0/<start_date>")
def starDate(start_date=None):

    #session = Session(engine)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    weather_stats = db_session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    temp_list = []
    for Tmin, Tmax, Tavg in weather_stats:
        temp_dict = {}
        temp_dict["Minimum Temp"] = Tmin
        temp_dict["Maximum Temp"] = Tmax
        temp_dict["Average Temp"] = Tavg
        temp_list.append(temp_dict)

    return jsonify(temp_list)
    #session.Close()

@app.route("/api/v1.0/<start_date>/<end_date>")
def startEndDate(start_date=None, end_date=None):

    #session = Session(engine)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    #start = datetime.strptime(start_date, "Y%-m%-%d")
    #end = datetime.strptime(start_date, "Y%-m%-%d")
    weather_stats = db_session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
         filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()
    temp_list = []

    for Tmin, Tmax, Tavg in weather_stats:
        temp_dict = {}
        temp_dict["Minimum Temp"] = Tmin
        temp_dict["Maximum Temp"] = Tmax
        temp_dict["Average Temp"] = Tavg
        temp_list.append(temp_dict)

    return jsonify(temp_list)
    #session.Close()

if __name__ == '__main__':
    app.run(debug=True)


