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
    device = device_id.NetworkDevice(device_name)
    diagnostic_request = diagnose.DiagnosticRequest(device, port, lag)
    diagnostic_handler = diagnose.DiagnosticHandler(conf, secret)
    diagnostic_handler.handle_request(diagnostic_request)


if __name__ == '__main__':
    asyncio.run(main())
