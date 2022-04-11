from __future__ import print_function
from __future__ import absolute_import

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from .BaseTopology import SimpleTopology

# Creates a two systems topology connected to 1 DM
# each system has 1 core each, the DM has 1 directory
# One L1 (and L2, depending on the protocol) are connected to each router.
# the core router is connected point-to-point with directory router
# XY routing is enforced (using link weights) to guarantee deadlock freedom.

class DM_2core(SimpleTopology):
    description='DM_2core'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        assert(options.num_cpus == 2)

        # one exta router for directory (DM)
        num_routers = options.num_cpus + 1

        link_latency = options.link_latency

        # First determine which nodes are cache cntrls vs. dirs vs. dma
        l1cache_nodes = [] # holds per core private L1 caches
        l2cache_nodes = [] # holds per socket private L2 caches
        dir_nodes = []
        dma_nodes = []
        for node in nodes:
            if node.type == 'L1Cache_Controller':
                l1cache_nodes.append(node)
            elif node.type == 'L2Cache_Controller':
                l2cache_nodes.append(node)
            elif node.type == 'Directory_Controller':
                dir_nodes.append(node)
            elif node.type == 'DMA_Controller':
                dma_nodes.append(node)

        assert(len(l2cache_nodes) == 2)
        assert(len(dir_nodes) == 1)
        assert(len(dma_nodes) == 0)          

        # Create the routers
        routers = [Router(router_id=i) \
            for i in range(num_routers)]
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0

        # Connect each L1 and L2 cache controller to the appropriate router
        ext_links = []
        for (i, n) in enumerate(l1cache_nodes):
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[i],
                                    latency = link_latency))
            link_count += 1

        for (i, n) in enumerate(l2cache_nodes):
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[i],
                                    latency = link_latency))
            link_count += 1

        # Connect the dir nodes to the last router
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[0],
                                int_node=routers[2],
                                latency = link_latency))
        link_count += 1
        
        network.ext_links = ext_links

        # Create the internal links between routers
        int_links = []

        int_links.append(IntLink(link_id=link_count,
                                src_node=routers[0],
                                dst_node=routers[2],
                                latency = link_latency,
                                weight=1))
        print_connection("Router ", get_router_id(routers[0]),
		                "Router ", get_router_id(routers[2]),
			            link_count)
        link_count += 1

        int_links.append(IntLink(link_id=link_count,
                                src_node=routers[1],
                                dst_node=routers[2],
                                latency = link_latency,
                                weight=1))
        print_connection("Router ", get_router_id(routers[1]),
                        "Router ", get_router_id(routers[2]),
                        link_count)                                
        link_count += 1

        int_links.append(IntLink(link_id=link_count,
                                src_node=routers[2],
                                dst_node=routers[0],
                                latency = link_latency,
                                weight=1))
        print_connection("Router ", get_router_id(routers[2]),
                        "Router ", get_router_id(routers[0]),
                        link_count)                                
        link_count += 1
        
        int_links.append(IntLink(link_id=link_count,
                                src_node=routers[2],
                                dst_node=routers[1],
                                latency = link_latency,
                                weight=1))
        print_connection("Router ", get_router_id(routers[2]),
                        "Router ", get_router_id(routers[1]),
                        link_count)                                
  
        network.int_links = int_links

def get_router_id(node) :
    return str(node).split('.')[3].split('routers')[1]


def print_connection(src_type, src_id, dst_type, dst_id, link_id):
    print (str(src_type) + "-" + str(src_id) + " connected to " + \
          str(dst_type) + "-" + str(dst_id) + " via Link-" + str(link_id))