"""start main app"""
#!/usr/env/python3
# -*- coding: UTF-8 -*-

import logging
from bupt_messager.bupt_messager import BUPTMessager

def main():
    bupt_messager = BUPTMessager()
    try:
        bupt_messager.run()
    except KeyboardInterrupt:
        logging.warning('Messager is stopping due to keyboard interrupt.')
        bupt_messager.stop()

if __name__ == '__main__':
    main()
