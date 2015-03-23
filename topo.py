#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
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
        info('*** Adding Core Switches')
        for cs in range(coreSwitch):
            switch = self.addSwitch('cs%s'%(cs),
                                    controller=c0,
                                    protocols='OpenFlow13')
        info('*** Adding Pod Switches')
        for pod in range(pods):
            for ag in range(agpp):
                switch = self.addSwitch('p%sa%s'%(pod, ag),
                                        controller=c0,
                                        protocols='OpenFlow13')
            for eg in range(egpp):
                switch = self.addSwitch('p%se%s'%(pod, eg),
                                        controller=c0,
                                        protocols='OpenFlow13')
                for h in range(hpe):
                    host = self.addHost('p%se%sh%s' %(pod, eg, h))
                    link = self.addLink('p%se%s' %(pod, eg),
                                        'p%se%sh%s' %(pod, eg, h))

def simTest():
    topo = FatTreeTopo()
    net = Mininet(topo=topo, build=False)
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
