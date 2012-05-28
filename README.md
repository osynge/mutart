mutart
======

Adds album art to flac files (and maybe other formats later) using meta data retrieved from LastFM (and maybe other metadata servers later)


#Command Line#

    ./mutart --help
    Usage: mutart [options]

    Options:
      --version          show program's version number and exit
      -h, --help         show this help message and exit
      --path=PATH        list subscriptions
      --artist=ARTIST    Artist Name
      --album=ALBUM      Artist Name
      --url=URL          Artist Name
      --apply            Artist Name
      --clear            Artist Name
      --logfile=LOGFILE  Logfile configuration file.


#Example Usage#

    ./mutart --path /media/music/flac/blues/
    
If the application shoudl update the art.

    ./mutart --path /media/music/flac/blues/ --apply
    
If the artist is confusing the LastFM search 

    ./mutart --path /media/music/flac/blues/ --artist 'muddy waters'

If the album is confusing the LastFM search 

    ./mutart --path /media/music/flac/blues/ --album ''whiskey blues"

if the LastFM search completely fails but you found an image URL

    ./mutart --path /media/music/flac/blues/ --url "http://bilder.preisvergleich.org/products/DE/30/000/003/852/E_000003852848_DE_30.jpg"

if you want to clear the album art:

    ./mutart --path /media/music/flac/blues/ --clear
