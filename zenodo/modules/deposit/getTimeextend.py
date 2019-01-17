# @author Carolin Bronowicz
# @version 1.0
import click, shapefile, sqlite3, csv, json, pygeoj
from osgeo import gdal, ogr, osr
import os
import pandas as pd
import numpy as np
import xarray as xr
import ogr2ogr
import json

#@click.command()
#@click.option('--path', prompt='Datapath', help='Path to the data.')
#@click.option('--time', 'detail', flag_value='time', default=True)
timeextendArray=[]

def getTimeextend(path, detail, folder):
    filepath = path
    # Program that extracts the time-extend of files.
    # same construction as in the "extractTool.py" file
    # if this file cannot find any time-values the file throws an 
    # "invalid file format or no time-values included!" exception
    try:
        getShapefiletime(filepath, detail)
    except Exception as e:
        try:
            getCSVtime(filepath, detail, folder)
        except Exception as e:
            try:
                getNetCDFtime(filepath, detail)
            except Exception as e:
                try:
                    getGeopackagetime(filepath, detail)
                except Exception as e:
                    try: 
                        getGeoTifftime(filepath, detail)    
                    except Exception as e:
                        try:
                            getGeoJsontime(filepath, detail)
                        except Exception as e:
                            try: 
                                getIsoTime(filepath, detail)    
                            except Exception as e:
                                click.echo ("invalid file format or no time-values included!")

def getShapefiletime(filepath, detail):
    # Shapefilesoes not have any time information so we return none
    click.echo("Shapefile")
    click.echo(detail)
    if detail =='time':
        sf = shapefile.Reader(filepath)
        click.echo("There is no time-value or invalid file")
        return None

"""Because we havent seen any testdata with time values included, we asume or we rather commit that there are no time values"""
def getGeoTifftime(filepath, detail):
    gdal.UseExceptions()
    click.echo("GeoTiff")
    if detail =='time':
        ds = gdal.Open(filepath)
        gdal.Info(ds)
        click.echo("there is no time value for GeoTIFF files")
        return None

def getCSVtime(filepath, detail, folder):
    # After opening the file we search in the header for collumns with names like
    # date, time or timestamp. If some of these collumns exists we collect
    # all the values from inside and calculate the min and max
    #FUNKTIONIERT NICHT BEI LEEREN ZELLEN
    click.echo("CSV")
    if detail =='time':
        click.echo("hallo")
        # Using Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
        df = pd.read_csv(filepath, sep=';|,',engine='python')
        listtime = ["time", "timestamp", "date", "Time", "Jahr", "Datum"]
        click.echo(listtime)
        click.echo(df.columns.values)
        intersection=intersect(listtime, df.columns.values)
        click.echo(intersection)
        if not intersection:
            print("No fitting header for time-values")
            # TODO: fehlerbehandlung  
            #try:
                #print("test2")
                #for t in listtime:
                    #if(x not in df.columns.values):
                        #click.echo("This file does not include time-values")
                    #else:
                        #time=df[t]
                        #timeextend =[min(time), max(time)]
                        #click.echo(timeextend)
                        #return timeextend
            #except Exception as e:
                #click.echo ("There is no time-value or invalid file.")
                #return None   
        else:
            time=df[intersection[0]]
            timeextend=[min(time), max(time)]
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Timeextend of this CSV file:")
                click.echo(timeextend)
                print("----------------------------------------------------------------")
                return timeextend
            if folder=='whole':
                timeextendArray.append(timeextend)
                print("timeextendArray:")
                print(timeextendArray)

def intersect(a, b):
    return list(set(a) & set(b))

