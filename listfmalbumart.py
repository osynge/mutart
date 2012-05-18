import urllib, urllib2
try:
    import json
except ImportError:
    import simplejson as json
 
class LastFM:
    def __init__(self ):
        self.API_URL = "http://ws.audioscrobbler.com/2.0/"
        self.API_KEY = "b25b959554ed76058ac220b7b2e0a026"
 
    def get_genre(self, genre, **kwargs):
        kwargs.update({
            "method":	"tag.gettopartists",
            "tag":		genre,
            "api_key":	self.API_KEY,
            "limit":	3,
            "format":	"json"
        })
        try:
            #Create an API Request
            url = self.API_URL + "?" + urllib.urlencode(kwargs)
            #Send Request and Collect it
            data = urllib2.urlopen( url )
            #Print it
            response_data = json.load( data )
            print response_data['topartists']['artist'][0]['name']
            #Close connection
            data.close()
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
    def album_getInfo(self, info, **kwargs):
        kwargs.update({
            "method":	"album.getInfo",
            "artist":		info['artist'],
            "album": info['album'],
            "api_key":	self.API_KEY,
            "limit":	3,
            "format":	"json",
            "autocorrect" : 1
        })
        try:
            #Create an API Request
            try:
                url = self.API_URL + "?" + urllib.urlencode(kwargs)
            except UnicodeEncodeError as (one):
                return None
            #Send Request and Collect it
            data = urllib2.urlopen( url )
            response_data = json.load( data )
            #Close connection
            data.close()
            if 'album' in response_data:
                return response_data
            return None
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
def main():
    last_request = LastFM()
    last_request.get_genre( "rock" )
    last_request.album_getInfo({"artist" : "AC/DC", "album" : "Live from Atlantic Studios"})


if __name__ == "__main__":
    main()
