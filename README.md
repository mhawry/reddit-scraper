Reddit Scraper
==============

reddit-scraper is a command-line application written in Python that scrapes and downloads a Reddit user's posts.


Installation
------------

To install reddit-scraper, clone the project and install the requirements.



Usage
-----

To scrape a Reddit user's posts:
```
$ python main.py --username <username>
```

You can also provide a destination for the posts to be downloaded to:
```
$ python main.py --username <username> --destination <destination>
```

*The destination parameter is optional. If no destination is provided, the posts will be downloaded to `<current working directory>/<username>`.*

*Note: The metadata will be downloaded to a JSON file. External links will be downloaded only if they contain an extension.*



Options
-------

```
--help        -h show this help message and exit

--username    -u Username of the Reddit user to scrape.

--destination -d Specify the download destination. By default, posts will be downloaded to <current working directory>/<username>.
```