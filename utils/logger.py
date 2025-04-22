
import logging
import os
from datetime import datetime

def get_module_logger(module_name):
    """Get a logger configured for a specific module"""
    logger = logging.getLogger(module_name)
    
    # Set default level
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    os.makedirs('logs', exist_ok=True)
    today = datetime.now().strftime('%Y%m%d')
    file_handler = logging.FileHandler(f'logs/nitrite_dynamics_{today}.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger if they haven't been added already
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# Default application logger
app_logger = get_module_logger('app')

def log_exception(logger, exception, context=""):
    """Log an exception with traceback and context"""
    import traceback
    error_msg = f"Exception during {context}: {str(exception)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    return error_msg

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
    try:
        logger_name = name or 'nitrite_dynamics'
        logger = logging.getLogger(logger_name)
        
        # Only configure logger once
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)
            
            # Console handler
            try:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(console_format)
                logger.addHandler(console_handler)
            except Exception as console_err:
                # If console handler fails, print but continue with file handler
                print(f"Warning: Failed to set up console logger: {str(console_err)}")
            
            # File handler with error handling
            try:
                # Ensure logs directory exists
                os.makedirs(logs_dir, exist_ok=True)
                
                # Create log filename with fallback if datetime fails
                try:
                    date_part = datetime.now().strftime("%Y%m%d")
                except:
                    # Fallback to simple timestamp if datetime fails
                    date_part = str(int(time.time()))
                
                log_file = os.path.join(logs_dir, f'nitrite_dynamics_{date_part}.log')
                
                # Add log rotation to prevent large log files
                from logging.handlers import RotatingFileHandler
                
                # Create rotating file handler with proper permissions
                file_handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10485760,  # 10MB
                    backupCount=5,
                    delay=True  # Only open file when first record is emitted
                )
                
                # Set file permissions if on Unix (fails gracefully on Windows)
                try:
                    import stat
                    os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
                except Exception:
                    pass  # Ignore permission errors
                
                file_handler.setLevel(logging.DEBUG)
                file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(file_format)
                
                logger.addHandler(file_handler)
            except Exception as file_err:
                # If file handler fails, log to console but don't crash
                print(f"Warning: Failed to set up file logger: {str(file_err)}")
                
            # Add a safety wrapper to prevent logging errors from crashing the app
            original_error = logger.error
            def safe_error(msg, *args, **kwargs):
                try:
                    return original_error(msg, *args, **kwargs)
                except Exception as e:
                    print(f"Error in logger.error: {str(e)}")
                    print(f"Original message: {msg}")
            logger.error = safe_error
        
        return logger
    except Exception as e:
        # Last resort fallback logger that won't crash
        print(f"CRITICAL: Failed to configure logger: {str(e)}")
        fallback_logger = logging.getLogger('fallback')
        if not fallback_logger.handlers:
            fallback_logger.addHandler(logging.StreamHandler(sys.stdout))
        return fallback_logger

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