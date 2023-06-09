import asyncio
import os

from log import LoggerConfigurator, logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config.config import Config
from jobs.forma_task_excel_locker import FormaTaskExcelLockerJob
from services.forma import FormaService

config = Config()
LoggerConfigurator.configure(config.log)


def start_jobs(scheduler: AsyncIOScheduler):
    jel_cfg = config.jobs.excel_locker
    if jel_cfg.is_enabled:
        sv_forma = FormaService(config=config.forma)
        job_ftel = FormaTaskExcelLockerJob(forma=sv_forma, config=jel_cfg.options)
        scheduler.add_job(job_ftel.run, 'interval', seconds=jel_cfg.interval_seconds)
        logger.debug("JOB: 'Excel locker' started")
    scheduler.start()
    logger.info('JOB: all jobs started')

def run_app():
    scheduler = AsyncIOScheduler()
    start_jobs(scheduler)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()

if __name__ == '__main__':
    run_app()
