import click,json, sqlite3, pygeoj, csv
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import extractTool
from scipy.spatial import ConvexHull
import dateparser
from pyproj import Proj, transform
#import sys

#import ogr2ogr
#ogr2ogr.BASEPATH = "/home/caro/Vorlagen/Geosoftware2/Metadatenextraktion"


def getCSVbbx(filepath, detail, folder, time):

    """returns the bounding Box CSV
    @see https://www.programiz.com/python-programming/reading-csv-files
    @param path Path to the file """
    
    #format validation
    pd.read_csv(filepath)
    click.echo("csv")
    CRSinfo = True
    listlat = ["Koordinate_Hochwert","lat","Latitude","latitude"]
    listlon = ["Koordinate_Rechtswert","lon","Longitude","longitude","lng"]
    listCRS = ["CRS","crs","Koordinatensystem","EPSG","Coordinate reference system", "coordinate system"]
    listtime = ["time", "timestamp", "date", "Time", "Jahr", "Datum"]
    try:
        deli=';'
        df = pd.read_csv(filepath, delimiter=deli,engine='python')
        #tests if there is a column named Coordinatesystem or similar
        click.echo("hi")
        #click.echo(df.columns.values)
        #click.echo(intersect(listCRS,df.columns.values))
        if not intersect(listCRS,df.columns.values):
            CRSinfo= False
            print("hu")
            print("No fitting header for a reference system")

        if not(((intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)))or (intersect(listtime, df.columns.values))):
            #output="No fitting header for latitudes or longitudes"
            raise Exception('No fitting ')
            #print(output)
            #return output

    except Exception as exce:
        deli=','
        df = pd.read_csv(filepath, delimiter=deli,engine='python')
        #tests if there is a column named Coordinatesystem or similar
        click.echo("hi")
        #click.echo(df.columns.values)
        #click.echo(intersect(listCRS,df.columns.values))
        if not intersect(listCRS,df.columns.values):
            CRSinfo= False
            
            print("No fitting header for a reference system2")
            z=intersect(listtime, df.columns.values)
            print (z)
            t=intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)
            print (intersect(listlat,df.columns.values))
            print("_______________")
            print(t)
            if not t:
                print("false")

        if not(((intersect(listlat,df.columns.values) and intersect(listlon,df.columns.values)))or (intersect(listtime, df.columns.values))):
            #output="No fitting header for latitudes or longitudes"
            #raise Exception('No fim')
        
            raise Exception("evtl kein csv oder ungueltiges Trennzeichen.")
            #print("keine Koordinaten vorhanden")
            #print(output)
            #return output
        print (exce)

    if detail =='bbox':
        click.echo("bbox")
        # Using Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
        #if folder=='single':
        mylat=intersect(listlat,df.columns.values)
        mylon=intersect(listlon,df.columns.values)
        lats=df[mylat[0]]
        lons=df[mylon[0]]
        bbox=[min(lats),min(lons),max(lats),max(lons)]
        # CRS transformation if there is information about crs
        if(CRSinfo):
            mycrsID=intersect(listCRS,df.columns.values)
            myCRS=df[mycrsID[0]]
            lat1t,lng1t = extractTool.transformToWGS84(min(lats),min(lons), myCRS)
            lat2t,lng2t = extractTool.transformToWGS84(max(lats),max(lons), myCRS)
            bbox=[lat1t,lng1t,lat2t,lng2t]
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the CSV object:")
                click.echo(bbox)
                print("----------------------------------------------------------------")
                extractTool.ret_value.append(bbox)
            if folder=='whole':
                extractTool.bboxArray.append(bbox)
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the CSV:")
                click.echo(bbox)
                print("----------------------------------------------------------------")
        else:
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the CSV object:")
                print(bbox)
                print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
                print("----------------------------------------------------------------")
                extractTool.ret_value.append([None])
            if folder=='whole':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the CSV file:")
                click.echo(bbox)
                click.echo("because of a missing crs this CSV is not part of the folder calculation.")
                print("----------------------------------------------------------------")

    else:
        extractTool.ret_value.append([None])

    #returns the convex hull of the coordinates from the CSV object.
    if detail == 'convexHull':
        click.echo("convexHull")
        mylat=intersect(listlat,df.columns.values)
        mylon=intersect(listlon,df.columns.values)
        lats=df[mylat[0]]
        lons=df[mylon[0]]
        coords=np.column_stack((lats, lons))
        #definition and calculation of the convex hull
        hull=ConvexHull(coords)
        hull_points=hull.vertices
        convHull=[]
        for z in hull_points:
            point=[coords[z][0], coords[z][1]]
            convHull.append(point)
        if(CRSinfo):
            mycrsID=intersect(listCRS,df.columns.values)
            myCRS=df[mycrsID[0]]
            inputProj='epsg:'
            inputProj+=str(myCRS[0])
            print(inputProj)
            inProj = Proj(init=inputProj)
            outProj = Proj(init='epsg:4326')
            for z in coords:
                z[0],z[1] = transform(inProj,outProj,z[0],z[1])
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("convex Hull of the csv file: ")
                click.echo(convHull)
                print("----------------------------------------------------------------")
                extractTool.ret_value.append(convHull)
            if folder=='whole':
                extractTool.bboxArray=extractTool.bboxArray+convHull
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("convex hull of the CSV:")
                click.echo(convHull)
                print("----------------------------------------------------------------")
                #return convHull
        else:
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Convex hull of the CSV object:")
                print(convHull)
                print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
                print("----------------------------------------------------------------")
                extractTool.ret_value.append([None])
            if folder=='whole':
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Convex hull of the CSV file:")
                click.echo(convHull)
                click.echo("because of a missing crs this CSV is not part of the folder calculation.")
                print("----------------------------------------------------------------")


    else:
        extractTool.ret_value.append([None])



    
    if (time):
        click.echo("hallo")
        # Using Pandas: http://pandas.pydata.org/pandas-docs/stable/io.html
        df = pd.read_csv(filepath, sep=';|,',engine='python')
        click.echo(listtime)
        click.echo(df.columns.values)
        intersection=intersect(listtime, df.columns.values)
        click.echo(intersection)
        if not intersection:
            print("No fitting header for time-values")
            extractTool.ret_value.append([None])
            # TODO: fehlerbehandlung  
            #try:
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
            print(min(time))
            print(max(time))
            timemin=str(min(time))
            timemax=str(max(time))
            timemax_formatted=dateparser.parse(timemax)
            timemin_formatted=dateparser.parse(timemin)
            timeextend=[timemin_formatted, timemax_formatted]
            print(timeextend)
            if folder=='single':
                print("----------------------------------------------------------------")
                click.echo("Timeextend of this CSV file:")
                click.echo(timeextend)
                print("----------------------------------------------------------------")
                extractTool.ret_value.append([timeextend])
                #return timeextend
            if folder=='whole':
                extractTool.timeextendArray.append(timeextend)
                print("timeextendArray:")
                print(extractTool.timeextendArray)

    else:
        extractTool.ret_value.append([None])
    if folder=='single':
        print(extractTool.ret_value)
        return extractTool.ret_value
# Hilfsfunktion fuer csv fehlerbehandlung
def intersect(a, b):
     return list(set(a) & set(b))
