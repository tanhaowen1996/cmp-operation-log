import pika
from .settings import MQ_URL


class PikaMixin:

    @staticmethod
    def get_conn():
        node_list = MQ_URL.split('&')
        all_endpoints = []
        for node in node_list:
            all_endpoints.append(pika.URLParameters(node))
        connection = pika.BlockingConnection(all_endpoints)
        channel = connection.channel()
        return channel

