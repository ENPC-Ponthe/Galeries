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
        }
    })
