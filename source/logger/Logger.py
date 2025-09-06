import logging
import logging.handlers
import os
import sys # Import sys for StreamHandler to specify stdout
from datetime import datetime

class Logger:
    """
    A Singleton Logger class designed to manage logging consistently across a project.

    It ensures only one instance of the logger exists and handles its configuration
    (log level, file output, rotation, etc.), preventing multiple basicConfig initializations.
    """
    _instance = None
    _is_initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Implements the Singleton pattern. Ensures only one instance of Logger is created.
        """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            # IMPORTANT: The _initialize_logger method is now called *after*
            # the __init__ method has finished its first run, which is handled
            # by the _is_initialized flag. We avoid calling it directly from __new__
            # to ensure self.log_file_path and other attributes are set up by __init__.
        return cls._instance

    def __init__(self,
                 log_file_name: str = "application.log",
                 log_dir: str = "logs",
                 level: int = logging.INFO,
                 console_output: bool = True,
                 max_bytes: int = 10 * 1024 * 1024, # 10 MB
                 backup_count: int = 5): # Keep 5 old log files
        """
        Initializes the logger. This method runs only once for the first instance.
        Subsequent calls will do nothing due to the _is_initialized flag.

        Args:
            log_file_name (str): The name of the log file (e.g., 'app.log').
            log_dir (str): The directory to store log files.
            level (int): The logging level (logging.DEBUG, logging.INFO, etc.).
            console_output (bool): True to output logs to the console, False otherwise.
            max_bytes (int): Maximum size of the log file before rotation (bytes).
            backup_count (int): Number of old log files to keep during rotation.
        """
        if self._is_initialized:
            return # If already initialized, do nothing

        # Set attributes first, so _configure_logger can access them
        self.log_dir = log_dir
        self.log_file_path = os.path.join(log_dir, log_file_name)
        self.level = level
        self.console_output = console_output
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Now, call the configuration method
        self._configure_logger()

        # Mark as initialized AFTER successful configuration
        self._is_initialized = True

        self.logger.info(f"Logger fully initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Log directory: {self.log_dir}")
        self.logger.info(f"Log file path: {self.log_file_path}")
        self.logger.info(f"Log level: {logging.getLevelName(self.level)}")
        self.logger.info(f"Console output enabled: {self.console_output}")

    def _configure_logger(self):
        """
        Configures the underlying Python logging.Logger object and its handlers.
        This method is called internally during the first initialization.
        """
        # Get the logger instance. Using a fixed name to ensure consistency across imports.
        self.logger = logging.getLogger("ProjectAppLogger") # Using a more specific name
        self.logger.setLevel(self.level)
        self.logger.propagate = False # Crucial: Prevent logs from propagating to the root logger

        # Remove existing handlers to prevent duplicate logs on re-initialization attempts
        # (useful in some testing scenarios or complex app restarts)
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

        # Formatter for log messages
        # Include %(name)s for clarity if you have multiple named loggers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # File Handler (with rotation)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_file_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8' # Ensures support for Vietnamese characters and other UTF-8
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console Handler (if enabled)
        if self.console_output:
            # Direct StreamHandler to sys.stdout for standard output
            console_handler = logging.StreamHandler(sys.stdout)
            # Use a slightly simpler formatter for console if preferred, or the same
            console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # Log that the configuration was performed
        # This log will go to the file handler, as the logger is now configured.
        self.logger.info(f"Logger configuration completed for '{self.logger.name}'.")

    def get_logger(self) -> logging.Logger:
        """
        Returns the configured logging.Logger object.
        """
        if not self._is_initialized:
            # This case should ideally not happen if Logger is always
            # initialized at the app's entry point.
            # You might want to raise an error or just log a warning here.
            # For robustness, we'll ensure it's configured even if called incorrectly.
            self._configure_logger() # Force configuration if somehow not initialized
            self._is_initialized = True
            self.logger.warning("Logger.get_logger() called before explicit initialization. Initializing with default settings.")
        return self.logger

# --- How to use this Logger class ---
# IMPORTANT: This block should typically be in your application's main entry point (e.g., main.py or app.py),
# NOT directly in the Logger.py file itself. Putting it in Logger.py makes it initialize
# every time you import anything from Logger.py, which defeats the purpose of central control.

# Example of how it should be used in your main script:
app_logger = Logger(
    log_file_name='inference_ndvi.log',
    log_dir='./logs',
    level=logging.INFO,
    console_output=True,
    max_bytes=10 * 1024 * 1024,
    backup_count=5
).get_logger()

