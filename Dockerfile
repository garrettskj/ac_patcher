FROM ubuntu:18.04

ENV SYSTEMD_IGNORE_CHROOT=yes
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
	radare2 \
	curl \
	python3-pip \
	python3-setuptools \
	python3-wheel \
	systemd \
    && apt-get clean

RUN pip3 install r2pipe

WORKDIR /srv
