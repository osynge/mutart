#!/usr/bin/env python3
from mutagen.flac import FLAC, Picture, FLACNoHeaderError, error

import os
from six.moves import urllib
# import urllib, urllib2
import logging
import optparse
import sys
try:
    import json
except ImportError:
    import simplejson as json
# import httplib

version = "0.0.1"


class LastFM:
    def __init__(self):
        self.log = logging.getLogger("LastFM")
        self.API_URL = "http://ws.audioscrobbler.com/2.0/"
        self.API_KEY = "c6e9c72bbec0497a87391feda206de05"

    def get_genre(self, genre, **kwargs):
        kwargs.update({
            "method":	"tag.gettopartists",
            "tag":		genre,
            "api_key":	self.API_KEY,
            "limit":	3,
            "format":	"json"
        })
        try:
            # Create an API Request
            url = self.API_URL + "?" + urllib.urlencode(kwargs)
            # Send Request and Collect it
            data = urllib.request.urlopen(url)
            # Print it
            response_data = json.load(data)
            print(response_data['topartists']['artist'][0]['name'])
            # Close connection
            data.close()
        except urllib.error.HTTPError as e:
            print("HTTP error: %d" % e.code)
        except urllib.error.URLError as e:
            print("Network error: %s" % e.reason.args[1])

    def album_getInfo(self, info, **kwargs):
        kwargs.update({
            "method":	"album.getInfo",
            "artist": info['artist'].encode('utf-8'),
            "album": info['album'].encode('utf-8'),
            "api_key":	self.API_KEY,
            "limit":	3,
            "format":	"json",
            "autocorrect": 1
        })
        try:
            # Create an API Request
            try:
                url = self.API_URL + "?" + urllib.parse.urlencode(kwargs)
            except UnicodeEncodeError as one:
                print("encoding error:%s" % (one))
                return None
            # Send Request and Collect it
            data = urllib.request.urlopen(url)
            response_data = json.load(data)
            # Close connection
            data.close()

            if 'album' in response_data:
                return response_data
            return None
        except urllib.error.HTTPError as e:
            self.log.error("HTTP error code: %d" % e.code)
        except urllib.error.URLError as e:
            self.log.error("Network error: %s" % e.reason.args[1])


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
    preferance = ['large', 'extralarge', 'mega', 'medium', 'small']
    preferance.reverse()
    bestUrl = None
    bestPreferanceIndex = -1
    # print "images=%s" % images
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
        self.log = logging.getLogger("DirAddCoverArt")
        self.path = path
        self.filepaths = []
        self.DefaultArtistList = []
        self.DefaultAlbumList = []

    def clearCoverArt(self):
        for fileShortName in os.listdir(self.path):
            fileName = os.path.join(self.path, fileShortName)

            if os.path.isdir(fileName):
                continue
            try:
                metadata = FLAC(fileName)
            except FLACNoHeaderError as strerror:
                self.log.info("strerror=%s" % (strerror))
                continue
            except error as E:
                self.log.info("strerror=%s" % (E))
                continue
            metadata.clear_pictures()
            metadata.save()
            del(metadata)

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
        self.filepaths = []
        for fileShortName in os.listdir(self.path):
            fileName = os.path.join(self.path, fileShortName)
            if os.path.isdir(fileName):
                continue
            try:
                metadata = FLAC(fileName)
            except FLACNoHeaderError as strerror:
                self.log.info("strerror=%s" % (strerror))
                continue
            except error as flacErorr:
                self.log.error("flacErorr=%s" % (flacErorr))
                continue
            if pict_test(metadata):
                self.log.info("Already has cover for:%s" % (fileName))
                continue

            self.filepaths.append(fileName)
            self.MutagenStructs[fileName] = metadata

            if self.AritistsList is None:
                try:
                    self.AritistsList = self.MutagenStructs[fileName]['artist']
                except KeyError:
                    pass
            else:
                try:
                    for artist in self.MutagenStructs[fileName]['artist']:
                        if artist not in self.AritistsList:
                            self.AritistsList.append(artist)
                except KeyError:
                    pass
            ####
            if self.AritistsUnion is None:
                try:
                    self.AritistsUnion = set(self.MutagenStructs[fileName]['artist'])
                except KeyError:
                    pass
            else:
                try:
                    self.AritistsUnion = self.AritistsUnion.union(self.MutagenStructs[fileName]['artist'])
                except KeyError:
                    pass
            if self.AritistsIntersection is None:
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
            if self.PerformerList is None:
                try:
                    self.PerformerList = self.MutagenStructs[fileName]['artist']
                except KeyError:
                    pass
            else:
                try:
                    for artist in self.MutagenStructs[fileName]['artist']:
                        if artist not in self.PerformerList:
                            self.PerformerList.append(artist)
                except KeyError:
                    pass
            ####
            if self.PerformerUnion is None:
                try:
                    self.PerformerUnion = set(self.MutagenStructs[fileName]['performer'])
                except KeyError:
                    pass
            else:
                try:
                    self.PerformerUnion = self.PerformerUnion.union(self.MutagenStructs[fileName]['performer'])
                except KeyError:
                    pass
            if self.PerformerIntersection is None:
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
            if self.AlbumList is None:
                try:
                    self.AlbumList = self.MutagenStructs[fileName]['album']
                except KeyError:
                    pass
            else:
                try:
                    for performer in self.MutagenStructs[fileName]['album']:
                        if performer not in self.AlbumList:
                            self.AlbumList.append(performer)
                except KeyError:
                    pass
            ####
            #
            if self.AlbumUnion is None:
                try:
                    self.AlbumUnion = set(self.MutagenStructs[fileName]['album'])
                except KeyError:
                    pass
            else:
                try:
                    self.AlbumUnion = self.AlbumUnion.union(self.MutagenStructs[fileName]['album'])
                except KeyError:
                    pass
            if self.AlbumIntersection is None:
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
        self.QueriedImages = {}
        if len(self.filepaths) == 0:
            return
        plannedQueries = {}
        if self.AlbumIntersection is None:
            return
        if self.AlbumUnion is None:
            return
        if len(self.AlbumIntersection) == len(self.AlbumUnion):
            # we know that we have one album.
            if len(self.AritistsIntersection) == len(self.AritistsUnion):
                # We know ArtistList and Album is conistent across Album
                for filePath in self.filepaths:
                    ArtistList = list(self.DefaultArtistList)
                    AlbumList = list(self.DefaultAlbumList)
                    try:
                        for artist in self.MutagenStructs[filePath]["artist"]:
                            if artist not in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    try:
                        for artist in self.MutagenStructs[filePath]["performer"]:
                            if artist not in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    try:
                        for album in self.MutagenStructs[filePath]["album"]:
                            if album not in AlbumList:
                                AlbumList.append(album)
                    except KeyError:
                        pass
                    plannedQueries[filePath] = []

                    for b in AlbumList:
                        for a in ArtistList:
                            plannedQueries[filePath].append({'album': b, 'artist': a})

            else:
                # We know we have one Album but dirfferent tracks:
                for filePath in self.filepaths:
                    ArtistList = list(self.DefaultArtistList)
                    AlbumList = list(self.DefaultAlbumList)
                    for artist in ['Various Artists', 'Various']:
                        if artist not in ArtistList:
                                ArtistList.append(artist)
                    plannedQueries[filePath] = []
                    try:
                        for artist in self.MutagenStructs[filePath]["artist"]:
                            if artist not in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass
                    try:
                        for artist in self.MutagenStructs[filePath]["performer"]:
                            if artist not in ArtistList:
                                ArtistList.append(artist)
                    except KeyError:
                        pass

                    try:
                        for album in self.MutagenStructs[filePath]["album"]:
                            if album not in AlbumList:
                                AlbumList.append(album)
                    except KeyError:
                        pass
                    for a in ArtistList:
                        for b in AlbumList:
                            plannedQueries[filePath].append({'album': b, 'artist': a})
        else:
            # We know this is not one Album
            print("We know this is not one Album so ignoring")
            return

        MadeQueries = []
        MadeUrl = []
        last_request = LastFM()
        LocalQueriedImages = {}
        plannedQueriesKeys = list(plannedQueries.keys())
        plannedQueriesKeys.sort()
        for filePath in plannedQueriesKeys:
            QueriesforFile = plannedQueries[filePath]
            index = -1
            for Querie in QueriesforFile:
                try:
                    index = MadeQueries.index(Querie)
                except ValueError:
                    lastmetadata = last_request.album_getInfo(Querie)
                    imageUrl = None
                    if lastmetadata is None:
                        self.log.warning("No url found for: %s" % (Querie))
                        imageUrl = None
                    else:
                        listOfLastFmImageUrls = findRightImageFromLastFm(lastmetadata['album']["image"])
                        imageUrl = []
                        for Aurl in listOfLastFmImageUrls:
                            if len(Aurl) != 0:
                                if Aurl not in imageUrl:
                                    imageUrl.append(Aurl)
                        if len(imageUrl) == 0:
                            self.log.warning("No valid url found for:%s:%s" % (filePath, Querie))
                            imageUrl = None
                    MadeQueries.append(Querie)
                    MadeUrl.append(imageUrl)
                    index = MadeQueries.index(Querie)
                if MadeUrl[index] is not None:
                    self.QueriedImages[filePath] = MadeUrl[index]
                    break
            if index == -1:
                # we had no queires for this file.
                print("we had no queires for this file.")
                continue
            if MadeUrl[index] is None:
                # Our last Query Was unsuccessfull
                continue
            LocalQueriedImages[filePath] = MadeUrl[index]
        for key in LocalQueriedImages.keys():
            if LocalQueriedImages[key] is not None:
                self.QueriedImages[key] = LocalQueriedImages[key]

    def SetUrl(self, url):
        self.QueriedImages = {}
        for filePath in self.filepaths:
            self.QueriedImages[filePath] = [url]

    def DisplayUrls(self):
        for flacPath in self.QueriedImages.keys():
            shortname = os.path.basename(flacPath)
            print("%s - %s" % (shortname, self.QueriedImages[flacPath]))

    def AddImages(self):
        MadeUrls = []
        MadeUrlsResults = []
        QueriedImagesKeys = list(self.QueriedImages.keys())
        QueriedImagesKeys.sort()
        for flacPath in QueriedImagesKeys:
            index = -1
            for Query in self.QueriedImages[flacPath]:
                try:
                    index = MadeUrls.index(Query)
                except ValueError:
                    try:
                        data = urllib.request.urlopen(Query)
                    except urllib.error.URLError:
                        print("Could not open URL: %s for file : %s" % (Query, flacPath))
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
            try:
                metadata = FLAC(flacPath)
            except FLACNoHeaderError as strerror:
                print(strerror)
                continue

            if pict_test(metadata):
                print("Already has cover are:%s" % (flacPath))
                continue

            image = Picture()
            image.type = 3
            image.desc = 'front cover'
            if Query.endswith('png'):
                image.mime = 'image/png'
            if Query.endswith('jpg'):
                image.mime = 'image/jpeg'
            image.data = MadeUrlsResults[index]
            metadata.add_picture(image)
            try:
                metadata.save()
            except IOError as e:
                print("exception=%s" % (e))
                continue


