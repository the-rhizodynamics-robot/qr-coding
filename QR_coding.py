#This is the path where the labels.csv file is located and where the final labels will be saved
path = "\PATH\TO\labels.csv"

import cv2
import numpy as np
import qrcode
from PIL import Image, ImageDraw
import imageio
import os
import re

#this reads in label data from csv
my_data = np.genfromtxt(path + "labels.csv", delimiter=',',encoding="utf8",dtype=None)

#this appends empty rows on matrix to make it a size multiple of 48, which is how many labels are on each page
my_data = np.vstack((my_data, np.empty([ (int(my_data.shape[0]/48)+1)*48-my_data.shape[0]+1,2], dtype=str)))


#number of times to loop though (basically the number of pages you are going to print). If you have 48 or fewer labels, it will equal 1.
#49-96, it will equal 2, etc.
num_loop = int((my_data.shape[0]-1)/48)

#keep track of what row of the file we are on 
count = 1

#we go one over num_loop to get the remainder of rows after dividing total row number by 48 (ie number of labels on page)
for num in range(1,num_loop + 1):
   
    #make large array where we'll put the images
    large=np.zeros((7260,5610))
    large=large+255
       

    # places 500x500 QR code and text into large numpy matrix
    #The sheet of labels I use has 12 rows
    for outer in range(0,12):
    
            #The sheet has 4 columns
            for inner in range(0,4):
                #read in first row
                row = my_data[count,]
        
                #make QR code of first cell
                qr = qrcode.QRCode(
                     version=1,
                     error_correction=qrcode.constants.ERROR_CORRECT_H,
                     box_size=10,
                     border=4,
                )
                qr.add_data(row[0])
                qr.make(fit=True)
                
                #creation of temp files was the first solution I found to get into flat 2d format
                temp = qr.make_image(fill_color="black", back_color="white")
                temp.save(path + "temp.png")
                img_rgb = cv2.imread(path + "temp.png")
                os.remove(path + "temp.png")
                
                # converts rgb image to 2D grayscale image
                img = cv2.cvtColor(img_rgb,cv2.IMREAD_GRAYSCALE)[:,:,0]
                
                # resizes the image from 330x330 (default) to 500x500
                img = cv2.resize(img,(500,500))
                
                #this is to avoid making a qr code for the header row. 
                if (not row[0]):
                    img = 255
                
                #Place QR code in appropriate location
                #These coordinates and offsets have to be optimized for different label dimensions
                large[round(40+outer*600):round(540+outer*600), round(170+1400*inner):round(670+1400*inner)] = img
                                
                #making image from description text
                img2 = Image.new('RGBA', (75, 75), color='#DDEEFF')
                d = ImageDraw.Draw(img2)
                conc = re.sub("(.{10})", "\\1\n", str(row[0])+ " "+ str(row[1]), 0, re.DOTALL)
                d.text((10,10), conc , fill=(255,0,0))
                img2.save(path + "temp2.png")
                img_rgb = cv2.imread(path + "temp2.png")
                os.remove(path + "temp2.png")
                  
                # converts rgb image to 2D grayscale image
                img = cv2.cvtColor(img_rgb,cv2.IMREAD_GRAYSCALE)[:,:,0]
                
                # resizes the image from 330x330 (default) to 500x500
                img = cv2.resize(img,(500,500))
                
                #Place description in appropriate location
                large[round(40+outer*600):round(540+outer*600), round(170+550+1400*inner):round(670+550+1400*inner)] = img
                
                count+=1
    
    #write final image
    imageio.imwrite(path + str(num)+ ".png", large)