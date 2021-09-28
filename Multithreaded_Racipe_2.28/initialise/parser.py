import pandas as pd
import numpy as np


def parse_topo(params, filename, process_seed):
    # reading topo data
    topo_data = pd.read_csv("{}/{}.topo".format(params['input_folder_name'], filename), sep=" ").to_numpy()
    np.random.seed(process_seed)
    # getting unique node names and assigning ids

    try:
        node_id_file = open("{}/{}.ids".format(params['input_folder_name'], filename), 'r').read().split("\n")[1:-1]
    except:
        raise FileNotFoundError(
            "Please add '{}.ids' file in the '{}' directory, with a list of genes and IDs.".format(filename, params[
                'input_folder_name']))
    node_names = []
    node_id = []
    for i in node_id_file:
        temp = i.split(" ")
        node_names.append(temp[0])
        node_id.append(int(temp[1]))

    # creating a node to id dictionary
    node_to_id = dict(zip(node_names, node_id))

    # checking if node ids are in ascending order starting from 0:
    for i in range(len(node_id)):
        if node_id[i] != i:
            raise ValueError("Please assign node IDs in an increasing order starting from 0 (i.e. 0,1,2,3...).")

    # sorting out topo_data
    for i in range(len(topo_data)):
        topo_data[i][0] = node_to_id[topo_data[i][0]]
        topo_data[i][1] = node_to_id[topo_data[i][1]]

    n = len(node_names)  # number of nodes

    # generating link matrix (source,target)
    link_matrix = np.zeros((n, n))
    for i in topo_data:
        link_matrix[i[0]][i[1]] = 1 if i[2] == 1 else -1

    # make a id to node dictionary
    id_to_node = dict(zip(node_id, node_names))

    # return statements
    return link_matrix, id_to_node
