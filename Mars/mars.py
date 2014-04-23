''' Style Guide
http://www.python.org/dev/peps/pep-0008/'''

''' standard library imports '''
import os
import sys

''' related third party imports ''' 
import gdal
import matplotlib.cm as cm
from PIL import Image,ImageChops

''' local imports '''
import VectorDrawing
import ImageShifting

''' Some functions for visualizing data from http://hirise.lpl.arizona.edu/dtm/ '''

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
	
def colourizeTile(inputFileName='DTEEC_023586_1425_024008_1425_A01.IMG',outFileName = 'combined.TIF',resolution =20,deleteIntermediaryFiles=False):

	'''
	Use GDAL utilities to visualize data
	Basically we are calling a bunch of GDAL utilities to help visualize the data
	'''

	''' Convert .IMG file into a .TIF file '''
	os.system('gdal_translate '+inputFileName+' MARS.TIF')

	''' Resize image using cubic spline to a resolution of (resolution) meters '''	
	os.system('gdalwarp -q -tr '+str(resolution)+' -'+str(resolution)+' -r cubic MARS.TIF SHRUNK.TIF')
	
	ds = gdal.Open('SHRUNK.TIF', gdal.GA_ReadOnly)
	DEM=(ds.GetRasterBand(1).ReadAsArray())
	createColorMapLUT(DEM.min(),DEM.max())
	
	''' do some hillshading '''
	os.system('gdaldem hillshade -q -az 45 -alt 45 -of PNG SHRUNK.TIF hillshade.TIF')

	''' produce an image which is colored by altitude , color map is stored in color_relief.txt '''
	os.system('gdaldem color-relief -q SHRUNK.TIF color_relief.txt color_relief.TIF')

	''' do some slope shading '''
	os.system('gdaldem slope -q SHRUNK.TIF slope.TIF')
	os.system('gdaldem color-relief -q slope.TIF color_slope.txt slopeshade.TIF')
	
	''' Merge components using Python Image Lib '''
	slopeshade = Image.open("slopeshade.TIF").convert('L')
	hillshade = Image.open("hillshade.TIF")
	colorRelief = Image.open("color_relief.TIF")
	shading = ImageChops.multiply(slopeshade, hillshade).convert('RGB')
	output = ImageChops.multiply(shading,colorRelief)

	output.save(outFileName)

	''' copy the projection info to the output file '''
	os.system('python gdalcopyproj.py SHRUNK.TIF '+outFileName)

	''' Save space by deleting all the intermediate files '''
	if deleteIntermediaryFiles ==True:
		os.system('rm slope.TIF')
		os.system('rm slopeshade.TIF')
		os.system('rm color_relief.TIF')
		os.system('rm hillshade.TIF')
		os.system('rm *aux.xml')
	
def downloadedScene(fpath ='http://hirise.lpl.arizona.edu/PDS/DTM/ESP/ORB_016900_016999/ESP_016907_1330_ESP_016973_1330/DTEED_016907_1330_016973_1330_U01.IMG'):
	''' Added in this function to be absolutely explicit about where the DEM's come from/which file to download '''
	os.system('wget '+fpath)
	
if __name__ == "__main__": 
	#downloadedScene()
	colourizeTile()
	print('Shifting image')
	ImageShifting.shiftImage()
	print('Drawing DEM')
	VectorDrawing.drawDEM()
