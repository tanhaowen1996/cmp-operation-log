import logging
import json
from django.core.management.base import BaseCommand
from operation_log.utils import PikaMixin
from operation_log.serializers import OperationLogSerializer
import re


LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s.%(funcName)s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Waiting to receiving notifications and process"

    volume_operation = {
        "attached": "挂载云硬盘",
        "detached": "卸载云硬盘",
        "extend": "扩容云硬盘"
    }

    server_operation = {
        "changeFlavor": '修改云主机规格',
        "changePassword": '修改云主机密码',
        "createImage": '创建云主机镜像',
        "os-start": '开启云主机',
        "os-stop": '关闭云主机',
        "reboot-hard": '硬重启云主机',
        "reboot-soft": '软重启云主机',
        "attachInterface": '云主机添加网卡',
        "attachVolume": '云主机挂载云硬盘',
        "createInstance": '创建云主机',
        "delInstance": '删除云主机',
        "delVolume": '云主机卸载云硬盘',
        "detachInterface": '云主机卸载网卡',
        "updateName": '重新命名',
    }

    def get_volume_operation(self, url, method):
        # import pdb
        # pdb.set_trace()
        if method == 'DELETE':
            return '删除云硬盘'
        if method == "PUT" or method == 'PATCH':
            return '修改云硬盘'
        type_id = re.findall(r'/v2/volume/([0-9a-f-]{36})', url)
        if type_id == []:
            return '创建云硬盘'
        operation_name = url.split('/')[-1]
        operation_name = operation_name.split('?')[0]
        return self.volume_operation[operation_name]

    def get_server_operation(self, url, method):
        operation_name = url.split('/')[-1]
        operation_name = operation_name.split('?')[0]
        return self.server_operation[operation_name]

    def callback(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        body_json = json.loads(body.decode())

        if body_json['method'] == 'GET':
            return None
        if not ('volume' in body_json['requestUrl'] or 'servers' in body_json['requestUrl']):
            return None

        if 'status' in body_json['requestUrl'] or \
                'getConsole' in body_json['requestUrl'] or \
                'attached_list' in body_json['requestUrl'] or \
                'detached_list' in body_json['requestUrl'] or \
                'ums' in body_json['requestUrl'] or \
                'listInstance' in body_json['requestUrl']:
            return None

        if 'volume' in body_json['requestUrl']:
            type = 'volume'
            type_name = self.get_volume_operation(body_json['requestUrl'], body_json['method'])
            get_type_id = re.findall(r'/v2/volume/([0-9a-f-]{36})', body_json['requestUrl'])
            try:
                if get_type_id == []:
                    response_json = json.loads(body_json['responseBody'])
                    for instance in response_json:
                        type_id = instance['id']
                        serializer = OperationLogSerializer(data=instance)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(
                            name=type_name,
                            user_id=body_json['accountInfo']['id'],
                            user_name=body_json['accountInfo']['loginName'],
                            type=type,
                            type_id=type_id,
                            type_name=type_name,
                            status='操作成功',
                            operation_ip=body_json['ip'],
                            operation_address=body_json['requestUrl'],
                        )
                    return None
                else:
                    type_id = get_type_id[0]
                    serializer = OperationLogSerializer(data=body_json)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(
                        name=type_name,
                        user_id=body_json['accountInfo']['id'],
                        user_name=body_json['accountInfo']['loginName'],
                        type=type,
                        type_id=type_id,
                        type_name=type_name,
                        status='操作成功',
                        operation_ip=body_json['ip'],
                        operation_address=body_json['requestUrl'],
                    )
                    return None
            except BaseException:
                return BaseException

        if 'servers' in body_json['requestUrl']:
            type = 'server'
            type_name = self.get_server_operation(body_json['requestUrl'], body_json['method'])
            get_type_id = re.findall(r'/v1/compute/servers/([0-9a-f-]{36})', body_json['requestUrl'])
            response_json = json.loads(body_json['responseBody'])
            status = "操作失败"
            if 'descr' in response_json.keys() and response_json['descr'] == "操作成功":
                status = "操作成功"
            try:
                if get_type_id == []:
                    if type_name == '创建云主机':
                        servers_data = response_json['data']
                        for server_data in servers_data:
                            type_id = server_data['id']
                            serializer = OperationLogSerializer(data=server_data)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(
                                name=type_name,
                                user_id=body_json['accountInfo']['id'],
                                user_name=body_json['accountInfo']['loginName'],
                                type=type,
                                type_id=type_id,
                                type_name=type_name,
                                status=status,
                                operation_ip=body_json['ip'],
                                operation_address=body_json['requestUrl'],
                            )
                        return None

                    if type_name == '删除云主机':
                        type_id = body_json['requestUrl'].split('/')[-1]
                        type_id = type_id.split('?')[1].split('=')[1].split('&')[0]
                        serializer = OperationLogSerializer(data=body_json)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(
                            name=type_name,
                            user_id=body_json['accountInfo']['id'],
                            user_name=body_json['accountInfo']['loginName'],
                            type=type,
                            type_id=type_id,
                            type_name=type_name,
                            status=status,
                            operation_ip=body_json['ip'],
                            operation_address=body_json['requestUrl'],
                        )
                        return None

                    if type_name == '重新命名' or type_name == '云主机添加网卡':
                        request_json = json.loads(body_json['requestBody'])
                        type_id = request_json['serverId']
                        serializer = OperationLogSerializer(data=request_json)
                        serializer.is_valid(raise_exception=True)
                        serializer.save(
                            name=type_name,
                            user_id=body_json['accountInfo']['id'],
                            user_name=body_json['accountInfo']['loginName'],
                            type=type,
                            type_id=type_id,
                            type_name=type_name,
                            status=status,
                            operation_ip=body_json['ip'],
                            operation_address=body_json['requestUrl'],
                        )
                        return None

                    if type_name == '关闭云主机' or type_name == '开启云主机':
                        request_json = json.loads(body_json['requestBody'])
                        servers_id = request_json['serverIds']
                        for server_id in servers_id:
                            type_id = server_id
                            serializer = OperationLogSerializer(data=server_id)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(
                                name=type_name,
                                user_id=body_json['accountInfo']['id'],
                                user_name=body_json['accountInfo']['loginName'],
                                type=type,
                                type_id=type_id,
                                type_name=type_name,
                                status=status,
                                operation_ip=body_json['ip'],
                                operation_address=body_json['requestUrl'],
                            )
                        return None

                    if type_name == '云主机挂载云硬盘':
                        request_json = json.loads(body_json['requestBody'])
                        servers = request_json
                        for server in servers:
                            type_id = server['server_id']
                            serializer = OperationLogSerializer(data=server)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(
                                name=type_name,
                                user_id=body_json['accountInfo']['id'],
                                user_name=body_json['accountInfo']['loginName'],
                                type=type,
                                type_id=type_id,
                                type_name=type_name,
                                status=status,
                                operation_ip=body_json['ip'],
                                operation_address=body_json['requestUrl'],
                            )
                        return None

                    if type_name == '云主机卸载网卡' or type_name == '云主机卸载云硬盘':
                        request_json = json.loads(body_json['requestBody'])
                        servers = request_json
                        for server in servers:
                            type_id = server['serverId']
                            serializer = OperationLogSerializer(data=server)
                            serializer.is_valid(raise_exception=True)
                            serializer.save(
                                name=type_name,
                                user_id=body_json['accountInfo']['id'],
                                user_name=body_json['accountInfo']['loginName'],
                                type=type,
                                type_id=type_id,
                                type_name=type_name,
                                status=status,
                                operation_ip=body_json['ip'],
                                operation_address=body_json['requestUrl'],
                            )
                        return None

                else:
                    type_id = get_type_id[0]
                    serializer = OperationLogSerializer(data=body_json)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(
                        name=type_name,
                        user_id=body_json['accountInfo']['id'],
                        user_name=body_json['accountInfo']['loginName'],
                        type=type,
                        type_id=type_id,
                        type_name=type_name,
                        status=status,
                        operation_ip=body_json['ip'],
                        operation_address=body_json['requestUrl'],
                    )
                    return None
            except BaseException:
                return BaseException


    def get_operation(self):
        channel = PikaMixin.get_conn()
        channel.queue_declare(queue='queue-2', durable=True)
        return channel

    def handle(self, *args, **kwargs):
        LOG.info("Server starting ...")
        channel = self.get_operation()
        channel.basic_consume('queue-2', self.callback)
        channel.start_consuming()

