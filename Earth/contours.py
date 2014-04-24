''' Style Guide
http://www.python.org/dev/peps/pep-0008/'''

''' standard library imports '''

''' related third party imports ''' 
import numpy as np
from skimage import measure
import cairo
from osgeo import gdal

def initializeCairoSurface(WIDTH,HEIGHT):    
    surface = cairo.ImageSurface (cairo.FORMAT_RGB24, WIDTH, HEIGHT)
    ctx = cairo.Context (surface)
    ctx.line_to (0,0) 
    ctx.line_to (0,HEIGHT) 
    ctx.line_to (WIDTH,HEIGHT) 
    ctx.line_to (WIDTH,0) 
    ctx.line_to (0,0) 
    r,g,b = 1,1,1
    ctx.set_source_rgb(r,g,b) 
    ctx.fill()
    return(ctx,surface)
    
def drawContour(ctx,xPoints,yPoints,z,contourNumber,lineWidth=1):
    for i in range(0,xPoints.size):
        x1,x2 = xPoints[i],yPoints[i]
        ctx.line_to (x1,x2) 
    
    #Set every 5th contour to have double thickness    
    if contourNumber%5==0:    
        ctx.set_line_width(lineWidth*2)
    else:
        ctx.set_line_width(lineWidth)
    ctx.stroke()        
        
def applyContours(contourInterval=100):
    
    ds = gdal.Open('warped.tif', gdal.GA_ReadOnly)
    heightmap=(ds.GetRasterBand(1).ReadAsArray())
    HEIGHT,WIDTH = heightmap.shape
    
    ctx,surface =initializeCairoSurface(WIDTH,HEIGHT)
    
    r,g,b = 0.5,0.5,0.5
    ctx.set_source_rgba(r, g, b)

    #Draw contours every contourInterval meters
    minContour = contourInterval*(int(heightmap.min())//contourInterval)
    maxContour = contourInterval*(1+int(heightmap.max())//contourInterval)
    contourNumber=0
    for z in range(minContour,maxContour,contourInterval):
        contours = measure.find_contours(heightmap, z)
        for n, contour in enumerate(contours):
            #Filter out contours which are not sufficiently large (noise filtration)
            if contour.size>1000:
                drawContour(ctx,contour[:, 1],contour[:, 0],z,contourNumber)
        contourNumber+=1

    surface.write_to_png("contours.png") # Output to PNG    

''' Only run if not called as a module '''
if __name__ == "__main__":
    applyContours()

