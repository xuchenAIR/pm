import heuristic.node as node_obj

PARAM_MOST_COMMON_PATHS = 'most_common_paths'


class HeuristicsNet(object):
    net_name = None
    nodes = {}

    activities = None
    start_activities = None
    end_activities = None
    activities_occur = None
    dfg_step_two = None
    triples = None

    dfg_step_two_matrix = {}
    freq_triples_matrix = {}
    dependency_matrix = {}
    dfg_matrix = {}
    performance_matrix = {}
    def __init__(self, frequency_dfg, activities=None, start_activities=None, end_activities=None,
                 activities_occurrences=None,
                 default_edges_color="#000000", performance_dfg=None, dfg_step_two=None, triples=None,
                 net_name='NET'):
        self.net_name = [net_name]





        self.dfg = frequency_dfg
        self.performance_dfg = performance_dfg


        self.node_type = "frequency" if self.performance_dfg is None else "performance"

        self.activities = activities
        # if self.activities is None:
        #     self.activities = dfg_utils.get_activities_from_dfg(frequency_dfg)
        # if start_activities is None:
        #     self.start_activities = [dfg_utils.infer_start_activities(frequency_dfg)]
        # else:
        #     self.start_activities = [start_activities]
        # if end_activities is None:
        #     self.end_activities = [dfg_utils.infer_end_activities(frequency_dfg)]
        # else:
        #     self.end_activities = [end_activities]
        self.start_activities = [start_activities]
        self.end_activities = [end_activities]
        self.activities_occur = activities_occurrences

        self.default_edges_color = [default_edges_color]
        self.dfg_step_two = dfg_step_two

        self.triples = triples


    def hueristic_calculate(self,dependency_thresh,and_measure_tresh,min_act_count,min_dfg_occur,
                            dfg_pre_clean_noise_tresh,loop_length_two_tresh):
        '''
        get dependency matrix, plot nodes
        :param dependency_thresh:
        :param and_measure_tresh:
        :param min_act_count:
        :param min_dfg_occur:
        :param dfg_pre_clean_noise_tresh:
        :param loop_length_two_tresh:
        :return:
        '''
        if dfg_pre_clean_noise_tresh > 0.0:
            self.dfg = clean_dfg_noise(self.dfg,self.activities,dfg_pre_clean_noise_tresh)
        # 映射成矩阵
        if self.dfg_step_two is not None:
            for p in self.dfg_step_two:
                a1 = p[0]
                a2 = p[1]
                value = self.dfg_step_two[p]
                if a1 not in self.dfg_step_two_matrix:
                    self.dfg_step_two_matrix[a1] = {}
                self.dfg_step_two_matrix[a1][a2] = value
        if self.triples is not None:
            for p in self.triples:
                a1 = p[0]
                a2 = p[1]
                a3 = p[2]
                value = self.triples[p]
                #...aba...循环结构
                if a1 == a3 and not a1 == a2:
                    if a1 not in self.freq_triples_matrix:
                        self.freq_triples_matrix[a1] = {}
                    self.freq_triples_matrix[a1][a2] = value
        #计算依赖度
        for p in self.dfg:
            a1 = p[0]
            a2 = p[1]
            value = self.dfg[p]
            perf_value = self.performance_dfg[p] if self.performance_dfg is not None else self.dfg[p]
            if a1 not in self.dependency_matrix:
                self.dependency_matrix[a1] = {}
                self.dfg_matrix[a1] = {}
                self.performance_matrix[a1] = {}
            self.dfg_matrix[a1][a2] = value
            self.performance_matrix[a1][a2] = perf_value
            if not a1 == a2:
                rev_couple = (a2, a1)
                c1 = value
                if rev_couple in self.dfg:
                    c2 = self.dfg[rev_couple]
                    dep = (c1 - c2) / (c1 + c2 + 1)
                else:
                    dep = c1 / (c1 + 1)
            else:
                dep = value / (value + 1)
            self.dependency_matrix[a1][a2] = dep
        #过滤满足阈值要求的活动
        for n1 in self.dependency_matrix:
            for n2 in self.dependency_matrix[n1]:
                #活动出现次数>阈值
                con1 = n1 in self.activities_occur and self.activities_occur[n1] >= min_act_count
                con2 = n2 in self.activities_occur and self.activities_occur[n2] >= min_act_count
                #关系对出现次数>阈值
                con3 = self.dfg_matrix[n1][n2] >= min_dfg_occur
                #依赖度>阈值
                con4 = self.dependency_matrix[n1][n2] >= dependency_thresh
                condition = con1 and con2 and con3 and con4
                if condition:
                    if n1 not in self.nodes:
                        self.nodes[n1] = node_obj.Node(self, n1, self.activities_occur[n1],
                                              is_start_node=(n1 in self.start_activities),
                                              is_end_node=(n1 in self.end_activities),
                                              default_edges_color=self.default_edges_color[0],
                                              node_type=self.node_type,
                                              net_name=self.net_name[0],
                                              nodes_dictionary=self.nodes)
                    if n2 not in self.nodes:
                        self.nodes[n2] = node_obj.Node(self, n2, self.activities_occur[n2],
                                              is_start_node=(n2 in self.start_activities),
                                              is_end_node=(n2 in self.end_activities),
                                              default_edges_color=self.default_edges_color[0],
                                              node_type=self.node_type,
                                              net_name=self.net_name[0],
                                              nodes_dictionary=self.nodes)

                    repr_value = self.performance_matrix[n1][n2]
                    self.nodes[n1].add_output_connection(self.nodes[n2], self.dependency_matrix[n1][n2],
                                                         self.dfg_matrix[n1][n2], repr_value=repr_value)
                    self.nodes[n2].add_input_connection(self.nodes[n1], self.dependency_matrix[n1][n2],
                                                        self.dfg_matrix[n1][n2], repr_value=repr_value)

        for node in self.nodes:
            self.nodes[node].calculate_and_measure_out(and_measure_thresh=and_measure_tresh)
            self.nodes[node].calculate_and_measure_in(and_measure_thresh=and_measure_tresh)
            self.nodes[node].calculate_loops_length_two(self.dfg_matrix, self.freq_triples_matrix,
                                                        loops_length_two_thresh=loop_length_two_tresh)
        nodes = list(self.nodes.keys())
        # 循环节构
        added_loops = set()
        for n1 in nodes:
            for n2 in self.nodes[n1].loop_length_two:
                if n1 in self.dfg_matrix and n2 in self.dfg_matrix[n1] and \
                        self.dfg_matrix[n1][n2] >= min_dfg_occur and \
                        n1 in self.activities_occur and self.activities_occur[n1] >= min_act_count and \
                        n2 in self.activities_occur and self.activities_occur[n2] >= min_act_count:
                    if not ((n1 in self.dependency_matrix and n2 in self.dependency_matrix[n1] and
                             self.dependency_matrix[n1][n2] >= dependency_thresh) or (
                                    n2 in self.dependency_matrix and n1 in self.dependency_matrix[n2] and
                                    self.dependency_matrix[n2][n1] >= dependency_thresh)):
                        if n2 not in self.nodes:
                            self.nodes[n2] = node_obj.Node(self, n2, self.activities_occurrences[n2],
                                                  is_start_node=(n2 in self.start_activities),
                                                  is_end_node=(n2 in self.end_activities),
                                                  default_edges_color=self.default_edges_color[0],
                                                  node_type=self.node_type, net_name=self.net_name[0],
                                                  nodes_dictionary=self.nodes)
                        v_n1_n2 = self.dfg_matrix[n1][n2] if n1 in self.dfg_matrix and n2 in self.dfg_matrix[n1] else 0
                        v_n2_n1 = self.dfg_matrix[n2][n1] if n2 in self.dfg_matrix and n1 in self.dfg_matrix[n2] else 0

                        repr_value = self.performance_matrix[n1][n2] if n1 in self.performance_matrix and n2 in \
                                                                        self.performance_matrix[n1] else 0

                        if (n1, n2) not in added_loops:
                            added_loops.add((n1, n2))
                            self.nodes[n1].add_output_connection(self.nodes[n2], 0,
                                                                 v_n1_n2, repr_value=repr_value)
                            self.nodes[n2].add_input_connection(self.nodes[n1], 0,
                                                                v_n2_n1, repr_value=repr_value)

                        if (n2, n1) not in added_loops:
                            added_loops.add((n2, n1))
                            self.nodes[n2].add_output_connection(self.nodes[n1], 0,
                                                                 v_n2_n1, repr_value=repr_value)
                            self.nodes[n1].add_input_connection(self.nodes[n2], 0,
                                                                v_n1_n2, repr_value=repr_value)
        if len(self.nodes) == 0:
            for act in self.activities:
                self.nodes[act] = node_obj.Node(self, act, self.activities_occurrences[act],
                                      is_start_node=(act in self.start_activities),
                                      is_end_node=(act in self.end_activities),
                                      default_edges_color=self.default_edges_color[0],
                                      node_type=self.node_type, net_name=self.net_name[0],
                                      nodes_dictionary=self.nodes)



