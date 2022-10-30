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
    result = pocker_parser.api.get(state='unread', detailType='simple')
    logger.info(f"Current Pocket queues size: {len(result)}")

if __name__ == '__main__':
    main()