from libs.webserver.executer_base import ExecuterBase

from flask import __version__ as flask_version
from icmplib import ping
import subprocess
import platform
import psutil
import re


__version__ = "2.3 Dev"


class BuildServiceInfo():
    """Clean way to assign system service information."""
    def __init__(self, name, status=9999, running=False, not_found=True):
        self.name = name
        self.status = status
        self.running = running
        self.not_found = not_found

    def update(self, **kwargs):
        self.__dict__.update(kwargs)

    def as_dict(self):
        return self.__dict__


class SystemInfoExecuter(ExecuterBase):

    def get_system_info_performance(self):
        data = dict()
        data["cpu_info"] = self.get_cpu_info()
        data["memory_info"] = self.get_memory_info()
        data["disk_info"] = self.get_disk_info()
        data["network_info"] = self.get_network_info()
        return data

    def get_cpu_info(self):
        cpu_info = dict()
        cpu_freq = dict(psutil.cpu_freq()._asdict())
        cpu_usage = psutil.cpu_times_percent(0.0)._asdict()
        cpu_percent = float(f'{(cpu_usage["system"] + cpu_usage["user"]):0.1f}')
        cpu_info["frequency"] = cpu_freq["current"]
        cpu_info["percent"] = cpu_percent
        return cpu_info

    def get_memory_info(self):
        return dict(psutil.virtual_memory()._asdict())

    def get_disk_info(self):
        return dict(psutil.disk_usage('/')._asdict())

    def get_network_info(self):
        network_info = []
        all_network_info = psutil.net_if_addrs()
        for current_nic in all_network_info:
            for current_address_family in all_network_info[current_nic]:
                if current_address_family.family == 2:
                    nic = dict()
                    io_counters = dict(psutil.net_io_counters(pernic=True)[current_nic]._asdict())
                    nic["name"] = current_nic
                    nic["address"] = current_address_family.address
                    nic["netmask"] = current_address_family.netmask
                    nic["bytes_recv"] = io_counters["bytes_recv"]
                    nic["bytes_sent"] = io_counters["bytes_sent"]
                    network_info.append(nic)
        return network_info

    def get_system_info_temperature(self):
        data = dict()
        data["raspi"] = self.get_raspi_temp()
        return data

    def get_raspi_temp(self):
        cpu_temp_dict = dict()
        if platform.system().lower() == "linux":
            temp = subprocess.check_output(["/usr/bin/vcgencmd", "measure_temp"], stderr=subprocess.STDOUT)
            cpu_temp_c = float(re.findall(r"\d+\.\d+", temp.decode('utf-8'))[0])
            cpu_temp_f = float(f"{(cpu_temp_c * 1.8 + 32):0.1f}")
            cpu_temp_dict["celsius"] = cpu_temp_c
            cpu_temp_dict["fahrenheit"] = cpu_temp_f
            return cpu_temp_dict
        cpu_temp_dict["celsius"] = 0
        cpu_temp_dict["fahrenheit"] = 0
        return cpu_temp_dict

    def get_services(self):
        services = ["mlsc", "hostapd", "dhcpcd", "dnsmasq"]
        return services

    def get_system_info_services(self):
        data = []
        for service in self.get_services():
            data.append(self.get_service_status(service))
        return data

    def get_service_status(self, service_name):
        service_info = BuildServiceInfo(service_name)
        if platform.system().lower() == "linux":
            try:
                # If service is running (0), it should return b'', else caught as exception.
                subprocess.check_output(f"systemctl status {service_name} >/dev/null 2>&1", shell=True)
                service_info.update(status=0, running=True, not_found=False)
            except subprocess.CalledProcessError as grepexc:
                # Catch error code if service is stopped (3), or not found (4).
                service_info.update(status=grepexc.returncode)
                if grepexc.returncode == 3:
                    service_info.update(not_found=False)
                elif grepexc.returncode == 4:
                    service_info.update(not_found=True)
                service_info.update(running=False)
            except Exception:
                self.logger.debug(f"Could not get service status: {service_name}")
        else:
            service_info.update(status=3, running=False, not_found=True)
        return service_info.as_dict()

    def get_system_info_device_status(self):
        devices = []
        for current_device_key in self._config["device_configs"]:
            current_device = dict()
            current_device_config = self._config["device_configs"][current_device_key]

            current_device["name"] = current_device_config["device_name"]
            current_device["id"] = current_device_key
            try:
                if current_device_config["output_type"] == "output_udp":
                    current_device["connected"] = self.check_device_status(current_device_config["output"]["output_udp"]["udp_client_ip"])
                else:
                    current_device["connected"] = True
            except Exception:
                self.logger.exception(f"Could not get device status of: {current_device['name']} - {current_device['id']}")
                current_device["connected"] = False

            devices.append(current_device)
        return devices

    def check_device_status(self, address):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """
        host = ping(address, count=1, interval=0.2)
        return host.is_alive

    def get_system_version(self):
        versions = [
            {
                "name": "mlsc",
                "version": __version__
            },
            {
                "name": "python",
                "version": platform.python_version()
            },
            {
                "name": "flask",
                "version": flask_version
            }
        ]

        return versions
