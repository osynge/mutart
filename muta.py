from mutagen.flac import FLAC, Picture, FLACNoHeaderError
from listfmalbumart import LastFM
import os
import urllib, urllib2
import logging
import optparse
import sys
try:
    import json
except ImportError:
    import simplejson as json
 
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
    #print "images=%s" % images
    for image in images:
        try:
            thisPreferanceIndex = preferance.index(image["size"])
        except ValueError:
            thisPreferanceIndex = -1
        if bestPreferanceIndex < thisPreferanceIndex:
            bestPreferanceIndex = thisPreferanceIndex
            bestUrl = image["#text"]
    return [bestUrl]
    
class DirAddCoverArtLastFm:
    def __init__(self, path):
        self.path = path
        self.filepaths = []
        self.DefaultArtistList = []
        self.DefaultAlbumList = []
        
    def readfiles(self):
        self.MutagenStructs = {}
        self.AritistsUnion = None
        self.AritistsIntersection = None
        self.AritistsList = None
        self.AlbumUnion = None
        self.AlbumIntersection = None
        self.AlbumList = None
        self.PerformerUnion = None
        self.PerformerIntersection = None
        self.PerformerList = None
        for fileShortName in os.listdir(self.path):
            
            fileName = os.path.join(self.path,fileShortName)
            if os.path.isdir(fileName):
                continue
            try:
                metadata = FLAC(fileName)
            except FLACNoHeaderError as (strerror):
                print "strerror=%s" % ( strerror)
                continue
            if pict_test(metadata):
                print "Already has cover are:%s" % (fileName)
                continue
            self.filepaths.append(fileName)
            self.MutagenStructs[fileName] = metadata
            if self.AritistsList == None:
                try:
                    self.AritistsList = self.MutagenStructs[fileName]['artist']
                except KeyError:
                    pass
            else:
                try:
                    for artist in self.MutagenStructs[fileName]['artist']:
                        if not artist in self.AritistsList:
                            self.AritistsList.append(artist)
                except KeyError:
                    pass
            ####
            if self.AritistsUnion == None:
                try:
                    self.AritistsUnion = set(self.MutagenStructs[fileName]['artist'])
                except KeyError:
                    pass
            else:
                try:
                    self.AritistsUnion = self.AritistsUnion.union(self.MutagenStructs[fileName]['artist'])
                except KeyError:
                    pass
            if self.AritistsIntersection == None:
                try:
                    self.AritistsIntersection = set(self.MutagenStructs[fileName]['artist'])
                except KeyError:
                    pass
            else:
                try:
                    self.AritistsIntersection = self.AritistsIntersection.intersection(self.MutagenStructs[fileName]['artist'])
                except KeyError:
                    pass
            ########
            if self.PerformerList == None:
                try:
                    self.PerformerList = self.MutagenStructs[fileName]['artist']
                except KeyError:
                    pass
            else:
                try:
                    for artist in self.MutagenStructs[fileName]['artist']:
                        if not artist in self.PerformerList:
                            self.PerformerList.append(artist)
                except KeyError:
                    pass
            ####
            if self.PerformerUnion == None:
                try:
                    self.PerformerUnion = set(self.MutagenStructs[fileName]['performer'])
                except KeyError:
                    pass
            else:
                try:
                    self.PerformerUnion = self.PerformerUnion.union(self.MutagenStructs[fileName]['performer'])
                except KeyError:
                    pass
            if self.PerformerIntersection == None:
                try:
                    self.PerformerIntersection = set(self.MutagenStructs[fileName]['performer'])
                except KeyError:
                    pass
            else:
                try:
                    self.PerformerIntersection = self.PerformerIntersection.intersection(self.MutagenStructs[fileName]['performer'])
                except KeyError:
                    pass
            #
            if self.AlbumList == None:
                try:
                    self.AlbumList = self.MutagenStructs[fileName]['album']
                except KeyError:
                    pass
            else:
                try:
                    for performer in self.MutagenStructs[fileName]['album']:
                        if not performer in self.AlbumList:
                            self.AlbumList.append(performer)
                except KeyError:
                    pass
            ####
            #
            if self.AlbumUnion == None:
                try:
                    self.AlbumUnion = set(self.MutagenStructs[fileName]['album'])
                except KeyError:
                    pass
            else:
                try:
                    self.AlbumUnion = self.AlbumUnion.union(self.MutagenStructs[fileName]['album'])
                except KeyError:
                    pass
            if self.AlbumIntersection == None:
                try:
                    self.AlbumIntersection = set(self.MutagenStructs[fileName]['album'])
                except KeyError:
                    pass
            else:
                try:
                    self.AlbumIntersection = self.AlbumIntersection.intersection(self.MutagenStructs[fileName]['album'])
                except KeyError:
                    pass
        
    def QueryLastFm(self):
        
        SuccessfullQueires = []
        self.QueriedImages = {}
        if len(self.filepaths) == 0:
            return
        plannedQueries = {}
        if self.AlbumIntersection == None:
            return
        if self.AlbumUnion == None:
            return
        if len(self.AlbumIntersection ) == len(self.AlbumUnion):
            # we know that we have one album.
            if len(self.AritistsIntersection ) == len(self.AritistsUnion):
                
                # We know ArtistList and Album is conistent across Album
                for filePath in self.filepaths:
                    ArtistList = list(self.DefaultArtistList)
                    AlbumList = list(self.DefaultAlbumList)
                    try:
                        for artist in self.MutagenStructs[filePath]["artist"]:
                            if not artist in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    try:
                        for artist in self.MutagenStructs[filePath]["performer"]:
                            if not artist in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    for artist in ['Various Artists','Various']:
                        if not artist in ArtistList:
                                ArtistList.append(artist)
                    try:
                        for album in self.MutagenStructs[filePath]["album"]:
                            if not album in AlbumList:
                                AlbumList.append(album)
                    except KeyError:
                        pass
                    
                        
                    plannedQueries[filePath] = []
                    
                    for b in AlbumList:
                        for a in ArtistList:
                            plannedQueries[filePath].append({'album': b,'artist' : a})
                    
            else:
                # We know we have one Album but dirfferent tracks:
                #print 'dddddddddd'
                for filePath in self.filepaths:
                    ArtistList = list(self.DefaultArtistList)
                    AlbumList = list(self.DefaultAlbumList)
                    #print AlbumList
                    #print ArtistList
                    plannedQueries[filePath] = []
                    try:
                        for artist in self.MutagenStructs[filePath]["artist"]:
                            if not artist in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    try:
                        for artist in self.MutagenStructs[filePath]["performer"]:
                            if not artist in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    for artist in ['Various Artists','Various']:
                        if not artist in ArtistList:
                                ArtistList.append(artist)
                    try:
                        for album in self.MutagenStructs[filePath]["album"]:
                            if not album in AlbumList:
                                AlbumList.append(album)
                    except KeyError:
                        pass
                    print "ArtistList=%s" % ArtistList
                    for a in ArtistList:
                        for b in AlbumList:
                            plannedQueries[filePath].append({'album': b,'artist' : a})
                    print "plannedQueries[filePath]=%s"  % plannedQueries[filePath]
                    
        else:
            # We know this is not one Album
            print "We know this is not one Album so ignoring"
            return
        #print ArtistList
        #print self.AritistsUnion,self.AritistsIntersection
        #print self.AlbumUnion,self.AlbumIntersection
        #print "self.AritistsList=%s" % self.AritistsList
        #print self.AlbumList
        #print "plannedQueries=%s" %plannedQueries
        MadeQueries = []
        MadeQueriesResults = []
        MadeUrl = []
        last_request = LastFM()
        LocalQueriedImages = {}
        for filePath in plannedQueries.keys():
            QueriesforFile = plannedQueries[filePath]
            index = -1
            #print QueriesforFile
            for Querie in QueriesforFile:
                try:
                    index = MadeQueries.index(Querie)
                except ValueError:
                    #print ' filling cache %s ----- %s' % (Querie,filePath)
                    #print type (Querie)
                    lastmetadata = last_request.album_getInfo(Querie)
                    #print "lastmetadata=%s" % lastmetadata
                    imageUrl =None
                    if lastmetadata == None:
                        print "No url found for: %s" % (Querie)
                        imageUrl =None
                    else:
                        listOfLastFmImageUrls = findRightImageFromLastFm(lastmetadata['album']["image"])
                        #print "listOfLastFmImageUrls=%s" % (listOfLastFmImageUrls)
                        imageUrl = []
                        for Aurl in listOfLastFmImageUrls:
                            if len(Aurl) != 0:
                                if Aurl not in imageUrl:
                                    imageUrl.append(Aurl)
                        if len(imageUrl) == 0:
                            imageUrl =None
                        
                   
                    
                    
                    #print "imageUrl=%s" % imageUrl
                    MadeQueries.append(Querie)
                    MadeUrl.append(imageUrl)
                    index = MadeQueries.index(Querie)
                if MadeUrl[index] != None:
                    #print "ddddddddddddddddddddddddddddddddddddddddddd"
                    #print "MadeUrl[index]=%s" % MadeUrl[index]
                    self.QueriedImages[filePath] = MadeUrl[index]
                    break
            if index == -1:
                # we had no queires for this file.
                print "we had no queires for this file."
                continue
            if MadeUrl[index] == None:
                # Our last Query Was unsuccessfull
                continue
            #print "MadeUrl[index]=%s" % (MadeUrl[index])
            LocalQueriedImages[filePath] = MadeUrl[index]
        #print "self.QueriedImages=%s" % (self.QueriedImages)
        for key in LocalQueriedImages.keys():
            if LocalQueriedImages[key] != None:
                self.QueriedImages[key] = LocalQueriedImages[key]
        print self.QueriedImages
    def  SetUrl(self,url):
        #print "called SetUrl"
        self.QueriedImages = {}
        for filePath in self.filepaths:
            self.QueriedImages[filePath] = [url]
            
    def DisplayUrls(self):
        for flacPath in self.QueriedImages.keys():
            shortname = os.path.basename(flacPath)
            print "%s - %s" % (shortname , self.QueriedImages[flacPath])
    def AddImages(self):
        MadeUrls = []
        MadeUrlsResults = []
        for flacPath in self.QueriedImages.keys():
            index = -1
            for Query in self.QueriedImages[flacPath]:
                try:
                    index = MadeUrls.index(Query)
                except ValueError:
                    #print ' filling --- cache %s:%s' % (Query,flacPath)
                    #print MadeUrls
                    try:
                        #print "Query=%s,%s" % (Query,type(Query))
                        
                        data = urllib2.urlopen(Query  )
                    except urllib2.URLError:
                        print "Could not open URL: %s for file : %s" % (imageUrl,filePath)
                        continue
                    MadeUrls.append(Query)
                    MadeUrlsResults.append(data.read())
                    index = MadeUrls.index(Query)
            if index == -1:
                # we had succesfull urls for this file
                continue
            if len(MadeUrlsResults[index]) == 0:
                # we had no data
                continue
            #print ' have %s for %s' % (Query,flacPath)
            try:
                metadata = FLAC(flacPath)
            except FLACNoHeaderError as (strerror):
                print strerror
                continue
            if pict_test(metadata):
                print "Already has cover are:%s" % (filePath)
                continue
            image = Picture()
            image.type = 3
            image.desc = 'front cover'
            if Query.endswith('png'):
                mime = 'image/png'
            if Query.endswith('jpg'):
                mime = 'image/jpeg'
            image.data = MadeUrlsResults[index]
            metadata.add_picture(image)
            metadata.save()

