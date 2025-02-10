# util Contents
## util/__init__.py
```py
from . import util_mylogger
# Add other utility modules here
```

## util/util_mylogger.py
```py
import logging
import datetime
import inspect
import sys

class MyLogger(logging.Logger):
    def __init__(self, name=__name__, level="INFO", add_file_handler=False):
        super().__init__(name)
        
        # Set level
        self._level = getattr(logging, level) if isinstance(level, str) else level
        self.setLevel(self._level)
        
        # Clear existing handlers
        if self.hasHandlers():
            self.handlers.clear()
            
        # Add handlers
        self._add_handler()
        if add_file_handler:
            self._add_file_handler(add_file_handler)
            
        self.propagate = True

    def _get_caller_info(self):
        """Get caller function name"""
        frame = inspect.currentframe()
        # Go up 2 frames to get the actual caller
        caller_frame = frame.f_back.f_back
        return caller_frame.f_code.co_name if caller_frame else "Unknown"

    def info(self, message):
        """Override info to add caller information"""
        caller = self._get_caller_info()
        super().info(f"{caller}: {message}")

    def debug(self, message):
        """Override debug to add caller information"""
        caller = self._get_caller_info()
        super().debug(f"{caller}: {message}")

    def warning(self, message):
        """Override warning to add caller information"""
        caller = self._get_caller_info()
        super().warning(f"{caller}: {message}")

    def error(self, message):
        """Override error to add caller information"""
        caller = self._get_caller_info()
        super().error(f"{caller}: {message}")

    def critical(self, message):
        """Override critical to add caller information"""
        caller = self._get_caller_info()
        super().critical(f"{caller}: {message}")

    def exception(self, message):
        """Override exception to add caller information"""
        caller = self._get_caller_info()
        super().exception(f"{caller}: {message}")

    def _add_handler(self):
        """Add stderr handler"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def _add_file_handler(self, filename):
        """Add file handler"""
        if isinstance(filename, str):
            log_filename = filename
        else:
            log_filename = f"/tmp/log_{self.name}.log"

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)-8s pid%(process)d %(name)s %(message)s'
        )
        handler = logging.FileHandler(log_filename, mode='a')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        self.addHandler(handler)
        print(f"Logging file: {log_filename}")

    def getEffectiveLevel(self):
        """Override getEffectiveLevel to use internal _level"""
        return self._level

# Register the custom logger class
logging.setLoggerClass(MyLogger)
```
