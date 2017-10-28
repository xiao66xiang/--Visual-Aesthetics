##################### Import Library #########################
import os
from flask import Flask, render_template, request, redirect, url_for,send_from_directory
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image
import pytesseract
import numpy as np
import cv2
import re
############################################################


############# Functions for image processing ################
def image_preprocess(image):
    
    #denoising image
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)    

    # detect edges in the image
    edged = cv2.Canny(gray,1,1)

    return edged

def detect_objects(filename,image,edged):
    listW = []

    #number of images
    total_images = 0
    words_size = 0
    images_size = 0
    
  
    # find contours    
    im2,cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

    exp = image.copy()
    #store object detected
    total = []

    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        if w>7 and h>7:            
            new_img=image[y:y+h,x:x+w]
            total.append(new_img)
            im = Image.fromarray(np.asarray(new_img))
            width, height = im.size
            # detect words in image
            word = pytesseract.image_to_string(im)
            word = re.sub(r'[^\w]', ' ', word)        
            if len(word)>1:
                words_size+=width*height
                cv2.rectangle(exp, (x+1,y+1), (x+w-1,y+h-1), (0, 0, 255), 1)
                l = word.split(' ')
                for i in l:                
                    if len(i)>1 and i.isalpha():
                        listW.append(i)
            #else, object is image                    
            else: 
                total_images+=1
                images_size+=width*height
                cv2.rectangle(exp, (x+1,y+1), (x+w-1,y+h-1), (0, 255, 0), 1)

    cv2.imwrite(os.path.join('upload', filename+'dilation.png'),exp)
    listW = filter(lambda a: a!='',listW)           
    total_words = len(listW)
    
    return total_words,total_images,words_size,images_size
          
                

def detect_TLCs(image,edged):

   
    #Dilating edged to create blocks of white color
    kernel = np.ones((5,5),np.uint8)
    dilation = cv2.dilate(edged, kernel, iterations = 3)
    
    # find contours
    #total number of objects found
    im2,cnts, hierarchy = cv2.findContours(dilation.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)

 
    return len(cnts)

#predict the aesthetic score
def score(vs):
    if vs > 2 and vs <= 3:
        result = 4
    elif vs > 3 and vs <= 4:
        result = 5
    elif vs > 4 and vs <= 5.5:
        result = 3
    elif vs > 5.5 and vs <= 8:
        result = 2
    else:
        result = 1

    return result

#############################################################