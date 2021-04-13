import os
import json
from PIL import Image

with open("./settings.json") as fin:
    projectdata = json.loads( fin.read() )
rootdir = projectdata["rootdir"]
blendeddir = projectdata["blendeddir"]
archivedir = projectdata["archivedir"]
timelapsevideodir = rootdir
framerates = [480] # video frame rate


def getLastDay( dir ):
    files = [file for file in os.listdir( dir ) if os.path.isfile(os.path.join(dir,file))]
    return sorted( files, reverse=True )[0].split('_')[0] if len(files)!=0 else None

def getDimensions( dir ):
    files = [file for file in os.listdir( dir ) if os.path.isfile(os.path.join(dir,file))]
    targetfile = files[0] if len(files)!=0 else None
    if targetfile:
        pic = Image.open( os.path.join( dir, targetfile ) )
        return '{}x{}'.format(pic.size[0],pic.size[1])
    else:
        return None

lastday = getLastDay( blendeddir )
outputdimensions = getDimensions( blendeddir )
if outputdimensions:
    for framerate in framerates:
        outputfn = os.path.join(timelapsevideodir,'{}-{}fps.mp4'.format(lastday,framerate))
        os.system('ffmpeg -framerate {} -pattern_type glob -i "{}*.jpg" -s:v {} -c:v libx264 -crf 17 -pix_fmt yuv420p "{}"'.format( framerate, blendeddir, outputdimensions, outputfn  ) )
