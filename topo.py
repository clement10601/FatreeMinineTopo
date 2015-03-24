#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os

class FatTreeTopo(Topo):
    info('CreatFatTreeTopo')
    """define Protocol"""
    protocal = 'OpenFlow13'
    """define controller"""
    crtlname = 'crtl0'
    crtlip ='127.0.0.1'
    crtlport = 6653
    crtl = RemoteController(crtlname, ip=crtlip, port=crtlport)
    """define Links types"""
    linkopts100M = dict(bw=100, delay='0ms', loss=0)
    linkopts1G = dict(bw=1000, delay='0ms', loss=5)
    coreSW = []
    aggSW = []
    eggSW = []
    hList = []
    """
    coreSwitch: Fat Free Topology Cores
    pods: group of switches that contain
    several aggregation switches and edge switches
    agpp: aggregation switches per pod
    egpp: edge switches per pod
    hpe: hosts per edge
    """
    def __init__(self):
        info('FTT Init')
        Topo.__init__(self)

    def topoCreate(self,coreSwitch,pods,agpp,egpp,hpe,**opts):
        info('Building Topo')
        self.coreSW = self.addCoreSwitch(coreSwitch)
        for pod in range(pods):
            self.aggSW.append(self.addAggregationSwitch(pod,agpp))
            self.eggSW.append(self.addEdgeSwitch(pod,agpp,egpp))
            for ew in range(egpp):
                self.hList.append(self.addFatHost(pod,ew,hpe))

    def addCoreSwitch(self,num):
        info('Adding Core Switch')
        CoreSwitch = []
        for n in range(num):
            CoreSwitch.append(self.addSwitch('Core%s'%(n),
                                             protocols=self.protocal))
        return CoreSwitch

    def addAggregationSwitch(self,pod,num):
        info('Adding Aggregation Switch')
        AggregationSwitch = []
        for n in range(num):
            AggregationSwitch.append(self.addSwitch('p%sa%s'%(pod,n),
                                                    protocols=self.protocal))
            if n == 0:
                self.addLink('p%sa%s'%(pod,n),'Core0',**self.linkopts1G)
                self.addLink('p%sa%s'%(pod,n),'Core1',**self.linkopts1G)
            else:
                self.addLink('p%sa%s'%(pod,n),'Core2',**self.linkopts1G)
                self.addLink('p%sa%s'%(pod,n),'Core3',**self.linkopts1G)
        return AggregationSwitch

    def addEdgeSwitch(self,pod,agpp,num):
        info('Adding Edge Switch')
        EdgeSwitch = []
        for n in range(num):
            EdgeSwitch.append(self.addSwitch('p%se%s'%(pod,n),
                                             protocols=self.protocal))
            for a in range(agpp):
                self.addLink('p%se%s'%(pod,n),'p%sa%s'%(pod,a))

        return EdgeSwitch

    def addFatHost(self,pod,edge,num):
        info('Adding Host')
        host = []
        for n in range(num):
            host.append(self.addHost('p%se%sh%s'%(pod,edge,n)))
        return host

    def addFatLinks(self,target1,target2,linktype):
        info('Adding Links')

def RunTest():
    """TOPO"""
    topo = FatTreeTopo()
    topo.topoCreate(4,4,2,2,2)

    CONTROLLER_NAME = topo.crtlname
    CONTROLLER_IP = topo.crtlip
    CONTROLLER_PORT = topo.crtlport
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.addController( CONTROLLER_NAME,controller=RemoteController,
                      ip=CONTROLLER_IP,
                      port=CONTROLLER_PORT)

    net.start()
    #dumpNodeConnections(net.hosts)
    #net.pingAll()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    if os.getuid() != 0:
        info("You are NOT root")
    elif os.getuid() == 0:
        RunTest()
