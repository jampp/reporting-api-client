FROM python:3.7

ENV USER=reporting-api-user
ENV REPO_NAME=reporting-api-client
ENV PREFIX=/opt
ENV REPO_PREFIX=$PREFIX/$REPO_NAME

RUN mkdir -p $REPO_PREFIX \
  && adduser \
    --quiet \
    --gecos "" \
    --home /home/$USER \
    --disabled-login $USER \
  && chown -R $USER: $REPO_PREFIX

RUN apt-get update && apt-get install -y python3-enchant

# Make installs first to avoid having to reinstall stuff without dependency changes.
COPY requirements-dev.txt $REPO_PREFIX
COPY requirements-doc.txt $REPO_PREFIX
RUN pip install -r $REPO_PREFIX/requirements-dev.txt -r $REPO_PREFIX/requirements-doc.txt

# Copy whole repo and install it.
COPY . $REPO_PREFIX
WORKDIR $REPO_PREFIX
RUN pip install -e $REPO_PREFIX

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chown -R $USER: $REPO_PREFIX

USER $USER

ENTRYPOINT [ "/entrypoint.sh" ]
