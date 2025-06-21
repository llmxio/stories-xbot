ARG BASE_IMAGE_NAME=fedora
ARG BASE_IMAGE_TAG=42

FROM ${BASE_IMAGE_NAME}:${BASE_IMAGE_TAG}

ARG USER_NAME=rs
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG CLANG_VERSION=20

# Set up locales (en_US and ru_RU)
RUN dnf install -y glibc-langpack-en glibc-langpack-ru glibc-locale-source && \
    mkdir -p /usr/lib/locale && \
    localedef --charmap=UTF-8 --inputfile=en_US -f UTF-8 en_US.UTF-8 || true && \
    localedef --charmap=UTF-8 --inputfile=ru_RU -f UTF-8 ru_RU.UTF-8 || true

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8 \
    TZ=Asia/Dubai

# Install dev tools and Python versions
RUN dnf install -y \
    sudo \
    bash-completion \
    git \
    vim \
    openssh-clients \
    pkgconf-pkg-config \
    gdb \
    gcc \
    gcc-c++ \
    make \
    cmake \
    ninja-build \
    doxygen \
    ccache \
    bzip2 \
    flex \
    python3-pip \
    python3-devel \
    uv \
    python3.10 python3.10-devel \
    python3.11 python3.11-devel \
    python3.12 python3.12-devel \
    python3.13 python3.13-devel \
    clang clang-tools-extra clang-devel \
    clang-libs clang-analyzer clang-resource-filesystem \
    clangd clang-tidy clang-format \
    libcxx libcxx-devel libcxxabi libcxxabi-devel \
    lldb lld llvm llvm-devel \
    libomp && \
    dnf clean all && rm -rf /var/cache/dnf

# Add non-root user
RUN groupadd --gid ${USER_GID} ${USER_NAME} && \
    useradd --uid ${USER_UID} --gid ${USER_NAME} -m -G wheel -s /bin/bash ${USER_NAME} && \
    su -l ${USER_NAME} -c 'mkdir -p $HOME/.cache' && \
    echo "${USER_NAME} ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER_NAME}  && \
    chmod 0440 /etc/sudoers.d/${USER_NAME} && mkdir /workspace && chown -R ${USER_NAME}:${USER_NAME} /workspace && \
    chmod 755 /workspace

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

CMD ["/bin/bash"]
