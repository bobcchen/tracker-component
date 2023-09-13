FROM python:3.8

WORKDIR /app
COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt

# install DeepSORT
RUN cd deep_sort_realtime && \
    pip3 install --no-cache-dir -e .

WORKDIR /app/component
CMD ["python3", "server.py"]
