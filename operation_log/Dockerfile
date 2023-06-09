# usage: docker build -t cmp-iaas:IMAGE_VERSION .
FROM registry-itwork.yonghui.cn/library/python:3.9-slim
MAINTAINER YH
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV TZ Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone
RUN sed -i -e 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
RUN chmod 777 /tmp/ && apt update && apt install -y locales tzdata
RUN dpkg-reconfigure -f noninteractive tzdata
RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.UTF-8

RUN apt install -y \
        gcc \
        libglib2.0-0 \
        libpq-dev \
        net-tools \
        vim
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U -i https://mirrors.aliyun.com/pypi/simple/ pip
RUN pip3 install -U -i https://mirrors.aliyun.com/pypi/simple/ -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt \
    && useradd -U app_user \
    && install -d -m 0755 -o app_user -g app_user /app/static


WORKDIR /app

COPY . .
RUN chmod +x docker/*.sh
ENTRYPOINT [ "docker/entrypoint.sh" ]

CMD ["docker/start.sh"]
