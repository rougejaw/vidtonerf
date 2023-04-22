import json
import sys
import numpy as np
import math
import sklearn.cluster
import random

if __name__ =='__main__':
    input_file = sys.argv[1]

    input_str = open(input_file)
    input = json.loads(input_str.read())


    #TODO Make this input passed in, with default value 100
    CLUSTERS = 100

    extrins = []
    angles = []
    for f in input["frames"]:
        extrinsic = np.array(f["extrinsic_matrix"])
        extrins+=[ extrinsic ]
    for i,e in enumerate(extrins):

        # t == rectangular coordinates
        t = e[0:3,3]

        # s == spherical coordinates

        # r = sqrt(x^2 + y^2 + z^2)
        r = math.sqrt((t[0]*t[0])+(t[1]*t[1])+(t[2]*t[2]))
        theta = math.acos(t[2]/r)
        phi = math.atan(t[1]/t[0])

        #convert radian to degrees

        theta = (theta * 180) / math.pi
        phi = (phi * 180) / math.pi

        s = [theta,phi]

        angles.append(s)

    km = sklearn.cluster.k_means(X=angles, n_clusters=CLUSTERS, n_init=10)

    seen_numbers=[]
    for i in km[1]:
        if (i not in seen_numbers):
            seen_numbers.append(i)

    #TODO account for this
    if (len(seen_numbers) != CLUSTERS):
        print("TOO FEW CLUSTERS")

    cluster_array = [ [] for _ in range(CLUSTERS) ]
    return_array = []

    for i in range(len(angles)):
        cluster_array[km[1][i]].append(i)

    #TODO instead of being completely random, take the point closest to the centroid
    for i in range(len(cluster_array)):
        return_array.append(cluster_array[i][random.randint(0,len(cluster_array[i])-1)])

    print(return_array)

    with open("new_"+input_file, "w") as outfile:
        json.dump(return_array, outfile, indent=4)