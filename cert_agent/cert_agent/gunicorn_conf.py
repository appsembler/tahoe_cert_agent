import logging
import os
import beeline


def post_worker_init(worker):
    logging.info(f'beeline initialization in process pid {os.getpid()}')
    if os.environ.get('HONEYCOMB_WRITEKEY'):
        beeline.init(
            writekey=os.environ['HONEYCOMB_WRITEKEY'],
            dataset=os.environ['HONEYCOMB_DATASET'],
            service_name='cert_agent')
