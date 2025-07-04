"""
Logging configuration for BERKE0S
"""

import os
import logging
import logging.handlers
from typing import Optional

def setup_logging(level: int = logging.INFO, config_dir: Optional[str] = None) -> logging.Logger:
    """Setup comprehensive logging for BERKE0S"""
    
    if config_dir is None:
        config_dir = os.path.expanduser("~/.berke0s")
    
    os.makedirs(config_dir, exist_ok=True)
    
    # Main log file
    log_file = os.path.join(config_dir, "berke0s.log")
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Create specialized loggers
    display_logger = logging.getLogger('display')
    display_log_file = os.path.join(config_dir, "display.log")
    display_handler = logging.handlers.RotatingFileHandler(
        display_log_file, maxBytes=5*1024*1024, backupCount=3
    )
    display_handler.setFormatter(detailed_formatter)
    display_logger.addHandler(display_handler)
    
    # Application logger
    app_logger = logging.getLogger('berke0s')
    
    app_logger.info("Logging system initialized")
    app_logger.info(f"Log level: {logging.getLevelName(level)}")
    app_logger.info(f"Log directory: {config_dir}")
    
    return app_logger