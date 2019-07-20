from contextlib import contextmanager

WHITE = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
ORANGE = '\033[33m'

START_MARKER = 'STARTINGTRANSMISSION' * 4
STOP_MARKER = 'ENDINGTRANSMISSION' * 4


@contextmanager
def pending_message(message):
    print(ORANGE, message, WHITE, sep='', end='', flush=True)
    yield
    print(GREEN, '\t[DONE]', WHITE, sep='')
