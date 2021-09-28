import numpy as np
import matplotlib.pyplot as plt
from math import pow
import os
from copy import copy
from scipy.stats import norm, zscore

import statsmodels.api as sm
from scipy.spatial.distance import jensenshannon
from statsmodels.stats.weightstats import DescrStatsW
#from scipy.stats import kde
# from scipy import stats

from matplotlib import rcParams

####
import initialise.initialise as initialise
import initialise.parser as parser
in_file = 'init.txt'

begin=1
process_count=1
numsplit = 3

params = initialise.initialise(in_file)
id_to_node=[]

for j in params['input_filenames']:
                random_seed = int(begin) + process_count
                link_matrix, id_to_node = parser.parse_topo(params,j, random_seed)
 #####

network_name =  params['input_filenames'][0] # name_solution.dat and name_async_unweigh_ssprob_all.txt files
discard_cols = 3

left= params['constant_node_count'][0]
right=len(id_to_node)-1

#give input as new solution file created by racipe

data=np.loadtxt("{}_solution.dat".format(network_name))[:,discard_cols - 1:]
weights_states = data[:,0]
data = data[:, 1:]

length=right-left+1

datacol = [data[:,u] for u in range(left,right + 1)]
print("dataloaded")

zscoredx = [0]* length
for u in range(length):
    weighted_mean = DescrStatsW(datacol[u], weights = weights_states, ddof = 0)
    zscoredx[u] = (datacol[u] - weighted_mean.mean)/weighted_mean.std

print("zscore done")

kdefitx = [sm.nonparametric.KDEUnivariate(zscoredx[u]) for u in range(0,length)]
for u in range(0,length):
    kdefitx[u].fit(bw = 0.1)
print("kdefit done")

pivot=[0]*length
pivotpos=[0]*length
n = len(kdefitx[0].support)

racipeclassify = {}

for i in range(len(zscoredx[0])):
    zarr=[0]*length
    power=int(2**(length-1) +1e-9)
    index=int(0)
    for u in range(length):

        zarr[u]=int(zscoredx[u][i] >0)
        index+=power*zarr[u]
        power=power/2
    index = int(index)
    try:
        racipeclassify[index] += weights_states[i]
    except:
        racipeclassify[index] = weights_states[i]

dividend = sum(weights_states)
for u in racipeclassify.keys():
    racipeclassify[u] = racipeclassify[u] / dividend

binlabelformat = "{0:0" + str(length) +  "b}"




final_index = []


for i in racipeclassify.keys():
    if racipeclassify[i] >= 0.01:
        final_index.append(i)


datasplit = []
weightsplit = []
for k in range(numsplit - 1):
    a = []
    for j in datacol:
        size = j.shape[0]//numsplit
        a.append(j[k * size : (k+1) * size])
    datasplit.append(a)
a = []
for j in datacol:
    size = j.shape[0]//numsplit
    a.append(j[(numsplit - 1) * size:])
datasplit.append(a)

size = len(weights_states)//numsplit
for i in range(numsplit - 1):
    weightsplit.append(weights_states[i * size : (i + 1) * size])
weightsplit.append(weights_states[(numsplit - 1) * size:])


racipeclassify_all = [0] * (numsplit + 1)
for i in range(numsplit + 1):
    racipeclassify_all[i] = copy(racipeclassify)

for splititer in range(numsplit):
    zscoredx = [0]* length
    for u in range(length):
        weighted_mean = DescrStatsW(datasplit[splititer][u], weights = weightsplit[splititer], ddof = 0)
        zscoredx[u] = (datasplit[splititer][u] - weighted_mean.mean)/weighted_mean.std
    print("zscore done")

    kdefitx = [sm.nonparametric.KDEUnivariate(zscoredx[u]) for u in range(0,length)]
    for u in range(0,length):
        kdefitx[u].fit(bw = 0.1)
    print("kdefit done")

    pivot=[0]*length
    pivotpos=[0]*length
    n = len(kdefitx[0].support)

    for i in racipeclassify_all[splititer + 1].keys():
        racipeclassify_all[splititer + 1][i] = 0
    for i in range(len(zscoredx[0])):
        zarr=[0]*length
        power=int(2**(length-1) +1e-9)
        index=int(0)
        for u in range(length):

            zarr[u]=int(zscoredx[u][i] >0)
            index+=power*zarr[u]
            power=power/2
        index = int(index)
        try:
            racipeclassify_all[splititer + 1][index] += weightsplit[splititer][i]
        except:
            racipeclassify_all[splititer + 1][index] = weightsplit[splititer][i]


    dividend = sum(weightsplit[splititer])
    for u in racipeclassify_all[splititer + 1].keys():
        racipeclassify_all[splititer + 1][u] = racipeclassify_all[splititer + 1][u] / dividend


    binlabelformat = "{0:0" + str(length) +  "b}"

error_final = {}
for i in racipeclassify_all[0].keys():
    nums = [racipeclassify_all[j][i] for j in range(1, numsplit + 1)]
    error_final[i] = np.std(nums)


racipe_probfilefull = open("Datafiles_error/{}_racipe_probfull_error.txt".format(network_name), 'w')
for i in racipeclassify.keys():
    label = binlabelformat.format(i)
    racipe_probfilefull.write("{} {:.6f} {:.6f}\n".format(label, racipeclassify[i], error_final[i]))


racipe_probfile = open("Datafiles_error/{}_racipe_prob_error.txt".format(network_name), 'w')
for i in final_index:
    label = binlabelformat.format(i)
    racipe_probfile.write("{} {:.6f} {:.6f}\n".format(label, racipeclassify[i], error_final[i]))

racipe_probfile.close()
racipe_probfilefull.close()
