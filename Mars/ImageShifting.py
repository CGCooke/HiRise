''' Style Guide
http://www.python.org/dev/peps/pep-0008/'''

''' standard library imports '''
import os
import sys
import math

''' related third party imports ''' 
from PIL import Image,ImageChops
import numpy as np
import gdal

def shiftImage(scenePath = 'SHRUNK.TIF'):
	ds = gdal.Open(scenePath, gdal.GA_ReadOnly)
	DEM=(ds.GetRasterBand(1).ReadAsArray())
	inputImg = np.asarray(Image.open('OUT.TIF'))
	
	outputImg = np.zeros((inputImg.shape[0],inputImg.shape[1]*2,3),dtype =np.uint8)
	
	''' There are 2 ways to do this, loop through every output pixel, or loop through every input pixel '''
	for i in range(0,inputImg.shape[1]):
		for j in range(0,inputImg.shape[0]):
			outputImg[j,i+inputImg.shape[1],:] = inputImg[j,i,:]
			try:
				outputImg[j,i,:] = inputImg[j,i+DEM[j,i]/100,:]   
			except:
				IndexError
	img = Image.fromarray(outputImg)
	img.save('shifted.TIF')
