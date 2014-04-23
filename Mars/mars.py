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
import cairo


def colourizeTile(inputFileName='*.IMG',outFileName = 'OUT.TIF'):

	''' Use GDAL utilities to visualize data '''

	os.system('gdal_translate '+inputFileName+' MARS.TIF')
	os.system('gdalwarp -q -tr 2 -2 -r cubic MARS.TIF SHRUNK.TIF')
	
	os.system('gdaldem hillshade -q -az 45 -alt 45 -of PNG SHRUNK.TIF hillshade.TIF')
	os.system('gdaldem color-relief -q SHRUNK.TIF color_relief.txt color_relief.TIF')
	os.system('gdaldem slope -q SHRUNK.TIF slope.TIF')
	os.system('gdaldem color-relief -q slope.TIF color_slope.txt slopeshade.TIF')
	
	#os.system('python contours.py')

	''' Merge components using Python Image Lib '''
	slopeshade = Image.open("slopeshade.TIF").convert('L')
	hillshade = Image.open("hillshade.TIF")
	colorRelief = Image.open("color_relief.TIF")
	shading = ImageChops.multiply(slopeshade, hillshade).convert('RGB')
	output = ImageChops.multiply(shading,colorRelief)

	#contours =  Image.open("contours.png")
	#output = ImageChops.multiply(output,contours)
	output.save(outFileName)

	''' copy the projection info to the output file '''
	os.system('python gdalcopyproj.py SHRUNK.TIF '+outFileName)

	''' Save space by deleting all the intermediate files '''
	
	os.system('rm slope.TIF')
	os.system('rm slopeshade.TIF')
	os.system('rm color_relief.TIF')
	os.system('rm hillshade.TIF')
	os.system('rm contours.png')
	os.system('rm *aux.xml')
	
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

def initializeCairoSurface(surfaceShape):    
	WIDTH,HEIGHT =surfaceShape
	surface = cairo.ImageSurface (cairo.FORMAT_RGB24, WIDTH, HEIGHT)
	ctx = cairo.Context (surface)
	ctx.line_to (0,0) 
	ctx.line_to (0,HEIGHT) 
	ctx.line_to (WIDTH,HEIGHT) 
	ctx.line_to (WIDTH,0) 
	ctx.line_to (0,0) 
	r,g,b = 0,0,0
	ctx.set_source_rgb(r,g,b) 
	ctx.fill()
	return(ctx,surface)

def drawTriangle(p1x,p1y,p2x,p2y,p3x,p3y,ctx):
	ctx.move_to(p1x,p1y)
	ctx.line_to(p2x,p2y)
	ctx.line_to(p3x,p3y)
	ctx.line_to(p1x,p1y)
	ctx.stroke()


def projectPoint(X,Y,Z,f):
	x = f*float(X)/float(Z)
	y = f*float(Y)/float(Z)
	return(x,y)

def compute2DCoordinates(i,j,DEM,surfaceShape):
	f =7
	''' how far to shift scene down '''
	depth = 5000

	X = i-DEM.shape[1]/2 - 10
	Y = j-DEM.shape[0]/2
	Z = DEM[j,i]-depth 
	''' Project from 3d to 2d '''
	x,y = projectPoint(X,Y,Z,f)

	''' Shift to fit sensor format '''
	x+=0.5
	y+=0.5
	x*= surfaceShape[0]
	y*= surfaceShape[1] 
	
	''' Flip coordinates up down because of Cairo coordinate space '''
	y = surfaceShape[1]-y	
	x = surfaceShape[0]-x	
	
	return(x,y)

def drawDEM(scenePath = 'SHRUNK.TIF'):

	surfaceShape = 3000,3000
	ctx,surface = initializeCairoSurface(surfaceShape)
	
	r,g,b = 0,0,0
	ctx.set_source_rgb(r,g,b) 
	ctx.set_line_width(0.25)
	ds = gdal.Open(scenePath, gdal.GA_ReadOnly)
	DEM=(ds.GetRasterBand(1).ReadAsArray())
	inputImg = np.asarray(Image.open('OUT.TIF'))

	for i in range(0,DEM.shape[1]-1):
		for j in range(0,DEM.shape[0]-1):
			
			r = inputImg[j,i,0]/255.0
			g = inputImg[j,i,1]/255.0
			b = inputImg[j,i,2]/255.0
			#r,g,b = 0,0,0
			ctx.set_source_rgb(r,g,b) 
			x1,y1 = compute2DCoordinates(i,j,DEM,surfaceShape)
			x2,y2 = compute2DCoordinates(i+1,j,DEM,surfaceShape)
			x3,y3 = compute2DCoordinates(i,j+1,DEM,surfaceShape)
			x4,y4 = compute2DCoordinates(i+1,j+1,DEM,surfaceShape)

			drawTriangle(x1,y1,x2,y2,x3,y3,ctx)
			drawTriangle(x2,y2,x3,y3,x4,y4,ctx)
	surface.write_to_png("contours.png") # Output to PNG          
	


if __name__ == "__main__":
	''' Just addded in for testing '''
	colourizeTile()
	#createStereoPair()
	#shiftImage()
	#createColorMapLUT(colorMap = cm.RdYlGn,numSteps=256):
	#drawDEM()
















