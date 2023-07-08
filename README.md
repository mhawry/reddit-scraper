Reddit Scraper
==============

reddit-scraper is a command-line application written in Python that scrapes a Reddit user's posts and downloads all images.


Installation
------------

To install reddit-scraper, clone the project and install the requirements.



Usage
-----

To scrape a Reddit user's posts:
```
$ python reddit_scraper --username <username>
```

You can also provide a destination for the posts to be downloaded to:
```
$ python reddit_scraper --username <username> --destination <destination>
```

If you wish, you can also download the metadata. A JSON file will be created for each post in the same directory as the images:
```
$ python reddit_scraper --username <username> --destination <destination> --include-metadata
```

The `destination` parameter is optional. If no destination is provided, the posts will be stored in `<current working directory>/<username>`.

The `include-metadata` parameter is optional. If it isn't provided the metadata will not be downloaded.

*Note: External links will be downloaded only if they contain an extension.*



Options
-------

```
--help             -h Show this help message and exit.

--username         -u Username of the Reddit user to scrape.

--destination      -d Specify the download destination. By default, posts will be stored in <current working directory>/<username>.

--quiet            -q Be quiet while scraping.

--limit            -l Maximum number of posts to scrape.

--include-metadata -m Download the metadata. A JSON file will be created for each post in the same directory as the images.
```