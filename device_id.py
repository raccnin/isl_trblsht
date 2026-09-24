from enum import StrEnum
import json
from dataclasses import dataclass, asdict
from netmiko.ssh_autodetect import SSHDetect


class Vendor(StrEnum):
    EDGECORE = "edgecore_sonic"
    JUNIPER = "juniper_junos"
    NOKIASRL = "nokia_srl"
    NOKIASROS = "nokia_sros"
    AUTO = "autodetect"


@dataclass
class NetworkDevice:
    name: str
    vendor: Vendor

    def to_netmiko(self, ssh_user, secret):
        return {
                'device_type': str(self.vendor),
                'host': self.name,
                'username': ssh_user,
                'password': secret
                }


def write_device(device, filepath):
    with open(filepath, 'a') as file:
        file.write(f"{json.dumps(asdict(device))}\n")


def get_device(device_name, file_path):
    # scan file for device name(s)
    # - stack of device names, popping once found
    # - would rather index by IP, could perform binary
    #   search on sorted 32 bit reps
    # identify device if in datafile
    with open(file_path, 'r') as file:
        for line in file:
            if line.find(device_name) != -1:
                device_json = json.loads(line)
                return NetworkDevice(**device_json)
    raise LookupError(f"get_device: could not locate device {device_name} in {file_path}")


def id_device(device_name, user, secret):
    # - get vendor from SSHDetect
    netmiko_device = {
                    'device_type': 'autodetect',
                    'host': device_name,
                    'username': user,
                    'password': secret
                    }
    print("attempting to guess vendor via SSH...")
    guesser = SSHDetect(**netmiko_device)
    vendor = guesser.autodetect()
    if vendor == None:
        print(f"failed to detect via SSH")
        vendor = get_vendor_from_user()
    return NetworkDevice(device_name, Vendor(vendor))


def get_vendor_from_user():
    while(True):
        print()
        vendor_type = input("""
            Please select the vendor type:
            0: Edgecore
            1: JunOS
            2: Nokia SRLinux
            3: Nokia SROS
        """)
        try:
            vendor_type = int(vendor_type)
            if (vendor_type < 0 or vendor_type > 5):
                raise Exception
            else:
                break
        except:
            print("enter a number between 0-5")
    match vendor_type:
        case 0:
            return Vendor.EDGECORE
        case 1:
            return Vendor.JUNIPER
        case 2:
            return Vendor.NOKIASRL
        case 3:
            return Vendor.NOKIASROS

def parse_alert(tsm_title):
    # of the form: P3 - [Icinga] Service Alert: {A-device} - ISL Port: {port} {lag}-{B-device} is CRITICAL
    pass