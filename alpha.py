#!/usr/bin/env python
# coding: utf-8

import uuid
from graphviz import Digraph
import pandas as pd
import time
from collections import Counter
import streamlit as st

FORMAT = "format"
DEBUG = "debug"
RANKDIR = "set_rankdir"
FOLDEER_PITRURE = 'picture/'
COLUMNS_DEBUG_LIST = ["case_id", "event_id", "time", "activity", "resource", "costs"]
COLUMNS_DEBUG_DIC = {'case_id':"case_id", "event_id":"event_id", "time":"time", "activity":"activity", "resource":"resource", "costs":"costs"}

class Identity(object):
    identity_dic = {}

    def __init__(self):
        self.identity_dic = {}

    def make_identity(self, name):
        self.identity_dic[name] = str(uuid.uuid1())
        return self.identity_dic[name]

    def get_id_from_name(self, name):
        return self.identity_dic[name]
Identity = Identity()

class Alpha_Miner:
    activitis = ''
    start = ''
    end = ''
    log = ''
    causal = ''
    parallel = ''
    paris = ''
    places = ''

    def __init__(self, start_activities, end_activities, log, causal, all_AC):
        self.activitis = all_AC
        self.start = start_activities
        self.end = end_activities
        self.log = log
        self.causal = causal
        self.parallel = {(f, t) for (f, t) in self.causal if (t, f) in self.causal}

    def filter(self, parallel, pair):  # 判断是否在平行关系中
        if (pair[0], pair[0]) in parallel or (pair[1], pair[1]) in parallel:
            return False
        return True

    def check_is_unrelated(self, parallel, causal, item_1, item_2):
        # for item1_x in item_1:
        #     for item2_y in item_2:
        #         pair = (item1_x, item2_y)
        #         pair_T = (item2_y, item1_x)
        #         if (pair in parallel or pair in causal) or (pair_T in parallel or pair_T in causal):
        #             return True
        for item1_x in item_1:
            for item2_y in item_2:
                pair = (item1_x, item2_y)
                if (pair in parallel or pair in causal) :
                    return True
        return False

    def pair_maximizer(self, pairs, pair):
        for p in pairs:
            if pair != p and pair[0].issubset(p[0]) and pair[1].issubset(p[1]):
                return False
        return True

class PetriNet(object):
    class Place(object):

        def __init__(self, name, in_arcs=None, out_arcs=None):
            self.__name = name
            self.__in_arcs = set() if in_arcs is None else in_arcs
            self.__out_arcs = set() if out_arcs is None else out_arcs

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        def __get_out_arcs(self):
            return self.__out_arcs

        def __get_in_arcs(self):
            return self.__in_arcs

        def __repr__(self):
            return str(self.name)

        name = property(__get_name, __set_name)
        in_arcs = property(__get_in_arcs)
        out_arcs = property(__get_out_arcs)

    class Transition(object):

        def __init__(self, name, label=None, in_arcs=None, out_arcs=None):
            self.__name = name
            self.__label = None if label is None else label
            self.__in_arcs = set() if in_arcs is None else in_arcs
            self.__out_arcs = set() if out_arcs is None else out_arcs

        def __set_name(self, name):
            self.__name = name

        def __get_name(self):
            return self.__name

        def __set_label(self, label):
            self.__label = label

        def __get_label(self):
            return self.__label

        def __get_out_arcs(self):
            return self.__out_arcs

        def __get_in_arcs(self):
            return self.__in_arcs

        def __repr__(self):
            if self.label is None:
                return str(self.name)
            else:
                return str(self.label)

        name = property(__get_name, __set_name)
        label = property(__get_label, __set_label)
        in_arcs = property(__get_in_arcs)
        out_arcs = property(__get_out_arcs)

    class Arc(object):

        def __init__(self, source, target, weight=1):
            if type(source) is type(target):
                raise Exception('Petri nets are bipartite graphs!')
            self.__source = source
            self.__target = target
            self.__weight = weight

        def __get_source(self):
            return self.__source

        def __get_target(self):
            return self.__target

        def __set_weight(self, weight):
            self.__wight = weight

        def __get_weight(self):
            return self.__weight

        def __repr__(self):
            if type(self.source) is PetriNet.Transition:
                if self.source.label:
                    return "(t)" + str(self.source.label) + "->" + "(p)" + str(self.target.name)
                else:
                    return "(t)" + str(self.source.name) + "->" + "(p)" + str(self.target.name)
            if type(self.target) is PetriNet.Transition:
                if self.target.label:
                    return "(p)" + str(self.source.name) + "->" + "(t)" + str(self.target.label)
                else:
                    return "(p)" + str(self.source.name) + "->" + "(t)" + str(self.target.name)

        source = property(__get_source)
        target = property(__get_target)
        weight = property(__get_weight, __set_weight)

    def __init__(self, name=None, places=None, transitions=None, arcs=None):
        self.__name = "" if name is None else name
        self.__places = set() if places is None else places
        self.__transitions = set() if transitions is None else transitions
        self.__arcs = set() if arcs is None else arcs

    def __get_name(self):
        return self.__name

    def __set_name(self, name):
        self.__name = name

    def __get_places(self):
        return self.__places

    def __get_transitions(self):
        return self.__transitions

    def __get_arcs(self):
        return self.__arcs

    name = property(__get_name, __set_name)
    places = property(__get_places)
    transitions = property(__get_transitions)
    arcs = property(__get_arcs)