def getGeoJsontime(filepath, detail):
    # After opening the file check if the file seems to have the right format
    # Then we search for words like date, creationDate or time at two different levels
    print("GeoJson")
    if detail =='time':
        ds = open(filepath)
        geojson = json.load(ds)
        print(" ")
        print("The time value of this file is:")
        timelist = list()
        if geojson["type"] == "FeatureCollection":
            first = geojson["features"]
            for time in geojson: 
                try:
                    #click.echo(first[0]["Date"])
                    time = first[0]["Date"]
                    timelist.append(time)
                except Exception as e:
                    try:
                        #click.echo(first[0]["creationDate"])
                        time = time[0]["creationDate"]
                        timelist.append(time)
                    except Exception as e:
                        try:
                            #click.echo(first[0]["date"])
                            time = first[0]["date"]
                            timelist.append(time)
                        except Exception as e:
                            try:
                                #click.echo(first[0]["time"])
                                time = first[0]["time"]
                                timelist.append(time)
                            except Exception as e:
                                try:
                                    #click.echo(first[0]["properties"]["date"])
                                    time = first[0]["properties"]["date"]
                                    timelist.append(time)
                                except Exception as e:
                                    try:
                                        #click.echo(first[0]["properties"]["time"])
                                        time = first[0]["properties"]["time"]
                                        timelist.append(time)
                                    except Exception as e:
                                        try:
                                            #click.echo(first[0]["geometry"][0]["properties"]["STAND_DER_DATEN"])
                                            time = first[0]["geometry"][0]["properties"]["STAND_DER_DATEN"]
                                            timelist.append(time)
                                        except Exception as e:
                                            click.echo("there is no time-value")
                                            return None         
        timemax = min(timelist)
        timemin = max(timelist)
        #click.echo(min(timelist))
        click.echo(max(timelist))
        return timemax #, timemin

def getNetCDFtime(filepath, detail):
    # @author Jannis Froehlking
    # After opening the file we are looking for 
    # time values and calculate the temporal extend 
    # with min and max functions
    click.echo("NetCDF")
    """returns the Time from NetCDF file
    @param path Path to the file """
    if detail =='time':
        ds = xr.open_dataset(filepath)
        try:
            mytime = ds.coords["time"]
            # print(ds.values)
            starttime = min(mytime)
            endtime = max(mytime)
            # Zeitliche Ausdehnung
            anfang = starttime.values
            ende = endtime.values
            print("the temporal extend of the NetCDF object is:")
            print(anfang)
            print(ende)
            return anfang, ende
        except Exception as e:
            click.echo ("There is no time-value or invalid file")
            return None
    
def getGeopackagetime(filepath, detail):
    # We open the file with the sqlite function and search for
    # words like time, timestamp or date and collect them
    # to calculate the temporal extend
    click.echo("GeoPackage")
    if detail =='time':
        #click.echo("DRIN")
        conn = sqlite3.connect(filepath)
        c = conn.cursor()
        c.execute("""SELECT time or timestamp or date
                        FROM gpkg_contents""")
        try:
            print c.fetchone()
            row = c.fetchall()
            print("The time value is:")
            print(row)
            return row
        except Exception as e:
            click.echo ("There is no time-value or invalid file")
            return None
        

def getIsoTime(filepath, detail):
    # We transform the gml file to a geojson file, then search for
    # words like "date", "timestamp", "time" and collect them
    click.echo("Iso")
    if detail =='time':
        ogr2ogr.main(["","-f", "GeoJSON", "time.json", filepath])
        iso = open("time.json")
        geojson = json.load(iso)
        # @see https://www.w3schools.com/python/python_file_remove.asp
        os.remove("time.json")
        print(" ")
        print("The time value of this file is:")
        if geojson["type"] == "FeatureCollection":
            first = geojson["features"]  
            time = []
            for i in range(0,5):            
                try:
                    click.echo(first[i]["Date"])
                    time = first[i]["Date"]
                    return time
                except Exception as e:
                    try:
                        click.echo(first[i]["properties"]["creationDate"])
                        time = time[i]["properties"]["creationDate"]
                        return time
                    except Exception as e:
                        try:
                            click.echo(first[i]["date"])
                            time = first[i]["date"]
                            return time
                        except Exception as e:
                            try:
                                click.echo(first[i]["time"])
                                time = first[i]["time"]
                                return time
                            except Exception as e:
                                try:
                                    click.echo(first[i]["properties"]["date"])
                                    time = first[i]["properties"]["date"]
                                    return time
                                except Exception as e:
                                    try:
                                        click.echo(first[i]["properties"]["time"])
                                        time = first[i]["properties"]["time"]
                                        return time
                                    except Exception as e:
                                        try:
                                            click.echo(first[i]["properties"]["Date"])
                                            time = first[i]["properties"]["Date"]
                                            return time
                                        except Exception as e:
                                            click.echo("there is no time-value")
                                            return None   
            print(time)
            return time

if __name__ == '__main__':
    getTimeextend()