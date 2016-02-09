from charms.reactive import when_not
from charms.reactive import when
from charms.reactive import set_state
from charms.reactive import remove_state

from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set

from charmhelpers.fetch import apt_install
from os import copyfile

from shlex import split
from subprocess import check_call

@when_not('ovs.prereq.installed')
def install_ovs_components():
    # define the package list of pre-reqs
    pkgs = ['openvswitch-switch']
   
   # Install, if we encounter an error, fatally halt the charm
    apt_install(pkgs, fatal=True)
    
   # copy and install the ovs script
   copyfile('files/ovs-docker', '/usr/local/bin/ovs-docker')
   set_state('ovs.prereq.installed')


@when_not('ovs.bridge_setup')
def setup_bridge_connections():
    # pipe this out to a subprocess job for now until we have a clear
    # definition of how we want to declare this network, the subnets
    # and how to properly add/remove them. This feels like a combination
    # of actions + charm config + relation data... but without a map this gets
    # hairy.

    # echo "setup ovs bridge = mwc-br1"
    # sudo ovs-vsctl add-br mwc-br1
    # ifconfig mwc-br1 10.42.11.1 netmask 255.255.255.0 up
    cmd = "ovs-vsctl add-br mwc-br1"
    check_call(split(cmd))
    cmd = "ifconfig mwc-br1 10.42.11.1 netmask 255.255.255.0 up".format(ip, netmask)
    check_call(split(cmd))


    # echo "adding port of ems"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_ems_1 --ipaddress=10.42.11.100/24  # noqa
    __ovs_docker('mwc-br1', 'eth0', 'epic_ems_1', '10.42.11.100/24')

    # echo "adding port of mme"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_mme_1 --ipaddress=10.42.11.101/24  # noqa
    __ovs_docker('mwc-br1', 'eth0', 'epic_mme_1', '10.42.11.101/24')
    # echo "adding port of hss"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_hss_1 --ipaddress=10.42.11.102/24  # noqa 
    __ovs_docker('mwc-br1', 'eth0', 'epic_hss_1', '10.42.11.102/24')
    # echo "adding port of pcrf"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_pcrf_1 --ipaddress=10.42.11.106/24  # noqa
    __ovs_docker('mwc-br1', 'eth0', 'epic_pcrf_1', '10.42.11.106/24')
    # echo "adding port of sgw"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_sgw_1 --ipaddress=10.42.11.103/24  # noqa
    __ovs_docker('mwc-br1', 'eth0', 'epic_sgw_1', '10.42.11.103/24')
    # echo "adding port of pgw"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_pgw_1 --ipaddress=10.42.11.104/24  # noqa
    __ovs_docker('mwc-br1', 'eth0', 'epic_pgw_1', '10.42.11.104/24')
    # echo "adding port of sdn_fabric"
    # sudo ovs-docker add-port mwc-br1 eth0 epic_fabric_1 --ipaddress=10.42.11.1/24  # noqa
    __ovs_docker('mwc-br1', 'eth0', 'epic_fabric_1', '10.42.11.1/24')

    # Setup C&C bridge
    # sudo ovs-vsctl add-port mwc-br1 eth1
    cmd = "ovs-vsctl add-port mwc-br1 eth1"
    check_call(split(cmd))



def __ovs_docker(bridge, device, label, ipaddress):
    ''' Interface with the OVS docker script packed with this charm. All
    commands are formatted as a subprocess job eg:
    ovs-docker add-port mwc-br1 eth0 epic_ems_1 --ipaddress=10.42.11.100/24

    @param bridge - Bridge Device
    @param device - Physical network device used for routing
    @param label - Label of the bridge
    @param ipaddress - CIDR to assign to the tagged traffic
    '''

    cmd = "ovs-docker add-port {0} {1} {2} --ipaddress={3}".format(bridge,
                                                                   device,
                                                                   label,
                                                                   ipaddress)
    check_call(split(cmd))


