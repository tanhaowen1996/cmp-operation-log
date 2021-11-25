import pika
from .settings import user, password, host, port, virtual_host


class PikaMixin:

    @staticmethod
    def get_conn():
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=credentials))
        channel = connection.channel()
        return channel

