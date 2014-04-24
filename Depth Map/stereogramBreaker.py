from PIL import Image
import numpy as np
import matplotlib.pyplot as plt 
import scipy.ndimage.interpolation

def SSD(template,imageSubsection):
	''' Function to find the sum of squares difference between an image subsection and a template '''
	diffsSquared = ((template-imageSubsection)**2)
	score = diffsSquared.sum()
	return(score)

def findBestMatch(stereogram,x,y,offset,maxShift,minShift):
	minScore = 256*256*3*patchSize*patchSize #largest possible score
	patch = stereogram[y:y+patchSize,x:x+patchSize]

	i =y 
	for j in range(offset+x+minShift,offset+x+maxShift):
		imageSubsection = stereogram[i:i+patchSize,j:j+patchSize]
		score = SSD(patch,imageSubsection)
		if score<minScore:
			bestJ = j
			minScore = score
	return(bestJ)

def buildDepthMap(stereogram,patchSize,stepSize,maxShift,minShift):
	offset = stereogram.shape[1]/2
	depthMap = np.zeros((stereogram.shape[0]-patchSize,offset-patchSize))
	for y in range(0,stereogram.shape[0]-patchSize,stepSize):
		print y
		for x in range(0,offset-patchSize-maxShift,stepSize):
			bestX = findBestMatch(stereogram,x,y,offset,maxShift,minShift)
			shift = bestX-x-offset
			if shift>maxShift:
				shift=maxShift
			if shift<minShift:
				shift=minShift
			depthMap[y:y+stepSize,x:x+stepSize]=shift
	return(depthMap)

def zoom(array,zoomFactor):
	''' Zoom in an array by a zoomFactor times '''
	return(scipy.ndimage.interpolation.zoom(array,zoomFactor))


patchSize = 10
stepSize = 1
stereogram = np.asarray(Image.open('Pentagon.jpg'))
stereogram = zoom(stereogram,0.25)
maxShift =20
minShift =0
depthMap= buildDepthMap(stereogram,patchSize,stepSize,maxShift,minShift)

plt.imshow(depthMap)
plt.colorbar()
plt.savefig('depthmap.png')


