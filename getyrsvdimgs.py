import praw
import json
import requests
import os
import pandas as pd

# Use these functions to check if a link is downloadable before trying to download it, derived from a function I found here: https://www.codementor.io/@aviaryan/downloading-files-from-urls-in-python-77q3bs0un
def is_imgvid(url):
    """
    Does the url contain a downloadable image or video
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('Content-Type')
    try:
        if 'image' in content_type.lower():
            return True
        if 'video' in content_type.lower():
            return True
    except: return False
    else:
        return False
    
# Use this function to make the filename, built from code found here: https://www.codementor.io/@aviaryan/downloading-files-from-urls-in-python-77q3bs0un
def makefname(url):
    if url.find('/') and (url.rsplit('/', 1)[1]):
        filename = url.rsplit('/', 1)[1]
        return filename

# Load a credentials file for authentication, see file in this repository named prawcreds-blank.json for the JSON I use
credname = input('Enter credentials file name: ')
credh = open(credname)
creddata = credh.read()
credinfo = json.loads(creddata)

# Get a Reddit instance
reddit = praw.Reddit(
    client_id=credinfo['credentials']['client_id'],
    client_secret=credinfo['credentials']['client_secret'],
    user_agent=credinfo['credentials']['user_agent'],
    username=credinfo['credentials']['username'],
    password=credinfo['credentials']['password'],
)

# Name the user and which subreddit from which you want saved submissions
redditor = input('Provide redditor handle: ')
subreddit = input('Which subreddit do you want: ')

# Create a directory to store images
imgDir = input('Enter directory path: ')
redditorDir = str(redditor)
subredditDir = str(subreddit)
path = os.path.join(imgDir, redditorDir, subredditDir)
print(path)
if not os.path.exists(path):
    os.mkdir(path)

# Get user's saved submissions; consider adding an input line for the limit, if I don't want every saved submission
saved = reddit.redditor(redditor).saved(limit = None)

# I want to store the description and filename of each image; they are nice to look at but less meaningful if I don't know what they are showing
descriptionList = []
filenameList = []

# Check the subreddit and download images that match desired subreddit
count = 0
for item in saved:
    if item.subreddit == str(subreddit):
        url = item.url
        print(url)
        if is_imgvid(url) == True:
            filename = makefname(url)
            filenameList.append(filename)
            testRequest = requests.get(url)
            print(testRequest.status_code)
            if testRequest.status_code == 200:
                count = count + 1
                imgData = requests.get(url).content
                with open(str(imgDir) + '/' + str(redditor) + '/' + str(subreddit) + '/' + filename, 'wb') as handler:
                    handler.write(imgData)
                description = item.title
                descriptionList.append(description)
                print ('Saved ' + filename)
            else: continue
print(str(count) + ' images downloaded.')

# Create a file that gives the description of each image keyed to the image filename
df = pd.DataFrame(list(zip(descriptionList, filenameList)), columns =['Description', 'Image File'])
df.to_csv(str(path) + '/imagedescriptions.csv', index = False)
    
