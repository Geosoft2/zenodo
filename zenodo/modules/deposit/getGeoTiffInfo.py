import click
import extractTool
from osgeo import gdal, ogr, osr

def getGeoTiffbbx(filepath, detail, folder, time):
    #Boolean variable that shows if the crs of the bbox is in wgs84
    wgs_84=True
    gdal.UseExceptions()
    ds = gdal.Open(filepath)
    """@see https://stackoverflow.com/questions/2922532/obtain-latitude-and-longitude-from-a-geotiff-file"""

    if detail =='bbox':
        """CRS Transformation"""
        try:
            #get the existing coordinate system
            old_cs= osr.SpatialReference()
            old_cs.ImportFromWkt(ds.GetProjectionRef())

            # create the new coordinate system
            wgs84_wkt = """
            GEOGCS["WGS 84",
                DATUM["WGS_1984",
                    SPHEROID["WGS 84",6378137,298.257223563,
                        AUTHORITY["EPSG","7030"]],
                    AUTHORITY["EPSG","6326"]],
                PRIMEM["Greenwich",0,
                    AUTHORITY["EPSG","8901"]],
                UNIT["degree",0.01745329251994328,
                    AUTHORITY["EPSG","9122"]],
                AUTHORITY["EPSG","4326"]]"""
            new_cs = osr.SpatialReference()
            new_cs .ImportFromWkt(wgs84_wkt)

            # create a transform object to convert between coordinate systems
            transform = osr.CoordinateTransformation(old_cs,new_cs)
        except Exception:
            wgs_84=False

        #get the point to transform, pixel (0,0) in this case
        width = ds.RasterXSize
        height = ds.RasterYSize
        gt = ds.GetGeoTransform()

        minx = gt[0]
        miny = gt[3] + width*gt[4] + height*gt[5]
        maxx = gt[0] + width*gt[1] + height*gt[2]
        maxy = gt[3]
        #get the coordinates in lat long
        latlongmin = transform.TransformPoint(minx,miny)
        latlongmax = transform.TransformPoint(maxx,maxy)
        bbox = [latlongmin[0], latlongmin[1], latlongmax[0], latlongmax[1]]
        if folder=='single':
            if wgs_84==True:
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoTiff:")
                click.echo(bbox)
                print("----------------------------------------------------------------")
                extractTool.ret_value.append(bbox)
            else:
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoTiff:")
                print(bbox)
                print("Missing CRS -----> Boundingbox will not be saved in zenodo.")
                print("----------------------------------------------------------------")
                extractTool.ret_value.append([None])
            #return (bbox)
        if folder=='whole':
            if wgs_84==True:
                extractTool.bboxArray.append(bbox)
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoTiff:")
                click.echo(bbox)
                print("----------------------------------------------------------------")
            else:
                print("----------------------------------------------------------------")
                click.echo("Filepath:")
                click.echo(filepath)
                click.echo("Boundingbox of the GeoTiff:")
                click.echo(bbox)
                click.echo("because of a missing crs this GeoTiff is not part of the folder calculation.")
                print("----------------------------------------------------------------")
    else:
        extractTool.ret_value.append([None])

    """second level of detail is not reasonable for geotiffs because they are rasterdata."""
    if detail == 'convexHull':
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo('There is no convex hull for GeoTIFF files.')
        print("----------------------------------------------------------------")
        extractTool.ret_value.append([None])
    else:
        extractTool.ret_value.append([None])

    if (time):
        print("----------------------------------------------------------------")
        click.echo("Filepath:")
        click.echo(filepath)
        click.echo('There is no time value for GeoTIFF files')
        print("----------------------------------------------------------------")
        timeval=[None]
        extractTool.ret_value.append(timeval)
    else:
        extractTool.ret_value.append([None])

    if folder=='single':
        print(extractTool.ret_value)
        return extractTool.ret_value

if __name__ == '__main__':
    getGeoTiffbbx()