import numpy as np

R = np.array([
    [-1.756492069,  -3.042333507,   1.139761726],  # 0
    [-2.91789798,   -5.053947553,   4.396223799],
    [-4.079303892,  -7.0655616, 7.652685873],
    [-4.543866256,  -7.870207219,   8.955270702],
    [-4.776147439,  -8.272530028,   9.606563117],
    [-5.240709803,  -9.077175647,   10.90914795],
    [-6.402115715,  -11.08878969,   14.16561002],
    [-7.563521626,  -13.10040374,   17.42207209],  # 7

    [-6.4,  -10,    21.3],  # 8
    [-6.4,  -6,     21.3],
    [-6.4,  -2,     21.3],
    [-6.4,  -0.4,   21.3],
    [-6.4,  0.4,    21.3],
    [-6.4,  2,      21.3],
    [-6.4,  6,      21.3],
    [-6.4,  10,     21.3],  # 15

    [3.512984138,   0,  1.139761726],  # 16
    [5.835795961,   0,  4.396223799],
    [8.158607784,   0,  7.652685873],
    [9.087732513,   0,  8.955270702],
    [9.552294877,   0,  9.606563117],
    [10.48141961,   0,  10.90914795],
    [12.80423143,   0,  14.16561002],
    [15.12704325,   0,  17.42207209],  # 23

    [13.70043101,   -2.5,    21.3],  # 24
    [10.2363294,    -4.5,    21.3],
    [6.772227782,   -6.5,    21.3],
    [5.386587136,   -7.3,    21.3],
    [4.693766812,   -7.7,    21.3],
    [3.308126166,   -8.5,    21.3],
    [-0.155975449,  -10.5,   21.3],
    [-3.620077064,  -12.5,   21.3],  # 31

    [-1.756492069,  3.042333507,    1.139761726],  # 32
    [-2.91789798,   5.053947553,    4.396223799],
    [-4.079303892,  7.0655616,  7.652685873],
    [-4.543866256,  7.870207219,    8.955270702],
    [-4.776147439,  8.272530028,    9.606563117],
    [-5.240709803,  9.077175647,    10.90914795],
    [-6.402115715,  11.08878969,    14.16561002],
    [-7.563521626,  13.10040374,    17.42207209],  # 39

    [-3.620077064,  12.5,   21.3],  # 40
    [-0.155975449,  10.5,   21.3],
    [3.308126166,   8.5,    21.3],
    [4.693766812,   7.7,    21.3],
    [5.386587136,   7.3,    21.3],
    [6.772227782,   6.5,    21.3],
    [10.2363294,    4.5,    21.3],
    [13.70043101,   2.5,    21.3],  # 47

    ]).T / 100.
    
fs = 48000;

if __name__ == "__main__":

    from point_cloud import PointCloud

    pyramic = PointCloud(X=R)

    pyramic.plot()
