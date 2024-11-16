# sudo mn --custom topo_custom.py --topo mytopo --mac --controller=remote,ip=127.0.0.1,port=6633 --switch ovsk
from mininet.topo import Topo

class MyTopo(Topo):
	def __init__(self):
		# initilaize topology
		Topo.__init__(self)
		# add hosts
		h1 = self.addHost('h1')
		h2 = self.addHost('h2')
		h3 = self.addHost('h3')
		h4 = self.addHost('h4')
		h5 = self.addHost('h5')
		h6 = self.addHost('h6')
		# add switches
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')
		# add links
		self.addLink(h1, s1, 0, 1)
		self.addLink(h2, s1, 0, 2)
		self.addLink(h3, s1, 0, 3)
		self.addLink(h4, s2, 0, 1)
		self.addLink(h5, s2, 0, 2)
		self.addLink(h6, s2, 0, 3)
		self.addLink(s1, s2, 4, 4)
topos = {'mytopo': (lambda: MyTopo())}
