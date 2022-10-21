from libs.config_converter.config_converter_base import ConfigConverterBase  # pylint: disable=E0611, E0401

import logging


class ConfigConverterV3(ConfigConverterBase):
    """
    Config V3 updates the format used for groups (list -> dict).
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.from_version = 2
        self.to_version = 3

    def upgrade(self, old_config):
        self.logger.info("Upgrade config to version 3.")

        upgrade_step_1 = self.format_global_groups(old_config)
        upgrade_step_2 = self.format_device_groups(upgrade_step_1)
        upgrade_step_3 = self.format_default_device_groups(upgrade_step_2)

        new_config = upgrade_step_3
        new_config["version"] = 3

        self.logger.info("Config upgraded to version 3.")
        return new_config

    def format_global_groups(self, old_config):
        # Change old list format of global groups to dict.
        global_groups = old_config["general_settings"]["device_groups"]

        if isinstance(global_groups, dict):
            return old_config

        new_global_groups = {f"group_{i}": group for i, group in enumerate(global_groups)}
        old_config["general_settings"]["device_groups"] = new_global_groups
        return old_config

    def format_device_groups(self, old_config):
        # Change old list format of device groups to dict.
        global_groups = old_config["general_settings"]["device_groups"]

        for device in old_config["device_configs"]:
            device_groups = old_config["device_configs"][device]["device_groups"]

            if isinstance(device_groups, dict):
                continue

            new_device_groups = dict()
            for group_id, group in global_groups.items():
                if group in device_groups:
                    new_device_groups[group_id] = group

            old_config["device_configs"][device]["device_groups"] = new_device_groups
        return old_config

    def format_default_device_groups(self, old_config):
        # Change old list format of default device groups to dict.
        old_config["default_device"]["device_groups"] = {}
        return old_config
