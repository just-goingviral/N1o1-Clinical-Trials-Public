"""
Logger utility for Nitrite Dynamics application
Provides consistent logging across the application
"""
import logging
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
def configure_logger(name=None):
    """Configure logger with standard formatting and outputs"""
    logger_name = name or 'nitrite_dynamics'
    logger = logging.getLogger(logger_name)
    
    # Only configure logger once
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        
        # File handler
        log_file = os.path.join(logs_dir, f'nitrite_dynamics_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# Main application logger
app_logger = configure_logger('nitrite_dynamics')

# Module-specific loggers
def get_module_logger(module_name):
    """Get logger for specific module"""
    return configure_logger(f'nitrite_dynamics.{module_name}')

# Function to log exceptions with detailed information
def log_exception(logger, e, context=None):
    """Log exception with detailed information"""
    context_info = f" while {context}" if context else ""
    logger.error(f"Exception{context_info}: {type(e).__name__}: {str(e)}", exc_info=True)