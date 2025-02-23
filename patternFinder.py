import re
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup
import urllib3
import cv2
from urllib.request import urlretrieve
from rembg import remove

http = urllib3.PoolManager()

def getImageFromWebsite(url:str, cropped: str):
  response = http.request('GET', url)
  soup = BeautifulSoup(response.data, "html.parser")
  images = soup.findAll('img', alt=True)
  backImages = [d for d in images if "Back of Envelope" in d['alt']]
  if (len(backImages) == 0): 
    return False
  maxImage = max(backImages, key=lambda x:x['height'])

  currentImage = maxImage['src'].replace('stencil/480x660/products/','stencil/1800x1800/products/')
  if ".gif" in currentImage:
    currentImage = currentImage.replace(".gif",'.png')

  urlretrieve(currentImage, "patternImage.png")

  input_image = Image.open("patternImage.png")
  output_image = remove(input_image)
  output_image.save(cropped)
  image = Image.open(cropped)
  bbox = image.getbbox()
  cropped_image = image.crop(bbox)
  cropped_image.save('cropped.png')
  return True

def cropImage(img):
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

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(gray, (25,25), 0)
  thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

  contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

  largest_contour = max(contours, key=cv2.contourArea)
  x, y, w, h = cv2.boundingRect(largest_contour)
  cropped_image = img[y:y+h, x:x+w]
  cv2.imwrite("cropped.png",cropped_image)

def searchFabrics(image: str):
  url = 'https://en.wikipedia.org/wiki/List_of_fabrics'
  response = http.request('GET', url)
  soup = BeautifulSoup(response.data, "html.parser")
  fabrics = soup.find_all("div", {"class": "mw-body-content"})[0].find_all("a")
  listOfFabrics = [fab.get('title') for fab in fabrics  if fab.get('title') is not None]
  pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
  text = pytesseract.image_to_string(Image.open(image))
  contained = [fabric for fabric in listOfFabrics if fabric in text]

  start_string = "Fabrics"
  end_string = "fabric"

  pattern = f"{start_string}(.*?){end_string}"
  match = re.search(pattern, text, re.DOTALL)

  if match:
      extracted_text = match.group(1).strip()
      return contained, extracted_text
  return contained, ""