import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost, RoutingUpdate, DiscoveryPacket
from hub import Hub
import sim.topo as topo
from sim.api import *


class ReceiveEntity (Entity):
    def __init__(self, expected, to_announce, time):
        self.expect = expected
        self.announce = to_announce
        self.num_rx = 0
        if(self.announce):
            self.timer = create_timer(time, self.send_announce)    

    def handle_rx(self, packet, port):
        if(not isinstance(packet, RoutingUpdate) and not isinstance(packet, DiscoveryPacket)):
            self.num_rx += 1
            if(not self.expect):
                print("Sent packet to unexpected destination!")
                os._exit(50)
            else:
                if(len(packet.trace) != len(self.expect) + 1):
                    print("Incorrect packet path!") 
                    print(packet.trace)
                    return
                
                for i in range(len(self.expect)):
                    if(packet.trace[i] != self.expect[i]):
                        print("Incorrect packet path!")
                        print(packet.trace[i])
                        print(self.expect[i])
                        return
                        #os._exit(50)
                os._exit(0) 
    
    def send_announce(self):
        if(self.announce):
            update = RoutingUpdate()
            update.add_destination(self.announce[0], self.announce[1])
            self.send(update, flood=True)




def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:
     h1--x ----- y
         |       |
         |       a
         |       |
         v ----- z--h2
    with link weight x<->y = 5
                     y<->a = 3
                     a<->z = 4
                     z<->v = 1
                     v<->x = 2
    run start()
        h1.ping(h2)
    expected path: x -> v -> z
    """

    switch_type.create('s1')
    switch_type.create('s2')
    switch_type.create('s3')
    switch_type.create('s4')
    switch_type.create('s5')

    switch_type.create('s6')
    switch_type.create('s7')
    switch_type.create('s8')
    switch_type.create('s9')


    host_type.create('h1a')
    host_type.create('h1b')
    host_type.create('h2a')
    host_type.create('h2b')

    ReceiveEntity.create('sneakylistener', [s7, s9, s8, s6, s2, s5, s4, s1] , [h1a, 1], 5)


    topo.link(sneakylistener, h1a)
    topo.link(sneakylistener, s1)
    topo.link(s1, h1b)
    topo.link(s2, s6)
    topo.link(s6, s8)
    topo.link(s8, s9)
    topo.link(s9, h2b)
    topo.link(s6, s7)
    topo.link(s7, s9)
    topo.link(s7, h2a)
    

    topo.link(s1, s3)
    topo.link(s3, s2)

    topo.link(s1, s4)
    topo.link(s4, s5)
    topo.link(s5, s2)

