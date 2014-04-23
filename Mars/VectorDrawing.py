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

def initializeCairoSurface(surfaceShape):
	''' Boiler plate code to initialize cairo surface '''
	WIDTH,HEIGHT =surfaceShape
	surface = cairo.ImageSurface (cairo.FORMAT_RGB24, WIDTH, HEIGHT)
	ctx = cairo.Context (surface)

	''' Setting the background of the surface to be black '''
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
	''' Draws a triangle between 3 points in 2d space '''
	ctx.move_to(p1x,p1y)
	ctx.line_to(p2x,p2y)
	ctx.line_to(p3x,p3y)
	ctx.line_to(p1x,p1y)
	ctx.stroke()

def projectPoint(X,Y,Z,f):
	'''
	Project point from 3D space to 2D space
	See http://en.wikipedia.org/wiki/Pinhole_camera_model
	'''

	x = f*float(X)/float(Z)
	y = f*float(Y)/float(Z)
	return(x,y)

def compute2DCoordinates(i,j,DEM,surfaceShape,xShift):
	f =7
	''' how far to shift scene down '''
	depth = 5000

	X = i-DEM.shape[1]/2 + xShift
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
	xShift = -10
	surfaceShape = 1000,1000
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
			x1,y1 = compute2DCoordinates(i,j,DEM,surfaceShape,xShift)
			x2,y2 = compute2DCoordinates(i+1,j,DEM,surfaceShape,xShift)
			x3,y3 = compute2DCoordinates(i,j+1,DEM,surfaceShape,xShift)
			x4,y4 = compute2DCoordinates(i+1,j+1,DEM,surfaceShape,xShift)

			drawTriangle(x1,y1,x2,y2,x3,y3,ctx)
			drawTriangle(x2,y2,x3,y3,x4,y4,ctx)
	surface.write_to_png("mesh.png") # Output to PNG          
