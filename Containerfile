# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-2.0-or-later

ARG IMAGE=registry.fedoraproject.org/fedora:latest

FROM ${IMAGE} as builder

RUN python3 -m venv --system-site-packages /opt/fedrq

COPY . /usr/src/fedrq

RUN /opt/fedrq/bin/pip install --verbose /usr/src/fedrq tomli_w


FROM ${IMAGE} as final

COPY contrib/container/rhel.toml /etc/fedrq/rhel.toml

COPY --from=builder /opt/fedrq /opt/fedrq

COPY contrib/container/000-container.toml /etc/fedrq/000-container.toml

ENV PATH="/opt/fedrq/bin:${PATH}"

RUN fedrq check-config

ENV XDG_CACHE_HOME=/fedrq-cache
ENTRYPOINT ["/opt/fedrq/bin/fedrq"]
CMD ["--help"]
VOLUME /fedrq-cache
