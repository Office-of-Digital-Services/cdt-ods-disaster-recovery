# declare default build args for later stages
ARG PYTHON_VERSION=3.12 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=cdt \
    USER_UID=1000 \
    USER_GID=1000

# multi-stage build
#
# stage 1: builds the web package from source
#          using the git metadata for version info
FROM python:${PYTHON_VERSION} AS build_wheel

# renew top-level args in this stage
ARG PYTHON_VERSION \
    PYTHONDONTWRITEBYTECODE \
    PYTHONUNBUFFERED \
    USER \
    USER_UID \
    USER_GID

# set env vars for the user, including HOME
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED} \
    PYTHONDONTWRITEBYTECODE=${PYTHONDONTWRITEBYTECODE} \
    HOME=/home/${USER} \
    USER=${USER} \
    PATH="/home/${USER}/.local/bin:$PATH" \
    # update env for local pip installs
    # see https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUSERBASE
    # since all `pip install` commands are in the context of $USER
    # $PYTHONUSERBASE is the location used by default
    PYTHONUSERBASE="/home/${USER}/.local" \
    # where to store the pip cache (use the default)
    # https://pip.pypa.io/en/stable/cli/pip/#cmdoption-cache-dir
    PIP_CACHE_DIR="/home/${USER}/.cache/pip"

# Create the user, their home directory, .cache/pip, and /build directory.
# Set ownership before switching user. This runs as root.
USER root
RUN groupadd --gid ${USER_GID} ${USER} 2>/dev/null || true && \
    useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USER} && \
    # pip cache dir must be created and owned by the user to work with BuildKit cache
    mkdir -p ${PIP_CACHE_DIR} && \
    # own the parent directory of PIP_CACHE_DIR
    chown -R ${USER}:${USER} /home/${USER}/.cache && \
    mkdir /build && \
    chown ${USER}:${USER} /build

# switch to non-root user
USER $USER
WORKDIR /build
# upgrade pip and install the 'build' package as user
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    python -m pip install --user --upgrade pip && \
    pip install --user build

# copy all source files; changes here will invalidate subsequent Docker layers
COPY . .
RUN git config --global --add safe.directory /build

# build the wheel, using the pip cache for any build-time dependencies
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    python -m build

# multi-stage build
#
# stage 2: installs the web package in a fresh base container
#          using the pre-built package, and copying only needed source
FROM python:${PYTHON_VERSION} AS app_container

# renew top-level args in this stage
ARG PYTHON_VERSION \
    PYTHONDONTWRITEBYTECODE \
    PYTHONUNBUFFERED \
    USER \
    USER_UID \
    USER_GID

# set env vars from args so they persist into running containers
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED} \
    PYTHONDONTWRITEBYTECODE=${PYTHONDONTWRITEBYTECODE} \
    HOME=/home/${USER} \
    USER=${USER} \
    USER_UID=${USER_UID} \
    USER_GID=${USER_GID} \
    PATH="/home/${USER}/.local/bin:$PATH" \
    # update env for local pip installs
    # see https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUSERBASE
    # since all `pip install` commands are in the context of $USER
    # $PYTHONUSERBASE is the location used by default
    PYTHONUSERBASE="/home/${USER}/.local" \
    # where to store the pip cache (use the default)
    # https://pip.pypa.io/en/stable/cli/pip/#cmdoption-cache-dir
    PIP_CACHE_DIR="/home/${USER}/.cache/pip" \
    RUNTIME_DIR="/${USER}/app"

ENV POSTGRES_SSLROOTCERT_PATH="${RUNTIME_DIR}/certs/azure_postgres_ca_bundle.pem"

EXPOSE 8000

USER root

# install apt packages using the archives and lists cache
RUN --mount=type=cache,id=apt-archives,sharing=locked,target=/var/cache/apt/archives \
    --mount=type=cache,id=apt-lists,sharing=locked,target=/var/lib/apt/lists \
    # (re)create non-root $USER and home directory (since it isn't copied from previous stage)
    groupadd --gid ${USER_GID} ${USER} 2>/dev/null || true && \
    useradd --uid ${USER_UID} --gid ${USER_GID} --create-home --shell /bin/bash ${USER} && \
    # pip cache dir must be created and owned by the user to work with BuildKit cache
    mkdir -p ${PIP_CACHE_DIR} && \
    # own the PIP_CACHE_DIR parent .cache dir
    chown -R ${USER}:${USER} /home/${USER}/.cache && \
    # setup $USER permissions for nginx
    mkdir -p /var/cache/nginx && \
    chown -R $USER:$USER /var/cache/nginx && \
    mkdir -p /var/lib/nginx && \
    chown -R $USER:$USER /var/lib/nginx && \
    mkdir -p /var/log/nginx && \
    chown -R $USER:$USER /var/log/nginx && \
    touch /var/log/nginx/error.log && \
    chown $USER:$USER /var/log/nginx/error.log && \
    touch /var/run/nginx.pid && \
    chown -R $USER:$USER /var/run/nginx.pid && \
    # setup directories and permissions for gunicorn, (eventual) app
    mkdir -p /$USER/app && \
    mkdir -p /$USER/run && \
    chown -R $USER:$USER /$USER && \
    # install server components
    apt-get update && \
    apt-get install -y --no-install-recommends build-essential nginx gettext && \
    # this cleanup is still important for the final image layer size
    # remove lists from the image layer, but they remain in the BuildKit cache mount
    rm -rf /var/lib/apt/lists/*

# enter source directory
WORKDIR /$USER

# copy mostly static files
COPY LICENSE app/LICENSE
COPY manage.py app/manage.py
COPY appcontainer/gunicorn.conf.py run/gunicorn.conf.py
# overwrite default nginx.conf
COPY appcontainer/nginx.conf /etc/nginx/nginx.conf
# copy certs for PostgreSQL verify-full
COPY appcontainer/certs/azure_postgres_ca_bundle.pem "${POSTGRES_SSLROOTCERT_PATH}"
# copy the wheel built in the previous stage
COPY --from=build_wheel /build/dist /build/dist

# switch to non-root $USER
USER $USER
WORKDIR ${RUNTIME_DIR}

# env var needed for gunicorn
ENV GUNICORN_CONF="/$USER/run/gunicorn.conf.py"

# copy runtime files
COPY bin bin
COPY web/static web/static

# install the locally built wheel and its dependencies using the pip cache
# setting uid,gid here is critical, as otherwise the Buildkit cache is mounted as root
# even though we are running in the context of non-root $USER
RUN --mount=type=cache,id=pipcache,target=${PIP_CACHE_DIR},uid=${USER_UID},gid=${USER_GID} \
    python -m pip install --user --upgrade pip && \
    pip install --user $(find /build/dist -name "cdt_disaster_recovery*.whl")

# configure container executable
ENTRYPOINT ["/bin/bash"]
CMD ["bin/start.sh"]