def AddCoverArt2(path,AddCoverArtMetadata):
    last_request = LastFM()
    for (path, dirs, files) in os.walk(path):
        obj = DirAddCoverArtLastFm(path)
        obj.readfiles()
        if "artist" in AddCoverArtMetadata:
            obj.DefaultArtistList = AddCoverArtMetadata["artist"]
        if "album" in AddCoverArtMetadata:
            obj.DefaultAlbumList = AddCoverArtMetadata["album"]
            
        
            #print obj.DefaultArtistList 
        if "url" in AddCoverArtMetadata:
            
            obj.SetUrl(AddCoverArtMetadata["url"])
        else:
            obj.QueryLastFm()
        
        #print obj.QueriedImages
        #obj.AddImages()
        obj.DisplayUrls()
        if "apply" in AddCoverArtMetadata:
            obj.AddImages()
        
        
        


def AddCoverArt(pathList,AddCoverArtMetadata):
    for path in pathList:
        AddCoverArt2(path,AddCoverArtMetadata)
        

def main():
    log = logging.getLogger("main")
    """Runs program and handles command line options"""
    parser = optparse.OptionParser(version = "%prog " + version)
    parser.add_option('--path', action ='append',help='list subscriptions')
    parser.add_option('--artist',action='append',help='Artist Name')
    parser.add_option('--album',action='append',help='Artist Name')
    parser.add_option('--url',action='store',help='Artist Name')
    parser.add_option('--apply',action='store_true',help='Artist Name')
    parser.add_option('--logfile', action ='store',help='Logfile configuration file.', metavar='LOGFILE')
    options, arguments = parser.parse_args() 
    # Set up log file
    logFile = None
    if options.logfile:
        logFile = options.logfile
    if logFile != None:
        if os.path.isfile(str(options.logfile)):
            logging.config.fileConfig(options.logfile)
        else:
            logging.basicConfig(level=logging.INFO)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.logfile))
            sys.exit(1)
    else:
        logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("main")
    
    metadata = {}
    if options.artist:
        if len(options.artist) > 0:
            metadata['artist'] = options.artist
    if options.album:
        if len(options.album) > 0:
            metadata['album'] = options.album
            #print type(metadata['album']), metadata['album'] 
    if options.apply:
        
        metadata['apply'] = True
    if options.url:
        if len(options.url) > 0:
            metadata['url'] = options.url
            
    if options.path:
        AddCoverArt(options.path,metadata)

if __name__ == "__main__":
    main()
