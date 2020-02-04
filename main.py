import logging
import argparse
import os
import requests
import tqdm
import json

USER_AGENT = 'Reddit JSON API/1.0'
LIMIT = 100


def fetch_posts(username):
    """Fetches all the posts from a user's profile"""
    posts_json = []
    after = ''

    # we can only fetch 100 posts per call with Reddit's json API
    # this will loop through them until we get them all
    while after is not None:
        r = requests.get('https://www.reddit.com/user/{}/submitted/.json?limit={}&after={}'.format(username, LIMIT, after),
                         headers={'User-Agent': USER_AGENT}).json()

        # in case the username doesn't exist
        if 'error' in r and r['error'] == 404:
            logging.error('{} is not a valid Reddit username'.format(username))
            return

        for child in r['data']['children']:
            posts_json.append(child)

        after = r['data']['after']

    return posts_json


def download_posts(username, destination):
    """Crawls through a user's posts and downloads them"""
    posts_json = fetch_posts(username)

    # in case the user doesn't have any posts
    if not posts_json:
        return

    download_dir = os.path.join(destination, username)

    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    for post_json in tqdm.tqdm(posts_json,
                               desc='Downloading posts from user {}'.format(username),
                               unit=' posts',
                               ncols=0):
        filename = '{}.json'.format(post_json['data']['id'])
        file = os.path.join(download_dir, '{}'.format(filename))

        with open(file, 'w') as json_file:
            json.dump(post_json['data'], json_file)

        if 'url' in post_json['data']:
            url = post_json['data']['url']
            filename = url.rsplit('/', 1)[-1]

            if filename:
                # skipping files that don't have an extension (could be for example an imgur gallery or gfycat link)
                # TODO: implement functionality to download imgur galleries and gifs
                if '.' not in filename:
                    continue

                r = requests.get(url, allow_redirects=True)
                file = os.path.join(download_dir, '{}'.format(filename))
                open(file, 'wb').write(r.content)

    return


def main():
    logging.getLogger().setLevel(logging.INFO)

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    current_dir = os.path.dirname(os.path.abspath(__file__))

    ap = argparse.ArgumentParser(description='reddit-scraper is a command-line application written in Python that scrapes and downloads a Reddit user\'s posts.',
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

    ap.add_argument('--username', '-u', help='Username of the Reddit user to scrape.')
    ap.add_argument('--destination', '-d', default=current_dir, help='Specify the download destination. By default, posts will be downloaded to <current working directory>/<username>.')

    args = ap.parse_args()

    if not args.username:
        logging.error('You must provide a username')  # username is mandatory
        return

    username = args.username
    destination = args.destination

    if not os.path.exists(destination):
        logging.error('The specified destination does not exist')
        return

    if not os.path.isdir(destination):
        logging.error('The specified destination is not a valid directory')
        return

    logging.info('Scraping posts from {}'.format(username))

    # if we reach this point we can start downloading the posts
    download_posts(username, destination)

    logging.info('Scraping complete')


if __name__ == '__main__':
    main()
