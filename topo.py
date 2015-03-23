#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.log import setLogLevel, info

formatter = "%r"
block = "####################"
c0 = RemoteController('c0', ip='127.0.0.1', port=6633)
class FatTreeTopo(Topo):
    """
    coreSwitch: Fat Free Topology Cores
    pods: group of switches that contain
          several aggregation switches and edge switches
    agpp: aggregation switches per pod
    egpp: edge switches per pod
    hpe:  hosts per edge
    """
    def __init__(self,coreSwitch=4,pods=4,agpp=2,egpp=2,hpe=2,**opts):
        Topo.__init__(self, **opts)
        """define Protocol"""
        protocal = 'OpenFlow13'
        """define controller"""
        crtl = c0
        """define Links types"""
        linkopts100M = dict(bw=100, delay='0ms', loss=0)
        linkopts1G = dict(bw=1000, delay='0ms', loss=5)

        info('*** Adding Core Switches')
        for cs in range(coreSwitch):
            sw = self.addSwitch('cs%s'%(cs),
                                    controller=crtl,
                                    protocols=protocal,
                                    stp=True)
        info('*** Adding Pod Switches')
        for pod in range(pods):
            """Add aggregation switches"""
            for ag in range(agpp):
                sw = self.addSwitch('p%sa%s'%(pod, ag),
                                        controller=crtl,
                                        protocols=protocal,
                                        stp=True)
                """Add Link between core switches and Aggregation switches"""
            for cs in range(0,coreSwitch/agpp):
                for ra in range(0,agpp/2):
                    link = self.addLink('cs%s'%(cs),
                                        'p%sa%s'%(pod,ra),
                                        **linkopts1G)
            for cs in range(coreSwitch/agpp,coreSwitch):
                for ra in range(agpp/2,agpp):
                    link = self.addLink('cs%s'%(cs),
                                        'p%sa%s'%(pod, ra),
                                        **linkopts1G)
            """Add edge switches"""
            for eg in range(egpp):
                sw = self.addSwitch('p%se%s'%(pod, eg),
                                        controller=crtl,
                                        protocols=protocal,
                                        stp=True)
                """Add Link between Edge switches and Aggregation switches"""
                for ag in range(agpp):
                    link = self.addLink('p%se%s'%(pod, eg),
                                        'p%sa%s'%(pod, ag),
                                        **linkopts100M)
                """Add Hosts per Edge switche"""
                """Add Link between Hosts and Edge switches"""
                for h in range(hpe):
                    host = self.addHost('p%se%sh%s' %(pod, eg, h))
                    link = self.addLink('p%se%s' %(pod, eg),
                                        'p%se%sh%s' %(pod, eg, h),
                                        **linkopts100M)
    def LinkCoreAg():
        print("Hey")


def simTest():
    topo = FatTreeTopo()
    net = Mininet(topo=topo,link=TCLink,controller=None,build=False)
    ryu_ctl = net.addController('c0',
                                controller=RemoteController,
                                ip='127.0.0.1', port=6633)

    net.build()
    print "NET BUILD"
    net.start()
    print "NET START"
    print formatter % (block)
    print "Dumping host connections"
    print formatter % (block)
    dumpNodeConnections(net.hosts)
    print formatter % (block)
    print "Testing network connectivity"
    print formatter % (block)
    net.pingAll()
    print formatter % (block)
    print "network CLI"
    print formatter % (block)
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simTest()
