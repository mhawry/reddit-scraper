import logging
import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from tqdm import tqdm
import json

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LIMIT_PER_PAGE = 100  # Maximum posts per API call
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
BASE_URL = "https://www.reddit.com/user/{username}/submitted/.json"


class RedditScraper:
    """Scrapes and downloads a Reddit user's posts.

    Attributes:
        limit_per_page: Maximum number of posts to fetch per API call
        destination: Directory to save downloaded content
        quiet: Whether to suppress progress output
        limit: Maximum total number of posts to download (0 for unlimited)
        include_metadata: Whether to save post metadata as JSON
    """

    def __init__(
        self,
        limit_per_page: int,
        destination: str,
        quiet: bool,
        limit: int = 0,
        include_metadata: bool = False
    ) -> None:
        """Initialize the RedditScraper.

        Args:
            limit_per_page: Maximum posts per API call
            destination: Download directory path
            quiet: Suppress progress output if True
            limit: Maximum total posts to download (0 for unlimited)
            include_metadata: Save post metadata if True
        """
        self.limit_per_page = limit_per_page
        self.destination = Path(destination)
        self.quiet = quiet
        self.limit = limit
        self.include_metadata = include_metadata

    def fetch_posts(self, username: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch posts from a user's Reddit account.

        Args:
            username: Reddit username to fetch posts from

        Returns:
            List of post data or None if user not found
        """
        after = ''
        posts_json = []
        count = 0

        try:
            while after is not None and (self.limit == 0 or count < self.limit):
                limit = min(self.limit_per_page, self.limit or self.limit_per_page)
                url = BASE_URL.format(username=username)
                params = {'limit': limit, 'after': after}
                headers = {'User-Agent': USER_AGENT}

                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                if 'error' in data and data['error'] == 404:
                    logging.error(f"User '{username}' not found")
                    return None

                for child in data['data']['children']:
                    posts_json.append(child)
                    count += 1
                    if self.limit != 0 and count >= self.limit:
                        break

                after = data['data']['after']

            return posts_json

        except requests.RequestException as e:
            logging.error(f"Error fetching posts: {e}")
            return None

    def download_posts(self, username: str) -> None:
        """Download posts from a Reddit user.

        Args:
            username: Reddit username to download posts from
        """
        posts_json = self.fetch_posts(username)
        if not posts_json:
            return

        download_dir = self.destination / username
        download_dir.mkdir(exist_ok=True)

        for post_json in tqdm(
            posts_json,
            desc=f"{datetime.now().strftime(DATETIME_FORMAT)} Downloading posts from {username}",
            unit=' posts',
            ncols=0,
            disable=self.quiet
        ):
            if 'url' not in post_json['data']:
                continue

            url = post_json['data']['url']
            filename = url.rsplit('/', 1)[-1]

            if not filename or '.' not in filename:
                continue

            try:
                response = requests.get(url, allow_redirects=True)
                response.raise_for_status()

                file_path = download_dir / filename
                with file_path.open('wb') as f:
                    f.write(response.content)

                if self.include_metadata:
                    metadata_path = download_dir / f"{post_json['data']['id']}.json"
                    with metadata_path.open('w') as f:
                        json.dump(post_json['data'], f)

            except (requests.RequestException, IOError) as e:
                logging.error(f"Error downloading {url}: {e}")


def main() -> None:
    """Main entry point for the Reddit scraper."""
    try:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt=DATETIME_FORMAT,
            level=logging.INFO
        )

        current_dir = Path(__file__).parent.absolute()

        parser = argparse.ArgumentParser(
            description="Scrape and download a Reddit user's posts and images.",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        parser.add_argument(
            '--username', '-u',
            help="Reddit username to scrape"
        )
        parser.add_argument(
            '--destination', '-d',
            default=current_dir,
            help="Download destination directory"
        )
        parser.add_argument(
            '--quiet', '-q',
            action='store_true',
            help="Suppress progress output"
        )
        parser.add_argument(
            '--limit', '-l',
            type=int,
            default=0,
            help="Maximum number of posts to download"
        )
        parser.add_argument(
            '--include-metadata',
            action='store_true',
            help="Save post metadata as JSON"
        )

        args = parser.parse_args()

        if not args.username:
            logging.error("Username is required")
            sys.exit(1)

        destination = Path(args.destination)
        if not destination.exists():
            logging.error(f"Destination directory does not exist: {destination}")
            sys.exit(1)

        if not destination.is_dir():
            logging.error(f"Destination is not a directory: {destination}")
            sys.exit(1)

        logging.info(f"Scraping posts from {args.username}")
        scraper = RedditScraper(
            limit_per_page=LIMIT_PER_PAGE,
            destination=args.destination,
            quiet=args.quiet,
            limit=args.limit,
            include_metadata=args.include_metadata
        )
        scraper.download_posts(args.username)
        logging.info("Scraping complete")

    except KeyboardInterrupt:
        logging.info("Shutdown requested... exiting")
        sys.exit(0)


if __name__ == '__main__':
    main()
