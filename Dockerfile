FROM python:3.9

RUN mkdir /app
ADD sysbench_plugin.py /app
ADD test_sysbench_plugin.py /app
ADD requirements.txt /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN /usr/local/bin/python3 test_sysbench_plugin.py

VOLUME /config

ENTRYPOINT ["/usr/local/bin/python3", "/app/sysbench_plugin.py"]
CMD ["-f", "/config/sysbench_cpu_example.yaml", "-s", "sysbenchcpu"]
