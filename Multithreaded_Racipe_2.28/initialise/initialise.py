import initialise.strictdict as strictdict
import os


def initialise(initfilename):
    # initial conditions dictionary
    params = {}
    params['maxtime'] = 200
    params['input_folder_name'] = 'input'
    params['output_folder_name'] = 'output'
    params['input_filenames'] = ""
    params['num_simulations'] = 1000
    params['constant_node_count'] = ""
    params['num_runs'] = 1
    params = strictdict.StrictDict(params)

    # parse initfile
    initfile = open(initfilename, 'r').read().split("\n")[:-1]
    if len(initfile) != len(params.keys()):
        raise ValueError("Too many or too less input arguments in {}".format(initfilename))
    for i in initfile:
        temp = i.split(" ")
        params[temp[0]] = temp[1]
    for i in range(3, len(initfile) - 1):
        params[initfile[i].split(" ")[0]] = int(params[initfile[i].split(" ")[0]])

    # params dictionary set properly now
    # next, split all filenames
    params['input_filenames'] = params['input_filenames'].split(",")

    # split all constant_node_count(s)
    params['constant_node_count'] = [int(i) for i in params['constant_node_count'].split(",")]

    if len(params['constant_node_count']) != len(params['input_filenames']):
        raise ValueError(
            "Different number of constant node counts and filenames, please recheck {} file".format(initfilename))
    if params['num_runs'] < 1:
        raise ValueError("{} cannot be less than 1.".format("num_runs" if params['num_threads'] else "num_threads"))
    return params


def create_folders(params):
    # create output folders if they don't exist
    try:
        os.mkdir('{}'.format(params['output_folder_name']))
        print("Made folder {}".format(params['output_folder_name']))
    except:
        print("Folder {} exists already.".format(params['output_folder_name']))
    try:
        os.mkdir('{}/graphs'.format(params['output_folder_name']))
        print("Made folder {}/graphs".format(params['output_folder_name']))
    except:
        print("Folder {}/graphs exists already.".format(params['output_folder_name']))
