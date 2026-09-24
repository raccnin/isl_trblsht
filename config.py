import yaml
import sys
import os


class Config:
    secret_url: str
    op_user: str
    id_file: str
    ssh_user: str

    def __init__(self, op_user, op_vault, op_item, id_file, ssh_user):
        self.id_file = id_file
        self.op_user = op_user
        self.secret_url = f"op://{op_vault}/{op_item}/password"
        self.ssh_user = ssh_user

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__

    def __str__(self):
        return f"id_file: {self.id_file}, op_user: {self.op_user}, secret_url: {self.secret_url}"


def load_config(config_path):
    with open(config_path, 'r') as file:
        return Config(**yaml.safe_load(file))


def resolve_directory():
    return os.path.dirname(os.path.abspath(sys.argv[0]))
