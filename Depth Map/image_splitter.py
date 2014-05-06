''' Image splitting utility that splits an image into two halves '''
import sys
from PIL import Image

img = Image.open(sys.argv[1])
w,h = img.size

''' Split image in two down middle '''
left = img.crop((0, 0, int(w/2), h))
right = img.crop((int(w/2), 0, w, h))

''' Save each half '''
left.save(sys.argv[1][:-4]+'_left.png')
right.save(sys.argv[1][:-4]+'_right.png')