class Marking(Counter):
    pass

    def __hash__(self):
        r = 0
        for p in self.items():
            r += 31 * hash(p[0]) * p[1]
        return r

    def __eq__(self, other):
        if not self.keys() == other.keys():
            return False
        for p in self.keys():
            if other.get(p) != self.get(p):
                return False
        return True

    def __le__(self, other):
        if not self.keys() <= other.keys():
            return False
        for p in self.keys():
            if other.get(p) < self.get(p):
                return False
        return True

    def __add__(self, other):
        m = Marking()
        for p in self.items():
            m[p[0]] = p[1]
        for p in other.items():
            m[p[0]] += p[1]
        return m

    def __sub__(self, other):
        m = Marking()
        for p in self.items():
            m[p[0]] = p[1]
        for p in other.items():
            m[p[0]] -= p[1]
            if m[p[0]] == 0:
                del m[p[0]]
        return m

    def __repr__(self):
        # return str([str(p.name) + ":" + str(self.get(p)) for p in self.keys()])
        # The previous representation had a bug, it took into account the order of the places with tokens
        return str([str(p.name) + ":" + str(self.get(p)) for p in sorted(list(self.keys()), key=lambda x: x.name)])




def read_csv_to_dataframe(data_name, sep=';', time_format="%d-%m-%Y:%H.%M",columns=COLUMNS_DEBUG_LIST):
    df = pd.read_csv(data_name, header=0, sep=sep)
    df.columns = columns
    df["time"] = pd.to_datetime(df.time, format=time_format)
    return df


def get_all_activities(df):
    # activities duplicated
    activities = []
    for ac in df.drop_duplicates(['activity']).activity:
        activities.append(ac)
    return activities


def get_log_from_df(df):
    '''
    时间升序
    :param df:
    :return:
    '''
    log = []
    # per caseID ,sorted by time，duplicated
    for i in df.drop_duplicates(['case_id']).case_id:
        trace = []
        for ac in df[df['case_id'].isin([i])].sort_values('time', ascending=True).activity:
            trace.append(ac)
        log.append(trace)
    return log


def get_activity_matrix(activities):
    matrix_AC = pd.DataFrame(data=None, columns=activities, index=activities)
    list_Row = matrix_AC._stat_axis.values.tolist()  # 行名称
    list_Col = matrix_AC.columns.values.tolist()  # 列名称
    return matrix_AC, list_Row, list_Col


