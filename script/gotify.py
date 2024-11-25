# Klipper extension for Pushover notification
#
# Copyright (C) 2024  Denys Shvets <denysshvets597@gmail.com>
#
# This file may be distributed under the terms of the GNU AGPLv3 license.

import http.client, urllib
import json
import ssl


class Gotify:
    def __init__(self, config) -> None:
        self.name = config.get_name().split()[-1]
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        filename = self.printer.lookup_object('print_stats')

        # configuration
        self.token = config.get('token')
        self.priority = config.get('priority', 5)
        self.server = config.get('server')
        self.serverport = config.get('serverport', "443")
        self.disable_certificate_validation = config.getboolean('disable_certificate_validation', False)

        # Register commands
        self.gcode.register_command(
            "GOTIFY_NOTIFY",
            self.cmd_GOTIFY_NOTIFY,
            desc=self.cmd_GOTIFY_NOTIFY_help)

    cmd_GOTIFY_NOTIFY_help = "Sending message to GOTIFY server"

    def cmd_GOTIFY_NOTIFY(self, params):

        message = params.get('MSG', '')
        title = params.get('TITLE', '')

        if message == '':
            self.gcode.respond_info(
                'Google GOTIFY based push notification for Klipper.\nUSAGE: GOTIFY_NOTIFY MSG="message" [TITLE="title"]\nTITLE parameter is optional')
            return

        # send message
        self.gcode.respond_info(f"Sending GOTIFY message: {title} - {message}")
        url = "/message"  # The endpoint path

        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",  # Required for JSON payload
            }
            payload = {
                "title": title,
                "message": message,
                "priority": int(self.priority),
            }
            if self.disable_certificate_validation:
                context = ssl._create_unverified_context()
            else:
                context = None
            conn = http.client.HTTPSConnection(self.server, 443, timeout=10, context=context)

            conn.request("POST", url, body=json.dumps(payload), headers=headers)
            response = conn.getresponse()
            message = response.read().decode()
            if response.status == 200:
                self.gcode.respond_info(f"{response.status} {response.reason}: {message}")
            else:
                raise self.gcode.error(f"{response.status} {response.reason}: {message}")
        except Exception as e:
            raise self.gcode.error(f"GOTIFY ERROR:\n{e}")


def load_config(config):
    return Gotify(config)
