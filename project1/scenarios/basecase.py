import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:
           s2--s3--s4   
          /          \  
        h1            s5 --- h2
          \          /  
           ---s1-----    

    run start()
        h1.ping(h2)
    expected path: h1 -> s1 -> s5 -> h2
    """

    switch_type.create('s1')
    switch_type.create('s2')
    switch_type.create('s3')
    switch_type.create('s4')
    switch_type.create('s5')

    host_type.create('h1')
    host_type.create('h2')


    topo.link(s1, h1)
    topo.link(s1, s5)
    topo.link(s2, h1)
    topo.link(s2, s3)
 
    topo.link(s4, s3)
    topo.link(s4, s5)
    topo.link(s5, h2)
