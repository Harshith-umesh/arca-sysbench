#!/usr/bin/env python3

"""
Copyright 2022 Harshith Umesh

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import sys
import typing
from dataclasses import dataclass, field
from typing import List,Dict
from arcaflow_plugin_sdk import plugin,schema
import subprocess



@dataclass
class SysbenchInputParams:
    """
    This is the data structure for the input parameters of the step defined below.
    """
    operation: str = field(metadata={"name": "Operation", "description": "Sysbench Operation to perform"})
    threads: int = field(metadata={"name": "Threads", "description": "Number of threads"})

@dataclass
class LatencyAggregates:
    avg: float
    min: float
    max: float
    P95thpercentile: float
    sum: float

@dataclass
class ThreadFairnessAggregates:
  avg: float
  stddev: float

@dataclass
class ThreadsFairness:
  events: ThreadFairnessAggregates
  executiontime: ThreadFairnessAggregates

@dataclass
class CPUspeed:
    eventspersecond: float


@dataclass
class SysbenchMemoryOutputParams:
    """
    This is the data structure for output parameters returned by sysbench.
    """

    totaltime: float
    totalnumberofevents: float
    blocksize: str
    totalsize: str
    operation: str
    scope: str
    Totaloperationspersecond: float
    Totaloperations: float
    Numberofthreads: float = 1

@dataclass
class SysbenchCpuOutputParams:
    """
    This is the data structure for output parameters returned by sysbench.
    """

    totaltime: float
    totalnumberofevents: float
    Primenumberslimit: float
    Numberofthreads: float = 1


@dataclass
class SysbenchMemoryResultParams:
    """
    This is the output results data structure for the success case.
    """
    transferred_MiB: float
    transferred_MiBpersec: float
    Latency: LatencyAggregates
    Threadsfairness: ThreadsFairness

@dataclass
class SysbenchCpuResultParams:
    """
    This is the output results data structure for the success case.
    """
    CPUspeed: CPUspeed
    Latency: LatencyAggregates
    Threadsfairness: ThreadsFairness


@dataclass
class WorkloadResultsCpu:
    """
    This is the output results data structure for the success case.
    """
    sysbench_output_params: SysbenchCpuOutputParams
    sysbench_results: SysbenchCpuResultParams

@dataclass
class WorkloadResultsMemory:
    """
    This is the output results data structure for the success case.
    """
    sysbench_output_params: SysbenchMemoryOutputParams
    sysbench_results: SysbenchMemoryResultParams

@dataclass
class WorkloadError:
    """
    This is the output data structure in the error  case.
    """
    error: str

sysbench_input_schema = plugin.build_object_schema(SysbenchInputParams)
sysbench_cpu_output_schema = plugin.build_object_schema(SysbenchCpuOutputParams)
sysbench_cpu_results_schema = plugin.build_object_schema(SysbenchCpuResultParams)
sysbench_memory_output_schema = plugin.build_object_schema(SysbenchMemoryOutputParams)
sysbench_memory_results_schema = plugin.build_object_schema(SysbenchMemoryResultParams)


def parse_output(output):

    output = output.replace(" ", "")
    section = None
    sysbench_output = {}
    sysbench_results = {}
    for line in output.splitlines():

        if ":" in line:
            key, value = line.split(":")
            if key[0].isdigit():
                key="P"+key
            if value == "":
                key = re.sub(r'\((.*?)\)', "", key)
                if "options" in key or "General" in key:
                    dictionary = sysbench_output
                else:
                    dictionary = sysbench_results
                    section = key
                    dictionary[section] = {}
                continue

            if dictionary == sysbench_output:
                if "totaltime" in key:
                    value = value.replace("s", "")
                    dictionary[key] = float(value)
                elif "Totaloperations" in key:
                    to, tops = value.split("(")
                    tops = tops.replace("persecond)", "")
                    dictionary["Totaloperations"] = float(to)
                    dictionary["Totaloperationspersecond"] = float(tops)
                elif value.isnumeric():
                    dictionary[key] = float(value)
                else:
                    dictionary[key] = value

            else:
                if "latency" in key:
                    section = "Latency"
                if "(avg/stddev)" in key:
                    key = key.replace("(avg/stddev)", "")
                    avg, stddev = value.split("/")
                    dictionary[section][key] = {}
                    dictionary[section][key]["avg"] = float(avg)
                    dictionary[section][key]["stddev"] = float(stddev)
                elif value.isnumeric():
                    dictionary[section][key] = float(value)
                else:
                    dictionary[section][key] = value
        if "transferred" in line:
            mem_t, mem_tps = line.split("transferred")
            mem_tps = re.sub("[()]", "", mem_tps)
            mem_t = float(mem_t.replace("MiB", ""))
            mem_tps = float(mem_tps.replace("MiB/sec", ""))

            sysbench_results["transferred_MiB"] = mem_t
            sysbench_results["transferred_MiBpersec"] = mem_tps
    print("sysbench output : " , sysbench_output)
    print("sysbench results:", sysbench_results)
    return sysbench_output,sysbench_results

# The following is a decorator (starting with @). We add this in front of our function to define the metadata for our
# step.
@plugin.step(
    id="sysbenchcpu",
    name="Sysbench CPU Workload",
    description="Run CPU performance test using the sysbench workload",
    outputs={"success": WorkloadResultsCpu, "error": WorkloadError},
)
def RunSysbenchCpu(params: SysbenchInputParams) -> typing.Tuple[str, typing.Union[WorkloadResultsCpu, WorkloadError]]:
    """
    The function  is the implementation for the step. It needs the decorator above to make it into a  step. The type
    hints for the params are required.

    :param params:

    :return: the string identifying which output it is, as well the output structure
    """

    print("==>> Running sysbench CPU workload ...")
    try:
        process_out = subprocess.check_output(['sysbench','--threads'+'='+str(params.threads),params.operation,'run'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return "error", WorkloadError("{} failed with return code {}:\n{}".format(error.cmd[0],error.returncode,error.output))

    stdoutput = process_out.strip().decode("utf-8")
    output,results = parse_output(stdoutput)
    print(output,results)
    print("==>> Workload run complete!")
    return "success", WorkloadResultsCpu(sysbench_cpu_output_schema.unserialize(output),sysbench_cpu_results_schema.unserialize(results))


#The following is a decorator (starting with @). We add this in front of our function to define the metadata for our step.
@plugin.step(
    id="sysbenchmemory",
    name="Sysbench Memory Workload",
    description="Run the Memory functions speed test using the sysbench workload",
    outputs={"success": WorkloadResultsMemory, "error": WorkloadError},
)
def RunSysbenchMemory(params: SysbenchInputParams) -> typing.Tuple[str, typing.Union[WorkloadResultsMemory, WorkloadError]]:
    """
    The function  is the implementation for the step. It needs the decorator above to make it into a  step. The type
    hints for the params are required.

    :param params:

    :return: the string identifying which output it is, as well the output structure
    """

    print("==>> Running sysbench Memory workload ...")
    try:
        process_out = subprocess.check_output(['sysbench','--threads'+'='+str(params.threads),params.operation,'run'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        return "error", WorkloadError("{} failed with return code {}:\n{}".format(error.cmd[0],error.returncode,error.output))

    stdoutput = process_out.strip().decode("utf-8")
    output,results = parse_output(stdoutput)
    print("==>> Workload run complete!")
    return "success", WorkloadResultsMemory(sysbench_memory_output_schema.unserialize(output),sysbench_memory_results_schema.unserialize(results))



if __name__ == "__main__":
    sys.exit(plugin.run(plugin.build_schema(
        # List your step functions here:
        RunSysbenchCpu,
        RunSysbenchMemory
    )))
