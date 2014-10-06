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
            self.neighbor_list[str(self.name)] = (None, 0)
            self.distance_Vector[(str(self.name),str(self.name))] = 0
            self.forward_table[str(self.name)] = None

        if type(packet) is DiscoveryPacket:
            self.handle_discoveryPacket(packet,port)
            print ("*******Router: {3} DiscoveryPacket: {0} -> {1}: Latency: {2}".format(packet.src.name, packet.dst, packet.latency, str(self.name)))
            # self.detail()
        elif type(packet) is RoutingUpdate:
            print ("Router: {2} RoutingUpdate: {0} -> {1}".format(packet.src, packet.dst, str(self.name)))
            print(packet.str_routing_table())
            print("before")
            self.detail()
            # if str(self.name) == "x" or str(self.name) == "y":
                # print ("Router: {2} RoutingUpdate: {0} -> {1}".format(packet.src, packet.dst, str(self.name)))
                # print("before")
                # self.detail()
            # self.detail()
            # if packet.str_routing_table() == "{'h1': 1}":
                # print("##################################")
                # self.detail()
            self.handle_RoutingUpdatePacket(packet,port)
            print("after")
            # if str(self.name) == "x" or str(self.name) == "y":
            self.detail()
            
            # self.detail()
        else:
            self.handle_otherPacket(packet,port)


    def handle_discoveryPacket (self, packet, port):
        me = str(self.name)
        changes = {}

        if packet.is_link_up == True:
            # increase 
            self.livePort.add(port)
            if self.neighbor_list.has_key(packet.src.name):
                change = packet.latency - self.neighbor_list[packet.src.name][0]
                self.neighbor_list[packet.src.name] = (port, packet.lantency)
                for k, v in self.forward_table.items():
                    if v == port:
                        self.distance_Vector[(me, k)] += change
                        if (self.neighbor_list.has_key[k] and 
                            (self.neighbor_list[k][1] < self.distance_Vector[(me, k)]) or
                             (self.neighbor_list[k][1] == self.distance_Vector[(me, k)] and self.neighbor_list[k][0] < self.forward_table[k])):
                            self.distance_Vector[(me, k)] = self.neighbor_list[k][1]
                            self.forward_table[k] = self.neighbor_list[k][0]
                        changes[k] = (self.forward_table[k], self.distance_Vector[(me, k)])
            else:
                self.neighbor_list[packet.src.name] = (port, packet.latency)
                if (not self.distance_Vector.has_key((me, packet.src.name))) or (self.neighbor_list[packet.src.name][1] < self.distance_Vector[(me, packet.src.name)]) or (self.neighbor_list[packet.src.name][1] == self.distance_Vector[(me, packet.src.name)] and port < self.forward_table[packet.src.name][0]):
                    self.distance_Vector[(me, packet.src.name)] = self.neighbor_list[packet.src.name][1]
                    self.forward_table[packet.src.name] = port
                    changes[packet.src.name] = (self.forward_table[packet.src.name], self.distance_Vector[(me, packet.src.name)])
                # for first time neighbor
                updatePacket = RoutingUpdate()
                for k, v in self.forward_table.items():
                    updatePacket.add_destination(k, self.distance_Vector[(me, k)])
                self.send(updatePacket, port, flood=False)
        else:
            if port in self.livePort:
                self.livePort.remove(port)
                if self.neighbor_list.has_key(packet.src.name):
                    self.neighbor_list[packet.src.name] = (port, float('inf'))
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
        if me == "x":
            print("in handle_discoveryPacket", changes)        
        self.sendRoutingUpdate(changes)

    def handle_RoutingUpdatePacket (self, packet, port):
        me = str(self.name)
        changes = {}
        for dst in packet.all_dests():
            self.distance_Vector[(packet.src.name, dst)] = packet.get_distance(dst)
            if self.forward_table.has_key(dst) and port == self.forward_table[dst]:
                self.distance_Vector[(me, dst)] = self.neighbor_list[packet.src.name][1] + self.distance_Vector[(packet.src.name, dst)]
                if self.neighbor_list.has_key(dst) and self.neighbor_list[dst][1] < self.distance_Vector[(me, dst)]:
                    self.distance_Vector[(me, dst)] = self.neighbor_list[dst][1]
                    self.forward_table[dst] = self.neighbor_list[dst][0]
                    changes[dst] = (self.forward_table[dst], self.distance_Vector[(me, dst)])
        changes = dict(changes.items() + self.calculateDV().items())
        self.sendRoutingUpdate(changes)

    def calculateDV (self):
        me = str(self.name)
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
        if me == "x":
            print('in calculateDV',changes)
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
                if str(self.name) == "x":
                    print('in sendRoutingUpdate',port, updatePacket.str_routing_table())

        
            

            # otherUpdate = RoutingUpdate()
            # for k, v in changes.items():
            #     otherUpdate.add_destination(k, v[1])
            # self.send(otherUpdate, self.livePort, flood=True)
                
    def handle_otherPacket (self, packet, port):
        # how to deal with ttl
        if packet.dst.name != str(self.name):
            self.send(packet, self.forward_table[packet.dst.name], flood=False)

    def detail(self):
        print("----------------------------------")
        print("Router: {0}".format(str(self.name)))
        
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


    




    # def handle_discoveryPacket (self, packet, port):    
        # distance = packet.latency
        # me = str(self.name)
        # destination = packet.src.name
        # dv_key = (me, destination)

        # updatePacket = RoutingUpdate()

        # if packet.is_link_up == True:
        #     self.neighbor_list[destination] = (port, distance)
        #     # <(source, destination) : distance>
        #     if self.distance_Vector.has_key(dv_key):
        #         # need more hanle here
        #         # print("distance_Vector has has_key: {0}".format(dv_key))
        #         # New link up
        #         # Compare with Distance vector and forwarding table If AC current distance < AC distance at Distance vector: update neede Otherwise no update needed
        #         if distance < self.distance_Vector[dv_key]:
        #             self.distance_Vector[dv_key] = distance
        #             self.forward_table[destination] = port
        #             updatePacket.add_destination(destination, distance)
        #     else:
        #         self.distance_Vector[dv_key] = distance
        #         self.forward_table[destination] = port
        #         updatePacket.add_destination(destination, distance)
        # else:
        #     # Hanld link down problem
        #     print("Hanle link down problem")
        #     # self.neighbor_list.pop(destination)
        #     self.neighbor_list[destination] = (None, float("inf"))
        #     if self.forward_table[destination] == port:
        #         for k, v in self.forward_table.items():
        #             if v == port:
        #                 self.distance_Vector[(me, k)] = float("inf")
        #                 updatePacket.add_destination(k, self.distance_Vector[(me, k)])
        #         print("DiscoveryPacket.lantency {0}".format(distance))
        #         # self.detail()

        # # Send routing update to all neighbors
        # if len(updatePacket.all_dests()) != 0:
        #     self.send(updatePacket, port=None, flood=True)



        


        # updatePacket = RoutingUpdate()
        # backPacket = RoutingUpdate()
        # excludePortList = [port]
        # me = str(self.name)
        # dv_changed = False

        # for src, dst in self.distance_Vector.items():
        #     if src != me:
        #         newOption = self.neighbor_list[src][1] + self.distance_Vector[(src, dst)]
        #         if src == income_source:
        #             if self.distance_Vector.has_key(me, dst):
        #                 if port == self.forward_table[destination]:
        #                     if (self.neighbor_list.has_key(destination) and
        #                          (self.neighbor_list[destination][1] < newOption or
        #                             (self.neighbor_list[destination][1] == newOption and
        #                             self.neighbor_list[destination][0] < port))):
        #                         self.distance_Vector[(me, destination)] = self.neighbor_list
        #                 else:

        #             else:


        #         else:







                
        #         if self.distance_Vector.has_key((me, dst)):

        #         else:
        #             self.distance_Vector[(me, dst)] = newOption
        #             self.forward_table [dst] = port
        #             if src == income_source:
        #                 backPacket.add_destination(dst, float('inf'))
        #             updatePacket.add_destination(dst, newOption)





        # for destination in packet.all_dests():
        #     self.distance_Vector[(income_source, destination)] = packet.get_distance(destination)
        #     newOption = self.neighbor_list[income_source][1] + self.distance_Vector[(income_source, destination)]
        #     if self.distance_Vector.has_key((me, destination)):
        #         if port == self.forward_table[destination]:
        #             if (self.neighbor_list.has_key(destination) and
        #                  (self.neighbor_list[destination][1] < newOption or
        #                     (self.neighbor_list[destination][1] == newOption and
        #                     self.neighbor_list[destination][0] < port))):
        #                 self.distance_Vector[(me, destination)] = self.neighbor_list[destination][1]
        #                 self.forward_table[destination] = self.neighbor_list[destination][0]               # Port number
        #                 backPacket.add_destination(destination, self.neighbor_list[destination][0])        # Cancel Poisoned Reversed
        #             else:
        #                 self.distance_Vector[(me, destination)] = newOption
        #                 backPacket.add_destination(destination, float('inf'))
        #             dv_changed = True
        #         else:
        #             if (newOption < self.distance_Vector[(me, destination)] or
        #                  (newOption == self.distance_Vector[(me, destination)] and 
        #                     port < self.forward_table[destination])):
        #                 self.distance_Vector[(me, destination)] = newOption
        #                 self.forward_table[destination] = port
        #                 backPacket.add_destination(destination, float('inf'))
        #                 dv_changed = True
        #     else:
        #         self.distance_Vector[(me, destination)] = newOption
        #         self.forward_table [destination] = port
        #         # poisoned reversed
        #         backPacket.add_destination(destination, float('inf'))
        #         dv_changed = True

        # if dv_changed:
        #     updatePacket = RoutingUpdate()
        #     for k, v in self.distance_Vector.items():
        #         if k[0] == me:
        #             updatePacket.add_destination(k[1], v)
        #     self.send(updatePacket, port, flood=True)

        # if len(backPacket.all_dests()) != 0:
        #     # for k, v in self.distance_Vector.items():
        #     #     if k[0] == me and not k[0] in backPacket.all_dests():
        #     #         backPacket.add_destination(k[1], v)
        #     self.send(backPacket, port, flood=False)

        # income_source = packet.src.name
        # backPacket = RoutingUpdate()
        
        # updatePacket = RoutingUpdate()
        # updatePort = [port]
        
        # # specialPRpacket = RoutingUpdate()
        # # specialPort = []

        # me = str(self.name)
        # # portList1=[]
        # # protList2

        # for destination in packet.all_dests():
        #     self.distance_Vector[(income_source, destination)] = packet.get_distance(destination)
        #     newOption = self.neighbor_list[income_source][1] + self.distance_Vector[(income_source, destination)]
        #     if self.distance_Vector.has_key((me, destination)):
        #         # Handle link down 
        #         # if the way we go to destination has to pass to the router just send us packet
        #         # means some link changes lantency or link down
        #         if port == self.forward_table[destination]:
        #             # print("on this path")
        #             # print(destination)
        #             # print("port: {0}".format(port))
        #             # print("forward_table[destination]: {0}".format(self.forward_table[destination]))
        #             # print('newOption {0}'.format(newOption))
        #             # print('self.distance_Vector[(income_source, destination)] {}'.format(self.distance_Vector[(income_source, destination)]))
        #             # print(packet.str_routing_table())
        #             if self.neighbor_list.has_key(destination) and self.neighbor_list[destination][1] < newOption:
        #                 self.distance_Vector[(me, destination)] = self.neighbor_list[destination][1]
        #                 self.forward_table[destination] = self.neighbor_list[destination][0]      # port number
        #                 for k, v in self.distance_Vector.items():
        #                     if k[0] == me:
        #                         updatePacket.add_destination(k[1],v)      # send all option to destion
        #                         backPacket.add_destination(k[1], v)       # cancel poison reversed

        #                 # specialPRpacket.add_destination(destination, float('inf'))                          # to new port to poision reverse
        #                 # specialPort.append(self.neighbor_list[destination][0])
        #                 # updatePort.append(self.neighbor_list[destination][0])
        #             elif self.neighbor_list.has_key(destination) and self.neighbor_list[destination][1] == newOption:
        #                 if self.neighbor_list[destination][0] < port:
        #                     self.distance_Vector[(me, destination)] = self.neighbor_list[destination][1]
        #                     self.forward_table[destination] = self.neighbor_list[destination][0]      # port number
        #                     updatePacket.add_destination(destination, self.neighbor_list[destination][1])
        #                     backPacket.add_destination(destination,self.neighbor_list[destination][1])
        #                 else:
        #                     self.distance_Vector[(me, destination)] = newOption
        #                     updatePacket.add_destination(destination, newOption)
        #                     backPacket.add_destination(destination, float('inf'))
        #             else:
        #                 self.distance_Vector[(me, destination)] = newOption
        #                 updatePacket.add_destination(destination, newOption)
        #                 backPacket.add_destination(destination, float('inf'))
        #             # if newOption > self.distance_Vector[(me, destination)]: # link increase or link down
        #             #     if self.neighbor_list.has_key(destination):
        #             #         if newOption > self.neighbor_list[destination][1]:
        #             #             self.distance_Vector[(me, destination)] = self.neighbor_list[destination][1]
        #             #             updatePacket.add_destination(destination, self.neighbor_list[destination][1])
        #             #             # cancel poisoned reversed
        #             #             backPacket.add_destination(destination, self.neighbor_list[destination][1])
        #             #         elif newOption == self.neighbor_list[destination][1]:
        #             #             if self.neighbor_list[destination][0] < port:
        #             #                 self.distance_Vector[(me, destination)] = self.neighbor_list[destination][1]
        #             #                 updatePacket.add_destination(destination, self.neighbor_list[destination][1])
        #             #                 # cancel poisoned reversed
        #             #                 backPacket.add_destination(destination, self.neighbor_list[destination][1])
        #             #         else:
        #             #             self.distance_Vector[(me, destination)] = newOption
        #             #             updatePacket.add_destination(destination, newOption)
        #             #             # remain poisoned reversed
        #             #     else:
        #             #         self.distance_Vector[(me, destination)] = newOption
        #             #         updatePacket.add_destination(destination, newOption)
        #             #         # remain poisoned reversed
        #             # elif newOption < self.distance_Vector[(income_source, destination)]:
        #             #     self.distance_Vector[(me, destination)] = newOption
        #             #     updatePacket.add_destination(destination, newOption)
        #             #     # remain poisoned reversed
        #         else:   # handle normal cases
        #             # Think about float("inf") == float("inf")
        #             print('destination {0}'.format(destination))
        #             print('newOption {0}'.format(newOption))
        #             if newOption < self.distance_Vector[(me, destination)]:
        #                 self.distance_Vector[(me, destination)] = newOption
        #                 self.forward_table[destination] = port
        #                 # Poisioned Revered
        #                 backPacket.add_destination(destination, float("inf"))
        #                 updatePacket.add_destination(destination, newOption)
        #             elif newOption == self.distance_Vector[(me, destination)]:
        #                 if port < self.forward_table[destination]:
        #                     self.forward_table[destination] = port
        #                     # Poisioned Revered
        #                     backPacket.add_destination(destination, float("inf"))
        #                     updatePacket.add_destination(destination, newOption)
        #     else:
        #         self.distance_Vector[(me, destination)] = newOption
        #         self.forward_table[destination] = port
        #         backPacket.add_destination(destination, float("inf"))
        #         updatePacket.add_destination(destination, newOption)

        # # self.detail()
        # # Send routing update to all neighbors
        # if len(updatePacket.all_dests()) != 0:
        #     self.send(updatePacket, updatePort, flood=True)
        # if len(backPacket.all_dests()) != 0:
        #     self.send(backPacket, port, flood=False)
        # # if len(specialPRpacket.all_dests()) != 0:
        #     # self.send(specialPRpacket, specialPort, flood=False)

        # print('#############################')
        # print(updatePacket.str_routing_table())
        # print(updatePort)
        # print(backPacket.str_routing_table())
        # print(port)
        # print(specialPRpacket.str_routing_table())
        # print(specialPort)
        # print('#############################')

