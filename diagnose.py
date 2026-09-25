import device_id
from netmiko import ConnectHandler
from dataclasses import dataclass
from device_id import NetworkDevice, Vendor
from config import Config


@dataclass
class DiagnosticRequest:
    device: NetworkDevice
    port: str
    lag: str


class DiagnosticHandler:
    config: Config
    secret: str

    def __init__(self, config, secret):
        self.config = config
        self.secret = secret

    def identify_device(self, device: NetworkDevice):
        # attempt file recognition
        try:
            candidate = device_id.get_device(device.name, self.config.id_file)
            return candidate
        except LookupError:
            print(f"device {device.name} not known, querying vendor")
            candidate = device_id.id_device(device.name,
                                            self.config.ssh_user,
                                            self.secret)
            return candidate

    def run_diagnostics(self, dr: DiagnosticRequest):
        print(f"running diagnostics for {dr.device.name}")
        for diagnostic in get_diagnostics(dr, 
                                          self.config.ssh_user,
                                          self.secret):
            print(diagnostic)

    def handle_request(self, dr: DiagnosticRequest):
        if dr.device.vendor == Vendor.AUTO:
           dr.device = self.identify_device(dr.device) 
        self.run_diagnostics(dr)
        


def get_commands(user, dr: DiagnosticRequest):
    match dr.device.vendor:
        case device_id.Vendor.EDGECORE:
            return get_edgecore_commands(user, dr)
        case device_id.Vendor.JUNIPER:
            return get_junos_commands(user, dr)
        case device_id.Vendor.NOKIASRL:
            return get_srl_commands(user, dr)
        case device_id.Vendor.NOKIASROS:
            return get_sros_commands(user, dr)
        case _:
            raise LookupError("vendor type not known")


def get_edgecore_commands(user, dr):
    prompt = f"{dr.device.name}#"
    return [prompt,[f"show interface brief {dr.port}",
            f"show etherchannel summary | begin {dr.lag}",
            f"show interface {dr.port} transceiver",
            f"show interface {dr.port} counters error-stats"]]


def get_junos_commands(user, dr):
    prompt = f"{{master}}\n{user}@{dr.device.name}-re0> "
    return [prompt, [f"show interfaces descriptions {dr.port}",
            f"show lacp interfaces {dr.lag} | no-more",
            f"show interfaces diagnostics optics {dr.port} | match \"cted|Phys|Lane|power|threshold\" | except \"receiver|volt|bias|temp\"",
            f"show interfaces extensive {dr.port} | match errors"]]


def get_srl_commands(user, dr):
    prompt = f"--{{ running }}--[  ]--\nA:{dr.device.name}# "
    return [prompt, [f"show interface {dr.port}",
            "show network-instance default protocols ospf neighbor",
            f"info from state interface {dr.port} | grep -E -A 9 \"input-power|output-power\"",
            f"show interface {dr.port} detail | grep -A 14 Traffic"]]


def get_sros_commands(user, dr):
    prompt = f"[/]\nA:{user}@{dr.device.name}# "
    port_channel = '/'.join(dr.port.split('/')[:-1])
    lag = ''.join([char for char in dr.lag if char.isnum()])
    return [prompt, [f"show port {dr.port} | match State",
            f"show lag {dr.lag} description | no-more",
            f"show port {port_channel} optical | no-more",
            f"show port {dr.port} | match Errors"]]


def get_diagnostics(dr, ssh_user, secret):
    netmiko_device = dr.device.to_netmiko(ssh_user, secret)
    prompt, commands = get_commands(ssh_user, dr)
    with ConnectHandler(**netmiko_device) as connection:
        for command in commands:
            try:
                yield prompt + command + '\n' + connection.send_command(command)
            except Exception as e:
                yield f"""
could not execute command due to {type(e)}:
    {command}:
        {e}
"""
