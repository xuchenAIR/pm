import heuristic.hueristc_abstarct as hueristc_abstarct
import heuristic.visual as visual
import os
import shutil
import subprocess
import sys
from alpha import PetriNet
import alpha
import networkx as nx
from alpha import Marking
from dealer_xes import Context
from pm4py.algo.filtering.log.timestamp import timestamp_filter
import datetime

def heuristic_net_csv(df,parameters=None):
    log = alpha.get_log_from_df(df)
    activities = alpha.get_all_activities(df)
    start_activities = {}
    end_activities = {}
    for t in log:
        if len(t) > 0:
            if t[0] not in start_activities:
                start_activities[t[0]] = 0
            start_activities[t[0]] += 1
            if t[-1] not in end_activities:
                end_activities[t[-1]] = 0
            end_activities[t[-1]] += 1
    activity_occs = get_activity_occurrences(log)
    dfg = get_dfg(log)
    dfg_step_two = get_dfg_step_two(log)
    triples = get_triples(log)
    hueristic_obj = hueristc_abstarct.hueristic_obj(start_activities=start_activities, end_activities=end_activities,
                                                    activity_occs=activity_occs, activities=activities, dfg=dfg,
                                                    dfg_step_two=dfg_step_two, triples=triples, parameters=parameters)
    hue_net = hueristic_obj.get_hueristic_result()
    file = visual.get_represent(hue_net)
    view(file)

    net, im, fm = get_pretri_net_from_heu_net(hue_net)
    Graph = alpha.graph()

    Graph.draw(net, im.popitem()[0], fm.popitem()[0], decorations=None, parameters=None,
               data_name='data/csv_Heuristic_p_net')

def filt_duration_log(log,time_start,time_end):
    filt_log = []
    for t in log:
        if time_start <= t[0]['time:timestamp'].date() and t[-1]['time:timestamp'].date() <= time_end:
            filt_log.append(t)
    return filt_log



