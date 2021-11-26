import pika
from .settings import MQ_USER, MQ_PASSWORD, MQ_HOST, MQ_PORT, MQ_VIRTUAL


class PikaMixin:

    @staticmethod
    def get_conn():
        credentials = pika.PlainCredentials(MQ_USER, MQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=MQ_HOST,
            port=MQ_PORT,
            virtual_host=MQ_VIRTUAL,
            credentials=credentials))
        channel = connection.channel()
        return channel

