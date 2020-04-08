DEPENDENCY_THRESH = 'dependency_tresh'
AND_MEASURE_THRESH = 'and_measure_tresh'
MIN_DFG_OCCUR = 'min_dfg_occur'
MIN_ACT_COUNT = 'min_act_count'
DFG_PRE_CLEAN_NOISE_THRESH = 'dfg_pre_clean_noise_tresh'
LOOP_LENGTH_TWO_THRESH = 'loop_length_two_tresh'
default_parameters = {DEPENDENCY_THRESH:0.5,AND_MEASURE_THRESH:0.65,MIN_ACT_COUNT:1,MIN_DFG_OCCUR:1,DFG_PRE_CLEAN_NOISE_THRESH:0.05,LOOP_LENGTH_TWO_THRESH:0.5}

class Node:
    def __init__(self, heuristics_net, node_name, node_occ, is_start_node=False, is_end_node=False,
                 default_edges_color="#000000", node_type="frequency", net_name="", nodes_dictionary=None):

        self.heuristics_net = heuristics_net
        self.node_name = node_name
        self.node_occ = node_occ
        self.is_start_activity = is_start_node
        self.is_end_activity = is_end_node
        self.input_connections = {}
        self.output_connections = {}
        self.and_measures_in = {}
        self.and_measures_out = {}
        self.loop_length_two = {}
        self.output_couples_and_measure = []
        self.default_edges_color = default_edges_color
        self.node_type = node_type
        self.net_name = net_name
        self.nodes_dictionary = nodes_dictionary

    def add_output_connection(self, other_node, dependency_value, dfg_value, repr_color=None, repr_value=None):
        '''
        add an output to another node
        :param other_node:
        :param dependency_value:
        :param dfg_value:
        :param repr_color:
        :param repr_value:
        :return:
        '''
        if repr_color is None:
            repr_color = self.default_edges_color
        if repr_value is None:
            repr_value = dfg_value
        edge = Edge(self, other_node, dependency_value, dfg_value, repr_value, repr_color=repr_color,
                    edge_type=self.node_type, net_name=self.net_name)
        if other_node not in self.output_connections:
            self.output_connections[other_node] = []
        self.output_connections[other_node].append(edge)

    def add_input_connection(self, other_node, dependency_value, dfg_value, repr_color=None, repr_value=None):
        '''
        add an input to another node
        :param other_node:
        :param dependency_value:
        :param dfg_value:
        :param repr_color:
        :param repr_value:
        :return:
        '''
        if repr_color is None:
            repr_color = self.default_edges_color
        if repr_value is None:
            repr_value = dfg_value
        edge = Edge(self, other_node, dependency_value, dfg_value, repr_value, repr_color=repr_color,
                    edge_type=self.node_type, net_name=self.net_name)
        if other_node not in self.input_connections:
            self.input_connections[other_node] = []
        self.input_connections[other_node].append(edge)

    def calculate_and_measure_out(self, and_measure_thresh=default_parameters[AND_MEASURE_THRESH]):
        '''
        get AND from output relations
        :param and_measure_thresh:
        :return:
        '''
        out_nodes = sorted(list(self.output_connections), key=lambda x: x.node_name)
        i = 0
        while i < len(out_nodes):
            n1 = out_nodes[i].node_name
            j = i + 1
            while j < len(out_nodes):
                n2 = out_nodes[j].node_name
                # n1->n2
                c1 = self.heuristics_net.dfg_matrix[n1][n2] if n1 in self.heuristics_net.dfg_matrix and \
                                                               n2 in self.heuristics_net.dfg_matrix[n1] else 0
                # n2->n1
                c2 = self.heuristics_net.dfg_matrix[n2][n1] if n2 in self.heuristics_net.dfg_matrix and \
                                                               n1 in self.heuristics_net.dfg_matrix[n2] else 0
                # self->n1
                c3 = self.heuristics_net.dfg_matrix[self.node_name][n1] if self.node_name in self.heuristics_net.dfg_matrix and n1 in self.heuristics_net.dfg_matrix[self.node_name] else 0
                # self->n2
                c4 = self.heuristics_net.dfg_matrix[self.node_name][n2] if self.node_name in self.heuristics_net.dfg_matrix and n2 in self.heuristics_net.dfg_matrix[self.node_name] else 0
                value = (c1 + c2) / (c3 + c4 + 1)
                if value >= and_measure_thresh:
                    if n1 not in self.and_measures_out:
                        self.and_measures_out[n1] = {}
                    self.and_measures_out[n1][n2] = value
                j = j + 1
            i = i + 1

    def calculate_and_measure_in(self, and_measure_thresh=default_parameters[AND_MEASURE_THRESH]):
        '''
                get AND from input relations
                :param and_measure_thresh:
                :return:
                '''
        in_nodes = sorted(list(self.input_connections), key=lambda x: x.node_name)
        i = 0
        while i < len(in_nodes):
            n1 = in_nodes[i].node_name
            j = i + 1
            while j < len(in_nodes):
                n2 = in_nodes[j].node_name
                # n1->n2
                c1 = self.heuristics_net.dfg_matrix[n1][n2] if n1 in self.heuristics_net.dfg_matrix and \
                                                               n2 in self.heuristics_net.dfg_matrix[n1] else 0
                # n2->n1
                c2 = self.heuristics_net.dfg_matrix[n2][n1] if n2 in self.heuristics_net.dfg_matrix and \
                                                               n1 in self.heuristics_net.dfg_matrix[n2] else 0
                # n1->self
                c3 = self.heuristics_net.dfg_matrix[n1][self.node_name] if n1 in self.heuristics_net.dfg_matrix and \
                                                                           self.node_name in self.heuristics_net.dfg_matrix[n1] else 0
                # n2->self
                c4 = self.heuristics_net.dfg_matrix[n2][self.node_name] if n2 in self.heuristics_net.dfg_matrix and \
                                                                           self.node_name in self.heuristics_net.dfg_matrix[n2] else 0
                value = (c1 + c2) / (c3 + c4 + 1)
                if value >= and_measure_thresh:
                    if n1 not in self.and_measures_in:
                        self.and_measures_in[n1] = {}
                    self.and_measures_in[n1][n2] = value
                j = j + 1
            i = i + 1

    def calculate_loops_length_two(self, dfg_matrix, freq_triples_matrix,
                                   loops_length_two_thresh=default_parameters[LOOP_LENGTH_TWO_THRESH]):
        '''
        get loops of length two
        :param dfg_matrix:
        :param freq_triples_matrix:
        :param loops_length_two_thresh:
        :return:
        '''
        if self.nodes_dictionary is not None and self.node_name in freq_triples_matrix:
            n1 = self.node_name
            for n2 in freq_triples_matrix[n1]:
                c1 = dfg_matrix[n1][n2] if n1 in dfg_matrix and n2 in dfg_matrix[n1] else 0
                # n1>>n2
                v1 = freq_triples_matrix[n1][n2] if n1 in freq_triples_matrix and n2 in freq_triples_matrix[n1] else 0
                v2 = freq_triples_matrix[n2][n1] if n2 in freq_triples_matrix and n1 in freq_triples_matrix[n2] else 0
                loop = (v1 + v2) / (v1 + v2 + 1)
                if loop >= loops_length_two_thresh:
                    self.loop_length_two[n2] = c1

    def __repr__(self):
        ret = "(node:" + self.node_name + " connections:{"
        for index, conn in enumerate(self.output_connections.keys()):
            if index > 0:
                ret = ret + ", "
            ret = ret + conn.node_name + ":" + str([x.dependency_value for x in self.output_connections[conn]])
        ret = ret + "})"
        return ret

    def __str__(self):
        return self.__repr__()



class Edge:
    def __init__(self, start_node, end_node, dependency_value, dfg_value, repr_value, label="", repr_color="#000000",
                 edge_type="frequency", net_name=""):
        self.start_node = start_node
        self.end_node = end_node
        self.dependency_value = dependency_value
        self.dfg_value = dfg_value
        self.repr_value = repr_value
        self.label = label
        self.repr_color = repr_color
        self.edge_type = edge_type
        self.net_name = net_name