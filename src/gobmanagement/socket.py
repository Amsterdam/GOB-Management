"""WebSocket interface

Broadcast 'new_logs' events on any new log messages

"""
import time
import threading

from gobmanagement.database import get_last_logid


class LogBroadcaster():

    CHECK_LOGS_INTERVAL = 5  # Check for new logs every 5 seconds

    def __init__(self, _socketio):
        """Initializes a broadcaster for new log records

        On any new log records a 'new_logs' event is broadcasted

        :param _socketio: SocketIO instance
        """
        self._socketio = _socketio
        self._clients = 0
        self._broadcaster = None

    def on_connect(self):
        """On connect of a new client

        Start a broadcast thread if not yet running

        :return: None
        """
        self._clients += 1
        self._start_broadcasts()
        print(f"Client connected", self._clients)

    def on_disconnect(self):
        """On disconnect of a new client

        Stop broadcast thread if no clients are connected anymore

        :return: None
        """
        self._clients -= 1
        print("Client disconnected", self._clients)

    def _start_broadcasts(self):
        """Start broadcast thread if not yet running

        :return: None
        """
        if self._broadcaster is None:
            self._broadcaster = threading.Thread(target=self._broadcasts)
            self._broadcaster.start()

    def _broadcasts(self):
        """Broadcast 'new_logs' events on any new log messages

        :return: None
        """
        print("Start broadcast new logs", self._clients)

        previous_last_logid = None
        while self._clients > 0:
            last_logid = get_last_logid()
            if last_logid != previous_last_logid:
                self._socketio.emit('new_logs', {'last_logid': last_logid})
                previous_last_logid = last_logid
            time.sleep(LogBroadcaster.CHECK_LOGS_INTERVAL)

        self._broadcaster = None
        print("End broadcast new logs", self._clients)
