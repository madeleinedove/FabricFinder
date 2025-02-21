from patternFinder import getImageFromWebsite, searchFabrics



## web crawler here

url = 'https://simplicity.com/vogue-patterns/v2100'

getImageFromWebsite(url,  "cropped.png")
searchFabrics("cropped.png")