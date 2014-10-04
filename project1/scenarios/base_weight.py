import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

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

    switch_type.create('x')
    switch_type.create('y')
    switch_type.create('z')
    host_type.create('h1')
    host_type.create('h2')


    topo.link(x, y, 2)
    topo.link(y, z, 1)
    topo.link(x, z, 7)
    topo.link(h1, x, 1)
    topo.link(h2, z, 1)