def Zero(matrix_AC, list_Row, list_Col):
    '''
    初始化   '#'表示活动无关
    '''
    for x in range(0, matrix_AC.shape[0]):
        for y in range(0, matrix_AC.shape[1]):
            matrix_AC.loc[list_Row[x], list_Col[y]] = '#'


def PerCase(matrix_AC, trace):
    '''
    把路径中的活动关系转为符号
        -> 表示 顺序关系
        <- 表示 被指向

    '''
    for x in range(0, len(trace) - 1):
        matrix_AC.loc[trace[x], trace[x + 1]] = '->'
        if matrix_AC.loc[trace[x + 1], trace[x]] == '#' or matrix_AC.loc[trace[x + 1], trace[x]] == '<-':
            matrix_AC.loc[trace[x + 1], trace[x]] = '<-'
        elif matrix_AC.loc[trace[x + 1], trace[x]] == '->':
            pass


def initialize_and_fill_matrixAC(matrix_AC, log, list_Row, list_Col):
    '''
    将所有路径对应的活动关系填入矩阵
    :param matrix_AC: 活动矩阵
    :param log: 所有的路径
    :param list_Row: 后动矩阵行
    :param list_Col: 活动矩阵列
    :return: 开始活动集合，结束活动集合
    '''
    Zero(matrix_AC, list_Row, list_Col)
    start_set = set()  # 开始活动集合
    end_set = set()  # 结束活动集合
    for every_case in log:  # 每组caseID下的活动顺序信息填入矩阵中
        start_set.add(every_case[0])
        end_set.add(every_case[-1])
        PerCase(matrix_AC, every_case)
    return start_set, end_set


def check_parallel(matrix_AC, list_Row, list_Col):
    '''
    检测并行,并行的值置为 '\\'
    获取所有并行任务对
    :return: 返回并行任务列表
    '''
    list_parallel = []
    for x in range(0, matrix_AC.shape[0]):
        for y in range(0, matrix_AC.shape[1]):
            if matrix_AC.loc[list_Row[x], list_Col[y]] == '->' and matrix_AC.loc[list_Col[y], list_Row[x]] == '->':
                list_parallel.append([list_Row[x], list_Col[y]])
                matrix_AC.loc[list_Row[x], list_Col[y]] = '||'
                matrix_AC.loc[list_Col[y], list_Row[x]] = '||'
    return list_parallel


def association_ab(matrix_AC, a, b):
    '''
    得到ab的关系
    :param a: ac_a
    :param b: ac_b
    :return: '->' or '#' or '||'
    '''
    if matrix_AC.loc[a, b] == '->':
        return '->'
    if matrix_AC.loc[a, b] == '#':
        return '#'
    if matrix_AC.loc[a, b] == '||':
        return '||'


def get_later(matrix_AC, ac, list_Col):
    '''
    获得所有后继活动
    :param matrix_AC:
    :param ac:
    :return:
    '''
    index_as = 0
    latter = []
    for asso in matrix_AC.loc[ac]:
        if asso == '->':
            latter.append(list_Col[index_as])
        index_as += 1
    return latter


def get_precede(matrix_AC, ac, list_Col):
    '''
    获取活动的前驱
    :param list_Col:
    :param matrix_AC:
    :param ac:
    :return:
    '''
    index_as = 0
    precede = []
    for asso in matrix_AC.loc[ac]:
        if asso == '<-':
            precede.append(list_Col[index_as])
        index_as += 1
    return precede


def precede_latter(matrix_AC, ac, list_Col):
    '''
    获取前驱与后继
    :param matrix_AC:
    :param ac:
    :return: list
    '''
    return get_precede(matrix_AC, ac, list_Col), get_later(matrix_AC, ac, list_Col)


def get_causal(log):
    '''
    获取因果关系
    :param log:
    :return: 直接关系list(tuple)
    '''
    causal = set()
    dfg = {}
    dfgs = map((lambda t: [(t[i - 1], t[i]) for i in range(1, len(t))]), log)
    dfgs = list(dfgs)
    for trace in dfgs:
        for p in trace:
            dfg[p] = 0
    for trace in dfgs:
        for p in trace:
            dfg[p] += 1
            if dfg[p] > 0:
                causal.add(p)
    return causal


