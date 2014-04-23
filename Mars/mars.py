''' Style Guide
http://www.python.org/dev/peps/pep-0008/'''

''' standard library imports '''
import os
import sys

''' related third party imports ''' 
import gdal

''' local imports '''
import VectorDrawing
import ImageShifting

''' Some functions for visualizing data from http://hirise.lpl.arizona.edu/dtm/ '''

def colourizeTile(inputFileName='DTEED_016907_1330_016973_1330_U01.IMG',outFileName = 'OUT.TIF',resolution =20,deleteIntermediaryFiles=False):

	'''
	Use GDAL utilities to visualize data
	Basically we are calling a bunch of GDAL utilities to help visualize the data
	'''

	''' Convert .IMG file into a .TIF file '''
	os.system('gdal_translate '+inputFileName+' MARS.TIF')

	''' Resize image using cubic spline to a resolution of (resolution) meters '''	
	os.system('gdalwarp -q -tr '+str(resolution)+' -'+str(resolution)+' -r cubic MARS.TIF SHRUNK.TIF')
	
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
	os.system('wget '+fpath)
	
if __name__ == "__main__": 
	downloadedScene()
	colourizeTile()
	print('Shifting image')
	ImageShifting.shiftImage()
	print('Drawing DEM')
	VectorDrawing.drawDEM()
