import json
import networkx

def dataset_to_graph(path_to_json):
    with open(path_to_json, 'r') as file:
        json_data = json.load(file)

    G = networkx.Graph()

    for id, element in enumerate(json_data):
        G.add_node(id, prop='id', field_type="number")
        for key in json_data[id].keys():
            if isinstance(json_data[id][key], dict):
                raise Exception('[Object] properties are not supported yet')
            elif isinstance(json_data[id][key], list):
                for value in json_data[id][key]:
                    if isinstance(value, dict):
                        raise Exception('[Object] in [Array] properties are not supported yet')
                    elif isinstance(value, list):
                        raise Exception('[Array] in [Array] properties are not supported yet')

                    G.add_node(value, prop=key, field_type="array")
                    G.add_edge(id, value, relation=key)
            else:
                G.add_node(json_data[id][key], prop=key, field_type="string")
                G.add_edge(id, json_data[id][key], relation=key)
    return G
