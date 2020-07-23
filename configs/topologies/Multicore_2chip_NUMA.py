from __future__ import print_function
from __future__ import absolute_import

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from .BaseTopology import SimpleTopology

# Creates a Mesh topology with 4 directories, one at each corner.
# One L1 (and L2, depending on the protocol) are connected to each router.
# XY routing is enforced (using link weights) to guarantee deadlock freedom.

class Multicore_2chip_NUMA(SimpleTopology):
    description='Multicore_2chip_NUMA'
    num_numa_nodes = 2

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        num_routers = options.num_cpus
        num_rows = options.mesh_rows

        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        if options.mem_replication:
            qpi_link_latency = 1
        else:
            qpi_link_latency = options.qpi_latency # FIXME static qpi latency


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

        # Obviously the number or rows must be <= the number of routers
        # and evenly divisible.  Also the number of caches must be a
        # multiple of the number of routers and the number of directories
        # must be four.
        assert(num_rows > 0 and num_rows <= num_routers)
        num_columns = int(num_routers / num_rows)
        assert(num_columns * num_rows == num_routers)
        l1caches_per_router, remainder = divmod(len(l1cache_nodes), num_routers)
        assert(remainder == 0)
        assert(len(l2cache_nodes) == 2)
        assert(len(dir_nodes) == 2)

        # Create the routers in the mesh
        routers = [Router(router_id=i) \
            for i in range(num_routers)]
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0

        # Connect each cache controller to the appropriate router
        ext_links = []
        for (i, n) in enumerate(l1cache_nodes):
            cntrl_level, router_id = divmod(i, num_routers)
            assert(cntrl_level < l1caches_per_router)
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[router_id],
                                    latency = link_latency))
            link_count += 1

        # Connect the l2 nodes to the corners - router[0] and router[num_routers-num_cols]
        ext_links.append(ExtLink(link_id=link_count, ext_node=l2cache_nodes[0],
                                int_node=routers[0],
                                latency = link_latency))
        link_count += 1
        ext_links.append(ExtLink(link_id=link_count, ext_node=l2cache_nodes[1],
                                int_node=routers[num_routers - num_columns],
                                latency = link_latency))
        link_count += 1

        # Connect the dir nodes to the corners - router[0] and router[num_routers-num_cols]
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[0],
                                int_node=routers[0],
                                latency = link_latency))
        link_count += 1
        ext_links.append(ExtLink(link_id=link_count, ext_node=dir_nodes[1],
                                int_node=routers[num_routers - num_columns],
                                latency = link_latency))
        link_count += 1

        # Connect the dma nodes to router 0.  These should only be DMA nodes.
        # we dont have any DMA nodes (Sysem emulation config)
        for (i, node) in enumerate(dma_nodes):
            assert(node.type == 'DMA_Controller')
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                     int_node=routers[0],
                                     latency = link_latency))

        network.ext_links = ext_links

        # Create the mesh links.
        int_links = []

        # East output to West input links (weight = 1)
        for row in range(num_rows):
            for col in range(num_columns):
                if (col + 1 < num_columns):
                    east_out = col + (row * num_columns)
                    west_in = (col + 1) + (row * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[east_out],
                                             dst_node=routers[west_in],
                                             src_outport="East",
                                             dst_inport="West",
                                             latency = link_latency,
                                             weight=1))
		    print_connection("Router ", get_router_id(routers[east_out]),
				     "Router ", get_router_id(routers[west_in]),
				     link_count)
                    link_count += 1

        # West output to East input links (weight = 1)
        for row in range(num_rows):
            for col in range(num_columns):
                if (col + 1 < num_columns):
                    east_in = col + (row * num_columns)
                    west_out = (col + 1) + (row * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[west_out],
                                             dst_node=routers[east_in],
                                             src_outport="West",
                                             dst_inport="East",
                                             latency = link_latency,
                                             weight=1))
		    print_connection("Router ", get_router_id(routers[west_out]),
				     "Router ", get_router_id(routers[east_in]),
				     link_count)
                    link_count += 1

        # North output to South input links (weight = 2)
        for col in range(num_columns):
            for row in range(num_rows):
                if ( ((row + 1) < num_rows) and ((row + 1) != (num_rows/2)) ):
                    north_out = col + (row * num_columns)
                    south_in = col + ((row + 1) * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[north_out],
                                             dst_node=routers[south_in],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency = link_latency,
                                             weight=2))
		    print_connection("Router ", get_router_id(routers[north_out]),
				     "Router ", get_router_id(routers[south_in]),
				     link_count)
                    link_count += 1

        # South output to North input links (weight = 2)
        for col in range(num_columns):
            for row in range(num_rows):
                if ( ((row + 1) < num_rows) and ((row + 1) != (num_rows/2)) ):
                    north_in = col + (row * num_columns)
                    south_out = col + ((row + 1) * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[south_out],
                                             dst_node=routers[north_in],
                                             src_outport="South",
                                             dst_inport="North",
                                             latency = link_latency,
                                             weight=2))
		    print_connection("Router ", get_router_id(routers[south_out]),
				     "Router ", get_router_id(routers[north_in]),
				     link_count)
                    link_count += 1

        # create QPI link North to south and south to north
        col = (num_columns -1) /2
        row = (num_rows-1) /2
        north = col + (row * num_columns)
        south = col + ((row + 1) * num_columns)
        int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[north],
                                             dst_node=routers[south],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency = qpi_link_latency,
                                             weight=2))
        print_connection("Router ", get_router_id(routers[north]),
			 "Router ", get_router_id(routers[south]),
			 link_count)
        link_count += 1
        int_links.append(IntLink(link_id=link_count,
                                    src_node=routers[south],
                                    dst_node=routers[north],
                                    src_outport="South",
                                    dst_inport="North",
                                    latency = qpi_link_latency,
                                    weight=2))
        print_connection("Router ", get_router_id(routers[south]),
		         "Router ", get_router_id(routers[north]),
			 link_count)
        link_count += 1        

        int_links.append

        network.int_links = int_links

def get_router_id(node) :
    return str(node).split('.')[3].split('routers')[1]


def print_connection(src_type, src_id, dst_type, dst_id, link_id):
    print (str(src_type) + "-" + str(src_id) + " connected to " + \
          str(dst_type) + "-" + str(dst_id) + " via Link-" + str(link_id))
