# Bahadir Altintas  baltintas@tulane.edu

''' MIT License

Copyright (c) 2022 Tulane University Biodiversitry Research Institute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import traits_tool_mini as ttm #import trait_tool_mini.py as module
import json,sys,glob,os,getopt
from PIL import Image, ImageDraw, ImageFont,ImageFilter,ImageEnhance,ImageOps
import cv2
import numpy as np


def main(argv):
    input_file = None
    output_file = None
    input_directory=None
    input_url=None
    input_csv=None
    csv_field=None
    boundingbox_directory=None
    scientificName="None"
    try:
      opts, args = getopt.getopt(argv,"hi:o:d:b:u:c:f:",["ifile=","ofile=","dir=","bdir=","url=","csv=","col="])
    except getopt.GetoptError:
        print("USAGE: ")
        print ("Single file Example: test.py -i <inputfile> -o <outputfile>")
        print ("Bulk directory Example: test.py -d <directroy_full_path> -o <outputfile>")
        print ("Bulk directory Example: test.py -d <directroy_full_path> -b <original_directory_full_path> -o <outputfile>")
        print ("Url Example: test.py -u <url_address> -o <outputfile>")
        print("-i or --ifile=\tInput file path")
        print("-d or --dir=\tSegmented image directory")
        print("-b or --bdir=\tBoundingbox image directory")
        print("-o or --ofile=\tOutput filename/path")


        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h" or opt == "--help":
            print("USAGE: ")
            print ("Single file Example: test.py -i <inputfile> -o <outputfile>")
            print ("Bulk directory Example: test.py -d <directroy_full_path> -o <outputfile>")
            print ("Bulk directory Example: test.py -d <directroy_full_path> -b <original_directory_full_path> -o <outputfile>")
            print ("Url Example: test.py -u <url_address> -o <outputfile>")
            print("-i or --ifile\tInput file path")
            print("-d or --dir\tSegmented image directory")
            print("-b or --bdir\tBoundingbox image directory")
            print("-o or --ofile\tOutput filename/path")


            sys.exit()

        
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-d", "--dir"):
            input_directory=arg
        elif opt in ("-b", "--bdir"):
            boundingbox_directory=arg
        elif opt in ("-u", "--url"):
            input_url=arg
        elif opt in ("-c","--csv"):
            input_csv=arg
    if output_file is not None:
        print ('Output file is ', output_file)
        if input_file is not None:
            print ('Input file is ', input_file)
            """ try: """
            calculate(input_file,output_file) 
            ttm.put_landmarks_on_image(input_file,LM,scientificName).save("lm_"+fileName)
            """ except:
                print("CALCULATION ERROR") """
               
        elif input_directory is not None:
            print ('Directory is ', input_directory)
            i=0
            for input_file in glob.iglob(input_directory+ '**/*.png', recursive=True):
                i+=1
                print(i)
                current_subfolder = input_file.split('/')[-2]
                scientificName=current_subfolder 
                #print(scientificName)
                try:
                    calculate(input_file, output_file) 
        
                    #generating new image file with lanmarks on it
                    ttm.put_landmarks_on_image(input_file,LM,scientificName).save("lm_"+fileName)
                    if boundingbox_directory is not None:
                        ttm.put_landmarks_on_image(boundingbox_directory+scientificName+"/"+fileName,LM,scientificName).save("lmbb_"+fileName)
                    print("#",i," DONE: [",scientificName,"] [",fileName,"]")
                except:
                    print("#",i," FAILED: [",scientificName,"] [",fileName,"]")
        elif input_url is not None:
            print('Url input entered')
            print ('Input URL :  ', input_url)
            if input_url[-1] == '/':
                print("URL is a directory")
                for file in ttm.listFD(input_url, "png"):
                    input_file=ttm.urlTofile(file)
                    calculate(input_file,output_file)
                    ttm.put_landmarks_on_image(input_file,LM,scientificName).save("lm_"+fileName)
            else:
                print("URL is a file path")

            """ try: """
            """ calculate(input_file,output_file) 
            ttm.put_landmarks_on_image(input_file,LM,scientificName).save("lm_"+fileName) """
            """ except:
                print("CALCULATION ERROR") """
    else: 
        output_file="output.json"


def calculate(input_file,output_file):
    #Load segmented image to array
    global fileName
    global traitsMapAll
    global LM
    fileName,traitsMapAll=ttm.extract_traits_map(input_file)
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
    

    #LANDMARK CALCULATION
    LM={}
    LM[1]="FAIL"
    LM[2]="FAIL"
    LM[3],LM[26],_,LM[28],LM[29]=ttm.get_trait_edges(traitsMapAll,6,"all") #head_left  head_right head_bottom head_centroid
    LM[4]="FAIL"
    LM[6],LM[7],LM[5],LM[8],LM[9]=ttm.get_trait_edges(traitsMapAll,7,"all") #eye_all
    LM[10],_,_,_,LM[30]=ttm.get_trait_edges(traitsMapAll,11,"all") #trunk_left ? #trunk_centroid
    LM[11],_,_,LM[12],LM[33]=ttm.get_trait_edges(traitsMapAll,0,"all") #dorsal_left? dorsal_bottom? #dorsal_fin_centroid
    LM[13]="FAIL"
    LM[14]="FAIL"
    LM[15]="FAIL"
    _,LM[16],_,_,_=ttm.get_trait_edges(traitsMapAll,11,"all") #right edge of the trunk? will be discussed
    LM[17]="FAIL"
    LM[18]="FAIL"
    LM[19]="FAIL"
    LM[20]="FAIL"
    LM[22],_,LM[21],_,LM[34]=ttm.get_trait_edges(traitsMapAll,3,"all") #anal_fin_top ? anal_fin_left ? anal_fin_centroid
    LM[23],_,_,_,LM[35]=ttm.get_trait_edges(traitsMapAll,4,"all") #pelvic_fin_left ? pelvic_fin_centroid
    LM[24],_,_,_,LM[32]=ttm.get_trait_edges(traitsMapAll,5,"all") #pectoral_fin_left ? pectoral_fin_centroid
    LM[25]="FAIL"
    LM[27]="FAIL"
    _,_,_,_,LM[31]=ttm.get_trait_edges(traitsMapAll,2,"all")

      
    
    #TRAITS CALCULATION

    TR={}
    TR[1]=ttm.get_trait_area(traitsMapAll,7) # eye area
    TR[2]=ttm.get_trait_area(traitsMapAll,6) # head area
    TR[3]=ttm.get_trait_area(traitsMapAll,11) # trunk area
    TR[4]=ttm.get_trait_area(traitsMapAll,2) # caudal fin area
    TR[5]=ttm.get_trait_area(traitsMapAll,5) # pectoral fin area
    TR[6]=ttm.get_trait_area(traitsMapAll,0) # Dorsal Fin area
    TR[7]=ttm.get_trait_area(traitsMapAll,3) # Anal fin area
    TR[8]=ttm.get_trait_area(traitsMapAll,4) # Pelvic Fin area
    TR[9]=TR[1]+TR[2] # head size = head area + eye area
    TR[10]=TR[3]+TR[1]+TR[2] # body size = trunk area + head area + eye area
    #TR[16]= LM[16][0]-LM[3][0]  # standard size = snout -trunk_right_maxX? will be discussed
    TR[16]=ttm.get_distance(LM[16],LM[3]) # standard size = snout -trunk_right_maxX? will be discussed
    TR[17]=ttm.get_distance(LM[3],LM[26]) # head length
    TR[18]=ttm.get_distance(LM[10],LM[28]) # head depth
    TR[19]=ttm.get_distance(LM[26],LM[16]) # body length
    TR[20]=ttm.get_distance(LM[11],LM[23]) # body depth
    TR[21]=ttm.get_radius(TR[1])*2 # eye diameter from r=sqrt(1/Pi)
    TR[22]="FAIL" #peduncle depth
    TR[23]=ttm.get_distance(LM[3],LM[9])-ttm.get_radius(TR[1]) # preorbital length
    TR[24]=ttm.get_distance(LM[9],LM[26])-ttm.get_radius(TR[1]) # postorbital length
    TR[25]="WILL BE DISCUSSED" #eye positioning
    TR[31]=ttm.get_ratio(TR[2],TR[3]) # head/trunk area ratio
    TR[32]="FAIL" # snout angle
    TR[33]="FAIL" #caudal angle
    TR[34]=ttm.get_distance(LM[9],LM[29])
    json_string='{"fileName": "'+fileName+'" }'
    LM_json_string=ttm.create_json_from_list("LM",LM)
    TR_json_string=ttm.create_json_from_list("TR",TR)

    #CALCULATING BLOBS OF THE SEGMENTS

    BLOBS=ttm.create_blob_list(traitsMapAll)
    BLOBS_json_string=ttm.create_json_from_list("BLOB",BLOBS)
    
    json_object = {**json.loads(json_string), **json.loads(BLOBS_json_string),**json.loads(LM_json_string), **json.loads(TR_json_string)}
    json_string = json.dumps(json_object) 
    f = open(output_file, "a")
    f.write(json_string+"\n")
    
    #print(json_string) 
    

try:
    calculate("INHS_FISH_7710.png","AAA.JSON") 
    tNum=6
    

    a=ttm.get_trait_image(traitsMapAll,tNum)
    image = cv2.cvtColor(np.array(a,dtype=np.uint8), cv2.COLOR_RGB2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (thresh, image) = cv2.threshold(image, 10, 255, cv2.THRESH_BINARY)
    blackAndWhiteImage = cv2.bitwise_not(image)

    print(blackAndWhiteImage)
    #image = cv2.imread('my.png',0)

    print(image.shape)
    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

   

    # Filter by Area.
    params.filterByArea = False
    params.minArea = 5

    params.filterByColor=False
    params.blobColor=254

    # Filter by Convexity
    params.filterByConvexity = False
    

    # Filter by Inertia
    params.filterByInertia = True
    


    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(blackAndWhiteImage)
    print(keypoints)
    for keyPoint in keypoints:
        x = keyPoint.pt[0]
        y = keyPoint.pt[1]
        s = keyPoint.size
        print(x,",",y,"-",s)

    blank = np.zeros((1, 1))
    blobs = cv2.drawKeypoints(blackAndWhiteImage, keypoints, blank, (0, 0, 255),cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    print("TRAIT has: ",ttm.get_trait_blobs(traitsMapAll,tNum)," blobs") 
    print(ttm.create_blob_list(traitsMapAll))
    cv2.imshow("Blobs Using Area", blobs)
    cv2.waitKey(0)
    cv2.destroyAllWindows() 

    # TEST
    from scipy.ndimage import label, generate_binary_structure
    img=np.where(blackAndWhiteImage > 0, 1, 0)
    print(img)
    labeled_array, num_features = label(img)
    print(num_features)
    # END TEST

except:
    print ("CALCULATION FAILED") 

# /home/bahadir/python_projects/Fish_related/classification/input/inhs-dataset/Species/Training_Set/
if __name__ == "__main__":
   main(sys.argv[1:])