import os
import sys
import logging
from datetime import datetime


class DailyFileHandler(logging.Handler):
    """Writes log records to instance/logs/log_YYYY-MM-DD.txt, rotating at midnight."""

    def __init__(self, log_dir):
        super().__init__()
        self._log_dir = log_dir
        self._current_date = None
        self._file = None

    def _get_file(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if today != self._current_date:
            if self._file:
                self._file.close()
            self._file = open(
                os.path.join(self._log_dir, f'log_{today}.txt'),
                'a', encoding='utf-8'
            )
            self._current_date = today
        return self._file

    def emit(self, record):
        try:
            msg = self.format(record)
            f = self._get_file()
            f.write(msg + '\n')
            f.flush()
        except Exception:
            self.handleError(record)

    def close(self):
        if self._file:
            self._file.close()
        super().close()


def setup_logging(instance_path):
    """
    Configure root logger with two handlers:
      - DailyFileHandler  → instance/logs/log_YYYY-MM-DD.txt
      - StreamHandler     → stdout (console)
    """
    log_dir = os.path.join(instance_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = DailyFileHandler(log_dir)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG) # logging.INFO for less detail
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
