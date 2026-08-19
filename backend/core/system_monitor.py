"""
JARVIS 4.0 - SYSTEM MONITOR

Real Windows system metrics:
- CPU
- RAM
- Disk
- Battery
- Network
- OS
- CPU cores
- Uptime
"""

import os
import platform
import time

import psutil


# =========================================================
# START TIME
# =========================================================

START_TIME = time.time()


# =========================================================
# NETWORK BASELINE
# =========================================================

try:

    _NETWORK_START = psutil.net_io_counters()

    NETWORK_START_SENT = (
        _NETWORK_START.bytes_sent
    )

    NETWORK_START_RECEIVED = (
        _NETWORK_START.bytes_recv
    )

except Exception:

    NETWORK_START_SENT = 0

    NETWORK_START_RECEIVED = 0


# =========================================================
# FORMAT BYTES
# =========================================================

def format_bytes(value: int) -> str:

    try:

        value = float(
            value or 0
        )

    except Exception:

        value = 0.0


    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ]


    index = 0


    while (
        value >= 1024
        and index < len(units) - 1
    ):

        value /= 1024

        index += 1


    if index == 0:

        return f"{int(value)} {units[index]}"


    return (
        f"{value:.2f} {units[index]}"
    )


# =========================================================
# FORMAT UPTIME
# =========================================================

def format_uptime(
    seconds: int
) -> str:

    try:

        seconds = int(
            seconds
        )

    except Exception:

        seconds = 0


    seconds = max(
        seconds,
        0
    )


    days = (
        seconds // 86400
    )

    seconds %= 86400


    hours = (
        seconds // 3600
    )

    seconds %= 3600


    minutes = (
        seconds // 60
    )


    seconds %= 60


    if days:

        return (
            f"{days}d "
            f"{hours}h "
            f"{minutes}m"
        )


    if hours:

        return (
            f"{hours}h "
            f"{minutes}m"
        )


    if minutes:

        return (
            f"{minutes}m "
            f"{seconds}s"
        )


    return f"{seconds}s"


# =========================================================
# BATTERY
# =========================================================

def get_battery():

    try:

        battery = (
            psutil.sensors_battery()
        )


        if battery is None:

            return {

                "available":
                    False,

                "percent":
                    None,

                "charging":
                    None,

                "seconds_left":
                    None,

            }


        seconds_left = (
            battery.secsleft
        )


        if seconds_left in (
            psutil.POWER_TIME_UNLIMITED,
            psutil.POWER_TIME_UNKNOWN,
        ):

            seconds_left = None


        return {

            "available":
                True,

            "percent":
                round(
                    float(
                        battery.percent
                    ),
                    1
                ),

            "charging":
                bool(
                    battery.power_plugged
                ),

            "seconds_left":
                (
                    int(
                        seconds_left
                    )
                    if seconds_left is not None
                    else None
                ),

        }


    except Exception as error:

        print(
            "[SYSTEM BATTERY ERROR]:",
            repr(error)
        )


        return {

            "available":
                False,

            "percent":
                None,

            "charging":
                None,

            "seconds_left":
                None,

        }


# =========================================================
# NETWORK
# =========================================================

def get_network():

    try:

        counters = (
            psutil.net_io_counters()
        )


        if counters is None:

            return {

                "available":
                    False,

                "bytes_sent":
                    0,

                "bytes_received":
                    0,

                "sent":
                    "0 B",

                "received":
                    "0 B",

            }


        current_sent = (
            counters.bytes_sent
        )

        current_received = (
            counters.bytes_recv
        )


        sent_delta = max(
            current_sent
            -
            NETWORK_START_SENT,
            0
        )


        received_delta = max(
            current_received
            -
            NETWORK_START_RECEIVED,
            0
        )


        return {

            "available":
                True,

            "bytes_sent":
                current_sent,

            "bytes_received":
                current_received,

            "sent":
                format_bytes(
                    sent_delta
                ),

            "received":
                format_bytes(
                    received_delta
                ),

        }


    except Exception as error:

        print(
            "[SYSTEM NETWORK ERROR]:",
            repr(error)
        )


        return {

            "available":
                False,

            "bytes_sent":
                0,

            "bytes_received":
                0,

            "sent":
                "0 B",

            "received":
                "0 B",

        }


# =========================================================
# SYSTEM SNAPSHOT
# =========================================================

def get_system_stats():

    try:

        cpu = psutil.cpu_percent(
            interval=0.2
        )


        memory = (
            psutil.virtual_memory()
        )


        disk = psutil.disk_usage(
            os.path.abspath(
                os.sep
            )
        )


        battery = (
            get_battery()
        )


        network = (
            get_network()
        )


        uptime_seconds = int(
            time.time()
            -
            START_TIME
        )


        return {

            "success":
                True,

            "timestamp":
                time.time(),

            "cpu":
                round(
                    float(cpu),
                    1
                ),

            "ram":
                round(
                    float(
                        memory.percent
                    ),
                    1
                ),

            "ram_used_gb":
                round(
                    memory.used
                    /
                    (1024 ** 3),
                    2
                ),

            "ram_total_gb":
                round(
                    memory.total
                    /
                    (1024 ** 3),
                    2
                ),

            "disk":
                round(
                    float(
                        disk.percent
                    ),
                    1
                ),

            "disk_used_gb":
                round(
                    disk.used
                    /
                    (1024 ** 3),
                    2
                ),

            "disk_total_gb":
                round(
                    disk.total
                    /
                    (1024 ** 3),
                    2
                ),

            "battery":
                battery,

            "network":
                network,

            "uptime":
                uptime_seconds,

            "uptime_text":
                format_uptime(
                    uptime_seconds
                ),

            "os":
                platform.system(),

            "os_release":
                platform.release(),

            "platform":
                platform.platform(),

            "processor":
                platform.processor(),

            "cpu_cores":
                psutil.cpu_count(
                    logical=True
                ),

            "physical_cores":
                psutil.cpu_count(
                    logical=False
                ),

        }


    except Exception as error:

        print(
            "[SYSTEM MONITOR ERROR]:",
            repr(error)
        )


        return {

            "success":
                False,

            "error":
                repr(error),

        }


# =========================================================
# SIMPLE STATUS
# =========================================================

def get_system_status():

    data = get_system_stats()


    if not data.get(
        "success",
        False
    ):

        return {

            "success":
                False,

            "online":
                False,

            "error":
                data.get(
                    "error"
                ),

        }


    return {

        "success":
            True,

        "online":
            True,

        "cpu":
            data.get(
                "cpu",
                0
            ),

        "ram":
            data.get(
                "ram",
                0
            ),

        "disk":
            data.get(
                "disk",
                0
            ),

        "battery":
            data.get(
                "battery"
            ),

        "network":
            data.get(
                "network"
            ),

        "uptime":
            data.get(
                "uptime"
            ),

        "uptime_text":
            data.get(
                "uptime_text",
                "0s"
            ),

    }


__all__ = [

    "get_system_stats",

    "get_system_status",

    "format_bytes",

    "format_uptime",

]