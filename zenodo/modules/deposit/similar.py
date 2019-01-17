import math
import detailebenen
import click
# import typ 

# Beispielkoordinaten
# bbox1 = [5.8663155, 47.270111, 15.041932 , 55.099159]
# bbox2 = [7.5234, 52.0326, 7.7556, 52.152]

# def mastersim(filepath):
    # bbox1 = detailebenen(filepath) blabla Hier muessen die Bboxen berechet werden
    # bbox2 = detailebee(filepath) blabla also detailebenen Aufrufen
    # sim = aehnlickeit(bbox1, bbox2)
    # Hier muss typ.py
    # input1 = typ.getTyp(filepath)
    # input2 = typ.getTyp(filepath)
    # whatDataType(input1, input2, sim)

"""returns the new calculated similarity score
:param input1: filepath from a file
:param input2: filepath from a file
:param imput3: similarity score from two bounding boxes
"""
def whatDataType(input1, input2, sim):
    if input1 == "raster" and input2 == "raster":
        click.echo("These files are rasterdata")
        return sim
    if input1 == "vector" and input2 == "vector":
        click.echo("These files are vectordata")
        return sim
    if input1 == "raster" and input2 == "vector" or input1 == "vector" and input2 == "raster":
        click.echo("These files are not the same datatype")
        sim = sim*5/4
        if sim > 1:
            sim = 1
        return sim

"""
Function to calculate the similarity score
:param bbox1: Bounding Box from a file
:param bbox2: Bounding Box from a file
:returns: similarity score from the two Bounding Boxes
"""
def aehnlickeit (bbox1,bbox2):
    
    if isinstance(bbox1[0], float) and isinstance(bbox1[1], float) and isinstance(bbox1[2], float) and isinstance(bbox1[3], float):
        if isinstance(bbox2[0], float) and isinstance(bbox2[1], float) and isinstance(bbox2[2], float) and isinstance(bbox2[3], float):

            if distance(bbox1,bbox2) < 20000:
                simdis = distance(bbox1,bbox2)/20000
            else:
                simdis = 1
            if abs(area(bbox1) - area(bbox2)) < 1000000:
                simA = (abs(area(bbox1) - area(bbox2)))/1000000
            else:
                simA = 1
            sim = (2 * simdis + simA)/3
            print(sim)
            return sim
        
    else:
        return None

"""
Function to calculate the mean latitude
:param list: 
:returns: the mean Latitude
"""
def meanLatitude (list):
    lat = (list[3]+list[1])/2
    return lat

"""
Function to calculate the mean longitude
:param list: 
:returns: the mean Longitude
"""
def meanLongitude (list):
    lon = (list[2]+list[0])/2
    return lon

"""
Function to calculate the latitude
:param list: 
:returns: the Latitude
"""
def width (list):
    x = (list[2]-list[0])*111.3 * (math.cos(meanLatitude(list)*math.pi/180))
    return x

"""
Function to calculate the mean longitude
:param list: 
:returns: the longitude
"""
def length (list):
    y =(list[3]-list[1])*111.3
    return y

"""
Function to calculate area
:param list: 
:returns: the area
"""
def area (list):
    A = width(list) * length(list)
    return A

"""
auxiliary calculation
:param bbox1: Bounding Box from a file
:param bbox2: Bounding Box from a file
:returns: the cosinus
"""
def lawOfCosines(bbox1,bbox2):
    cos = math.sin((meanLatitude(bbox1) * math.pi/180))*math.sin((meanLatitude(bbox2)*math.pi/180)) + math.cos((meanLatitude(bbox1)*math.pi/180)) * math.cos((meanLatitude(bbox2)*math.pi/180)) * math.cos((meanLongitude(bbox1)*math.pi/180)-(meanLongitude(bbox2)*math.pi/180))
    return cos

"""
function to calculate the distace between two Bounding Boxes
:param bbox1: Bounding Box from a file
:param bbox2: Bounding Box from a file
:returns: the distance
"""
def distance(bbox1,bbox2):
    dist = math.acos(lawOfCosines(bbox1,bbox2)) * 6378.388
    return dist

if __name__ == '__main__':
    aehnlickeit(bbox1, bbox2)
