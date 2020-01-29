import requests
from requests.auth import HTTPBasicAuth

from gobcore.message_broker.config import MESSAGE_BROKER, MESSAGE_BROKER_PORT, MESSAGE_BROKER_VHOST
from gobcore.message_broker.config import MESSAGE_BROKER_USER, MESSAGE_BROKER_PASSWORD


def _request(path, method="get"):
    """
    Gets Message Broker management info

    :param path: path within management API
    :return: Response
    """
    url = f"http://{MESSAGE_BROKER}:{MESSAGE_BROKER_PORT}/api/{path}"
    return getattr(requests, method)(url, auth=HTTPBasicAuth(MESSAGE_BROKER_USER, MESSAGE_BROKER_PASSWORD))


def purge_queue(queue):
    """
    Purges a queue (removes all waiting messages)

    :param queue: queue to purge
    :return: Response
    """
    response = _request(f"queues/{MESSAGE_BROKER_VHOST}/{queue}/contents", method='delete')
    if response.status_code == 204:
        # No response means that purge has succeeded
        return {
            'result': 'OK'
        }, 200
    else:
        return response.json(), response.status_code


def get_queues():
    """
    Returns the GOB queues

    :return:
    """
    response = _request(f"queues/{MESSAGE_BROKER_VHOST}")
    return response.json(), response.status_code
