from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

def SSD(template,mask,imageSubsection):
	''' Function to find the sum of squares difference between a mask and a template '''
	diffsSquared = ((template-imageSubsection)**2)
	diffsSquared *=mask
	score = diffsSquared.sum()
	return(score)

''' Load template and image to search from file '''
template = np.asarray(Image.open('2_5m.png'))
searchArea = np.asarray(Image.open('FindPlane.png'))
searchArea  = searchArea[:,:,:3]

''' fiddle with template to extract out alpha mask '''
mask = np.dstack((template[:,:,3],template[:,:,3],template[:,:,3]))
mask = mask/255.0
template = template[:,:,0:3]

''' set min score to be a really big number '''
minScore = 256*256*3*template.shape[0]*template.shape[1] #largest possible score

''' create an array that will hold the SSD score '''
scoreArray = np.zeros((searchArea.shape[0]-template.shape[0],searchArea.shape[1]-template.shape[1]))

'''
For every pixel in the image where the template can fit,
Find the SSD score '''

for i in range(0,searchArea.shape[0]-template.shape[0]):
	print(i)
	for j in range(0,searchArea.shape[1]-template.shape[1]):
		imageSubsection = searchArea[i:i+template.shape[0],j:j+template.shape[1]]
		score = SSD(template,mask,imageSubsection)
		''' Keep track of the best matches found '''
		if score<minScore:
			bestI,bestJ = i,j
			minScore = score
		scoreArray[i,j] = score
print(bestI,bestJ)
 
''' Draw a pretty picture of where the best matches were '''
plt.imshow(scoreArray)
plt.show()

