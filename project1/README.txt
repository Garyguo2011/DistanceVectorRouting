Project 1 Distance Vector Routing

1. Name: Xu He, Xinran Guo

2. (1) How could we divide this problem into certain modularities so that we can debug or change 
       our code more easily
   (2) When some link is down, how could we handle the cost change for correlated paths
   (3) Where to add 50 cap implementation into the code
   
3. Bellman-Ford Algorithm

4. The code can handle link weights and incremental updates. As for link weights, the main concern is that 
the path with more hops may be shorter than the one with less hops, and also we can change the weight of 
a link during the run. As for the incremental updates, we need to specify which distance is changed and 
put the changed distances into a list and let an independent function to handle send those changes.

