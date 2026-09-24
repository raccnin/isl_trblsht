import asyncio
import config
import sys
import os
import get_pass
import device_id
import diagnose

'''
1. load config
2. load device file
3. identify devices
4. run diagnostics
5. aggregate diagnostics
'''


def load_config():
    running_dir = config.resolve_directory()
    config_path = running_dir + '/config.yml'
    return config.load_config(config_path)


def get_device(device_name, configuration, secret):
    try:
        device = device_id.get_device(device_name, configuration.id_file)
    except LookupError:
        # SSHDetect only actually works for junos :(
        print(f"device {device_name} not known, getting vendor...")
        device = device_id.id_device(device_name,
                                     configuration.ssh_user,
                                     secret)
        device_id.write_device(device, configuration.id_file)
        print(f"device identified as: {device.vendor}")
    return device


def get_diagnostics(diagnostic_request, configuration, secret):
    print(f"running diagnostics for {diagnostic_request.device.name}...")
    for diagnostic in diagnose.get_diagnostics(diagnostic_request, configuration.ssh_user, secret):
        print(diagnostic)


async def main():

    # get configuration
    conf = load_config()
    # get password
    op_client = await get_pass.open_client(conf.op_user)
    secret = await get_pass.get_pass(op_client, conf.secret_url)
    # identify device
    # TODO: parse alert
    # TODO: handle multiple devices
    device_name = sys.argv[1]
    port = sys.argv[2]
    lag = sys.argv[3]
    device = get_device(device_name, conf, secret)
    diagnostic_request = diagnose.DiagnosticRequest(device, port, lag)
    # run diagnostic commands for device
    get_diagnostics(diagnostic_request, conf, secret)

if __name__ == '__main__':
    asyncio.run(main())
