import tempfile
import pydotplus
import math

def get_represent(heu_net, parameters=None):
    '''
    get represent
    :param heu_net:
    :param parameters:
    :return:
    '''
    if parameters is None:
        parameters = {}

    image_format = parameters["format"] if "format" in parameters else "png"

    graph = pydotplus.Dot(strict=True)
    graph.obj_dict['attributes']['bgcolor'] = 'transparent'

    corr_nodes = {}
    corr_nodes_names = {}
    is_frequency = False

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        node_occ = node.node_occ
        # graycolor = transform_to_hex_2(max(255 - math.log(node_occ) * 9, 0))
        graycolor = '#FFFFFF'
        if node.node_type == "frequency":
            is_frequency = True
            n = pydotplus.Node(name=node_name, shape="box", style="filled",
                               label=node_name + " (" + str(node_occ) + ")", fillcolor=graycolor)
        else:
            n = pydotplus.Node(name=node_name, shape="box", style="filled",
                               label=node_name, fillcolor=graycolor)
        corr_nodes[node] = n
        corr_nodes_names[node_name] = n
        graph.add_node(n)

    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    this_pen_width = 1.0 + math.log(1 + edge.repr_value) / 11.0
                    repr_value = str(edge.repr_value)
                    e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],label=str(repr_value),
                                       color=edge.repr_color,fontcolor=edge.repr_color, penwidth=this_pen_width)
                    graph.add_edge(e)

    for index, sa_list in enumerate(heu_net.start_activities):
        effective_sa_list = [n for n in sa_list if n in corr_nodes_names]
        if effective_sa_list:
            start_i = pydotplus.Node(name="start_" + str(index), label="@@S", color=heu_net.default_edges_color[index],
                                     fontsize="8", fontcolor="#32CD32", fillcolor="#32CD32",
                                     style="filled")
            graph.add_node(start_i)
            for node_name in effective_sa_list:
                sa = corr_nodes_names[node_name]
                if type(heu_net.start_activities[index]) is dict:
                    if is_frequency:
                        occ = heu_net.start_activities[index][node_name]
                        this_pen_width = 1.0 + math.log(1 + occ) / 11.0

                        e = pydotplus.Edge(src=start_i, dst=sa, label=str(occ),
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                        graph.add_edge(e)

    for index, ea_list in enumerate(heu_net.end_activities):
        effective_ea_list = [n for n in ea_list if n in corr_nodes_names]
        if effective_ea_list:
            end_i = pydotplus.Node(name="end_" + str(index), label="@@E", color="#",
                                   fillcolor="#FFA500", fontcolor="#FFA500", fontsize="8",
                                   style="filled")
            graph.add_node(end_i)
            for node_name in effective_ea_list:
                ea = corr_nodes_names[node_name]
                if type(heu_net.end_activities[index]) is dict:
                    if is_frequency:
                        occ = heu_net.end_activities[index][node_name]
                        this_pen_width = 1.0 + math.log(1 + occ) / 11.0
                        e = pydotplus.Edge(src=ea, dst=end_i, label=str(occ),
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)

                        graph.add_edge(e)
    file_name = tempfile.NamedTemporaryFile(suffix='.' + image_format)
    file_name.close()
    graph.write(file_name.name, format=image_format)
    return file_name