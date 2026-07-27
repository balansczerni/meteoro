# https://danepubliczne.imgw.pl/pl/datastore
# datastore/getfiledown/Arch/Telemetria/Meteo/2018/Meteo_2018-01.zip

import requests
import os

def main():
    x = listAllLinks()
    for link in x:
        downloading(link)
    print(x)

    pass

def listAllLinks():

    listOffAllLinks = []

    for x in range(2008, 2027):
        x = str(x)
        for y in range(1, 13):
            y = str(y)
            if len(y) == 1:
                y = "0" + y
            currentLink = linkcreator(x,y)
            listOffAllLinks.append(currentLink)
    return listOffAllLinks

def downloading(link):
    print("DOWNLOADING: " + link)
    file_Path = realDownloading(link)
    size = os.path.getsize(file_Path)
    if size < 300:
        print("CHANGING .zip to .ZIP")
        link = link[0:-3] + "ZIP"
        realDownloading(link)

def realDownloading(link):
    response = requests.get(link)
    file_Name = link[-17:]
    file_Path = "export/" + file_Name
    if response.status_code == 200:
        with open(file_Path, 'wb') as file:
            file.write(response.content)
        print('File downloaded successfully')
    else:
        print('Failed to download file')
    return file_Path



def linkcreator(rok, miesiac):
    baseLink = "https://danepubliczne.imgw.pl/pl/datastore/"
    ext1 = "getfiledown/Arch/Telemetria/Meteo/"
    ext2 = "/Meteo_"
    ext3 = ".zip"
    newLink = baseLink + ext1 + rok + ext2 + rok + "-" + miesiac + ext3
    #print(newLink)
    return newLink


if __name__ == "__main__":
    main()
