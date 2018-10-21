import logging.config as config
import os

LOG_FILE = "ponthe.log"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "instance", "club_folder", "logs", LOG_FILE)

def logging_init():
    config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
            'slack': {
                'class': 'slack_logger.SlackFormatter'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout',
                'formatter': 'default'
            },
            'rotating': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': 'DEBUG',
                'filename': LOG_PATH,
                'when': 'midnight',
                'backupCount': 365,
                'encoding': 'utf-8',
                'formatter': 'default'
            },
            'slack': {
                'class': 'slack_logger.SlackHandler',
                'url': os.environ.get('WEBHOOK_URL'),
                'username': 'Galeries Ponthé',
                'level': 'WARNING',
                'formatter': 'slack'
            }
        },
        'root': {
            'handlers': ['console', 'rotating']#, 'slack']
        }
    })
