from mutagen.flac import FLAC, Picture, FLACNoHeaderError
from listfmalbumart import LastFM
import os
import urllib, urllib2
import logging
import optparse

version = "0.0.1"


def add_flac_cover(filename, albumart):
    audio = File(filename)

    image = Picture()
    image.type = 3
    if albumart.endswith('png'):
        mime = 'image/png'
    else:
        mime = 'image/jpeg'
    image.desc = 'front cover'
    with open(albumart, 'rb') as f: # better than open(albumart, 'rb').read() ?
        image.data = f.read()

    audio.add_picture(image)
    audio.save()

def pict_test(audio):
    try: 
        x = audio.pictures
        if x:
            return True
    except Exception:
        pass  
    if 'covr' in audio or 'APIC:' in audio:
        return True
    return False




def findRightImageFromLastFm(images):
    preferance = ['large','extralarge','mega','medium','small']
    preferance.reverse()
    bestUrl = None
    bestPreferanceIndex = -1
    images[0]["size"]
    for image in images:
        try:
            thisPreferanceIndex = preferance.index(image["size"])
        except ValueError:
            thisPreferanceIndex = -1
        if bestPreferanceIndex < thisPreferanceIndex:
            bestPreferanceIndex = thisPreferanceIndex
            bestUrl = image["#text"]
    return bestUrl
    


def AddCoverArt2(path,AddCoverArtMetadata):
    print path
    last_request = LastFM()
    for (path, dirs, files) in os.walk(path):
        filemetadata = {}
        for filename in files:
            filePath = os.path.join(path,filename)
            try:
                metadata = FLAC(filePath)
            except FLACNoHeaderError as (strerror):
                print strerror
                continue
            if pict_test(metadata):
                print "Already has cover are:%s" % (filePath)
                continue
            metadataArtst = None
            metadataAlbum = None
            try:
                metadataAlbum = metadata['album']
            except KeyError:
                print "foo %s " % metadata
                continue
            try:
                metadataArtst = metadata['artist']
            except KeyError:
                pass
            try:
                metadataArtst = metadata['performer']
            except KeyError:
                pass
            if "artist" in AddCoverArtMetadata:
                metadataArtst = AddCoverArtMetadata["artist"]
            if "album" in AddCoverArtMetadata:
                metadataArtst = AddCoverArtMetadata["artist"]
            if metadataArtst == None:
                print "No artist skipping: %s" % (filePath)
                continue
            lastmetadata = last_request.album_getInfo({"artist" : metadataArtst[0], "album" : metadataAlbum[0]})
            #lastmetadata = last_request.album_getInfo({"artist" : "various", "album" : metadataAlbum[0]})
            if lastmetadata == None:
                continue
            imageprefs = []
            imageUrl = findRightImageFromLastFm(lastmetadata['album']["image"])
            if len(imageUrl) == 0:
                print "No cover art Url found for: %s" % (filePath)
                continue
            print imageUrl, metadataArtst, metadataAlbum
            image = Picture()
            image.type = 3
            image.desc = 'front cover'
            if imageUrl.endswith('png'):
                mime = 'image/png'
            if imageUrl.endswith('jpg'):
                mime = 'image/jpeg'
            try:
                data = urllib2.urlopen(imageUrl  )
            except urllib2.URLError:
                print "Could not open URL: %s for file : %s" % (imageUrl,filePath)
                continue
            image.data = data.read()
            metadata.add_picture(image)
            metadata.save()




def AddCoverArt(pathList,AddCoverArtMetadata):
    print pathList
    for path in pathList:
        AddCoverArt2(path,AddCoverArtMetadata)
        

def main():
    log = logging.getLogger("main")
    """Runs program and handles command line options"""
    parser = optparse.OptionParser(version = "%prog " + version)
    parser.add_option('--path', action ='append',help='list subscriptions')
    parser.add_option('--artist',action='append',help='Artist Name')
    parser.add_option('--album',action='append',help='Artist Name')
    options, arguments = parser.parse_args() 
    metadata = {}
    if options.artist:
        if len(options.artist) > 0:
            metadata['artist'] = options.artist
    if options.artist:
        if len(options.artist) > 0:
            metadata['album'] = options.artist
    
    if options.path:
        AddCoverArt(options.path,metadata)

if __name__ == "__main__":
    main()
