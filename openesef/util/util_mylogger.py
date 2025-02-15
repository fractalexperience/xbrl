import logging
import datetime
#import inspect
#import sys

import logging
import datetime
import os

def setup_logger(name, level=logging.INFO, level_file=None, log_dir="/tmp", include_console=True):
    """
    Set up logger with file handler including date and PID
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        include_console: Whether to add console handler
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True) 

    if not level_file:
        level_file = level 

    # Get current date and PID
    today = datetime.datetime.now().strftime('%Y%m%d')
    pid = os.getpid()
    
    # Create log filename
    log_filename = os.path.join(log_dir, f"log_{name}_{today}_pid{pid}.log")
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(level_file)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add console handler if requested
    if include_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    #return logger, log_filename
    return logger
# Set up logger
if __name__ == "__main__":
    logger, log_file = setup_logger(__name__)
    logger.info(f"Logging to: {log_file}")
    logger.info("Starting application")
    #do_something()

# class MyLogger(logging.Logger):
#     def __init__(self, name=__name__, level="INFO", add_file_handler=False):
#         super().__init__(name)
        
#         # Set level
#         self._level = getattr(logging, level) if isinstance(level, str) else level
#         self.setLevel(self._level)
        
#         # Clear existing handlers
#         if self.hasHandlers():
#             self.handlers.clear()
            
#         # Add handlers
#         self._add_handler()
#         if add_file_handler:
#             self._add_file_handler(add_file_handler)
            
#         self.propagate = True

#     def _get_caller_info(self):
#         """Get caller function name"""
#         frame = inspect.currentframe()
#         # Go up 2 frames to get the actual caller
#         caller_frame = frame.f_back.f_back
#         return caller_frame.f_code.co_name if caller_frame else "Unknown"

#     def info(self, message):
#         """Override info to add caller information"""
#         caller = self._get_caller_info()
#         super().info(f"{caller}: {message}")

#     def debug(self, message):
#         """Override debug to add caller information"""
#         caller = self._get_caller_info()
#         super().debug(f"{caller}: {message}")

#     def warning(self, message):
#         """Override warning to add caller information"""
#         caller = self._get_caller_info()
#         super().warning(f"{caller}: {message}")

#     def error(self, message):
#         """Override error to add caller information"""
#         caller = self._get_caller_info()
#         super().error(f"{caller}: {message}")

#     def critical(self, message):
#         """Override critical to add caller information"""
#         caller = self._get_caller_info()
#         super().critical(f"{caller}: {message}")

#     def exception(self, message):
#         """Override exception to add caller information"""
#         caller = self._get_caller_info()
#         super().exception(f"{caller}: {message}")

#     def _add_handler(self):
#         """Add stderr handler"""
#         formatter = logging.Formatter(
#             '%(asctime)s - %(name)s - PID:%(process)d - %(levelname)s - %(message)s'
#         )
#         handler = logging.StreamHandler(sys.stderr)
#         handler.setFormatter(formatter)
#         self.addHandler(handler)

#     def _add_file_handler(self, filename):
#         """Add file handler"""
#         if isinstance(filename, str):
#             log_filename = filename
#         else:
#             log_filename = f"/tmp/log_{self.name}.log"

#         formatter = logging.Formatter(
#             '%(asctime)s %(levelname)-8s pid%(process)d %(name)s %(message)s'
#         )
#         handler = logging.FileHandler(log_filename, mode='a')
#         handler.setFormatter(formatter)
#         handler.setLevel(logging.DEBUG)
#         self.addHandler(handler)
#         print(f"Logging file: {log_filename}")

#     def getEffectiveLevel(self):
#         """Override getEffectiveLevel to use internal _level"""
#         return self._level

# # Register the custom logger class
# logging.setLoggerClass(MyLogger)