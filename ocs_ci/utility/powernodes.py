import logging

from ocs_ci.ocs import constants
from ocs_ci.ocs.exceptions import UnexpectedBehaviour
from ocs_ci.ocs.node import wait_for_nodes_status, get_worker_nodes, get_master_nodes
from ocs_ci.ocs.ocp import wait_for_cluster_connectivity
from ocs_ci.utility.utils import TimeoutSampler, exec_cmd

logger = logging.getLogger(__name__)


class POWERNODES(object):
    """
    Wrapper for PowerNodes
    """

    def verify_machine_is_down(self, node):
        """
        Verify if PowerNode is completely powered off

        Args:
            node (object): Node objects

        Returns:
            bool: True if machine is down, False otherwise

        """
        result = exec_cmd(f"sudo virsh domstate test-ocp4-6-{node.name}")
        if result.stdout.lower().rstrip() == b"running":
            return False
        else:
            return True

    def stop_powernodes_machines(self, powernode_machines, force=True):
        """
        Stop PowerNode Machines

        Args:
            powernode_machines (list): PowerNode objects
            force (bool): True for PowerNode ungraceful power off, False for
                graceful PowerNode shutdown - for future use

        Raises:
            UnexpectedBehaviour: If PowerNode machine is still up

        """
        for node in powernode_machines:
            cmd = f"sudo virsh shutdown test-ocp4-6-{node.name}"
            result = exec_cmd(cmd)
            """
            if result.returncode == 0:
                return False
            else
                return True
            """
            logger.info(f"Result of shutdown {result}")
            logger.info("Verifying node is down")
            ret = TimeoutSampler(
                timeout=900,
                sleep=3,
                func=self.verify_machine_is_down,
                node=node,
            )
            logger.info(ret)
            if not ret.wait_for_func_status(result=True):
                raise UnexpectedBehaviour("Node {node.name} is still Running")

    def start_powernodes_machines(self, powernode_machines, force=True):
        """
        Start PowerNode Machines

        Args:
            powernode_machines (list): List of PowerNode machines
            wait (bool): Wait for PowerNodes to start - for future use

        """
        for node in powernode_machines:
            result = exec_cmd(f"sudo virsh start test-ocp4-6-{node.name}")
            logger.info(f"Result of shutdown {result}")

        wait_for_cluster_connectivity(tries=900)
        wait_for_nodes_status(
            node_names=get_master_nodes(), status=constants.NODE_READY, timeout=900
        )
        wait_for_nodes_status(
            node_names=get_worker_nodes(), status=constants.NODE_READY, timeout=900
        )

    def restart_powernodes_machines(self, powernode_machines, force=True):
        """

        Restart PowerNode Machines

        Args:
            powernode_machines (list): PowerNode objects
            force (bool): True for PowerNode ungraceful power off, False for
                graceful PowerNode shutdown - for future use

        """
        self.stop_powernodes_machines(powernode_machines, force=force)
        self.start_powernodes_machines(powernode_machines, force=force)