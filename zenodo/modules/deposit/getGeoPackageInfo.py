import click, json, sqlite3, csv, pygeoj, extractTool as de
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import sqlite3
from pyproj import Proj, transform
from scipy.spatial import ConvexHull

#Boolean variable that shows if the crs of the bbox is in wgs84
wgs_84=False

def getGeopackagebbx(filepath, detail, folder, time):
    """returns the bounding Box Geopackage
    @param path Path to the file
    @see https://docs.python.org/2/library/sqlite3.html"""
    
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    # @see: https://www.geopackage.org/spec121/index.html#_contents_2
    c.execute("""SELECT min(min_y), min(min_x), max(max_y), max(max_x), srs_id
                    FROM gpkg_contents""")
    row = c.fetchall()
    try:
        lat1=row[0][0]
        lng1=row[0][1]
        lat2=row[0][2]
        lng2=row[0][3]
        myCRS=row[0][4]
        if not(lat1 and lat2):
            print("keine koord")
    except (not(lat1 and lat2)):
        raise Exception ("There are no coordinate values in this file.")
        # Especially the KML data files have this id, which is wgs84
        # No need to transform
    if detail =='bbox':
        if ((myCRS=="CRS84" or myCRS == 4326) and (lat1 and lng1)):
            wgs_84=True
            bbox=[lat1,lng1,lat2,lng2]
        elif(myCRS):
            print("second if")
            wgs_84=True
            print("vor")
            lat1t,lng1t = de.transformToWGS84(lat1,lng1,myCRS)
            print("transformation success")
            lat2t,lng2t = de.transformToWGS84(lat2,lng2,myCRS)
            bbox=[lat1t,lng1t,lat2t,lng2t]
        else:
            print("There is no crs provided.")
            bbox=[lat1,lng1,lat2,lng2]


        if folder=='single':
            if wgs_84==True:
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoPackage object:")
                print(bbox)
                print("----------------------------------------------------------------")
                de.ret_value.append(bbox)
            else:
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoPackage object:")
                print(bbox)
                print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
                print("----------------------------------------------------------------")
                de.ret_value.append([None])
        if folder=='whole':
            if wgs_84==True:
                de.bboxArray.append(bbox)
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoPackage:")
                click.echo(bbox)
                print("----------------------------------------------------------------")
            else:
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoPackage:")
                click.echo(bbox)
                click.echo("because of a missing crs this GeoPackage is not part of the folder calculation.")
                print("----------------------------------------------------------------")

    else:
        de.ret_value.append([None])
    if detail == 'convexHull':
        conn = sqlite3.connect(filepath)
        c = conn.cursor()
        c.execute("""SELECT min_x,min_y, max_x, max_y, srs_id
                     FROM gpkg_contents""")
        
        points = c.fetchall()
        pointlist=[]
        for z in points:
            pointlist.append(de.transformToWGS84(z[0], z[1], myCRS))
            pointlist.append(de.transformToWGS84(z[2], z[3], myCRS))
        hull=ConvexHull(pointlist)
        hull_points=hull.vertices
        convHull=[]
        for y in hull_points:
            point=[pointlist[y][0], pointlist[y][1]]
            convHull.append(point)
        if folder=='single':   
            print("----------------------------------------------------------------")
            click.echo("Filepath:")
            click.echo(filepath)
            click.echo("Convex hull of the GeoPackage object:")
            print(convHull)
            print("----------------------------------------------------------------")
            de.ret_value.append(convHull)
        if folder=='whole':
            print("----------------------------------------------------------------")
            de.bboxArray=de.bboxArray+convHull
            click.echo("convex hull whole")
            click.echo(convHull)
        
    else:
        de.ret_value.append([None])
    if (time):
        out="There is no time-value for GeoPackage files."
        print(out)
        timeval=[None]
        de.ret_value.append(timeval)

    else:
        de.ret_value.append([None])
    if folder=='single':
        print(de.ret_value)
        return de.ret_value
        #return None

if __name__ == '__main__':
    getGeopackagebbx()
