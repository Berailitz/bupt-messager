"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
import sys
import threading
from bupt_messager.bupt_messager import BUPTMessager

def main():
    if '--debug' in sys.argv:
        bupt_messager = BUPTMessager(debug_mode=True)
    else:
        bupt_messager = BUPTMessager()
    try:
        bupt_messager.start()
    except Exception as identifier:
        logging.warning(f'Messager is going to stop due to: {identifier}.')
        bupt_messager.stop()
        logging.info(f'Messager: stooped.')
        logging.info(f'Left workers: {threading.enumerate()}')

if __name__ == '__main__':
    main()
