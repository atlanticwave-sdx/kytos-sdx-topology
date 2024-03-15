"""
SDX Topology main Unit test
"""
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from napps.kytos.sdx_topology.main import Main as AppMain
from .helpers import get_controller_mock, get_test_client


@dataclass
class TestMain(AppMain):
    """Test the Main class."""
    # pylint: disable=too-many-public-methods, protected-access,C0302
    napp = AppMain(get_controller_mock())

    def setup_method(self):
        """Execute steps before each tests."""
        patch('kytos.core.helpers.run_on_thread', lambda x: x).start()
        # pylint: disable=W0201
        self.controller = get_controller_mock()
        self.controller.napps[("kytos", "topology")] = MagicMock()
        self.controller.switches = MagicMock()
        self.napp = AppMain(controller)
        self.api_client = get_test_client(self.controller, self.napp)
        self.base_endpoint = 'kytos/sdx_topology/v1'

    async def test_get_event_listeners(self, event_loop):
        """Verify all event listeners registered."""
        expected_events = [
                "kytos/topology.switch.enabled",
                "kytos/topology.switch.disabled",
                "kytos/topology.switch.metadata.added",
                "kytos/topology.interface.metadata.added",
                "kytos/topology.link.metadata.added",
                "kytos/topology.switch.metadata.removed",
                "kytos/topology.interface.metadata.removed",
                "kytos/topology.link.metadata.removed",
                'kytos/topology.notify_link_up_if_status',
                'kytos/core.shutdown',
                'kytos/core.shutdown.kytos/topology',
                '.*.topo_controller.upsert_switch',
                '.*.of_lldp.network_status.updated',
                '.*.switch.interfaces.created',
                '.*.topology.switch.interface.created',
                '.*.switch.interface.deleted',
                '.*.switch.port.created',
                'topology.interruption.start',
                'topology.interruption.end',
                "kytos/topology.link_up",
                "kytos/topology.link_down",
                '.*.connection.lost',
                '.*.switch.interface.link_down',
                '.*.switch.interface.link_up',
                '.*.switch.(new|reconnected)'
                ]
        actual_events = self.napp.listeners()
        assert sorted(expected_events) == sorted(actual_events)

    async def test_create_update_topology(self, event_loop):
        """ Function that will take care of create or update sdx topology """
        print (dir(TestMain))
        response = self.napp.get_version_control()
        assert "id" in response
