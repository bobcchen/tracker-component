FROM python:3.8

WORKDIR /app
COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt

# install DeepSORT
RUN cd / && \
    git clone https://github.com/levan92/deep_sort_realtime && \
    cd deep_sort_realtime && \
    git checkout 012ec4951580bbf844b5cd4536fe57128ed89b64 && \
    pip3 install --no-cache-dir -e .

WORKDIR /app/component
CMD ["python3", "server.py"]
