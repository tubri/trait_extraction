#!/usr/bin/env python
# Tool to extract traits(features) from segmented images
# by @xbahadirx
# bahadiraltintas@gmail.com


import os,sys
from pickle import TRUE
import numpy as np
from PIL import Image, ImageDraw, ImageFont,ImageFilter
import cv2
import math
import warnings
from bs4 import BeautifulSoup
import requests
import urllib.request
from pathlib import Path
from urllib.parse import urlparse, unquote

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=np.VisibleDeprecationWarning)
np.set_printoptions(threshold=sys.maxsize)

def create_json_from_list(listName,arrayName):
    a=list(enumerate(arrayName))
    json_string='{'
    for i in arrayName:
        json_string=json_string+'"'+str(listName)+'['+str(i)+']": "'+str(arrayName[i])+'"'
        if i!=a[-1][1]:
            json_string=json_string+','
    json_string=json_string+'}'
    return json_string

def check_trait_available(trait_index):
    if np.where(traitsAvailable==trait_index)[0]>=0:
        return True
    else:
        return False

def create_colorScheme(): #This colorscheme can be modified and applied for different segmentation color shchemes
    colorScheme=[("Dorsal Fin",(254,0,0)),
    ("Adipsos Fin",(0,254,0)),
    ("Caudal Fin",(0,0,254)),
    ("Anal Fin",(254,254,0)),
    ("Pelvic Fin",(0,254,254)),
    ("Pectoral Fin",(254,0,254)),
    ("Head(minus eye)",(254,254,254)),
    ("Eye",(0,254,102)),
    ("Caudal Fin Ray",(254,102,102)),
    ("Alt Fin Ray",(254,102,204)),
    ("Alt Fin Spine",(254,204,102)),
    ("Trunk",(0,124,124))]
    colorScheme=np.array(colorScheme,dtype=object)
    return colorScheme

def get_radius(area):
    if  area>0:
        r=math.sqrt(area/math.pi)
        return r
    else:
        return 0  

def getAngle(a, b, c): # calculates the angle between 3 points given x,y coordinates
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang

def get_distance(firstPoint,secondPoint): #calculates distance between two given point coordinates
    
    if firstPoint[0]!="NULL" and firstPoint[1]!="NULL" and firstPoint[0]!="FAIL" and firstPoint[1]!="FAIL" and secondPoint[0]!="NULL" and secondPoint[1]!="NULL" and secondPoint[0]!="FAIL" and secondPoint[1]!="FAIL":
        dist=((((secondPoint[0] - firstPoint[0] )**2) + ((secondPoint[1]-firstPoint[1])**2) )**0.5)
        return dist
    else:
        
        return 0

def rgb2traitName(rgbColor,colorScheme):

    for namesx in colorScheme:

        if namesx[1]==rgbColor:

            return(namesx[0])

def searchArray(arr1,arr2):
    for i in range(len(arr2)):
        if(arr2[i,1]==arr1):
            return True

def get_trait_minmax_ofPoint(traitsMapAll,trait_index, target, index):  #index : 0 for y-axis : 1 for x-axis
    arr=traitsMapAll[trait_index]
    a=np.array([])
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if (arr[i][j] == target):
                a=np.append(a,[target,arr[i,index]])
    a=np.reshape(a,(int(len(a)/2),2))
    return int(min(a[:,1])),int(max(a[:,1]))

def get_trait_names(trait_index=None):   
    colorScheme=create_colorScheme()
    if trait_index is not None:
        traitNames=colorScheme[trait_index,0]
    else:
        traitNames=colorScheme[:,0]
    return traitNames

def get_trait_colors(trait_index=None):   
    colorScheme=create_colorScheme()
    if trait_index is not None:
        traitColors=colorScheme[trait_index,1]
    else:
        traitColors=colorScheme[:,1]
    
    return traitColors


