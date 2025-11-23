# General Scripts
<h2><a href="https://github.com/9Oc/Squash-P2P-Script-Emporium/blob/main/general/globaltags.py">globaltags</a>
<a href="https://www.python.org/downloads/release/python-3100/"><img src="https://img.shields.io/badge/Python-3.10%2B-brightgreen" alt="Python 3.10+"></a></h2>

`globaltags.py` generates an mkv XML tag file containing the TMDB, IMDB, and TVDB2 IDs for a given TMDB ID.

Dependencies:

`pip install tvdb_v4_official requests rich`

Note that you must provide your TMDB and TVDB API keys at the top of the script.
```
TMDB_API_KEY = "TMDB_API_KEY" # <-- your TMDB api key here
TVDB_API_KEY = "TVDB_API_KEY" # <-- your TVDB api key here
```

<hr>

### Usage
A TMDB ID is the only argument accepted.

`globaltags.py <TMDB ID>`
<hr>
Example output:

```
globaltags.py 9005
Fetching data for TMDB ID: 9005

TMDB match: The Ice Harvest (2005)
TMDB ID: 9005
TMDB URL: https://www.themoviedb.org/movie/9005

IMDB ID: tt0400525
IMDB URL: https://www.imdb.com/title/tt0400525

TVDB match: The Ice Harvest (2005)
TVDB ID: 8208
TVDB URL: https://www.thetvdb.com/movies/the-ice-harvest

XML file saved as: .global_tags_The Ice Harvest_2005.xml

<?xml version="1.0" encoding="UTF-8"?>
<Tags>
  <Tag>
    <Simple>
      <Name>TMDB</Name>
      <String>movie/9005</String>
    </Simple>
    <Simple>
      <Name>IMDB</Name>
      <String>tt0400525</String>
    </Simple>
    <Simple>
      <Name>TVDB2</Name>
      <String>movies/8208</String>
    </Simple>
  </Tag>
</Tags>
```
