from sim.api import *
from sim.basics import *

import time

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
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
            # if (packet.src == 'h1a'):
            print ("*******Router: {3} DiscoveryPacket: {0} -> {1}: Latency: {2}".format(packet.src, packet.dst, packet.latency, self))
            # self.detail()
        elif type(packet) is RoutingUpdate:
            print ("Router: {2} RoutingUpdate: {0} -> {1}".format(packet.src, packet.dst, self))
            print(packet.str_routing_table())
            print("before")
            self.detail()
            # if self == "x" or self == "y":
                # print ("Router: {2} RoutingUpdate: {0} -> {1}".format(packet.src, packet.dst, self))
                # print("before")
                # self.detail()
            # self.detail()
            # if packet.str_routing_table() == "{'h1': 1}":
                # print("##################################")
                # self.detail()
            self.handle_RoutingUpdatePacket(packet,port)
            print("after")
            # if self == "x" or self == "y":
            self.detail()
            
            # self.detail()
        else:
            self.handle_otherPacket(packet,port)


    def handle_discoveryPacket (self, packet, port):
        me = self
        changes = {}

        if packet.is_link_up == True:
            # increase 
            self.livePort.add(port)
            if self.neighbor_list.has_key(packet.src):
                change = packet.latency - self.neighbor_list[packet.src][0]
                self.neighbor_list[packet.src] = (port, packet.latency)
                for k, v in self.forward_table.items():
                    if v == port:
                        self.distance_Vector[(me, k)] += change
                        if (self.neighbor_list.has_key(k) and 
                            (self.neighbor_list[k][1] < self.distance_Vector[(me, k)]) or
                             (self.neighbor_list[k][1] == self.distance_Vector[(me, k)] and self.neighbor_list[k][0] < self.forward_table[k])):
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
                        # else
                            # do nothing

        changes = dict(changes.items() + self.calculateDV().items())
        # if me == "x":
            # print("in handle_discoveryPacket", changes)        
        self.sendRoutingUpdate(changes)

    def handle_RoutingUpdatePacket (self, packet, port):
        me = self
        changes = {}
        for dst in packet.all_dests():
            self.distance_Vector[(packet.src, dst)] = packet.get_distance(dst)
            if self.forward_table.has_key(dst) and port == self.forward_table[dst]:
                self.distance_Vector[(me, dst)] = self.neighbor_list[packet.src][1] + self.distance_Vector[(packet.src, dst)]
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
        # self.detail()
        for k in self.distance_Vector.keys():
            src = k[0]
            dst = k[1]
            if src != me:
                option = self.neighbor_list[src][1] + self.distance_Vector[(src, dst)]
                # print(option)
                if ((not self.distance_Vector.has_key((me, dst))) or 
                    (option < self.distance_Vector[(me, dst)]) or
                    (option == self.distance_Vector[(me, dst)] and self.neighbor_list[src][0] < self.forward_table[dst])):
                    self.distance_Vector[(me, dst)] = option
                    self.forward_table[dst] = self.neighbor_list[src][0]
                    changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
            if src == me and (self.distance_Vector[(src, dst)] > 50 and self.distance_Vector[(src, dst)] != float('inf')):
                self.distance_Vector[(src, dst)] = float('inf')
                self.forward_table[dst] = None
                changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
        # if me == "x":
        #     print('in calculateDV',changes)
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
                # if self == "x":
                #     print('in sendRoutingUpdate',port, updatePacket.str_routing_table())
            # otherUpdate = RoutingUpdate()
            # for k, v in changes.items():
            #     otherUpdate.add_destination(k, v[1])
            # self.send(otherUpdate, self.livePort, flood=True)
                
    def handle_otherPacket (self, packet, port):
        # how to deal with ttl
        if packet.dst != self and self.distance_Vector[(self, packet.dst)] != float('inf'):
            self.send(packet, self.forward_table[packet.dst], flood=False)

    def detail(self):
        print("----------------------------------")
        print("Router: {0}".format(self))
        
        print("neighbor_list:")
        for k,v in self.neighbor_list.items():
            print ("{0}: {1}".format(k, v))
        
        print("forward_table:")
        for k,v in self.forward_table.items():
            print ("{0}: {1}".format(k, v))

        print("distance_Vector:")
        for k,v in self.distance_Vector.items():
            print ("{0}: {1}".format(k, v)) 
        print("----------------------------------")