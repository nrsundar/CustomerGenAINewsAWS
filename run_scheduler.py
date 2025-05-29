#!/usr/bin/env python3
"""
GenAI Content Monitor - Scheduler Runner
Entry point for running the automated scheduler
"""

import os
import sys
import signal
import logging
from dotenv import load_dotenv

from scheduler import ContentScheduler
from utils import setup_logging

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    """Main scheduler runner"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get schedule interval from environment or command line
    schedule_interval = "daily"  # default
    
    if len(sys.argv) > 1:
        schedule_interval = sys.argv[1]
    else:
        schedule_interval = os.getenv("SCHEDULE_INTERVAL", "daily")
    
    logger.info(f"Starting GenAI Content Monitor Scheduler")
    logger.info(f"Schedule interval: {schedule_interval}")
    
    # Validate schedule interval
    valid_intervals = [
        "hourly", "every_2_hours", "every_6_hours", 
        "daily", "twice_daily", "weekly"
    ]
    
    if schedule_interval not in valid_intervals:
        logger.error(f"Invalid schedule interval: {schedule_interval}")
        logger.error(f"Valid options: {', '.join(valid_intervals)}")
        sys.exit(1)
    
    try:
        # Create and start scheduler
        scheduler = ContentScheduler(schedule_interval)
        
        logger.info("Scheduler configuration:")
        for job_info in scheduler.list_jobs():
            logger.info(f"  - {job_info['function']}: {job_info['next_run']} ({job_info['interval']} {job_info['unit']})")
        
        logger.info(f"Next run: {scheduler.get_next_run_time()}")
        logger.info("Press Ctrl+C to stop the scheduler")
        
        # Start the scheduler (this will block)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
