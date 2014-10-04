from sim.api import *
from sim.basics import *

'''
Create your distance vector router in this file.
'''
class DVRouter (Entity):
    def __init__(self):
        # Add your code here!
        # neighbor_list <neighbor, distance>
        # self.neighbor_list = {str(self.name): 0}
        self.neighbor_list = {}
        # distance_Vector - <(src, des), distance>
        # self.distance_Vector = {(str(self.name), str(self.name)): 0}
        self.distance_Vector = {}
        # forward_table - < destination, (port_number, distance) >
        # self.forward_table = {str(self.name): (None, 0)}
        self.forward_table = {}
        

    def handle_rx (self, packet, port):
        # Add your code here!
        if type(packet) is DiscoveryPacket:
            self.handle_discoveryPacket(packet,port)
            # print ("Router: {3} DiscoveryPacket: {0} -> {1}: Latency: {2}".format(packet.src.name, packet.dst, packet.latency, str(self.name)))
            # self.detail()
        elif type(packet) is RoutingUpdate:
            self.handle_RoutingUpdatePacket(packet,port)
            print ("Router: {2} RoutingUpdate: {0} -> {1}".format(packet.src, packet.dst, str(self.name)))
            print(packet.str_routing_table())
            self.detail()
        else:
            self.handle_otherPacket(packet,port)


    def handle_discoveryPacket (self, packet, port):
        distance = packet.latency
        source = str(self.name)
        destination = packet.src.name

        updatePacket = RoutingUpdate()

        if packet.is_link_up == True:
            self.neighbor_list[destination] = distance
            # <(source, destination) : distance>
            dv_key = (source, destination)
            if self.distance_Vector.has_key(dv_key):
                # need more hanle here
                print("distance_Vector has has_key: {0}".format(dv_key))
                # Compare with Distance vector and forwarding table
                # If AC current distance < AC distance at Distance vector: update needed
                # Otherwise no update needed
            else:
                self.distance_Vector[dv_key] = distance
                self.forward_table[packet.src.name] = (port, distance)
                updatePacket.add_destination(destination, distance)
        else:
            # Hanld link down problem
            print("Hanle link down problem")

        # Send routing update to all neighbors
        if len(updatePacket.all_dests()) != 0:
            self.send(updatePacket, port=None, flood=True)


    def handle_RoutingUpdatePacket (self, packet, port):
        income_source = packet.src.name
        backPacket = RoutingUpdate()
        updatePacket = RoutingUpdate()
        me = str(self.name)

        for destination in packet.all_dests():
            self.distance_Vector[(income_source, destination)] = packet.get_distance(destination)
            newOption = self.neighbor_list[income_source] + self.distance_Vector[(income_source, destination)]
            if self.distance_Vector.has_key((me, destination)):
                # Think about float("inf") == float("inf")
                if newOption < self.distance_Vector[(me, destination)]:
                    self.distance_Vector[(me, destination)] = newOption
                    self.forward_table[destination] = (port, newOption)
                    # Poisioned Revered
                    backPacket.add_destination(destination, float("inf"))
                    updatePacket.add_destination(destination, newOption)
                elif newOption == self.distance_Vector[(me, destination)]:
                    currentPort = self.forward_table[destination][0]
                    if port < currentPort:
                        self.forward_table[destination] = (port, newOption)
                        # Poisioned Revered
                        backPacket.add_destination(destination, float("inf"))
                        updatePacket.add_destination(destination, newOption)
            else:
                self.distance_Vector[(me, destination)] = newOption
                self.forward_table[destination] = (port, newOption)
                backPacket.add_destination(destination, float("inf"))
                updatePacket.add_destination(destination, newOption)

        # Send routing update to all neighbors
        if len(updatePacket.all_dests()) != 0:
            self.send(updatePacket, port, flood=True)
        if len(backPacket.all_dests()) != 0:
            self.send(backPacket, port, flood=False)

    def handle_otherPacket (self, packet, port):
        # how to deal with ttl
        if packet.dst.name != str(self.name):
            self.send(packet, self.forward_table[packet.dst.name][0], flood=False)

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


