import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:
         x ----- y
         |       |
         |       |
         v ----- z
    with link weight x<->y = 1
                     y<->z = 3
                     z<->v = 1
                     v<->x = 2
    run start()
        x.ping(z)
    expected path: x -> v -> z
    """

    host_type.create('x')
    switch_type.create('y')
    host_type.create('z')
    switch_type.create('v')



    topo.link(x, y, 1)
    topo.link(y, z, 3)
    topo.link(z, v, 1)
    topo.link(v, x, 2)

