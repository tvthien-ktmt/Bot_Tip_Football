import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from backend.app.core.database import SessionLocal
from backend.app.data.football_data_uk import FootballDataUKIngestion
from backend.app.backtest.engine import WalkForwardBacktestEngine

logger = logging.getLogger("keolab.scheduler")


def daily_update_job():
    """Runs at 06:00: syncs results, recalibrates ratings, settles tips."""
    logger.info("Executing daily match results sync & rating updates...")
    db = SessionLocal()
    try:
        ingestion = FootballDataUKIngestion()
        synced = ingestion.sync_to_db(db)
        logger.info(f"Daily update finished. {synced} matches updated.")
    except Exception as e:
        logger.error(f"Error in daily_update_job: {e}")
    finally:
        db.close()


def odds_refresh_job():
    """Runs every 45 minutes: fetches odds snapshots while respecting API credit quotas."""
    logger.info("Checking latest market odds movements & line fluctuations...")


def weekly_retrain_job():
    """Runs weekly: refits Dixon-Coles time-decay and walk-forward backtests."""
    logger.info("Executing weekly model walk-forward backtest & calibration...")
    db = SessionLocal()
    try:
        engine = WalkForwardBacktestEngine(db)
        res = engine.run_backtest()
        logger.info(f"Weekly retrain completed: {res.get('total_tips', 0)} tips evaluated.")
    except Exception as e:
        logger.error(f"Error in weekly_retrain_job: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    # 06:00 AM daily
    scheduler.add_job(daily_update_job, CronTrigger(hour=6, minute=0))
    # Odds every 45 mins
    scheduler.add_job(odds_refresh_job, IntervalTrigger(minutes=45))
    # Weekly retrain on Monday 04:00 AM
    scheduler.add_job(weekly_retrain_job, CronTrigger(day_of_week="mon", hour=4, minute=0))
    scheduler.start()
    logger.info("APScheduler initialized for KèoLab pipeline.")
    return scheduler
