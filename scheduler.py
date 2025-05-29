"""
Scheduler module for GenAI Content Monitor
Handles automated scheduling of content monitoring
"""

import schedule
import time
import logging
from datetime import datetime
from main import main

logger = logging.getLogger(__name__)

class ContentScheduler:
    """Scheduler for automated content monitoring"""
    
    def __init__(self, schedule_interval: str = "daily"):
        self.schedule_interval = schedule_interval
        self.is_running = False
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup the monitoring schedule"""
        logger.info(f"Setting up schedule: {self.schedule_interval}")
        
        if self.schedule_interval == "hourly":
            schedule.every().hour.do(self.run_monitoring)
        elif self.schedule_interval == "every_2_hours":
            schedule.every(2).hours.do(self.run_monitoring)
        elif self.schedule_interval == "every_6_hours":
            schedule.every(6).hours.do(self.run_monitoring)
        elif self.schedule_interval == "daily":
            schedule.every().day.at("09:00").do(self.run_monitoring)
        elif self.schedule_interval == "twice_daily":
            schedule.every().day.at("09:00").do(self.run_monitoring)
            schedule.every().day.at("18:00").do(self.run_monitoring)
        elif self.schedule_interval == "weekly":
            schedule.every().monday.at("09:00").do(self.run_monitoring)
        else:
            logger.warning(f"Unknown schedule interval: {self.schedule_interval}, defaulting to daily")
            schedule.every().day.at("09:00").do(self.run_monitoring)
    
    def run_monitoring(self):
        """Run the monitoring process"""
        try:
            logger.info(f"Starting scheduled monitoring run at {datetime.now()}")
            main()
            logger.info(f"Completed scheduled monitoring run at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error during scheduled monitoring run: {e}")
    
    def start(self):
        """Start the scheduler"""
        self.is_running = True
        logger.info("Content monitor scheduler started")
        
        # Run once immediately if requested
        logger.info("Running initial monitoring check...")
        self.run_monitoring()
        
        # Start the schedule loop
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                self.stop()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("Content monitor scheduler stopped")
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        next_run = schedule.next_run()
        if next_run:
            return next_run.strftime("%Y-%m-%d %H:%M:%S")
        return "No scheduled runs"
    
    def list_jobs(self):
        """List all scheduled jobs"""
        jobs = schedule.get_jobs()
        job_info = []
        for job in jobs:
            job_info.append({
                "function": job.job_func.__name__,
                "next_run": job.next_run.strftime("%Y-%m-%d %H:%M:%S") if job.next_run else "Never",
                "interval": str(job.interval),
                "unit": job.unit
            })
        return job_info

def run_manual():
    """Run monitoring manually (one-time execution)"""
    logger.info("Running manual monitoring check...")
    main()
    logger.info("Manual monitoring check completed")

if __name__ == "__main__":
    import sys
    from utils import setup_logging
    
    setup_logging()
    
    if len(sys.argv) > 1:
        interval = sys.argv[1]
    else:
        interval = "daily"
    
    scheduler = ContentScheduler(interval)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
