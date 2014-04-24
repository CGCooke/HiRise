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
import matplotlib.cm as cm

def createColorMapLUT(minHeight,maxHeight,cmap = cm.jet,numSteps=256):
	'''
	Create a colormap for visualization
	You can choose any colormap from : http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps?action=AttachFile&do=get&target=colormaps3.png 
	RICHARD : Use this function to generate fancy colormaps!
	Pro tip : tacking on _r to the end of the name of any color map reverses it,
	for example, YlGn -> YlGn_r 
	'''
	colorMap =[]
	f =open('color_relief.txt','w')
	for i in range(0,numSteps):
		r,g,b,a= cmap(i/float(numSteps))
		height = minHeight + (maxHeight-minHeight)*(i/numSteps)
		f.write(str(height)+','+str(int(255*r))+','+str(int(255*g))+','+str(int(255*b))+'\n')
	f.close()

def downloadDEMFromCGIAR(lat,lon):
	''' Download a DEM from CGIAR FTP repository '''
	#uppper right lon = 67*5 - 180
	#upper right lat = 19*5 + 65
	#7*5 = 30 + k 
	#19*5 = -30 + k 

	''' Compute the input file name '''
	tileX = int(math.ceil((lon+180)/5.0))
	tileY = -1*int(math.ceil((lat-65)/5.0))
	
	''' Download from CGIAR '''
	fileName = 'srtm_'+str(tileX).zfill(2)+'_'+str(tileY).zfill(2)+'.zip'
	''' Check to see if we have already downloaded the file '''
	if fileName not in os.listdir('.'):
		os.system('''wget --user=data_public --password='GDdci' http://data.cgiar-csi.org/srtm/tiles/GeoTIFF/'''+fileName)
		os.system('unzip '+fileName)

def renderTile(lat,lon,deleteIntermediaryFiles=False):
	'''
	Render a DEM by using hillshading, slopeshading, hyposomatic tinting and controus
	DEM is projected to UTM
	Should also try this http://www.shadedrelief.com/shelton/
	'''
	outFileName ='out.TIF'

	''' Compute the input file name '''
	tileX = int(math.ceil((lon+180)/5.0))
	tileY = -1*int(math.ceil((lat-65)/5.0))
	inputFileName = 'srtm_'+str(tileX).zfill(2)+'_'+str(tileY).zfill(2)+'.tif'

	''' Change the UTM zone depending on location '''
	utmZone = int((math.floor((lon + 180)/6) % 60) + 1)
	
	''' Check to see if file is in northern or southern hemisphere '''
	if lat<0:
		EPSGCode = 'EPSG:327'+str(utmZone)
	else:
		EPSGCode = 'EPSG:326'+str(utmZone)

	''' Use GDAL utilities to visualize data '''

	''' 100 meter resolution is used because input data is 90 meter resolution, and 100 meter resoultion is numericall neater,
	and slightly undersamples data. '''
	
	os.system('gdalwarp -q -t_srs '+EPSGCode+' -tr 100 -100 -r cubic -srcnodata -32768  '+inputFileName+' warped.TIF')

	''' Set the colorscheme to range from the min height to max height in DEM '''
	ds = gdal.Open('warped.TIF', gdal.GA_ReadOnly)
	DEM=(ds.GetRasterBand(1).ReadAsArray())
	createColorMapLUT(DEM.min(),DEM.max(),cmap =cm.YlGn_r)

	os.system('gdaldem hillshade -q -az 45 -alt 45 -of PNG warped.TIF hillshade.TIF')
	os.system('gdaldem color-relief -q warped.TIF color_relief.txt color_relief.TIF')
	os.system('gdaldem slope -q warped.TIF slope.TIF')
	os.system('gdaldem color-relief -q slope.TIF color_slope.txt slopeshade.TIF')
	
	os.system('python contours.py')

	''' Merge components using Python Image Lib '''
	slopeshade = Image.open("slopeshade.TIF").convert('L')
	hillshade = Image.open("hillshade.TIF")
	colorRelief = Image.open("color_relief.TIF")
	shading = ImageChops.multiply(slopeshade, hillshade).convert('RGB')
	output = ImageChops.multiply(shading,colorRelief)

	contours =  Image.open("contours.png")
	output = ImageChops.multiply(output,contours)
	output.save(outFileName)

	''' copy the projection info to the output file '''
	os.system('python gdalcopyproj.py warped.TIF '+outFileName)

	''' Save space by deleting all the intermediate files '''
	if deleteIntermediaryFiles ==True:
		os.system('rm slope.TIF')
		os.system('rm slopeshade.TIF')
		os.system('rm color_relief.TIF')
		os.system('rm hillshade.TIF')
		os.system('rm warped.TIF')
		os.system('rm contours.png')
		os.system('rm *aux.xml')
	
if __name__ == "__main__":
	lon,lat = float(sys.argv[1]),float(sys.argv[2])
	#lat,lon = -13.1631,-72.54
	downloadDEMFromCGIAR(lat,lon)    
	renderTile(lat,lon)
