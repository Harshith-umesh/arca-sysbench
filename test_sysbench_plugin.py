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
import unittest
import sysbench_plugin
from arcaflow_plugin_sdk import plugin


class SysbenchPluginTest(unittest.TestCase):
    @staticmethod
    def test_serialization():
        plugin.test_object_serialization(
            sysbench_plugin.SysbenchInputParams(
                operation="cpu",
                threads=2
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_cpu_output_schema.unserialize(
                {'Numberofthreads': 2.0, 'Primenumberslimit': 10000.0, 'totaltime': 10.0008, 'totalnumberofevents': 26401.0}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_cpu_results_schema.unserialize(
                {'CPUspeed': {'eventspersecond': '2639.51'}, 'Latency': {'min': '0.67', 'avg': '0.76', 'max': '1.26', 'P95thpercentile': '0.87', 'sum': '19987.57'}, 'Threadsfairness': {'events': {'avg': 13200.5, 'stddev': 17.5}, 'executiontime': {'avg': 9.9938, 'stddev': 0.0}}}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.SysbenchInputParams(
                operation="memory",
                threads=3
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_memory_output_schema.unserialize(
                {'Numberofthreads': 2.0, 'blocksize': '1KiB', 'totalsize': '102400MiB', 'operation': 'write', 'scope': 'global', 'Totaloperations': 72227995.0, 'Totaloperationspersecond': 7221925.38, 'totaltime': 10.0001, 'totalnumberofevents': 72227995.0}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.sysbench_memory_results_schema.unserialize(
                {'transferred_MiB': 70535.15, 'transferred_MiBpersec': 7052.66, 'Latency': {'min': '0.00', 'avg': '0.00', 'max': '1.18', 'P95thpercentile': '0.00', 'sum': '13699.95'}, 'Threadsfairness': {'events': {'avg': 36113997.5, 'stddev': 710393.5}, 'executiontime': {'avg': 6.85, 'stddev': 0.07}}}
            )
        )

        plugin.test_object_serialization(
            sysbench_plugin.WorkloadError(
                error="This is an error"
            )
        )

    def test_functional_cpu(self):
        input = sysbench_plugin.SysbenchInputParams(
            operation="cpu",
            threads=2
        )

        output_id, output_data = sysbench_plugin.RunSysbenchCpu(input)

        self.assertEqual("success", output_id)
        self.assertGreaterEqual(output_data.sysbench_output_params.Numberofthreads,1)
        self.assertGreater(output_data.sysbench_output_params.totaltime,0)
        self.assertGreater(output_data.sysbench_output_params.totalnumberofevents,0)
        self.assertGreater(output_data.sysbench_results.CPUspeed.eventspersecond,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.avg,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.sum,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.events.avg,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.executiontime.avg,0)
        

    def test_functional_memory(self):
        input = sysbench_plugin.SysbenchInputParams(
            operation="memory",
            threads=2
        )

        output_id, output_data = sysbench_plugin.RunSysbenchMemory(input)

        self.assertEqual("success", output_id)
        self.assertGreaterEqual(output_data.sysbench_output_params.Numberofthreads,1)
        self.assertGreater(output_data.sysbench_output_params.totaltime,0)
        self.assertGreater(output_data.sysbench_output_params.Totaloperations,0)
        self.assertIsNotNone(output_data.sysbench_output_params.blocksize)
        self.assertIsNotNone(output_data.sysbench_output_params.operation)
        self.assertGreater(output_data.sysbench_results.transferred_MiB,0)
        self.assertGreater(output_data.sysbench_results.transferred_MiBpersec,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.avg,0)
        self.assertGreaterEqual(output_data.sysbench_results.Latency.sum,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.events.avg,0)
        self.assertGreater(output_data.sysbench_results.Threadsfairness.executiontime.avg,0)


if __name__ == '__main__':
    unittest.main()
