# docker build -t detrack --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) .

FROM nvcr.io/nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04

ENV cwd="/home/"
WORKDIR $cwd

RUN apt-get -y update
# RUN apt-get -y upgrade
RUN apt -y update

RUN apt-get install -y \
    software-properties-common \
    build-essential \
    checkinstall \
    cmake \
    pkg-config \
    yasm \
    git \
    vim \
    curl \
    wget \
    gfortran \
    libjpeg8-dev \
    libpng-dev \
    libtiff5-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libdc1394-22-dev \
    libxine2-dev \
    sudo \
    apt-transport-https \
    libcanberra-gtk-module \
    libcanberra-gtk3-module \
    dbus-x11 \
    vlc \
    iputils-ping \
    python3-dev \
    python3-pip

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata python3-tk

RUN apt-get clean && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && apt-get -y autoremove

RUN rm -rf /var/cache/apt/archives/

### APT END ###

ENV TZ=Asia/Singapore
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN python3 -m pip install --no-cache-dir --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install --no-cache-dir gdown

# install DeepSORT
RUN cd / && \
    git clone https://github.com/levan92/deep_sort_realtime && \
    cd deep_sort_realtime && \
    git checkout 012ec4951580bbf844b5cd4536fe57128ed89b64 && \
    cd deep_sort_realtime/embedder/weights && \
    bash download_tf_wts.sh && \
    cd ../../.. && \
    pip3 install --no-cache-dir -e .

WORKDIR /app/component
CMD ["python3", "server.py"]
