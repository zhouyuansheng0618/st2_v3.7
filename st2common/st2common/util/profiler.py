# Copyright 2020 The StackStorm Authors.
# Copyright 2019 Extreme Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import atexit
import platform
import cProfile

import eventlet
from eventlet.green import profile

__all__ = ["setup_regular_profiler", "setup_eventlet_profiler"]


def setup_regular_profiler(service_name: str) -> None:
    """
    Set up regular Python cProf profiler and write result to a file on exit.
    """
    profiler = cProfile.Profile()
    profiler.enable()

    file_path = os.path.join(
        "/tmp", "%s-%s-%s.cprof" % (service_name, platform.machine(), int(time.time()))
    )

    print("Eventlet profiler enabled")
    print("Profiling data will be saved to %s on exit" % (file_path))

    def stop_profiler():
        profiler.disable()
        profiler.dump_stats(file_path)
        print("Profiling data written to %s" % (file_path))
        print("You can view it using: ")
        print("\t python3 -m pstats %s" % (file_path))

    atexit.register(stop_profiler)


def setup_eventlet_profiler(service_name: str) -> None:
    """
    Set up eventlet profiler and write results to a file on exit.

    Only to be used with eventlet code (aka an StackStorm service minus the CLI).
    """
    is_patched = eventlet.patcher.is_monkey_patched("os")
    if not is_patched:
        raise ValueError(
            "No eventlet monkey patching detected. Code may not be using eventlet"
        )

    profiler = profile.Profile()
    profiler.start()

    file_path = os.path.join(
        "/tmp", "%s-%s-%s.cprof" % (service_name, platform.machine(), int(time.time()))
    )

    print("Eventlet profiler enabled")
    print("Profiling data will be saved to %s on exit" % (file_path))

    def stop_profiler():
        profiler.stop()
        profiler.dump_stats(file_path)
        print("Profiling data written to %s" % (file_path))
        print("You can view it using: ")
        print("\t python3 -m pstats %s" % (file_path))

    atexit.register(stop_profiler)
