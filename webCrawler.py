from patternFinder import getImageFromWebsite, searchFabrics
import sys

def getResultsByBrand(brandUrl, firstPatternNumber, lastPatternNumber):
  count = 0
  patternNumber = firstPatternNumber
  
  while (count < 5):
    url = brandUrl + str(patternNumber)
    didGetImage = getImageFromWebsite(url,  "cropped.png")
    print(url)
    if (didGetImage):
      count +=1
      getImageFromWebsite(url,  "cropped.png")
      listFabrics, stringFabrics = searchFabrics("cropped.png")
      print(listFabrics)
      print(stringFabrics)
    patternNumber += 1


print("Simplicity")
url = "https://simplicity.com/simplicity/s"
getResultsByBrand(url,1021,9977)