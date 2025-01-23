FROM python:slim

# keep python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# turn off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# install poetry
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update                                                            \
 && apt-get install --yes --no-install-recommends curl cron postgresql-client \
 && curl -sSL https://install.python-poetry.org/ | python3 -                  \
 && apt-get purge --yes curl                                                  \
 && apt-get autoremove --yes                                                  \
 && apt-get clean                                                             \
 && rm --force --recursive /var/lib/apt/lists/*

ENV PATH="${PATH}:/root/.local/bin"

# copying source
WORKDIR /usr/src/app
COPY . .

RUN poetry config virtualenvs.create false                  \
 && poetry install --no-interaction --no-ansi --without dev

ENTRYPOINT [ "/usr/src/app/bin/entrypoint.sh" ]