def get_trait_edges(traitsMapAll,trait_index,pointName="all"): #gets min and max position of the segmented traits (both for x and y-axis)
    #example: get_feature_edges(traitsMapAll,0,"yMin") -> will return maximum y-coordinate of [0]th  trait(Dorsal Fin) 
    #Trait Index (from colorScheme)
    #[0] Dorsal Fin
    #[1] Adipsos Fin
    #[2] Caudal Fin
    #[3] Anal Fin
    #[4] Pelvic Fin
    #[5] Pectoral Fin
    #[6] Head(minus eye)
    #[7] Eye
    #[8] Caudal Fin Ray
    #[9] Alt Fin Ray
    #[10] Alt Fin Spine
    #[11] Trunk
    #pointname
    #top
    #left
    #bottom
    #right
    """ print(traitsAvailable)
    print(np.where(traitsAvailable==trait_index)[0]*3) """
    if check_trait_available(trait_index):
        xMin=min(traitsMapAll[trait_index][:,1])
        xMin_y=traitsMapAll[trait_index][np.where(traitsMapAll[trait_index][:,1]==xMin)[0][round(len(np.where(traitsMapAll[trait_index][:,1]==xMin)[0])/2)],0]
        xMax=max(traitsMapAll[trait_index][:,1])
        xMax_y=traitsMapAll[trait_index][np.where(traitsMapAll[trait_index][:,1]==xMax)[0][round(len(np.where(traitsMapAll[trait_index][:,1]==xMax)[0])/2)],0]
        left= [xMin,xMin_y]
        right=[xMax,xMax_y]
        yMin=min(traitsMapAll[trait_index][:,0])
        yMin_x=traitsMapAll[trait_index][np.where(traitsMapAll[trait_index][:,0]==yMin)[0][round(len(np.where(traitsMapAll[trait_index][:,0]==yMin)[0])/2)],1]
        top=[yMin_x,yMin]
        yMax=max(traitsMapAll[trait_index][:,0])
        yMax_x=traitsMapAll[trait_index][np.where(traitsMapAll[trait_index][:,0]==yMax)[0][round(len(np.where(traitsMapAll[trait_index][:,0]==yMax)[0])/2)],1]
        bottom=[yMax_x,yMax]
        centroidX=round(sum(traitsMapAll[trait_index][:,1])/len(traitsMapAll[trait_index][:,1]))
        centroidY=round(sum(traitsMapAll[trait_index][:,0])/len(traitsMapAll[trait_index][:,0]))
        centroid=[centroidX,centroidY]
        if pointName=="left":
            return left
        elif pointName=="right":
            return right
        elif pointName=="top":
            return top
        elif pointName=="bottom":
            return bottom
        elif pointName=="centroid":
            return centroid
        elif pointName=="all":
            return left,right,top,bottom,centroid
        else:
            print("You should specify proper pointName ('left','right','top','bottom','centroid' or 'all')")
            return  ["NULL","NULL"],["NULL","NULL"],["NULL","NULL"],["NULL","NULL"],["NULL","NULL"]
    else:
        print("\t[",get_trait_names(trait_index),"] does not exist!")
        
        return  ["NULL","NULL"],["NULL","NULL"],["NULL","NULL"],["NULL","NULL"],["NULL","NULL"]
        
def get_trait_area(traitsMapAll,trait_index):
    
    if check_trait_available(trait_index):
       return len(traitsMapAll[trait_index])
    else:
        return 0

def get_ratio(val1,val2):
    if val1 is not None and val2 is not None and val2!=0:
        return val1/val2
    elif val2==0:
        return "FAIL:div Zero"
    else:
        return None

def get_trait_dimensions(traitsMapAll,trait_index,dimType): #returns width and height of given trait_index
    
    if check_trait_available(trait_index):
        left,right,top,bottom,centroid=get_trait_edges(traitsMapAll,trait_index,"all")

        width=right[0]-left[0]
        height=bottom[1]-top[1]
        if dimType=="width":
            return width
        elif dimType=="height":
            return height
        elif dimType=="all":
            return width,height
        else:
            print("You should specify proper dimName ('width', 'height' or 'all')")
            return "NULL"
    else:
        return None,None
