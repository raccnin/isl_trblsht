import device_id
from netmiko import ConnectHandler
from dataclasses import dataclass
from device_id import NetworkDevice
from config import Config
import get_pass


@dataclass
class DiagnosticRequest:
    device: NetworkDevice
    port: str
    lag: str


def get_commands(dr: DiagnosticRequest):
    match dr.device.vendor:
        case device_id.Vendor.EDGECORE:
            return get_edgecore_commands(dr.port, dr.lag)
        case device_id.Vendor.JUNIPER:
            return get_junos_commands(dr.port, dr.lag)
        case device_id.Vendor.NOKIASRL:
            return get_srl_commands(dr.port, dr.lag)
        case device_id.Vendor.NOKIASROS:
            return get_sros_commands(dr.port, dr.lag)
        case _:
            raise LookupError("vendor type not known")


def get_edgecore_commands(port, lag):
    return [f"show interface brief {port}",
            f"show etherchannel summary | begin {lag}",
            f"show interface {port} transceiver",
            f"show interface {port} counters error-stats"]


def get_junos_commands(port, lag):
    return [f"show interfaces descriptions {port}",
            f"show lacp interfaces {lag} | no-more",
            f"show interfaces diagnostics optics {port} | match \"cted|Phys|Lane|power|threshold\" | except \"receiver|volt|bias|temp\"",
            f"show interfaces extensive {port} | match errors"]


def get_srl_commands(port, lag):
    return [f"show interface {port}",
            "show network-instance default protocols ospf neighbor",
            f"info from state interface {port} | grep -E -A 9 \"input-power|output-power\"",
            f"show interface {port} detail | grep -A 14 Traffic"]


def get_sros_commands(port, lag):
    port_channel = '/'.join(port.split('/')[:-1])
    lag = ''.join([char for char in lag if char.isnum()])
    return [f"show port {port} | match State",
            f"show lag {lag} description | no-more",
            f"show port {port_channel} optical | no-more",
            f"show port {port} | match Errors"]


def get_diagnostics(dr, ssh_user, secret):
    netmiko_device = dr.device.to_netmiko(ssh_user, secret)
    commands = get_commands(dr)
    with ConnectHandler(**netmiko_device) as connection:
        for command in commands:
            try:
                yield connection.send_command(command)
            except Exception as e:
                yield f"""
could not execute command due to {type(e)}:
    {command}:
        {e}
"""
