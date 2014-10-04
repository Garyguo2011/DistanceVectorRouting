import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:

                    h3
         ---------- /
         |        |/
         |  v --- w
         | /|\   /|\ 
         |/ | h1/ | \ 
   h0 -- u  |  /  |  z -- h5
         |  | /   | /
         |  |/    |/
         -- x---- y
            |     |
            h2    h4

    with link weight u<->v = 2
                     u<->x = 1
                     u<->w = 5
                     v<->x = 2
                     v<->w = 3
                     w<->y = 1
                     w<->x = 3
                     w<->z = 5
                     y<->x = 1
                     y<->z = 2
                     h0<->u = 1
                     h1<->v = 1
                     h2<->x = 1
                     h3<->w = 1
                     h4<->y = 1
                     h5<->z = 1
    """

    switch_type.create('u')
    switch_type.create('v')
    switch_type.create('x')
    switch_type.create('w')
    switch_type.create('y')
    switch_type.create('z')
    host_type.create('h0')
    host_type.create('h1')
    host_type.create('h2')
    host_type.create('h3')
    host_type.create('h4')
    host_type.create('h5')


    topo.link(u, v, 2)
    topo.link(u, x, 1)
    topo.link(u, w, 5)
    topo.link(v, x, 2)
    topo.link(v, w, 3)
    topo.link(w, y, 1)
    topo.link(w, x, 3)
    topo.link(w, z, 5)
    topo.link(y, x, 1)
    topo.link(y, z, 2)
    topo.link(u, h0, 1)
    topo.link(v, h1, 1)
    topo.link(x, h2, 1)
    topo.link(w, h3, 1)
    topo.link(y, h4, 1)
    topo.link(z, h5, 1)


