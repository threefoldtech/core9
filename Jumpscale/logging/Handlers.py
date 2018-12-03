import logging
import time
import os

import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import MemoryHandler

from .Filter import ModuleFilter
from .LimitFormater import LimitFormater


FILE_FORMAT = '%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)-8s - %(message)s'
CONSOLE_FORMAT = '%(cyan)s[%(asctime)s]%(reset)s - %(filename)-18s:%(lineno)-4d:%(name)-20s - %(log_color)s%(levelname)-8s%(reset)s - %(message)s'
# CONSOLE_FORMAT = '%(cyan)s[%(asctime)s]%(reset)s - %(filename)-20s:%(lineno)-4d - %(log_color)s%(levelname)-5s%(reset)s - %(message)s'


class Handlers():

    def __init__(self):
        self._fileRotateHandler = None
        self._consoleHandler = None
        self._memoryHandler = None
        self._telegramHandler = None
        self._all = []

    @property
    def fileRotateHandler(self, name='jumpscale'):
        if self._fileRotateHandler is None:
            from Jumpscale import j
            if not j.sal.fs.exists("%s/log/" % j.dirs.VARDIR):
                j.sal.fs.createDir("%s/log/" % j.dirs.VARDIR)
            filename = "%s/log/%s.log" % (j.dirs.VARDIR, name)
            formatter = logging.Formatter(FILE_FORMAT)
            fh = TimedRotatingFileHandler(
                filename, when='D', interval=1, backupCount=7, encoding=None, delay=False, utc=False, atTime=None)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self._fileRotateHandler = fh
            self._all.append(self._fileRotateHandler)
        return self._fileRotateHandler

    @property
    def consoleHandler(self):
        if self._consoleHandler is None:
            formatter = LimitFormater(
                fmt=CONSOLE_FORMAT,
                datefmt="%a%d %H:%M",
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
                secondary_log_colors={},
                style='%',
                lenght=37
            )
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            self._consoleHandler = ch
            self._all.append(self._consoleHandler)
        return self._consoleHandler

    def redisHandler(self, redis_client=None):
        if redis_client is None:
            self.redis_client = j.core.db
        raise RuntimeError("need to implement redishandler")

    @property
    def memoryHandler(self):
        if self._memoryHandler is None:
            self._memoryHandler = MemoryHandler(capacity=10000)
            self._all.append(self._memoryHandler)
        return self._memoryHandler

    def telegramHandler(self, client, chat_id, level=logging.CRITICAL):
        """
        Create a telegram handler to forward logs to a telegram group.
        @param client: A jumpscale telegram_bot client 
        @param chat_id: Telegram chat id to which logs need to be forwarded
        @param level: Loglevel that should be handeld by this handler
        """
        if self._telegramHandler is None:
            self._telegramHandler = TelegramHandler(client, chat_id)
            self._telegramHandler.setLevel(level)
            self._telegramHandler.setFormatter(TelegramFormatter())
            self._all.append(self._telegramHandler)
        return self._telegramHandler


class TelegramHandler(logging.Handler):
    """
    Handler to forward logs to a telegram group
    """

    def __init__(self, client, chat_id):
        """
        Create a telegram handler to forward logs to a telegram group.
        @param client: A jumpscale telegram_bot client 
        @param chat_id: Telegram chat id to which logs need to be forwarded
        """
        super(TelegramHandler, self).__init__()
        self.telegram_client = client
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.telegram_client.send_message(self.chat_id, log_entry, parse_mode="Markdown")


class TelegramFormatter(logging.Formatter):

    def format(self, record):
        return "```\n%s\n```" % super(TelegramFormatter, self).format(record)
