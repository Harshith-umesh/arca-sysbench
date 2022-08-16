FROM quay.io/centos/centos:stream8

RUN dnf -y module install python39 && dnf -y install python39 python39-pip 
RUN curl -s https://packagecloud.io/install/repositories/akopytov/sysbench/script.rpm.sh | bash
RUN dnf -y install sysbench
RUN mkdir /app
ADD sysbench_plugin.py /app
ADD test_sysbench_plugin.py /app
ADD requirements.txt /app
ADD tests /app/tests/
ADD configs /app/configs/
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN python3.9 test_sysbench_plugin.py

ENTRYPOINT ["python3.9", "/app/sysbench_plugin.py"]
CMD ["-f", "configs/sysbench_cpu_example.yaml", "-s", "sysbenchcpu"]

LABEL org.opencontainers.image.title="Sysbench Arcalot Plugin"