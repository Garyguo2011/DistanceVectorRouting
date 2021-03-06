from sim.api import *
from sim.basics import *
import time

class Hub (Entity):
  """ A simple hub -- floods all packets """

  def handle_rx (self, packet, port):
    """
    Just sends the packet back out of every port except the one it came
    in on.
    """
    if type(packet) is DiscoveryPacket:
    	print ("Router: {3} DiscoveryPacket: {0} -> {1}: Latency: {2}".format(packet.src.name, packet.dst, packet.latency, str(self.name)))
    # self.send(packet, port, flood=True
