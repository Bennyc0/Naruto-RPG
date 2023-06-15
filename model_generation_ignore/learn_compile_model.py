from PIL import Image
import glob

image_train = []
image_test = []

# Settings images into the list
for filename in glob.glob('learning_images/*.jpg'): #assuming jpg
    im=Image.open(filename)
    image_learning.append(im)
for filename in glob.glob('testing_images/*.jpg'): #assuming jpg
    im=Image.open(filename)
    image_list.append(im)
for filename in glob.glob('validation_images/*.jpg'): #assuming jpg
    im=Image.open(filename)
    image_validation.append(im)

