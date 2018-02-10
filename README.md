# BUPT Messager

A Messager that forwards notifications, containing:
 - A spider that crawles `my.bupt.edu.cn`.
 - A Telegram [bot](https://telegram.me/bupt_messager) that provides a few commands.

### Features
 - Web VPN support
 - Captcha recognition
 - Interact with buttons and commands
 - Remote control via Telegram
 - Message queued embeded

### Requirements
 - MySQL
 - A Telegram bot account
 - Python 3.6+
 - Packages in `requirements.txt`
 - [Tesseract](https://github.com/tesseract-ocr/tesseract)

### Installation
1. Talk to [BotFather](https://telegram.me/BotFather) and create a bot.
1. Make sure MySQL, Python and Tesseract are properly installed and that SQL server is running.
1. Create an SQL user and initialize database using sql files in folder `sql`.
1. Set up a pyenv enviroment (recommend)and install dependencies via pip.
1. Copy `credentials.default.py` to `credentials.py` and edit it.
1. Edit `config.py` if necessary.
1. run `python run.py`.

### Start commands
 - `--debug`: Set log level to `logging.DEBUG`
 - `--no-bot`: Bot will not response to commands and callbacks
 - `--no-spider`: No notification will be fetched

### Bot commands
 - `/start`: Start the chat and subscribe.
 - `/latest {list_length}`: Read a list of latest notifications, 5 items by default.
 - `/status {status_amount}`: Checkout latest status and errors.
 - `/restart {start_commands}`: Restart the application.
