import config
import unittest
import sys
import os
import device_id
import json


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.test_path = f'{os.path.dirname(os.path.abspath(sys.argv[0]))}/test_config.yml'
        self.user_val = 'user'
        self.vault_val = 'vault'
        self.item_val = 'item'
        self.file_val = 'file'
        self.ssh_user = 'ssh_user'
        test_config = f"""
---
op_user: {self.user_val}
op_vault: {self.vault_val}
op_item: {self.item_val}
ssh_user: {self.ssh_user}

id_file: {self.file_val}
        """
        with open(self.test_path, 'w') as file:
            file.write(test_config)

    def tearDown(self):
        os.remove(self.test_path)

    def test_resolve_directory(self):
        working_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        resolved = config.resolve_directory()
        self.assertEqual(str(working_directory), str(resolved))

    def test_load_config(self):
        test_conf = config.load_config(self.test_path)
        self.assertEqual(
                test_conf,
                config.Config(
                    self.user_val,
                    self.vault_val,
                    self.item_val,
                    self.file_val,
                    self.ssh_user
                )
            )


class TestDeviceID(unittest.TestCase):

    def setUp(self):
        self.test_path = config.resolve_directory()+'/test.jsonl'
        self.test_ipv4 = '1.1.1.1'
        self.device_name = 'dummy_device'
        self.test_vendor = device_id.Vendor.EDGECORE
        test_data = f"""
{{\"ipv4\":\"{self.test_ipv4}\",\"name\":\"{self.device_name}\",\"vendor\":\"{self.test_vendor}\"}}
        """
        with open(self.test_path, 'w') as file:
            file.write(test_data)

    def tearDown(self):
        os.remove(self.test_path)

    def test_get_device_known(self):
        test_device = device_id.get_device(self.device_name, self.test_path)
        true_device = device_id.NetworkDevice(self.test_ipv4,
                                              self.device_name,
                                              self.test_vendor)
        self.assertEqual(test_device, true_device)

    def test_get_device_unknown(self):
        # unsure how to test without some form of container setup + automation
        pass


if __name__ == '__main__':
    unittest.main()