def AddCoverArt2(path, AddCoverArtMetadata):
    for (path, dirs, files) in os.walk(path):
        obj = DirAddCoverArtLastFm(path)
        if "clear" in AddCoverArtMetadata:
            obj.clearCoverArt()

        obj.readfiles()
        if "artist" in AddCoverArtMetadata:
            obj.DefaultArtistList = AddCoverArtMetadata["artist"]
        if "album" in AddCoverArtMetadata:
            obj.DefaultAlbumList = AddCoverArtMetadata["album"]

        if "url" in AddCoverArtMetadata:
            obj.SetUrl(AddCoverArtMetadata["url"])
        else:
            obj.QueryLastFm()

        obj.DisplayUrls()
        if "apply" in AddCoverArtMetadata:
            obj.AddImages()


def AddCoverArt(pathList, AddCoverArtMetadata):
    for path in pathList:
        AddCoverArt2(path, AddCoverArtMetadata)


def main():
    log = logging.getLogger("main")
    """Runs program and handles command line options"""
    parser = optparse.OptionParser(version="%prog " + version)
    parser.add_option('--path', action='append', help='Music file path')
    parser.add_option('--artist', action='append', help='Artist Name')
    parser.add_option('--album', action='append', help='Artist Name')
    parser.add_option('--url', action='store', help='Artist Name')
    parser.add_option('--apply', action='store_true', help='Artist Name')
    parser.add_option('--clear', action='store_true', help='Artist Name')
    parser.add_option('-L', '--logcfg', action='store', help='Logfile configuration file.', metavar='CFG_LOGFILE')
    parser.add_option('--verbose', action='count', help='Change global log level, increasing log output.', metavar='LOGFILE')
    parser.add_option('--quiet', action='count', help='Change global log level, decreasing log output.', metavar='LOGFILE')
    options, arguments = parser.parse_args()
    # Set up basic variables
    logFile = None
    # Set up log file

    LoggingLevel = logging.WARNING
    LoggingLevelCounter = 2
    if options.verbose:
        LoggingLevelCounter = LoggingLevelCounter - options.verbose
        if options.verbose == 1:
            LoggingLevel = logging.INFO
        if options.verbose == 2:
            LoggingLevel = logging.DEBUG
    if options.quiet:
        LoggingLevelCounter = LoggingLevelCounter + options.quiet
    if LoggingLevelCounter <= 0:
        LoggingLevel = logging.DEBUG
    if LoggingLevelCounter == 1:
        LoggingLevel = logging.INFO
    if LoggingLevelCounter == 2:
        LoggingLevel = logging.WARNING
    if LoggingLevelCounter == 3:
        LoggingLevel = logging.ERROR
    if LoggingLevelCounter == 4:
        LoggingLevel = logging.FATAL
    if LoggingLevelCounter >= 5:
        LoggingLevel = logging.CRITICAL

    if options.logcfg:
        logFile = options.logcfg
    if logFile is not None:
        if os.path.isfile(str(options.log_config)):
            logging.config.fileConfig(options.log_config)
        else:
            logging.basicConfig(level=LoggingLevel)
            log = logging.getLogger("main")
            log.error("Logfile configuration file '%s' was not found." % (options.log_config))
            sys.exit(1)
    else:

        logging.basicConfig(level=LoggingLevel)
    log = logging.getLogger("main")

    metadata = {}
    if options.artist:
        if len(options.artist) > 0:
            metadata['artist'] = options.artist
    if options.album:
        if len(options.album) > 0:
            metadata['album'] = options.album
    if options.apply:
        metadata['apply'] = True
    if options.clear:
        metadata['clear'] = True
    if options.url:
        if len(options.url) > 0:
            metadata['url'] = options.url

    if options.path:
        AddCoverArt(options.path, metadata)


if __name__ == "__main__":
    main()
