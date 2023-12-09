import json
import sys
import numpy as np
import math
import sklearn.cluster

if __name__ == '__main__':
    input_file = sys.argv[1]
    CLUSTERS = 100
    if len(sys.argv) > 2:
        CLUSTERS = int(sys.argv[2])

    with open(input_file) as file:
        input = json.loads(file.read())

    extrins = []
    angles = []
    for f in input["frames"]:
        extrinsic = np.array(f["extrinsic_matrix"])
        extrins.append(extrinsic)
    for e in extrins:
        t = e[0:3, 3]
        r = math.sqrt(sum(t**2))
        theta = math.acos(t[2]/r)
        phi = math.atan2(t[1], t[0])  #atan accounts for when x=0
        theta = (theta * 180) / math.pi
        phi = (phi * 180) / math.pi
        s = [theta, phi]
        angles.append(s)

    km = sklearn.cluster.KMeans(n_clusters=CLUSTERS, n_init=10).fit(angles)

    if len(set(km.labels_)) != CLUSTERS:
        print("TOO FEW CLUSTERS")

    cluster_array = [[] for _ in range(CLUSTERS)]
    return_array = []

    for i, label in enumerate(km.labels_):
        cluster_array[label].append(i)

    for i, cluster in enumerate(cluster_array):
        centroid = km.cluster_centers_[i]
        closest_point = min(cluster, key=lambda x: np.linalg.norm(np.array(angles[x]) - centroid))
        return_array.append(closest_point)

    print(return_array)

    with open("new_" + input_file, "w") as outfile:
        json.dump(return_array, outfile, indent=4)
