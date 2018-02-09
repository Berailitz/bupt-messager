"""Start main app."""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
import sys
import threading
from bupt_messager.bupt_messager import BUPTMessager


def main():
    """Prase arguments started with `--`.
    """
    debug_mode = '--debug' in sys.argv
    no_bot_mode = '--no-bot' in sys.argv
    no_spider_mode = '--no-spider' in sys.argv
    bupt_messager = BUPTMessager(debug_mode=debug_mode, no_bot_mode=no_bot_mode, no_spider_mode=no_spider_mode)
    try:
        bupt_messager.start()
    except Exception as identifier:
        logging.warning(f'Messager is going to stop due to: {identifier}.')
        bupt_messager.stop()
        logging.info(f'Messager: stooped.')
        logging.info(f'Left workers: {threading.enumerate()}')


if __name__ == '__main__':
    main()
