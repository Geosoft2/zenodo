import click, json, sqlite3, csv, pygeoj
from osgeo import gdal, ogr, osr
import pandas as pd
import numpy as np
import xarray as xr
import os
import getShapefileInfo, getGeoTiffInfo, getCSVInfo, getIsoInfo, getGeoJsonInfo, getNetCDFInfo, getGeoPackageInfo, extractTool
from scipy.spatial import ConvexHull

def openFolder(filepath, detail, folder, time):
    folderpath= filepath
    click.echo("folderfolderfolder")
    docs=os.listdir(folderpath)
    for x in docs:
        docPath= folderpath +"/"+ x
        try:
            click.echo("folderShape")
            getShapefileInfo.getShapefilebbx(docPath, detail, folder, time)
        except Exception as e:
            try:
                click.echo("folderGeoJSON")
                getGeoJsonInfo.getGeoJsonbbx(docPath, detail, folder, time)
            except Exception as e:
                try:
                    click.echo(e)
                    click.echo("folderNetCDF")
                    getNetCDFInfo.getNetCDFbbx(docPath, detail, folder, time)
                except Exception as e:
                    try:
                        click.echo("folderCSV")
                        getCSVInfo.getCSVbbx(docPath, detail, folder, time)
                    except Exception as e:
                        try:
                            click.echo("folderGeoTIFF")
                            getGeoTiffInfo.getGeoTiffbbx(docPath, detail, folder, time)
                        except Exception as e:
                            try:
                                click.echo("folderGeoPackage")
                                getGeoPackageInfo.getGeopackagebbx(docPath, detail, folder, time)
                                print("aufter geopackage")
                            except Exception as e:
                                try:
                                    click.echo("folderISO")
                                    getIsoInfo.getIsobbx(docPath, detail, folder, time)
                                except Exception as e:
                                    try:
                                        click.echo("folderfolder")
                                        openFolder(docPath, detail, folder, time)
                                    except Exception as e:
                                        click.echo("fodlerInvalid")
                                        click.echo ("invalid file format in folder!")
                                        return None
    ret_value_folder=[]                                    
    if folder=='whole':
        if detail=='bbox':
            print("if")
            bboxes=extractTool.bboxArray
            print("222222222")
            print(bboxes)
            min1=100000000
            min2=100000000
            max1=-10000000
            max2=-10000000
            lat1List=[lat1 for lat1, lng1, lat2, lng2 in bboxes]
            #print(lat1List)
            for x in lat1List:
                if x<min1:
                    min1=x


            lng1List=[lng1 for lat1, lng1, lat2, lng2 in bboxes]
            #print(lng1List)
            for x in lng1List:
                if x<min2:
                    min2=x

            lat2List=[lat2 for lat1, lng1, lat2, lng2 in bboxes]
            #print(lat2List)
            for x in lat2List:
                if x>max1:
                    max1=x


            lng2List=[lng2 for lat1, lng1, lat2, lng2 in bboxes]
            #print(lng2List)
            for x in lng2List:
                if x>max2:
                    max2=x

            folderbbox=[min1, min2, max1, max2]
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("boundingbox of the whole folder:")
            print(folderbbox)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            ret_value_folder.append(folderbbox)
            #return folderbbox
        else:
            ret_value_folder.append([None])
        if detail=='convexHull':
            print("tzttztztztz")
            points=extractTool.bboxArray
            print("gi")
            print(points)
            print(ConvexHull(points))
            hull=ConvexHull(points)
            print("hi")
            hull_points=hull.vertices
            convHull=[]
            print("concon")
            for y in hull_points:
                point=[points[y][0], points[y][1]]
                convHull.append(point)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            click.echo("convex hull of the folder:")    
            click.echo(convHull)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            #return convHull
            ret_value_folder.append(convHull)
        else:
            ret_value_folder.append([None])
        if (time):
            times=extractTool.timeextendArray
            mindate=[]
            maxdate=[]
            for z in times:
                mindate.append(z[0])
                maxdate.append(z[1])
            min_mindate=min(mindate)
            max_maxdate=max(maxdate)
            folder_timeextend=[min_mindate, max_maxdate]
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            click.echo("timeextend of the folder:")    
            click.echo(min_mindate)
            click.echo(max_maxdate)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            #return folder_timeextend
            ret_value_folder.append(convHull)
        else:
            ret_value_folder.append([None])

    print(ret_value_folder)
    return ret_value_folder

        


if __name__ == '__main__':
    openFolder()