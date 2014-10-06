from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # neighbor_list <neighbor, (port , distance)>
        self.neighbor_list = {}
        # distance_Vector - <(src, des), distance>
        self.distance_Vector = {}
        # forward_table - < destination, port_number >
        self.forward_table = {}
        self.livePort = set()

    def handle_rx (self, packet, port):
        # Add your code here!
        if (len(self.neighbor_list) == 0 and len(self.distance_Vector) == 0 and len(self.forward_table) == 0):
            self.neighbor_list[self] = (None, 0)
            self.distance_Vector[(self,self)] = 0
            self.forward_table[self] = None
        if type(packet) is DiscoveryPacket:
            self.handle_discoveryPacket(packet,port)
        elif type(packet) is RoutingUpdate:
            self.handle_RoutingUpdatePacket(packet,port)
        else:
            self.handle_otherPacket(packet,port)

    def handle_discoveryPacket (self, packet, port):
        me = self
        changes = {}
        
        # clean up garbage
        if self.neighbor_list.has_key(packet.src) and self.neighbor_list[packet.src][1] == float('inf'):
            self.neighbor_list.pop(packet.src)

        if packet.is_link_up == True:
            self.livePort.add(port)
            if self.neighbor_list.has_key(packet.src):
                change = packet.latency - self.neighbor_list[packet.src][0]
                self.neighbor_list[packet.src] = (port, packet.latency)
                for k, v in self.forward_table.items():
                    if v == port:
                        self.distance_Vector[(me, k)] += change
                        if (self.neighbor_list.has_key[k] and (self.neighbor_list[k][1] < self.distance_Vector[(me, k)]) or (self.neighbor_list[k][1] == self.distance_Vector[(me, k)] and self.neighbor_list[k][0] < self.forward_table[k])):
                            self.distance_Vector[(me, k)] = self.neighbor_list[k][1]
                            self.forward_table[k] = self.neighbor_list[k][0]
                        changes[k] = (self.forward_table[k], self.distance_Vector[(me, k)])
            else:
                self.neighbor_list[packet.src] = (port, packet.latency)
                if (not self.distance_Vector.has_key((me, packet.src))) or (self.neighbor_list[packet.src][1] < self.distance_Vector[(me, packet.src)]) or (self.neighbor_list[packet.src][1] == self.distance_Vector[(me, packet.src)] and port < self.forward_table[packet.src][0]):
                    self.distance_Vector[(me, packet.src)] = self.neighbor_list[packet.src][1]
                    self.forward_table[packet.src] = port
                    changes[packet.src] = (self.forward_table[packet.src], self.distance_Vector[(me, packet.src)])
                # for first time neighbor
                updatePacket = RoutingUpdate()
                for k, v in self.forward_table.items():
                    updatePacket.add_destination(k, self.distance_Vector[(me, k)])
                self.send(updatePacket, port, flood=False)
        else:
            if port in self.livePort:
                self.livePort.remove(port)
                if self.neighbor_list.has_key(packet.src):
                    self.neighbor_list[packet.src] = (port, float('inf'))
                    for k, v in self.forward_table.items():
                        if v == port:
                            self.distance_Vector[(me, k)] = float('inf')
                            if self.neighbor_list.has_key(k):
                                self.distance_Vector[(me, k)] = self.neighbor_list[k][1]
                                self.forward_table[k] = self.neighbor_list[k][0]
                                changes[k] = (self.forward_table[k], self.distance_Vector[(me, k)])
                            else:
                                changes[k] = (self.forward_table[k], self.distance_Vector[(me, k)])
        changes = dict(changes.items() + self.calculateDV().items())
        self.sendRoutingUpdate(changes)

    def handle_RoutingUpdatePacket (self, packet, port):
        me = self
        changes = {}
        for dst in packet.all_dests():
            self.distance_Vector[(packet.src, dst)] = packet.get_distance(dst)
            if self.forward_table.has_key(dst) and port == self.forward_table[dst]:
                if self.distance_Vector[(me, dst)] != self.neighbor_list[packet.src][1] + self.distance_Vector[(packet.src, dst)]:
                    self.distance_Vector[(me, dst)] = self.neighbor_list[packet.src][1] + self.distance_Vector[(packet.src, dst)]
                    changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
                if self.neighbor_list.has_key(dst) and self.neighbor_list[dst][1] < self.distance_Vector[(me, dst)]:
                    self.distance_Vector[(me, dst)] = self.neighbor_list[dst][1]
                    self.forward_table[dst] = self.neighbor_list[dst][0]
                    changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
        changes = dict(changes.items() + self.calculateDV().items())
        self.sendRoutingUpdate(changes)

    def calculateDV (self):
        me = self
        # < destination , (distance, port)>
        changes = {}
        for k in self.distance_Vector.keys():
            src = k[0]
            dst = k[1]
            if src != me:
                option = self.neighbor_list[src][1] + self.distance_Vector[(src, dst)]
                if ((not self.distance_Vector.has_key((me, dst))) or (option < self.distance_Vector[(me, dst)]) or (option == self.distance_Vector[(me, dst)] and self.neighbor_list[src][0] < self.forward_table[dst])):
                    self.distance_Vector[(me, dst)] = option
                    self.forward_table[dst] = self.neighbor_list[src][0]
                    changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
            if src == me and self.distance_Vector[(src, dst)] > 50 and self.distance_Vector[(src, dst)] != float('inf'):
                self.distance_Vector[(src, dst)] = float('inf')
                changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
        return changes

    def sendRoutingUpdate(self, changes):
        if len(changes.items()) != 0:
            for port in self.livePort:
                updatePacket = RoutingUpdate()
                for k,v in changes.items():
                    if port == v[0] and ((self.neighbor_list.has_key(k) and v[0] != self.neighbor_list[k][0]) or (not self.neighbor_list.has_key(k))):
                        # poisoned reversed
                        updatePacket.add_destination(k, float('inf'))
                    else:
                        updatePacket.add_destination(k, v[1])
                self.send(updatePacket, port, flood=False)

    def handle_otherPacket (self, packet, port):
        if packet.dst != self and self.distance_Vector[(self, packet.dst)] != float('inf'):
            self.send(packet, self.forward_table[packet.dst], flood=False)