def clean_dfg_noise(dfg, activities, noise_threshold, parameters=None):
    if parameters is None:
        parameters = {}
    most_common_paths = parameters[
        PARAM_MOST_COMMON_PATHS] if PARAM_MOST_COMMON_PATHS in parameters else None
    if most_common_paths is None:
        most_common_paths = []

    new_dfg = None
    active_max_count = {}

    for act in activities:
        active_max_count[act] = get_max_activity_count(dfg, act)

    for p in dfg:
        if type(p[0]) is str:
            if new_dfg is None:
                new_dfg = {}
            act1 = p[0]
            act2 = p[1]
            val = dfg[p]
        else:
            if new_dfg is None:
                new_dfg = []
            act1 = p[0][0]
            act2 = p[0][1]
            val = p[1]
        if not p in most_common_paths and val < min(active_max_count[act1] * noise_threshold,
                                                     active_max_count[act2] * noise_threshold):
            pass
        else:
            if type(p[0]) is str:
                new_dfg[p] = dfg[p]
                pass
            else:
                new_dfg.append(p)
                pass
    if new_dfg is None:
        return dfg

    return new_dfg

def get_max_activity_count(dfg, act):
    '''
    get maximum count of in/out about activity
    :param dfg:
    :param act:
    :return:
    '''
    ingoing = get_in(dfg)
    outgoing = get_out(dfg)
    max_value = -1
    if act in ingoing:
        for act2 in ingoing[act]:
            if ingoing[act][act2] > max_value:
                max_value = ingoing[act][act2]
    if act in outgoing:
        for act2 in outgoing[act]:
            if outgoing[act][act2] > max_value:
                max_value = outgoing[act][act2]
    return max_value

def get_in(dfg):
    ingoing = {}
    for el in dfg:
        if type(el[0]) is str:
            if not el[1] in ingoing:
                ingoing[el[1]] = {}
            ingoing[el[1]][el[0]] = dfg[el]
        else:
            if not el[0][1] in ingoing:
                ingoing[el[0][1]] = {}
            ingoing[el[0][1]][el[0][0]] = el[1]
    return ingoing

def get_out(dfg):
    outgoing = {}
    for el in dfg:
        if type(el[0]) is str:
            if not el[0] in outgoing:
                outgoing[el[0]] = {}
            outgoing[el[0]][el[1]] = dfg[el]
        else:
            if not el[0][0] in outgoing:
                outgoing[el[0][0]] = {}
            outgoing[el[0][0]][el[0][1]] = el[1]
    return outgoing
