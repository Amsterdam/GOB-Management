import re

from flask import request

from gobcore.secure.request import extract_roles
from gobcore.secure.config import GOB_ADMIN, GOB_ADMIN_R

from gobmanagement.config import API_BASE_PATH, PUBLIC_API_BASE_PATH

_PUBLIC = 'public'
_PERMISSIONS = {
    '/status/health/?': {
        'methods': ['GET'],
        'roles': _PUBLIC,
    },
    f'{API_BASE_PATH}/job/?': {
        'methods': ['POST'],
        'roles': [GOB_ADMIN],
    },
    f'{API_BASE_PATH}/job/.+': {
        'methods': ['DELETE'],
        'roles': [GOB_ADMIN],
    },
    f'{API_BASE_PATH}/socket.io/.*': {
        'methods': ['GET', 'POST'],
        'roles': _PUBLIC,
    },
    f'{PUBLIC_API_BASE_PATH}/state/.*': {
        'methods': ['GET'],
        'roles': _PUBLIC,
    },
    f'{API_BASE_PATH}/queue/.*': {
        'methods': ['DELETE'],
        'roles': [GOB_ADMIN],
    },
    f'{PUBLIC_API_BASE_PATH}/catalogs/?': {
        'methods': ['GET'],
        'roles': _PUBLIC,
    },
    f'{PUBLIC_API_BASE_PATH}/queues/?': {
        'methods': ['GET'],
        'roles': _PUBLIC,
    },
    f'{PUBLIC_API_BASE_PATH}/graphql/?': {
        'methods': ['GET', 'POST'],
        'roles': _PUBLIC,
    },
    '/.*': {
        'methods': ['GET', 'POST'],
        'roles': [GOB_ADMIN, GOB_ADMIN_R],
    },
}


class SecurityMiddleware:
    """SecurityMiddleware

    Request path is matched against paths in _PERMISSIONS. Paths (keys) in _PERMISSIONS are expected to be valid
    regexes.

    - Longest path in _PERMISSIONS matched with requested path is checked.
    - If the longest matched path does not match on request method, access is denied, even though there might be a
      shorter matching path with the correct request method.
    - User should have ANY role listed in roles list, unless roles is set to _PUBLIC.

    This class takes the user roles from the token.
    """

    def __init__(self, app):
        self.app = app
        self.app.before_request(self._before_request)

    def _before_request(self):
        """Called on every request.

        :return:
        """
        if request.method == 'OPTIONS':
            return

        match = self._match_path(request.path, request.method)
        user_roles = extract_roles(request.headers)

        if not match or not self._is_allowed_access(user_roles, match):
            return "Forbidden", 403

    def _is_allowed_access(self, user_roles: list, match):
        """

        :param user_roles:
        :param match:
        :return:
        """
        if match['roles'] == _PUBLIC:
            # Public route
            return True

        matched_roles = [r for r in user_roles if r in match['roles']]

        return len(matched_roles) > 0

    def _match_path(self, path: str, method: str) -> dict:
        """Returns the path match from _PERMISSIONS if any matches, or else None.

        :param path:
        :param method:
        :return:
        """
        matches = [match_path for match_path in _PERMISSIONS.keys() if re.match(match_path, path)]
        if matches:
            # Take longest match
            match = _PERMISSIONS[sorted(matches, key=len, reverse=True)[0]]
            return match if method in match['methods'] else None
