"""
Main module of amlight/sdx Kytos Network Application.
"""
import os
import shelve
import requests
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from napps.kytos.sdx_topology.convert_topology import (
        ParseConvertTopology)  # pylint: disable=E0401
from napps.kytos.sdx_topology import settings, utils, topology_mock \
        # pylint: disable=E0401
from napps.kytos.topology.main import Main as KytosTopologyMain \
        # pylint: disable=E0401

from kytos.core import KytosNApp, log, rest
from kytos.core.events import KytosEvent
from kytos.core.helpers import listen_to
from kytos.core.rest_api import (HTTPException, JSONResponse, Request,
                                 content_type_json_or_415, get_json_or_400)

HSH = "##########"
URN = "urn:sdx:"


class Main(KytosNApp):  # pylint: disable=R0904
    """Main class of amlight/sdx NApp.

    This class is the entry point for this NApp.
    """

    def setup(self):
        """Replace the '__init__' method for the KytosNApp subclass.

        The setup method is automatically called by the controller when your
        application is loaded.

        So, if you have any setup routine, insert it here.
        """
        log.debug(f"{HSH}{HSH}{HSH}")
        log.debug(f"{HSH}sdx topology{HSH}")
        log.debug(f"{HSH}{HSH}{HSH}")
        self.event_info = {}  # pylint: disable=W0201
        self.shelve_loaded = False  # pylint: disable=W0201

    def execute(self):
        """Run after the setup method execution.

        You can also use this method in loop mode if you add to the above setup
        method a line like the following example:

            self.execute_as_loop(30)  # 30-second interval.
        """
        self.load_shelve()

    def shutdown(self):
        """Run when your NApp is unloaded.

        If you have some cleanup procedure, insert it here.
        """

    @listen_to("kytos/topology.unloaded")
    def unload_topology(self):  # pylint: disable=W0613
        """Function meant for validation, to make sure that the shelve
        has been loaded before all the other functions that use it begins to
        call it."""
        self.shelve_loaded = False  # pylint: disable=W0201

    def test_kytos_topology(self):
        """ Test if the Topology napp has loaded """
        try:
            _ = self.get_kytos_topology()
            return True
        except Exception as err:  # pylint: disable=W0703
            log.debug(err)
            return False

    @staticmethod
    def get_kytos_topology():
        """retrieve topology from API"""
        kytos_topology = requests.get(
                settings.KYTOS_TOPOLOGY, timeout=10).json()
        return kytos_topology["topology"]

    def validate_sdx_topology(self, sdx_topology):
        """ return 200 if validated topology following the SDX data model"""
        validate_topology = requests.post(
                settings.SDX_TOPOLOGY_VALIDATE,
                timeout=10,
                json=sdx_topology)
        return validate_topology

    def convert_topology(self, event_type=0, event_timestamp=None):
        """Function that will take care of update the shelve containing
        the version control that will be updated every time a change is
        detected in kytos topology, and return a new sdx topology"""
        try:
            # open the topology shelve
            with shelve.open("topology_shelve") as open_shelve:
                version = open_shelve['version']
                self.dict_shelve = dict(open_shelve)  # pylint: disable=W0201
                open_shelve.close()
            if version >= 1 and event_type != 0:
                timestamp = utils.get_timestamp()
                if event_type == 1:
                    version += 1
                elif event_type == 2:
                    timestamp = event_timestamp
                return ParseConvertTopology(
                    topology=self.get_kytos_topology(),
                    version=version,
                    timestamp=timestamp,
                    model_version=self.dict_shelve['model_version'],
                    oxp_name=self.dict_shelve['oxp_name'],
                    oxp_url=self.dict_shelve['oxp_url'],
                ).parse_convert_topology()
            return topology_mock.topology_mock()
        except Exception as err:  # pylint: disable=W0703
            log.debug(err)
            return ("Validation Error", 400)

    def post_sdx_topology(self, event_type=0, event_timestamp=None):
        """ return the topology following the SDX data model"""
        try:
            if event_type != 0:
                topology_update = self.convert_topology(
                        event_type, event_timestamp)
                sdx_topology = {
                        "id": topology_update["id"],
                        "name": topology_update["name"],
                        "version": topology_update["version"],
                        "model_version": topology_update["model_version"],
                        "timestamp": topology_update["timestamp"],
                        "nodes": topology_update["nodes"],
                        "links": topology_update["links"],
                        }
            else:
                sdx_topology = topology_mock.topology_mock()
            evaluate_topology = self.validate_topology()
            if evaluate_topology.status_code == 200:
                post_topology = requests.post(
                        settings.SDX_LC_TOPOLOGY,
                        timeout=10,
                        json=sdx_topology)
                if post_topology.status_code == 200:
                    if event_type != 0:
                        # open the topology shelve
                        with shelve.open("topology_shelve") as open_shelve:
                            open_shelve['version'] = sdx_topology["version"]
                            open_shelve['timestamp'] = \
                                sdx_topology["timestamp"]
                            open_shelve['nodes'] = sdx_topology["nodes"]
                            open_shelve['links'] = sdx_topology["links"]
                            # now, we simply close the shelf file.
                            open_shelve.close()
                    return (sdx_topology, 200)
                return (post_topology.json(), 400)
            return (evaluate_topology.json(), 400)
        except Exception as err:  # pylint: disable=W0703
            log.debug(err)
        return ("No SDX Topology loaded", 401)

    @listen_to("kytos/topology.*")
    def listen_event(self, event=None):
        """Function meant for listen topology"""
        f_name = " listen_event "
        log.debug(f"{HSH}{f_name}listen event {HSH}")
        if event is not None and self.get_kytos_topology():
            if event.name in settings.ADMIN_EVENTS:
                event_type = 1
            elif event.name in settings.OPERATIONAL_EVENTS and \
                    event.timestamp is not None:
                event_type = 2
            else:
                return {"event": "not action event"}
            # open the event shelve
            with shelve.open("events_shelve") as log_events:
                shelve_events = log_events['events']
                shelve_events.append(event.name)
                log_events['events'] = shelve_events
                log_events.close()
            return self.post_sdx_topology(event_type, event.timestamp)
        log.debug(
                f"{HSH} event:{event}, topology: {self.get_kytos_topology()}")
        return {"event": event, "topology": self.get_kytos_topology()}

    def load_shelve(self):  # pylint: disable=W0613
        """Function meant for validation, to make sure that the store_shelve
        has been loaded before all the other functions that use it begins to
        call it."""
        if not self.shelve_loaded:  # pylint: disable=E0203
            # open the sdx topology shelve file
            with shelve.open("topology_shelve") as open_shelve:
                if 'id' not in open_shelve.keys() or \
                        'name' not in open_shelve.keys():
                    # initialize sdx topology
                    open_shelve['id'] = URN+"topology:"+os.environ.get(
                            "OXPO_URL")
                    open_shelve['name'] = os.environ.get("OXPO_NAME")
                    open_shelve['url'] = os.environ.get("OXPO_URL")
                    open_shelve['version'] = 0
                    open_shelve['model_version'] = os.environ.get(
                            "MODEL_VERSION")
                    open_shelve['timestamp'] = utils.get_timestamp()
                    open_shelve['nodes'] = []
                    open_shelve['links'] = []
                self.dict_shelve = dict(open_shelve)  # pylint: disable=W0201
                self.shelve_loaded = True  # pylint: disable=W0201
                # now, we simply close the shelf file.
                open_shelve.close()
            # open the events shelve file
            with shelve.open("events_shelve") as events_shelve:
                events_shelve['events'] = []
                events_shelve.close()

    # rest api tests

    @rest("v1/validate_sdx_topology")
    def get_validate_sdx_topology(self, sdx_topology):
        """ REST to return the validated sdx topology status"""
        return self.validate_sdx_topology(sdx_topology)

    @rest("v1/convert_topology")
    def get_converted_topology(self, event_type=0, event_timestamp=None):
        """ REST to return the converted sdx topology"""
        return self.convert_topology(event_type, event_timestamp)

    @rest("v1/sdx_topology")
    def get_sdx_topology(self, event_type=0, event_timestamp=None):
        """ REST to return the sdx topology loaded"""
        return self.post_sdx_topology(event_type, event_timestamp)

    @rest("v1/listen_event", methods=["POST"])
    def get_listen_event(self, _request: Request) -> JSONResponse:
        """consume call listen Event"""
        f_name = " get_listen_event "
        log.debug(f"{HSH}{f_name}{HSH}")
        try:
            event = KytosEvent(
                    name=request.name, content=request.content)
            # self.controller.buffers.app.put(event)
            sdx_topology = self.listen_event(event)
            return JSONResponse({"sdx_topology": sdx_topology})
        except requests.exceptions.HTTPError as http_error:
            raise SystemExit(
                    http_error, detail="listen topology fails") from http_error

    @rest("v1/shelve/topology", methods=["GET"])
    def get_shelve_topology(self, _request: Request) -> JSONResponse:
        """return sdx topology shelve"""
        open_shelve = shelve.open("topology_shelve")
        dict_shelve = dict(open_shelve)
        open_shelve.close()
        return JSONResponse(dict_shelve)

    @rest("v1/shelve/events", methods=["GET"])
    def get_shelve_events(self, _request: Request) -> JSONResponse:
        """return events shelve"""
        f_name = " get_shelve_events "
        log.debug(f"{HSH}{f_name}{HSH}")
        with shelve.open("events_shelve") as open_shelve:
            events = open_shelve['events']
        open_shelve.close()
        return JSONResponse({"events": events})
