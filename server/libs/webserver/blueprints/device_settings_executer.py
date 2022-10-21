from libs.webserver.executer_base import ExecuterBase, handle_config_errors


class DeviceSettingsExecuter(ExecuterBase):

    # Return setting_value
    @handle_config_errors
    def get_device_setting(self, device, setting_key):
        return self._config["device_configs"][device][setting_key]

    @handle_config_errors
    def get_device_settings(self, device):
        device_settings_dict = dict()
        for device_setting_key in self._config["device_configs"][device]:
            device_settings_dict[device_setting_key] = self._config["device_configs"][device][device_setting_key]
        return device_settings_dict

    @handle_config_errors
    def set_device_setting(self, device, settings):
        if not isinstance(settings, dict) or not settings:
            return None

        for setting_key, setting_value in settings.items():
            self._config["device_configs"][device][setting_key] = setting_value
        self.save_config()

        self.refresh_device(device)
        return self._config["device_configs"][device][setting_key]

    # Return setting_value
    @handle_config_errors
    def get_output_type_device_setting(self, device, output_type_key, setting_key):
        return self._config["device_configs"][device]["output"][output_type_key][setting_key]

    @handle_config_errors
    def get_all_output_type_settings(self, device):
        result = dict()
        output_types = self._config["device_configs"][device]["output"]
        # Flatten output types to one dict.
        for key, value in output_types.items():
            if isinstance(value, dict):
                result.update(value)
            else:
                result[key] = value
        return result

    @handle_config_errors
    def set_output_type_device_setting(self, device, output_type_key, settings):
        if not isinstance(settings, dict) or not settings:
            return None

        for setting_key, setting_value in settings.items():
            self._config["device_configs"][device]["output"][output_type_key][setting_key] = setting_value
        self.save_config()

        self.refresh_device(device)
        return self._config["device_configs"][device]["output"][output_type_key][setting_key]
