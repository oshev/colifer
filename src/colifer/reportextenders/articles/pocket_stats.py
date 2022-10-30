"""Module to gather basic Pocket stats."""

from colifer.config import Config
import logging
from colifer.reportextenders.articles.pocket_parser import PocketParser

LOGGING_FORMAT = '[%(levelname)s] %(asctime)s %(name)s:%(lineno)d - %(message)s'

logging.basicConfig(level="INFO", format=LOGGING_FORMAT)
logger = logging.getLogger(__name__)


def main():
    config = Config()
    pocker_parser = PocketParser(config.get_param('Pocket'))
    result_unread = pocker_parser.api.get(state='unread', detailType='simple')
    result_archived = pocker_parser.api.get(state='archived', detailType='simple')
    logger.info(f"\nPocket stats: \n"
                f"   Unread queue size: {len(result_unread[0]['list'])}\n"
                f"   Number archived: {len(result_archived[0]['list'])}")

if __name__ == '__main__':
    main()