def extract_traits_map(file_name):
    global traitsAvailable,traitsMapAll
    head, tail = os.path.split(file_name)
    traitNames=get_trait_names()
    colorScheme=create_colorScheme()
    ####
    img = Image.open(file_name)
    colors = img.convert('RGB').getcolors() 
    colorx=np.array(colors,dtype=object)
    im = img.convert("RGB")
    na = np.array(im,dtype=object)
    
    # Median filter to remove outliers
    im = im.filter(ImageFilter.MedianFilter(3))
    cntr=np.array([])
    traitsMap=[]
    numTraits=0
    for x in colorScheme:
    
        if(searchArray(x[1],colorx)):
            numTraits=numTraits+1
            colorMapY, colorMapX = np.where(np.all(na==x[1],axis=2))
            traitsMap.append(np.stack((colorMapY, colorMapX),axis=1))
            cntr=np.append(cntr,[[x[1],"",""]])

    cntr=np.reshape(cntr,(int(len(cntr)/3),3)) 
 
    traitNamesAvailable=np.array([])
    for f in cntr:
        traitNamesAvailable=np.append(traitNamesAvailable,str(rgb2traitName(f[0],colorScheme)))
    traitsAvailable=np.array([])
    for i in range(np.size(traitNamesAvailable)):
        x = np.where(traitNames == traitNamesAvailable[i])
        traitsAvailable=np.append(traitsAvailable,int(x[0]))
    traitsMapAll=[]
    for i in range(len(colorScheme)):
        if(np.size((np.where(traitsAvailable==i)))>0):
            traitsMapAll.append(traitsMap[int(np.where(traitsAvailable==i)[0])])
        else:
            traitsMapAll.append("NULL")
          
    return tail,traitsMapAll

def get_all_edges(traitsMapAll):
    a={}
    for i in range(len(traitsMapAll)):
        a[i]=get_trait_edges(traitsMapAll,i,"all")
    return a

def get_trait_image(traitsMapAll,trait_index):
    if check_trait_available(trait_index):
        left,right,top,bottom,centroid=get_trait_edges(traitsMapAll,trait_index)
        w,h=get_trait_dimensions(traitsMapAll,trait_index,"all")
        data = np.zeros((h+20, w+20, 3), dtype=np.uint8)
        data[0:w, 0:h] = [0,0,0] # red patch in upper left
        for datax in traitsMapAll[trait_index]:
            data[datax[0]-top[1]+10,datax[1]-left[0]+10]=get_trait_colors(trait_index)

        img = Image.fromarray(data, 'RGB')
        return img
    else:
        return None
def get_trait_blobs(traitsMapAll,trait_index):
    if check_trait_available(trait_index):
        image=get_trait_image(traitsMapAll,trait_index)
        image = cv2.cvtColor(np.array(image,dtype=np.uint8), cv2.COLOR_RGB2BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        (thresh, image) = cv2.threshold(image, 10, 255, cv2.THRESH_BINARY)
        blackAndWhiteImage = cv2.bitwise_not(image)

        
        params = cv2.SimpleBlobDetector_Params()

    

        # Filter by Area.
        params.filterByArea = False
        params.minArea = 5

        params.filterByColor=False
        params.blobColor=0

        # Filter by Convexity
        params.filterByConvexity = False


        # Filter by Inertia
        params.filterByInertia = False



        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(blackAndWhiteImage)
        return(len(keypoints))   
    else:
        return None

def create_blob_list(traitsMapAll):
    blob={}
    for trait_index in traitsAvailable:
        #print(get_trait_names(int(trait_index)),"->",get_trait_blobs(traitsMapAll,int(trait_index)))
        blob[get_trait_names(int(trait_index))]=get_trait_blobs(traitsMapAll,int(trait_index))
    return(blob)



def put_landmarks_on_image(input_file,landMarks,scientificName=None):
    head, tail = os.path.split(input_file)
    img = Image.open(input_file) 
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    r=2
    for i in landMarks:
        #print(i)
        coord=landMarks[i]
        #print("LM:[",i,"] : ",coord)
        
        if coord!="FAIL" and coord!="NULL" and coord!=["NULL","NULL"]:
            font = ImageFont.load_default()
            draw.ellipse((coord[0]-r, coord[1]-r, coord[0]+r, coord[1]+r), fill=(255,204,0))   
            draw.text((coord[0]-11, coord[1]-11),str(i),font=font, fill=(204,153,204))
            
    draw.text((1, 1),scientificName+" - "+tail,font=font, fill=(255,255,255))
    return img

def listFD(url, ext=''):
    page = requests.get(url).text
    #print(page)
    soup = BeautifulSoup(page, 'html.parser')
    return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]    

def urlTofile(url):
    path = urlparse(url).path
    name = path[path.rfind('/')+1:]
    print(name)
    urllib.request.urlretrieve(url, name)
    return name

