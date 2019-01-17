import click
import shapefile
import extractTool
from scipy.spatial import ConvexHull

def getShapefilebbx(filepath, detail, folder, time):
    """Extracts metadata from shapefiles.

    :param filepath: Path to the file
    :param detail: bbox, convexHull or time
    :param folder: whole or single
    :return: selected detail of the shapefile
    """
    #if the file is a valid shapefile it will be opened with this function.
    #otherwise an exception will be thrown.
    sf = shapefile.Reader(filepath)

    if detail =='bbox':
        print("shapefile bbox")
        output = sf.bbox
        if folder=='single':
            print("----------------------------------------------------------------")
            click.echo("Filepath:")
            click.echo(filepath)
            click.echo("Boundingbox of the Shapefile:")
            click.echo(output)
            click.echo("Missing CRS -----> Boundingbox will not be saved in zenodo.")
            print("----------------------------------------------------------------")
            extractTool.ret_value.append([None])
            #extractTool.ret_value.append(output)
            #print("ret_val")
            #print(extractTool.ret_value)
        if folder=='whole':
            print("----------------------------------------------------------------")
            click.echo("Filepath:")
            click.echo(filepath)
            click.echo("Boundingbox of the Shapefile:")
            click.echo(output)
            click.echo("Shapefiles cannot be used for the calculation of the whole folder because of the missing crs.")
            print("----------------------------------------------------------------")
            #TODO
            #adds the boundingbox of the shapefile to the bboxArray
            #extractTool.bboxArray.append(output)
    else:
        extractTool.ret_value.append([None])
    #calculation of the convex hull of the shapefile
    if detail == 'convexHull':
        shapes=sf.shapes()
        allPts=[]
        for z in shapes:
            points=z.points
            allPts=allPts+points
        hull=ConvexHull(allPts)
        hull_points=hull.vertices
        convHull=[]
        for y in hull_points:
            point=[allPts[y][0], allPts[y][1]]
            convHull.append(point)
        if folder =='single':
            print("----------------------------------------------------------------")
            click.echo("Filepath:")
            click.echo(filepath)
            click.echo("The convex hull of the Shapefile is:")    
            click.echo(convHull)
            print("Missing CRS -----> Convex hull will not be saved in zenodo.")
            print("----------------------------------------------------------------")
            extractTool.ret_value.append([None])
        if folder=='whole':
            print("----------------------------------------------------------------")
            click.echo("Filepath:")
            click.echo(filepath)
            click.echo("The convex hull of the Shapefile is:")    
            click.echo(convHull)
            click.echo("Shapefiles cannot be used for the calculation of the folder because of the missing crs.")
            print("----------------------------------------------------------------")
            #TODO
            #extractTool.bboxArray=extractTool.bboxArray+convHull
            #click.echo(extractTool.bboxArray)
    else:
        extractTool.ret_value.append([None])
    if (time):
        echo="There is no timevalue for Shapefiles"
        click.echo(echo)
        timeval=[None]
        extractTool.ret_value.append(timeval)

    else:
        extractTool.ret_value.append([None])

    if folder=='single':
        print(extractTool.ret_value)
        return extractTool.ret_value


    
if __name__ == '__main__':
    getShapefilebbx()
