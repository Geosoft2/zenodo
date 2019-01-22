#import click, json, sqlite3, csv, pygeoj
#from osgeo import gdal, ogr, osr
#import pandas as pd
#import numpy as np
#import xarray as xr
#import os
from pyproj import Proj, transform
import click
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getIsoInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo, openFolder

"""global variable to save the bbox values of single files it is used for the boundingbox extraction of a whole folder"""
bboxArray = []
timeextendArray=[]
ret_value=[]

""" Advantage of our code is that the file extension is not important for the metadataextraction but the content of the file"""

@click.command()
@click.option('--path',required=True, help='please insert the path to the data here.')
@click.option('--time', is_flag=True, help='returns the time extend of one object')
@click.option('--detail', type=click.Choice(['bbox', 'convexHull']), default='bbox', help='select which information you want to get')
@click.option('--folder', type=click.Choice(['single', 'whole']), default='single', help='select if you want to get the Metadata from the whole folder or for each seperate file.')

def getMetadata(path, detail, folder, time):
    """ 
    
    """
    filepath = path
    # Program that extracts the boudingbox of files.

    try:
        click.echo("detailShape")
        getShapefileInfo.getShapefilebbx(filepath, detail, folder, time)
    except Exception as e:
        try:
            print("This is no valid Shapefile.")
            click.echo("detailjson")
            getGeoJsonInfo.getGeoJsonbbx(filepath, detail, folder, time)
        except Exception as e:
            try:
                print("error")
                print(e)
                click.echo("detail_netcdf")
                getNetCDFInfo.getNetCDFbbx(filepath, detail, folder, time)
            except Exception as e:
                try:
                    print("detail_csv")
                    getCSVInfo.getCSVbbx(filepath, detail, folder, time)
                except Exception as e:
                    try:
                        print("detail geopackage")
                        getGeoPackageInfo.getGeopackagebbx(filepath, detail, folder, time)
                    except Exception as e:
                        try:
                            print (e)
                            print("neu")
                            click.echo("detail geotiff")
                            getGeoTiffInfo.getGeoTiffbbx(filepath, detail, folder, time)
                        except Exception as e:
                            try:
                                click.echo("detailiso")
                                getIsoInfo.getIsobbx(filepath, detail, folder, time)
                            except Exception as e:
                                try:
                                    click.echo(e)
                                    click.echo("detail folder")
                                    openFolder.openFolder(filepath, detail, folder, time)
                                except Exception as e:
                                    click.echo(e)
                                    click.echo ("invalid file format!!!!!")
                                    return 0

"""
@desc: Method for transform the coordinate reference system to WGS84 using the PyProj (https://github.com/jswhit/pyproj)
@param: latitude, longitude and the source ref system
"""
def transformToWGS84(lat, lng, sourceCRS):
    # formatting the input CRS
    try:
        inputProj='epsg:'
        inputProj+=str(sourceCRS)
        inProj = Proj(init=inputProj)
        # epsg:4326 is WGS84
        outProj = Proj(init='epsg:4326')
        latT, lngT = transform(inProj,outProj,lat,lng)
        return(latT,lngT)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    getMetadata()
