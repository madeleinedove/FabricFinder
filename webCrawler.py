from patternFinder import getImageFromWebsite, searchFabrics



## web crawler here

count = 0
patternNumber = 1020
print("Simplicity")
while (count < 5):

  url = 'https://simplicity.com/simplicity/s' + str(patternNumber)
  
  didGetImage = getImageFromWebsite(url,  "cropped.png")
  if (didGetImage):
    print(url)
    count +=1
    getImageFromWebsite(url,  "cropped.png")
    searchFabrics("cropped.png")
  patternNumber += 1