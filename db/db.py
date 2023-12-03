from .DBException import DBException
from .dataset_to_graph import dataset_to_graph
import numpy

def init_graph(file_path):
    return dataset_to_graph(file_path)

def get_props(graph):
    props = set()

    for node, data in graph.nodes(data=True):
        prop = data.get('prop')
        if prop:
            props.add(prop)
    return list(props)

def get_ids(graph, neighbors):
    ids = set()
    for neighbor in neighbors:
        for node, data in graph.nodes(data=True):
            prop = data.get('prop')
            if prop == 'id' and node == neighbor:
                ids.add(node)
    return ids

def query_rule(graph, rule):
    result = []


    if (isinstance(rule.get('rules'), list) and rule.get('op') is None):
        rule['op'] = 'and'

    if rule.get('op')  is None and rule.get('val') is not None:
        rule['op'] = 'eq'

    validate_rule(graph, rule)

    operator = rule.get('op')
    property = rule.get('prop')
    value = rule.get('val')

    ids = None

    if operator == 'and' or operator == 'or':
        rules = rule.get('rules')
        for rule in rules:
            more_ids = query_rule(graph, rule)
            if operator == 'and':
                ids = more_ids if ids is None else ids & more_ids
            else:
                ids = more_ids if ids is None else ids | more_ids

    else:
        ids = set()

        if (operator == 'nin' or operator == 'ne' or operator == 'ntxt'):
            for node, data in graph.nodes(data=True):
                prop = data.get('prop')
                if prop == 'id':
                    ids.add(node)

        for node, data in graph.nodes(data=True):
            prop = data.get('prop')

            if prop != property:
                continue

            if operator == 'eq' and node == value:
                ids = ids | get_ids(graph, graph.neighbors(node))

            elif operator == 'ne' and node == value:
                ids = ids - get_ids(graph, graph.neighbors(node))

            elif operator == 'txt' and str(value).lower() in str(node).lower():
                ids = ids | get_ids(graph, graph.neighbors(node))

            elif operator == 'ntxt' and str(value).lower() not in str(node).lower():
                ids = get_ids(graph, graph.neighbors(node))

            elif operator == 'in' and node in value:
                ids = ids | get_ids(graph, graph.neighbors(node))

            elif operator == 'nin' and node not in value:
                ids = ids - get_ids(graph, graph.neighbors(node))

    return ids

def validate_rule(graph, rule):
    operator = rule.get('op')
    property = rule.get('prop')
    value = rule.get('val')
    rules = rule.get('rules')
    result = []

    if (operator == 'and' or operator == 'or') and rules is None:
        raise DBException('Rules are required')

    if operator != 'and' and operator != 'or' and property is None:
        print(rule)
        raise DBException('Property is required')

    if operator != 'and' and operator != 'or' and value is None:
        raise DBException('Value is required')

    if (operator == 'and' or operator == 'or') and not isinstance(rule.get('rules'), list):
        raise DBException('Rules must be an array, if operator is [and] or [or]')

    if operator not in ['and', 'or', 'eq', 'ne', 'in', 'nin', 'txt', 'ntxt']:
        raise DBException('Operator is not supported. Supported operators are [and, or, eq, ne, in, nin, txt, ntxt]')

    if property is not None:
        properties = get_props(graph)
        if property not in properties:
            raise DBException('Property is not supported. Supported properties are: ' + ', '.join(properties))

    return rule

def find(graph, rules={}, offset=0, limit=30):
    result = False
    if (isinstance(rules, list)):
        result = query_rule(graph, {'op': 'and', 'rules': rules})
    else:
        result = query_rule(graph, rules)

    ids = list(result)
    response = []

    for node, data in graph.nodes(data=True):
        prop = data.get('prop')
        if prop == 'id' and node in ids:
            item = {}
            for neighbor in graph.neighbors(node):
                if graph.nodes[neighbor]['field_type'] == 'array':
                    if item.get(graph.nodes[neighbor]['prop']) is None:
                        item[graph.nodes[neighbor]['prop']] = []
                    item[graph.nodes[neighbor]['prop']].append(neighbor)
                else:
                    item[graph.nodes[neighbor]['prop']] = neighbor
            response.append(item)

    # TODO implement offset and limit, to be able to handle bigger sets
    return response
