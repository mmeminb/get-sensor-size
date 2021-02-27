import argparse
from bs4 import BeautifulSoup
import requests
import difflib
from PIL import Image
import PIL.ExifTags
import numpy as np

"""
Explanations
    "sensor-size.py" gets camera model name from image's exif data and get sensor size from www.dpreview.com
    Output of ReadImageGetSensorSize(dir) function is numpy array of sensor size.
    
    Parameters:
    --imagePath -> image's directory
    
    Command Line Example:
    python sensor-size.py --imagePath /home/emin/Desktop/image.jpg
    
    Example's Output:
    [22.3 14.9]
"""
def ReadImageGetSensorSize(dir):
    try:
        img = Image.open(dir)
        model = GetCameraModelFromExifData(img)
        link = GetModelLinkFromdpreview(model)
        sensorData = GetSensorData(link)
        strSensor = ParseSensorData(sensorData)
        sensorArray = np.asarray(strSensor, dtype=np.float32)
        return sensorArray

    except:
        return None

def GetCameraModelFromExifData(img):
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    return exif.get('Model')

def GetModelLinkFromdpreview(modelName):
    dpreviewSearchLink = 'https://www.dpreview.com/search?query='

    ##searching link for dpreview
    link = dpreviewSearchLink + modelName.replace(' ','+')
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')

    try:
        div1 = soup.find('div', class_ = 'subsection topProduct')
        link = div1.find('a', href = True)
        if(link['href'] != None):
            return link['href']
    except:
        try:
            cameraList = []
            cameraLinkList = []

            for td in soup.find_all('td', class_='productName'):
                ##camera name
                cameraList.append(td.a.text)

                ##camera link
                a = td.find('a', href = True)
                cameraLinkList.append(a['href'])

            closestModel = difflib.get_close_matches(modelName, cameraList, len(cameraList), 0)[0]
            indexOfModel = cameraList.index(closestModel)
            linkOfModel = cameraLinkList[indexOfModel]
            return linkOfModel
        except:
            return None

def GetSensorData(link):
    source = requests.get(link).text
    soup = BeautifulSoup(source, 'lxml')

    trList = []
    rightTable = soup.find('div', class_='rightColumn quickSpecs')
    for tr in rightTable.find_all('tr'):
        for td in tr.find_all('td'): 
            trList.append(td.text)

    indexOfSensorData = trList.index('Sensor size') + 1
    return trList[indexOfSensorData]

def ParseSensorData(sensorData):
    splSensorData = sensorData.split(' ')
    indiceOfX = splSensorData.index('x')
    strSensor = float(splSensorData[indiceOfX-1][1:]), float(splSensorData[indiceOfX+1])
    return strSensor

def ParseInputs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--imagePath', type=str)
    parameters = parser.parse_args()
    return parameters

def main():
    prm = ParseInputs()
    sensorSizeArray = ReadImageGetSensorSize(prm.imagePath)
    print(sensorSizeArray)

if __name__ == '__main__':
    main()



