import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub
import sim.topo as topo

def create (switch_type = Hub, host_type = BasicHost):
    """
    Creates a topology with loops that looks like:
     h1--A ----- D--h4
         |\     /|
         | --C-- |
         |       |
     h2--B ----- E--h3
    with link weight A<->B = 2
                     A<->D = 7
                     A<->C = 1
                     B<->E = 5
                     C<->D = 2
                     D<->E = 3
                     h1<->A = 1
                     h2<->B = 1
                     h3<->E = 1
                     h4<->D = 1
    run h1.ping(h4)
    expected path: A -> C -> D

    run h1.ping(h3)
    expected path: A -> C -> D -> E

    run h2.ping(h4)
    expected path: B -> A -> C -> D
    """

    switch_type.create('A')
    switch_type.create('B')
    switch_type.create('C')
    switch_type.create('D')
    switch_type.create('E')
    host_type.create('h1')
    host_type.create('h2')
    host_type.create('h3')
    host_type.create('h4')


    topo.link(A, B, 2)
    topo.link(A, D, 7)
    topo.link(A, C, 1)
    topo.link(B, E, 5)
    topo.link(C, D, 2)
    topo.link(D, E, 3)
    topo.link(A, h1, 1)
    topo.link(B, h2, 1)
    topo.link(E, h3, 1)
    topo.link(D, h4, 1)


