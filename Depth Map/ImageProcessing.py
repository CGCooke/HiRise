from PIL import Image
import numpy as np


def SSD(template,mask,imageSubsection):
	diffsSquared = ((template-imageSubsection)**2)
	diffsSquared *=mask
	score = diffsSquared.sum()
	return(score)


template = np.asarray(Image.open('2_5m.png'))
searchArea = np.asarray(Image.open('FindPlane.png'))
searchArea  = searchArea[:,:,:3]

#searchArea=searchArea[1000:5000,1000:5000,:]
mask = np.dstack((template[:,:,3],template[:,:,3],template[:,:,3]))
mask = mask/255.0
template = template[:,:,0:3]


minScore = 256*256*3*template.shape[0]*template.shape[1] #largest possible score
scoreArray = np.zeros((searchArea.shape[0]-template.shape[0],searchArea.shape[1]-template.shape[1]))
for i in range(0,searchArea.shape[0]-template.shape[0]):
	print i
	for j in range(0,searchArea.shape[1]-template.shape[1]):
		imageSubsection = searchArea[i:i+template.shape[0],j:j+template.shape[1]]
		score = SSD(template,mask,imageSubsection)
		if score<minScore:
			bestI,bestJ = i,j
			minScore = score
		scoreArray[i,j] = score
print bestI,bestJ

import matplotlib.pyplot as plt 
plt.imshow(scoreArray)
plt.show()

