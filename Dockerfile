FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55

ENV SYSTEMD_IGNORE_CHROOT=yes \
    DEBIAN_FRONTEND=noninteractive

ARG RADARE2_VERSION=6.2.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        python3 \
        python3-pip \
        systemd \
    && curl -fsSL -o /tmp/radare2.deb \
        "https://github.com/radareorg/radare2/releases/download/${RADARE2_VERSION}/radare2_${RADARE2_VERSION}_amd64.deb" \
    && apt-get install -y --no-install-recommends /tmp/radare2.deb \
    && rm -f /tmp/radare2.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ubuntu 24.04's system Python is PEP 668 "externally managed"; this
# container is single-purpose, so --break-system-packages is fine here.
RUN pip3 install --no-cache-dir --break-system-packages r2pipe

WORKDIR /srv
