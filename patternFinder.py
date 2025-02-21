import re
from PIL import Image, ImageChops
import pytesseract
from bs4 import BeautifulSoup
import urllib3
import cv2
import numpy as np
from urllib.request import urlretrieve


def cropImage(save_as: str):
  # (1) Convert to gray, and threshold
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  th, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

  ## (2) Morph-op to remove noise
  kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
  morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)

  ## (3) Find the max-area contour
  cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
  cnt = sorted(cnts, key=cv2.contourArea)[-1]

  ## (4) Crop and save it
  x,y,w,h = cv2.boundingRect(cnt)
  dst = img[y:y+h, x:x+w]
  cv2.imwrite("cropped.png",dst)

  image = cv2.imread(save_as)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, (25,25), 0)
  thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

  contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  mask = np.ones(image.shape[:2], dtype="uint8") * 255

  if contours:
    for f in contours:
      x,y,w,h = cv2.boundingRect(f)
      if w*h>1000:
        cv2.rectangle(mask, (x, y), (x + w, y + h), (36,255,12), 2)

  cv2.imshow("boxes", mask)
  
  cv2.imshow('image', image)
  cv2.waitKey()

  largest_contour = max(contours, key=cv2.contourArea)
  x, y, w, h = cv2.boundingRect(largest_contour)
  cropped_image = image[y:y+h, x:x+w]
  cv2.imwrite("001.png",cropped_image)

http = urllib3.PoolManager()


# url = 'https://en.wikipedia.org/wiki/List_of_fabrics'
# response = http.request('GET', url)
# soup = BeautifulSoup(response.data, "html.parser")
# fabrics = soup.find_all("div", {"class": "mw-body-content"})[0].find_all("a")
# listOfFabrics = [fab.get('title') for fab in fabrics  if fab.get('title') is not None]


url = 'https://simplicity.com/mccalls/m8538'#'https://simplicity.com/mccalls/m8260' #https://simplicity.com/mccalls/m8538'
response = http.request('GET', url)
soup = BeautifulSoup(response.data, "html.parser")
images = soup.findAll('img', alt=True)
backImages = [d for d in images if "Back of Envelope" in d['alt']]
maxImage = max(backImages, key=lambda x:x['height'])

currentImage = maxImage['src'].replace('stencil/480x660/products/','stencil/1800x1800/products/')
if ".gif" in currentImage:
  currentImage = currentImage.replace(".gif",'.png')

save_as = "patternImage.PNG"
down, temp = urlretrieve(currentImage, save_as)

img = cv2.imread(save_as)


if img.any() != None:
  cropImage(save_as=save_as)
else:
  print("Unable to process this url" + url)

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# text = pytesseract.image_to_string(Image.open('001.png'))

# start_string = "Suggested Fabrics"
# end_string = "Sizes"

# # Use regular expressions to extract the text between the two strings
# pattern = f"{start_string}(.*?){end_string}"
# match = re.search(pattern, text, re.DOTALL)

# if match:
#     extracted_text = match.group(1).strip()
#     print(extracted_text)
#     matchingFabrics = set.intersection(set(extracted_text.lower().split()), set(s.lower() for s in listOfFabrics))
#     print(matchingFabrics)
# else:
#     print("Text not found between the specified strings.")