import requests
from requests.auth import HTTPBasicAuth

from gobcore.message_broker.config import MESSAGE_BROKER, MESSAGE_BROKER_PORT, MESSAGE_BROKER_VHOST
from gobcore.message_broker.config import MESSAGE_BROKER_USER, MESSAGE_BROKER_PASSWORD


def _get(path):
    """
    Gets Message Broker management info

    :param path: path within management API
    :return: Response
    """
    url = f"http://{MESSAGE_BROKER}:{MESSAGE_BROKER_PORT}/api/{path}"
    return requests.get(url,
                        auth=HTTPBasicAuth(MESSAGE_BROKER_USER, MESSAGE_BROKER_PASSWORD))


def get_queues():
    """
    Returns the GOB queues

    :return:
    """
    response = _get(f"queues/{MESSAGE_BROKER_VHOST}")
    return response.json(), response.status_code
