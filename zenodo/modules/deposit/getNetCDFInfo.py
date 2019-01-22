import click, json, sqlite3, csv, pygeoj, extractTool
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import dateparser

def getNetCDFbbx(filepath, detail, folder, time):
    """returns the bounding Box NetCDF
    @param path Path to the file """
    print("drin")
    #validation if file is netcdf
    ds = xr.open_dataset(filepath)
    if detail =='bbox':
        print("bbox")
        try:
            lats = ds.coords["lat"]
            lons = ds.coords["lon"]

        except Exception as e:
            lats = ds.coords["latitude"]
            lons = ds.coords["longitude"]
        #print(ds.values)
        minlat=min(lats).values
        minlatFloat=float(minlat)
        minlon=min(lons).values
        minlonFloat=float(minlon)
        maxlat=max(lats).values
        maxlatFloat=float(maxlat)
        maxlon=max(lons).values
        maxlonFloat=float(maxlon)


        bbox = [minlatFloat,minlonFloat,maxlatFloat,maxlonFloat]
        #click.echo(bbox)

        if folder=='single':
            print("----------------------------------------------------------------")
            click.echo("Filepath:")
            click.echo(filepath)
            click.echo("Boundingbox of the NetCDF Object:")
            click.echo(bbox)
            print("----------------------------------------------------------------")
            extractTool.ret_value.append(bbox)
            #print("test")
            #return bbox
        if folder=='whole':
            #fuer Boundingbox des Ordners
            extractTool.bboxArray.append(bbox)
            click.echo(filepath)
            print(bbox)
            #return bbox
    else:
        extractTool.ret_value.append([None])
    if detail == 'convexHull':
        ds = xr.open_dataset(filepath)
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo('Sorry there is no second level of detail for NetCDF files')
        print("----------------------------------------------------------------")
        extractTool.ret_value.append([None])
    
    else:
        extractTool.ret_value.append([None])

        
    # @author Jannis Froehlking
    # After opening the file we are looking for 
    # time values and calculate the temporal extend 
    # with min and max functions
    """returns the Time from NetCDF file
    @param path Path to the file """
    if (time):
        #ds = xr.open_dataset(filepath)
        try:
            mytime = ds.coords["time"]
            # print(ds.values)
            starttime = min(mytime)
            endtime = max(mytime)
            # Zeitliche Ausdehnung
            anfang = str(starttime.values)
            ende = str(endtime.values)
            timemax_formatted=dateparser.parse(ende)
            timemin_formatted=dateparser.parse(anfang)
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                print("the temporal extend of the NetCDF object is:")
                print(timemin_formatted)
                print(timemax_formatted)
                print("----------------------------------------------------------------")
                extractTool.ret_value.append([timemin_formatted, timemax_formatted])

            if folder=='whole':
                timeextend=[timemin_formatted, timemax_formatted]
                extractTool.timeextendArray.append(timeextend)
                #print(timeextend[0])
                print("timeextendArray:")
                print(extractTool.timeextendArray)
                #return anfang, ende
        except Exception as e:
            extractTool.ret_value.append([None])
            click.echo ("There is no time-value or invalid file")
            #return None
    else:
        extractTool.ret_value.append([None])

    
    ds.close()
    if folder=='single':
        print(extractTool.ret_value)
        return extractTool.ret_value
        #print("fertig")

if __name__ == '__main__':
    getNetCDFbbx()