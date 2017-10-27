import logging.config


LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'ptscripts_formatter': {
            'format': '[{levelname}][{name}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'formatter': 'ptscripts_formatter',
        },
    },
    'loggers': {
        'ptscripts': {
            'handlers': ['consoleHandler'],
            'level': 'INFO',
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
