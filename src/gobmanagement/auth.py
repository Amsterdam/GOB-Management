import re

from flask import request


class RequestUser:

    def __init__(self):
        self._props = {}
        auth_pattern = "^X-Auth-"
        for header, value in request.headers.items():
            if re.match(auth_pattern, header):
                header = re.sub(auth_pattern, "", header)
                self._props[header] = value
                setattr(self, header, value)

    def __str__(self):
        return "USER: " + ', '.join(f"{k}='{v}'" for k, v in self._props.items())