def heuristic_net_xes(context,time_start,time_end,parameters=None):
    if parameters is None:
        parameters = {}
    time_start = datetime.datetime(time_start.year, time_start.month, time_start.day, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
    time_end = datetime.datetime(time_end.year, time_end.month, time_end.day+1,0,0,0).strftime('%Y-%m-%d %H:%M:%S')
    filtered_log = timestamp_filter.filter_traces_intersecting(context.log, time_start, time_end)
    filt_context = Context(log=filtered_log)
    start_activities = filt_context.start_activities
    end_activities = filt_context.end_activities
    activity_occs = get_activity_occurrences(filt_context.log_simple)
    activities = filt_context.activities
    dfg = get_dfg(filt_context.log_simple)
    dfg_step_two = get_dfg_step_two(filt_context.log_simple)
    triples = get_triples(filt_context.log_simple)
    hueristic_obj = hueristc_abstarct.hueristic_obj(start_activities=start_activities,end_activities=end_activities,
                                                    activity_occs=activity_occs,activities=activities,dfg=dfg,
                                                    dfg_step_two=dfg_step_two,triples=triples,parameters=parameters)
    hue_net = hueristic_obj.get_hueristic_result()
    file = visual.get_represent(hue_net)
    view(file)

    net, im, fm = get_pretri_net_from_heu_net(hue_net)
    Graph = alpha.graph()

    Graph.draw(net, im.popitem()[0], fm.popitem()[0], decorations=None, parameters=None, data_name='data/xes_Heuristic_p_net')


def get_pretri_net_from_heu_net(heu_net, parameters=None):
    '''
    get petri net from heu net
    :param heu_net:
    :param parameters:
    :return:
    '''

    if parameters is None:
        parameters = {}
    net = PetriNet("")
    initial = Marking()
    finacial = Marking()

    start_places = []
    end_places = []
    hid_trans_count = 0

    # start_place end_place
    for index, s_list in enumerate(heu_net.start_activities):
        start = PetriNet.Place("Start")
        start_places.append(start)
        net.places.add(start)
        initial[start] = 1
    for index, e_list in enumerate(heu_net.end_activities):
        end = PetriNet.Place("End")
        end_places.append(end)
        net.places.add(end)
        finacial[end] = 1

    act_transition = {}
    who_is_entering = {}#前驱
    who_is_exiting = {}#后继
    for act1_name in heu_net.nodes:
        act1 = heu_net.nodes[act1_name]
        if act1_name not in act_transition:
            act_transition[act1_name] = PetriNet.Transition(act1_name, act1_name)
            net.transitions.add(act_transition[act1_name])
            who_is_entering[act1_name] = set()
            who_is_exiting[act1_name] = set()
            for index, start_list in enumerate(heu_net.start_activities):
                if act1_name in start_list:
                    # 起始活动 None输入
                    who_is_entering[act1_name].add((None, index))
            for index, end_list in enumerate(heu_net.end_activities):
                if act1_name in end_list:
                    # 结束活动 输出None
                    who_is_exiting[act1_name].add((None, index))
        # 指向的node加入transition
        for act2 in act1.output_connections:
            act2_name = act2.node_name
            if act2_name not in act_transition:
                act_transition[act2_name] = PetriNet.Transition(act2_name, act2_name)
                net.transitions.add(act_transition[act2_name])
                who_is_entering[act2_name] = set()
                who_is_exiting[act2_name] = set()
                for index, start_list in enumerate(heu_net.start_activities):
                    if act2_name in start_list:
                        who_is_entering[act2_name].add((None, index))
                for index, end_list in enumerate(heu_net.end_activities):
                    if act2_name in end_list:
                        who_is_exiting[act2_name].add((None, index))
            #act1->act2
            who_is_entering[act2_name].add((act1_name, None))
            who_is_exiting[act1_name].add((act2_name, None))

    places_entering = {}
    for act1 in who_is_entering:# act 前驱
        #and in 前驱
        cliques = find_bindings(heu_net.nodes[act1].and_measures_in)
        places_entering[act1] = {}
        entering_activities = list(who_is_entering[act1])
        entering_activities_wo_source = sorted([x for x in entering_activities if x[0] is not None], key=lambda x: x[0])#实际前驱
        entering_activities_only_source = [x for x in entering_activities if x[0] is None]#None
        if entering_activities_wo_source:
            master_place = PetriNet.Place("pre_" + act1)
            net.places.add(master_place)
            alpha.add_arc_from_to(master_place, act_transition[act1], net)# pre_act->act
            if len(entering_activities) == 1:
                places_entering[act1][entering_activities[0]] = master_place
            else:
                for index, act in enumerate(entering_activities_wo_source):
                    if act[0] in heu_net.nodes[act1].and_measures_in:
                        z = 0
                        while z < len(cliques):
                            if act[0] in cliques[z]:
                                hid_trans_count = hid_trans_count + 1
                                hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                                net.transitions.add(hid_trans)
                                alpha.add_arc_from_to(hid_trans, master_place, net)
                                for act2 in cliques[z]:
                                    if (act2, None) not in places_entering[act1]:
                                        s_place = PetriNet.Place("splace_in_" + act1 + "_" + act2 + "_" + str(index))
                                        net.places.add(s_place)
                                        places_entering[act1][(act2, None)] = s_place
                                    alpha.add_arc_from_to(places_entering[act1][(act2, None)], hid_trans, net)
                                del cliques[z]
                                continue
                            z = z + 1
                        pass
                    elif act not in places_entering[act1]:
                        hid_trans_count = hid_trans_count + 1
                        hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                        net.transitions.add(hid_trans)
                        alpha.add_arc_from_to(hid_trans, master_place, net)
                        if act not in places_entering[act1]:
                            s_place = PetriNet.Place("splace_in_" + act1 + "_" + str(index))
                            net.places.add(s_place)
                            places_entering[act1][act] = s_place
                        alpha.add_arc_from_to(places_entering[act1][act], hid_trans, net)
        for el in entering_activities_only_source:
            if len(entering_activities) == 1:
                alpha.add_arc_from_to(start_places[el[1]], act_transition[act1], net)
            else:
                hid_trans_count = hid_trans_count + 1
                hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                net.transitions.add(hid_trans)
                alpha.add_arc_from_to(start_places[el[1]], hid_trans, net)
                alpha.add_arc_from_to(hid_trans, master_place, net)
    for act1 in who_is_exiting:
        cliques = find_bindings(heu_net.nodes[act1].and_measures_out)
        exiting_activities = list(who_is_exiting[act1])
        exiting_activities_wo_sink = sorted([x for x in exiting_activities if x[0] is not None], key=lambda x: x[0])
        exiting_activities_only_sink = [x for x in exiting_activities if x[0] is None]
        if exiting_activities_wo_sink:
            if len(exiting_activities) == 1 and len(exiting_activities_wo_sink) == 1:
                ex_act = exiting_activities_wo_sink[0]
                if (act1, None) in places_entering[ex_act[0]]:
                    alpha.add_arc_from_to(act_transition[act1], places_entering[ex_act[0]][(act1, None)], net)
            else:
                int_place = PetriNet.Place("intplace_" + str(act1))
                net.places.add(int_place)
                alpha.add_arc_from_to(act_transition[act1], int_place, net)
                for ex_act in exiting_activities_wo_sink:
                    if (act1, None) in places_entering[ex_act[0]]:
                        if ex_act[0] in heu_net.nodes[act1].and_measures_out:
                            z = 0
                            while z < len(cliques):
                                if ex_act[0] in cliques[z]:
                                    hid_trans_count = hid_trans_count + 1
                                    hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                                    net.transitions.add(hid_trans)
                                    alpha.add_arc_from_to(int_place, hid_trans, net)
                                    for act in cliques[z]:
                                        alpha.add_arc_from_to(hid_trans, places_entering[act][(act1, None)], net)
                                    del cliques[z]
                                    continue
                                z = z + 1
                        else:
                            hid_trans_count = hid_trans_count + 1
                            hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                            net.transitions.add(hid_trans)
                            alpha.add_arc_from_to(int_place, hid_trans, net)
                            alpha.add_arc_from_to(hid_trans, places_entering[ex_act[0]][(act1, None)], net)
        for el in exiting_activities_only_sink:
            if len(exiting_activities) == 1:
                alpha.add_arc_from_to(act_transition[act1], end_places[el[1]], net)
            else:
                hid_trans_count = hid_trans_count + 1
                hid_trans = PetriNet.Transition("hid_" + str(hid_trans_count), None)
                net.transitions.add(hid_trans)
                alpha.add_arc_from_to(int_place, hid_trans, net)
                alpha.add_arc_from_to(hid_trans, end_places[el[1]], net)
    net = remove_rendundant_invisible_transitions(net)
    return net, initial, finacial

def remove_rendundant_invisible_transitions(net):
    """
    Remove redundant transitions from Petri net

    Parameters
    -----------
    net
        Petri net

    Returns
    -----------
    net
        Cleaned net
    """
    trans = [x for x in list(net.transitions) if not x.label]
    i = 0
    while i < len(trans):
        if trans[i] in net.transitions:
            preset_i = set(x.source for x in trans[i].in_arcs)
            postset_i = set(x.target for x in trans[i].out_arcs)
            j = 0
            while j < len(trans):
                if not j == i:
                    preset_j = set(x.source for x in trans[j].in_arcs)
                    postset_j = set(x.target for x in trans[j].out_arcs)
                    if len(preset_j) == len(preset_i) and len(postset_j) < len(postset_i):
                        if len(preset_j.intersection(preset_i)) == len(preset_j) and len(
                                postset_j.intersection(postset_i)) == len(postset_j):
                            remove_transition(net, trans[j])
                            del trans[j]
                            continue
                j = j + 1
            i = i + 1
    return net

def remove_transition(net, trans):
    """
    Remove a transition from a Petri net

    Parameters
    ----------
    net
        Petri net
    trans
        Transition to remove

    Returns
    ----------
    net
        Petri net
    """
    if trans in net.transitions:
        in_arcs = trans.in_arcs
        for arc in in_arcs:
            place = arc.source
            place.out_arcs.remove(arc)
            net.arcs.remove(arc)
        out_arcs = trans.out_arcs
        for arc in out_arcs:
            place = arc.target
            place.in_arcs.remove(arc)
            net.arcs.remove(arc)
        net.transitions.remove(trans)
    return net

def find_bindings(and_measures):
    """
    Find the bindings given the AND measures

    Parameters
    -------------
    and_measures
        AND measures

    Returns
    -------------
    bindings
        Bindings
    """
    G = nx.Graph()
    allocated_nodes = set()
    for n1 in list(and_measures.keys()):
        if n1 not in allocated_nodes:
            allocated_nodes.add(n1)
            G.add_node(n1)
        for n2 in list(and_measures[n1].keys()):
            if n2 not in allocated_nodes:
                allocated_nodes.add(n2)
                G.add_node(n1)
            G.add_edge(n1, n2)
    ret = list(nx.find_cliques(G))
    return ret

def get_dfg(log):
    '''
    directly follow graph
    :param log:
    :return:
    '''
    dfg = {}
    dfgs = map((lambda t: [(t[i - 1], t[i]) for i in range(1, len(t))]), log)
    dfgs = list(dfgs)
    for trace in dfgs:
        for p in trace:
            if p not in dfg:
                dfg[p] = 0
            dfg[p] += 1
    return dfg

def get_activity_occurrences(log):
    '''
    活动出现次数
    :param log:
    :return:
    '''
    activity_occurrences = {}
    for t in log:
        for e in t:
            if e not in activity_occurrences:
                activity_occurrences[e] = 0
            activity_occurrences[e] += 1
    return activity_occurrences

def get_dfg_step_two(log):
    '''
    步距为2的二元组
    :param log:
    :return:
    '''
    dfg_step_two = {}
    dfgs = map((lambda t: [(t[i - 2], t[i]) for i in range(2, len(t))]), log)
    dfgs = list(dfgs)
    for trace in dfgs:
        for p in trace:
            if p not in dfg_step_two:
                dfg_step_two[p] = 0
            dfg_step_two[p] += 1
    return dfg_step_two

def get_triples(log):
    '''
    三元组(a,b,c)
    :param log:
    :return:
    '''
    dfg_triples = {}
    dfgs = map((lambda t: [(t[i - 2], t[i - 1], t[i]) for i in range(2, len(t))]),log)
    dfgs = list(dfgs)
    for trace in dfgs:
        for p in trace:
            if p not in dfg_triples:
                dfg_triples[p] = 0
            dfg_triples[p] += 1
    return dfg_triples


def view(figure):
    '''
    view on the screen
    :param figure:
    :return:
    '''
    try:
        filename = figure.name
        figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

    if sys.platform.startswith('darwin'):
        subprocess.call(('open', figure))
    elif os.name == 'nt':  # For Windows
        os.startfile(figure)
    elif os.name == 'posix':  # For Linux, Mac, etc.
        subprocess.call(('xdg-open', figure))

def save(figure, output_file_path):
    '''
    save a figure
    :param figure:
    :param output_file_path:
    :return:
    '''
    try:
        filename = figure.name
        figure = filename
    except AttributeError:
        # continue without problems, a proper path has been provided
        pass

    shutil.copyfile(figure, output_file_path)