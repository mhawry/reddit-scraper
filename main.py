import logging
import argparse
import os
import sys
import requests
import tqdm
import json
from typing import Optional

LIMIT_PER_PAGE = 100  # we can only fetch 100 posts per call with Reddit's API
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'


def fetch_posts(username: str) -> Optional[list]:
    """Fetches all the posts from a user's profile"""
    after = ''
    posts_json = []

    # this will loop through the posts page by page
    while after is not None:
        r = requests.get(f"https://www.reddit.com/user/{username}/submitted/.json?limit={LIMIT_PER_PAGE}&after={after}",
                         headers={'User-Agent': USER_AGENT}).json()

        # in case the username doesn't exist
        if 'error' in r and r['error'] == 404:
            logging.error(f"{username} is not a valid Reddit username")
            return

        for child in r['data']['children']:
            posts_json.append(child)

        after = r['data']['after']

    return posts_json


def download_posts(username: str, destination: str, include_metadata: bool) -> None:
    """Crawls through a user's posts and downloads them"""
    posts_json = fetch_posts(username)

    # in case the user doesn't have any posts
    if not posts_json:
        return

    download_dir = os.path.join(destination, username)

    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    for post_json in tqdm.tqdm(posts_json,
                               desc=f"Downloading posts from user {username}",
                               unit=' posts',
                               ncols=0):
        if 'url' in post_json['data']:
            url = post_json['data']['url']
            filename = url.rsplit('/', 1)[-1]

            if filename:
                # skipping files that don't have an extension (could be for example an imgur gallery or gfycat link)
                # TODO: implement functionality to download imgur galleries and gifs
                if '.' not in filename:
                    continue

                r = requests.get(url, allow_redirects=True)
                file = os.path.join(download_dir, filename)
                open(file, 'wb').write(r.content)

                if include_metadata:
                    filename = f"{post_json['data']['id']}.json"
                    file = os.path.join(download_dir, filename)

                    with open(file, 'w') as json_file:
                        json.dump(post_json['data'], json_file)

    return


def main():
    try:
        logging.getLogger().setLevel(logging.INFO)

        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

        current_dir = os.path.dirname(os.path.abspath(__file__))

        ap = argparse.ArgumentParser(description="reddit-scraper is a command-line application written in Python that scrapes a Reddit user's posts and downloads all images.",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

        ap.add_argument('--username', '-u', help="Username of the Reddit user to scrape.")
        ap.add_argument('--destination', '-d', default=current_dir, help="Specify the download destination. By default, posts will be stored in <current working directory>/<username>.")
        ap.add_argument('--include-metadata', '-m', dest='include_metadata', default=False, action='store_true', help="Download the metadata. A JSON file will be created for each post in the same directory as the images.")

        args = ap.parse_args()

        if not args.username:
            logging.error("You must provide a username")  # username is mandatory
            return

        if not os.path.exists(args.destination):
            logging.error("The specified destination does not exist")
            return

        if not os.path.isdir(args.destination):
            logging.error("The specified destination is not a valid directory")
            return

        logging.info(f"Scraping posts from {args.username}")

        # if we reach this point we can start downloading the posts
        download_posts(args.username, args.destination, args.include_metadata)

        logging.info("Scraping complete")
    except KeyboardInterrupt:
        print("Shutdown requested... exiting")

    sys.exit(0)


if __name__ == '__main__':
    main()