def get_parallel(list_parallel):
    '''
    获得平行关系 list -> set
    :param list_parallel:
    :return:
    '''
    parallel = set()
    for pll in list_parallel:
        parallel.add(tuple(pll))
    return parallel


def get_pairs(alpha):
    '''
    在alpha中加入pairs
    pairs ：活动关系对
    :param alpha: object
    '''
    pairs = []
    for p in alpha.causal:
        if p not in alpha.parallel and alpha.filter(alpha.parallel,p):
            pairs.append(tuple(({p[0]}, {p[1]})))
    alpha.pairs = pairs


def merge_subset(alpha):
    '''
    merge (A,B) to (A',B')
    A is the subset of A' and B is the subset of B'
    :param alpha: object
    '''
    for i in range(0, len(alpha.pairs)):
        t1 = alpha.pairs[i]
        for j in range(i, len(alpha.pairs)):
            t2 = alpha.pairs[j]
            if t1 != t2:
                if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                    if not (alpha.check_is_unrelated(alpha.parallel, alpha.causal, t1[0], t2[0])
                            or
                            alpha.check_is_unrelated(alpha.parallel, alpha.causal, t1[1], t2[1])):
                        new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                        if new_alpha_pair not in alpha.pairs:
                            alpha.pairs.append((t1[0] | t2[0], t1[1] | t2[1]))


def delete_non_maximium_pair(alpha):
    '''
    delete non-maximium pair
    get places as ({'ac_a'},{'ac_b'})
    :param alpha:
    :param pairs:
    :return:
    '''
    maximizer_list = []
    for p in alpha.pairs:
        if alpha.pair_maximizer(alpha.pairs, p):
            maximizer_list.append(p)
    alpha.places = maximizer_list


def add_start(net, start_activities, ac_transition_dict):
    '''
    加入一个start place 并指向所有的 开始活动
    :param net: PetriNet Object
    :param start_activities:
    :param ac_transition_dict:
    :return:
    '''
    start = PetriNet.Place('start')
    net.places.add(start)
    for s in start_activities:
        add_arc_from_to(start, ac_transition_dict[s], net)
    return start


def add_end(net, end_activities, ac_transition_dict):
    '''
    加入一个end place 并指向所有的 结束活动
    :param net:
    :param end_activities:
    :param ac_transition_dict:
    :return:
    '''
    end = PetriNet.Place('end')
    net.places.add(end)
    for e in end_activities:
        add_arc_from_to(ac_transition_dict[e], end, net)
    return end


def add_arc_from_to(fr, to, net, weight=1):
    '''
    添加一条有向弧
    :param fr: source
    :param to: target
    :param net: object
    :param weight: scole
    :return:
    '''
    arc = PetriNet.Arc(fr, to, weight)
    net.arcs.add(arc)
    fr.out_arcs.add(arc)
    to.in_arcs.add(arc)
    return arc


def get_net(alpha):
    '''
    从alpha获取petri-net对象
    :param alpha: object
    :return: net,start_place,end_place
    '''
    net = PetriNet('alpha_net_' + str(time.time()))
    ac_transition_dict = {}  # 所有的transition-字典集
    for i in range(0, len(alpha.activitis)):
        ac_transition_dict[alpha.activitis[i]] = PetriNet.Transition(alpha.activitis[i], alpha.activitis[i])
        net.transitions.add(ac_transition_dict[alpha.activitis[i]])
    start_place = add_start(net, alpha.start, ac_transition_dict)
    end_place = add_end(net, alpha.end, ac_transition_dict)
    for pair in alpha.places:
        net_place = PetriNet.Place(str(pair))
        net.places.add(net_place)
        for in_arc in pair[0]:
            add_arc_from_to(ac_transition_dict[in_arc], net_place, net)  # 前驱->place
        for out_arc in pair[1]:
            add_arc_from_to(net_place, ac_transition_dict[out_arc], net)  # place->后继
    return net, start_place, end_place


