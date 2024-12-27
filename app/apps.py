from django.apps import AppConfig
import subprocess
import os


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        result = subprocess.run(["wg", "show", "interfaces"], capture_output=True, text=True)
        interfaces = result.stdout.split()
        for interface in interfaces:
            subprocess.run(["wg-quick", "down", interface])

        config_path = "/etc/wireguard"
        for wg_conf in os.listdir(config_path):
            file_path = os.path.join(config_path, wg_conf)
            subprocess.run(["chmod", "600", file_path])
            subprocess.run(["wg-quick", "up", file_path])
