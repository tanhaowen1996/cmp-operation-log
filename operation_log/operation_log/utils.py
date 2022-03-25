import logging
import random

import pika
from .settings import MQ_URL


class PikaMixin:

    @staticmethod
    def get_conn():
        node_list = MQ_URL.split('&')
        all_endpoints = []
        for node in node_list:
            all_endpoints.append(pika.URLParameters(node))
        random.shuffle(all_endpoints)
        for url in all_endpoints:
            try:
                logging.basicConfig(level=logging.DEBUG)
                connection = pika.BlockingConnection(url)
            except Exception as ex:
                print(str(ex))
            else:
                break
        channel = connection.channel()
        return channel

