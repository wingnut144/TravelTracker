"""
Scheduler for automated tasks
Runs email scanning at regular intervals
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/scheduler.log')
    ]
)

logger = logging.getLogger(__name__)

def scan_emails_job():
    """Job to scan emails for flight confirmations"""
    from app import app
    from email_scanner import scan_all_email_accounts
    
    logger.info('Starting scheduled email scan...')
    
    try:
        with app.app_context():
            trips_created = scan_all_email_accounts()
            logger.info(f'Email scan completed. Created {trips_created} new trips.')
    except Exception as e:
        logger.error(f'Error during email scan: {str(e)}', exc_info=True)


def update_flight_statuses_job():
    """Job to update flight statuses from airline APIs"""
    from app import app, db
    from models import Flight
    from airline_apis import AirlineAPIManager
    from datetime import datetime, timedelta
    
    logger.info('Starting flight status updates...')
    
    try:
        with app.app_context():
            # Get flights in the next 48 hours
            now = datetime.utcnow()
            upcoming_window = now + timedelta(hours=48)
            
            flights = Flight.query.filter(
                Flight.departure_time >= now,
                Flight.departure_time <= upcoming_window,
                Flight.status != 'cancelled'
            ).all()
            
            api_manager = AirlineAPIManager(app.config)
            updated_count = 0
            
            for flight in flights:
                try:
                    if api_manager.update_flight_status(flight):
                        updated_count += 1
                except Exception as e:
                    logger.error(f'Error updating flight {flight.id}: {str(e)}')
            
            logger.info(f'Updated {updated_count} flight statuses.')
    
    except Exception as e:
        logger.error(f'Error during flight status update: {str(e)}', exc_info=True)


def cleanup_expired_shares_job():
    """Job to cleanup expired external shares"""
    from app import app, db
    from models import TripShare
    from datetime import datetime
    
    logger.info('Starting cleanup of expired shares...')
    
    try:
        with app.app_context():
            now = datetime.utcnow()
            
            expired_shares = TripShare.query.filter(
                TripShare.expires_at < now,
                TripShare.expires_at.isnot(None)
            ).all()
            
            for share in expired_shares:
                db.session.delete(share)
            
            db.session.commit()
            logger.info(f'Cleaned up {len(expired_shares)} expired shares.')
    
    except Exception as e:
        logger.error(f'Error during share cleanup: {str(e)}', exc_info=True)


def sync_foursquare_checkins_job():
    """Job to sync Foursquare check-ins for active trips"""
    from app import app, db
    from models import Trip, User, UserSettings
    from utils import sync_trip_checkins
    from datetime import datetime, timedelta
    
    logger.info('Starting Foursquare check-in sync...')
    
    try:
        with app.app_context():
            # Get all current and upcoming trips with Foursquare enabled
            now = datetime.utcnow()
            seven_days_ago = now - timedelta(days=7)
            
            trips = Trip.query.join(User).join(UserSettings).filter(
                UserSettings.foursquare_enabled == True,
                Trip.end_date >= seven_days_ago  # Include recent past trips
            ).all()
            
            total_new = 0
            for trip in trips:
                try:
                    new_checkins = sync_trip_checkins(trip)
                    total_new += new_checkins
                    if new_checkins > 0:
                        logger.info(f'Added {new_checkins} check-ins to trip {trip.id}: {trip.title}')
                except Exception as e:
                    logger.error(f'Error syncing trip {trip.id}: {str(e)}')
            
            logger.info(f'Foursquare sync completed. Added {total_new} total check-ins.')
    
    except Exception as e:
        logger.error(f'Error during Foursquare sync: {str(e)}', exc_info=True)


def main():
    """Main scheduler"""
    from app import app
    
    # Get configuration
    scan_interval = int(os.environ.get('EMAIL_SCAN_INTERVAL', 300))  # 5 minutes default
    
    logger.info(f'Starting scheduler with {scan_interval}s email scan interval')
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Add email scanning job
    scheduler.add_job(
        scan_emails_job,
        trigger=IntervalTrigger(seconds=scan_interval),
        id='scan_emails',
        name='Scan emails for flight confirmations',
        replace_existing=True
    )
    
    # Add flight status update job (every 30 minutes)
    scheduler.add_job(
        update_flight_statuses_job,
        trigger=IntervalTrigger(minutes=30),
        id='update_flights',
        name='Update flight statuses',
        replace_existing=True
    )
    
    # Add share cleanup job (daily at 2 AM)
    scheduler.add_job(
        cleanup_expired_shares_job,
        trigger='cron',
        hour=2,
        minute=0,
        id='cleanup_shares',
        name='Cleanup expired shares',
        replace_existing=True
    )
    
    # Add Foursquare check-in sync job (every hour)
    scheduler.add_job(
        sync_foursquare_checkins_job,
        trigger=IntervalTrigger(hours=1),
        id='sync_foursquare',
        name='Sync Foursquare check-ins',
        replace_existing=True
    )
    
    logger.info('Scheduler started successfully')
    logger.info(f'Jobs: {[job.id for job in scheduler.get_jobs()]}')
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Scheduler stopped')


if __name__ == '__main__':
    main()
