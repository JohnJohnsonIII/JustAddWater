import json
import os
import picamera
from PIL import Image, ImageFont, ImageDraw
from datetime import date, datetime, timedelta

#import adafruit_dht
# NEED TO INSTALL picamera submodule
# NEED TO INSTALL pillow submodule

with open("./settings.json") as fin:
    projectdata = json.loads( fin.read() )
rootdir = projectdata["rootdir"]
blendeddir = projectdata["blendeddir"]
archivedir = projectdata["archivedir"]

def setupDirectories():
    if not os.path.isdir( os.path.join(rootdir) ):
        os.mkdir( rootdir )

    if not os.path.isdir( os.path.join(rootdir, blendeddir) ):
        os.mkdir( os.path.join(rootdir, blendeddir) )

    if not os.path.isdir( os.path.join(rootdir,archivedir ) ):
        os.mkdir( os.path.join(rootdir,archivedir ) )

    for camera in projectdata["cameras"]:
        if not os.path.isdir( os.path.join(rootdir,camera["savedir"]) ):
            os.mkdir( os.path.join(rootdir,camera["savedir"]) )
        if not os.path.isdir( os.path.join(rootdir,archivedir, camera["savedir"]) ):
            os.mkdir( os.path.join(rootdir,archivedir,camera["savedir"]) )

def record_temp_humidity():
    try:
        humidity = dhtSensor.humidity
        temp_c = dhtSensor.temperature
        temp_f = format(temp_c * 9.0 / 5.0 + 32.0, ".2f")
        humidity = format(humidity,".2f")
        print("{},{},{}\n".format(currentdate,temp_f,humidity))
        f = open( os.path.join( rootdir,"tempandhum.txt" ),"a+")
        f.write("{},{},{}\n".format(currentdate,temp_f,humidity))
        f.close()
    except RuntimeError:
        print("RuntimeError, trying again...")

def takePictures():
    for camera in projectdata["cameras"]:
        filename = os.path.join(rootdir,camera["savedir"],currentdate+'.jpg')
        if camera["cameratype"]=="usbcamera":
            os.system( 'fswebcam -s brightness={}% -d {} -r {} --no-banner {}'.format( camera["brightness"],camera["device"],camera["resolution"],filename) )
        else:
            with picamera.PiCamera() as thecamera:
                thecamera.resolution = eval( camera["resolution"] )
                thecamera.capture( filename )

def archivePictures():
    for camera in projectdata["cameras"]:
        if os.path.isfile( os.path.join(rootdir,camera["savedir"],currentdate+'.jpg') ):
            os.rename( os.path.join(rootdir,camera["savedir"],currentdate+'.jpg'), os.path.join(rootdir,archivedir,camera["savedir"],currentdate+'.jpg'))

def getFirstDay( dir ):
    files = [file for file in os.listdir( dir ) if os.path.isfile(os.path.join( dir,file))]
    thedate = sorted( files )[0].split('_')[0] if len(files)!=0 else None
    print( thedate )
    return thedate

def blendFiles( imgdate ):
    font = ImageFont.truetype(os.path.join(rootdir,"times-ro.ttf"), 100)
    dayzero = getFirstDay( os.path.join( rootdir, blendeddir ) )
    dayzero = dayzero or imgdate.split('_')[0]
    y,m,d = dayzero.split('-')
    dayzero = date(int(y),int(m),int(d))
    # Get number of days since commencement of our project to overlay
    thedate,thetime = imgdate.split('_')
    y,m,d = thedate.split('-')
    daystring = ((date(int(y),int(m),int(d)) - dayzero).days)+1

    # loop over all cameras to figure out total width of blended image and get height of tallest image
    blendedwidth = 0
    blendedheight = 0
    for camera in projectdata["cameras"]:
        camera["image"] = Image.open( os.path.join( rootdir, camera["savedir"], imgdate+".jpg" ) )
        blendedwidth += camera["image"].size[0]
        blendedheight = camera["image"].size[1] if camera["image"].size[1]>blendedheight else blendedheight
    
    # now create the new image of all the images juxtaposed side by side
    blendedpic = Image.new(mode = "RGB", size = ( blendedwidth, blendedheight ) )    
    totalwidth = 0
    for camera in projectdata["cameras"]:
        blendedpic.paste( camera["image"], (totalwidth,0) )
        totalwidth += camera["image"].size[0]
    
    # Let's make a text box indicating what day of the project this image represents. 
    # Let's make the size proportional to the width/3.6 and the height/3.9 => Found by trial and error
    textwidth = int( blendedwidth/(3.6 * len(projectdata["cameras"])) )
    textheight = int( blendedheight/3.9)
    textpic = Image.new("RGB",(textwidth,textheight), (0,0,0)) 
    draw = ImageDraw.Draw( textpic )
    # draw text with spacing equivalent to 10% indent and somewhat middle of the text image
    draw.text( (int(textwidth/10), int(textheight/2)), "Day {}".format(daystring),(255,255,255),font=font)
    #textpic.putalpha(30)
    # now stick the text image in about the center of our blended image
    textpos = ( int(( blendedpic.size[0]-textwidth)/2), int(( blendedpic.size[1]-textheight)/2))
    blendedpic.paste(textpic,textpos)
    blendedpic.save( os.path.join(rootdir, blendeddir,imgdate+'.jpg'))

# ASSUMPTIONS
# I INTEND FOR THIS PARTICULAR PROJECT TO HAVE TWO CAMERAS THAT WILL TAKE IMAGES WITH THE SAME OUTPUT DIMENSIONS.
# I ALSO INTEND FOR THESE TO BE THE SAME DIMENSIONS THROUGHOUT THE PROJECT
# THIS IS NECESSARY FOR THE BLEND SECTION, WHERE WE OVERLAY A TEXT FIELD OF THE DAY COUNT. MORE THAN TWO SIDE BY SIDE IMAGES WOULD BE UNWIELDY.
# INDIVIDUAL IMAGES WITH OVERLAY MAY BE A FUTURE OPTION.

currentdate = datetime.now().strftime("%Y-%m-%d_%H%M")
setupDirectories()
#dhtSensor = adafruit_dht.DHT22(board.D24)
takePictures()
blendFiles( currentdate )
archivePictures()