class graph:

    def __init__(self):
        pass

    def draw(self, net, initial, final, decorations=None, parameters=None, data_name='data_result'):
        if parameters is None:
            parameters = {}
        image_format = "png"
        debug = False
        set_rankdir = None
        if FORMAT in parameters:
            image_format = parameters["format"]
        if DEBUG in parameters:
            debug = parameters["debug"]
        if RANKDIR in parameters:
            set_rankdir = parameters["set_rankdir"]
        return self.visualization(net, data_name, image_format=image_format, initial=initial,
                                  final=final, decorations=decorations, debug=debug,
                                  set_rankdir=set_rankdir)

    def visualization(self, net, data_name, image_format="png", initial=None, final=None, decorations=None,
                      debug=False, set_rankdir=None):
        filename = FOLDEER_PITRURE + data_name.split('/')[1] + '_' + str(time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())) + '.gv'
        viz = Digraph(net.name, filename=filename, engine='dot', graph_attr={'bgcolor': 'transparent'})
        if set_rankdir:
            viz.graph_attr['rankdir'] = set_rankdir
        else:
            viz.graph_attr['rankdir'] = 'LR'
        viz.attr('node', shape='box')
        transitions_list = sorted(list(net.transitions),
                                  key=lambda x: (x.label if x.label is not None else "t", x.name))
        # 添加transitions
        for trasition in transitions_list:
            if trasition.label is not None:
                if (decorations is not None) and trasition in decorations and (
                        "label" in decorations[trasition] and "color" in decorations[trasition]):
                    viz.node(str(Identity.make_identity(trasition.label)),
                             decorations[trasition]["label"], style='filled',
                             fillcolor=decorations[trasition]["color"], border='1')
                else:
                    viz.node(str(Identity.make_identity(trasition.label)), str(trasition.label), )
            else:
                if debug:
                    viz.node(str(Identity.make_identity(trasition.name)), str(trasition.name))
                else:
                    viz.node(str(Identity.make_identity(trasition.name)), "", style='filled', fillcolor="black")
        viz.attr('node', shape='circle', fixedsize='true', width='0.5')
        places_start = sorted([x for x in list(net.places) if x in [initial]],key=lambda x: x.name)
        places_end = sorted([x for x in list(net.places) if x in [final] and not x in [initial]],key=lambda x: x.name)
        places_exclude_start_end = sorted(
            [x for x in list(net.places) if x not in [initial] and x not in [final]],
            key=lambda x: x.name)
        # 按顺序添加尽可能让图保持左右顺序
        places_graph_list = places_start + places_exclude_start_end + places_end

        # 添加places
        for p in places_graph_list:
            if p in places_start:
                viz.node(str(Identity.make_identity(p.name)), str(p.name), style='filled', fillcolor="green")
            elif p in places_end:
                viz.node(str(Identity.make_identity(p.name)), str(p.name), style='filled', fillcolor="green")
            else:
                if debug:
                    viz.node(str(Identity.make_identity(p.name)), str(p.name))
                else:
                    viz.node(str(Identity.make_identity(p.name)), "")

        # 添加有向边
        arcs_graph_list = sorted(list(net.arcs), key=lambda x: (x.source.name, x.target.name))
        for a in arcs_graph_list:
            if (decorations is not None) and (a in decorations):
                viz.edge((Identity.get_id_from_name(a.source.name)), Identity.get_id_from_name(a.target.name),
                         label=decorations[a]["label"],
                         penwidth=decorations[a]["penwidth"])
            else:
                viz.edge(Identity.get_id_from_name(a.source.name), Identity.get_id_from_name(a.target.name))
        viz.attr(overlap='false')
        viz.attr(fontsize='10')
        viz.format = image_format
        viz.view()


