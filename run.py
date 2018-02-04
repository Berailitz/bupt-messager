"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
import threading
from bupt_messager.bupt_messager import BUPTMessager

def main():
    bupt_messager = BUPTMessager()
    try:
        bupt_messager.run()
    except KeyboardInterrupt:
        logging.warning('Messager is going to stop due to keyboard interrupt.')
        bupt_messager.stop()
        logging.info(f'Messager: stooped.')

if __name__ == '__main__':
    main()
