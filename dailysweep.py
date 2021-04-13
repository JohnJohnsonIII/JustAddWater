import os
import ftplib
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
import json


with open("./credentials.json") as fin:
    credentials = json.loads( fin.read() )
with open("./settings.json") as fin:
    settings = json.loads( fin.read() )


yesterday = datetime.now() - timedelta(1)
yesterday = datetime.strftime( yesterday, "%Y-%m-%d")
yesterday = datetime.strptime( "2021-04-07", "%Y-%m-%d")
ftp = ftplib.FTP( credentials["servername"], credentials["user"], credentials["password"] )
ftp.cwd( credentials[ "remoteroot" ] )
ftp.storlines( 'STOR '+'tempandhum.txt', open( os.path.join( setting["rootdir"], 'tempandhum.txt'), 'rb' ) )
for camera in settings["cameras"]:
    ftp.cwd( settings["remoteroot"]+settings["archivedir"]+camera[ "saveddir" ] )
    files = [f for f in listdir( os.path.join( settings["rootdir"], settings["archivedir"], camera["savedir"] ) ) if isfile(join( os.path.join( settings["rootdir"], settings["archivedir"], camera["savedir"] ) , f)) and f[0:17]==('usbcam-'+yesterday)]
    files = sorted(files)
    for f in files:
        ftp.storbinary('STOR '+f, open( os.path.join( os.path.join( settings["rootdir"], settings["archivedir"], camera["savedir"] ),f), 'rb'))
