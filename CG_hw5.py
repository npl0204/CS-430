#!/usr/bin/python3
import argparse
import numpy as np
from numpy import linalg as LA
import re 
import sys
import math

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str)
parser.add_argument('-g', type=str)
parser.add_argument('-i', type=str)
parser.add_argument('-j', type=int)
parser.add_argument('-k', type=int)
parser.add_argument('-o', type=int)
parser.add_argument('-p', type=int)
parser.add_argument('-x', type=float)
parser.add_argument('-y', type=float)
parser.add_argument('-z', type=float)
parser.add_argument('-X', type=float)
parser.add_argument('-Y', type=float)
parser.add_argument('-Z', type=float)
parser.add_argument('-q', type=float)
parser.add_argument('-r', type=float)
parser.add_argument('-w', type=float)
parser.add_argument('-Q', type=float)
parser.add_argument('-R', type=float)
parser.add_argument('-W', type=float)
parser.add_argument('-u', type=float)
parser.add_argument('-v', type=float)
parser.add_argument('-U', type=float)
parser.add_argument('-V', type=float)
parser.add_argument('-P', action='store_true')
parser.add_argument('-B', type=float)
parser.add_argument('-F', type=float)

args = parser.parse_args()

fileName = args.f if args.f else 'bound-sprellpsd.smf'
fileName2 = args.g if args.g else ' '
fileName3 = args.i if args.i else ' '
lowerVPx = args.j if args.j else 0
lowerVPy = args.k if args.k else 0
upperVPx = args.o if args.o else 500
upperVPy = args.p if args.p else 500
xPRP = args.x if args.x else 0.0
yPRP = args.y if args.y else 0.0
zPRP = args.z if args.z else 1.0
xVRP = args.X if args.X else 0.0
yVRP = args.Y if args.Y else 0.0
zVRP = args.Z if args.Z else 0.0
xVPN = args.q if args.q else 0.0
yVPN = args.r if args.r else 0.0
zVPN = args.w if args.w else -1.0
xVUP = args.Q if args.Q else 0.0
yVUP = args.R if args.R else 1.0
zVUP = args.W if args.W else 0.0
minVRCx = args.u if args.u else -0.7
minVRCy = args.v if args.v else -0.7
maxVRCx = args.U if args.U else 0.7
maxVRCy = args.V if args.V else 0.7
paraPro = args.P
front = args.F if args.F else 0.6
back = args.B if args.B else -0.6

Maxval = 256

def read_file(file):
    Lines = file.readlines()
    vertices = []
    faces = []
    for line in Lines:
        line = re.split(r'\s{1,}', line.strip())
        if str(line[0]) == 'v':
            vertices.append([float(line[1]), float(line[2]), float(line[3]), 1])
        elif str(line[0]) == 'f':
            faces.append([int(line[1])-1, int(line[2])-1, int(line[3])-1])
    return vertices, faces

file1 = open(fileName, 'r')
vertices1, faces1 = read_file(file1)

# 1. Translate VRP to the origin
TVRP = [[1,0,0,-xVRP], [0,1,0,-yVRP], [0,0,1,-zVRP], [0,0,0,1]]
# 2. Rotate so VPN becomes z, VUP becomes y and u becomes x 
rz = np.divide([xVPN,yVPN,zVPN], LA.norm([xVPN,yVPN,zVPN]))
rx = np.divide(np.cross([xVUP,yVUP,zVUP], rz), LA.norm(np.cross([xVUP,yVUP,zVUP], rz)))
ry = np.cross(rz, rx)
R = [[rx[0],rx[1],rx[2],0],[ry[0],ry[1],ry[2],0],[rz[0],rz[1],rz[2],0],[0,0,0,1]]
# 3'. Translate COP to origin
TPRP = [[1,0,0,-xPRP], [0,1,0,-yPRP], [0,0,1,-zPRP], [0,0,0,1]]
# # 3. Shear to make direction of the projection become parallel to z
shx = (1/2*(maxVRCx+minVRCx)-xPRP)/zPRP
shy = (1/2*(maxVRCy+minVRCy)-yPRP)/zPRP
SHpar = [[1,0,shx,0],[0,1,shy,0],[0,0,1,0],[0,0,0,1]]
# 4. Translate and scale into a canonical view volume
Tpar = [[1,0,0,-(maxVRCx+minVRCx)/2],[0,1,0,-(maxVRCy+minVRCy)/2],[0,0,1,-front],[0,0,0,1]]
Spar = [[2/(maxVRCx-minVRCx),0,0,0],[0,2/(maxVRCy-minVRCy),0,0],[0,0,1/(front-back),0],[0,0,0,1]]
Sper = [[(2*zPRP)/((maxVRCx-minVRCx)*(zPRP-back)),0,0,0],[0,(2*zPRP)/((maxVRCy-minVRCy)*(zPRP-back)),0,0],[0,0,1/(zPRP-back),0],[0,0,0,1]]
# 5. Perspective to parallel
zmin = (zPRP - front)/(back - zPRP)
M = [[1,0,0,0],[0,1,0,0],[0,0,1/(1+zmin), -zmin/(1+zmin)],[0,0,-1,0]]

# def parallel_projection(vertices):
#     parallel_projection = []
#     Npar = np.dot(Spar,np.dot(Tpar,np.dot(SHpar,np.dot(R,TVRP))))
#     for i in vertices:
#         parallel_projection.append(np.dot(Npar, i))
#     return parallel_projection

# def perspective_projection(vertices):
#     perspective_projection = []
#     z = []
#     Nper = np.dot(M, np.dot(Sper,np.dot(SHpar,np.dot(TPRP,np.dot(R,TVRP)))))
#     for i in vertices:
#         perspective_projection.append(np.dot(Nper, i))
#         z.append(perspective_projection[-1][2])
#         perspective_projection[-1] /= perspective_projection[-1][3]
#     return perspective_projection, z

def mapping(vertices, faces):
    T1 = [[1,0,0,lowerVPx],[0,1,0,lowerVPy],[0,0,1,1],[0,0,0,1]]
    S = [[(upperVPx-lowerVPx)/2,0,0,0],[0,(upperVPy-lowerVPy)/2,0,0],[0,0,1,0],[0,0,0,1]]
    T2 = [[1,0,0,1],[0,1,0,1],[0,0,1,1],[0,0,0,1]]
    M_VV3DV = np.dot(T1, np.dot(S, T2))
    if paraPro:
        projection = []
        Npar = np.dot(Spar,np.dot(Tpar,np.dot(SHpar,np.dot(R,TVRP))))
        for i in vertices:
            projection.append(np.dot(Npar, i))
        graph = []
        projection_ = []
        for face in faces:
            projection_.append([projection[face[0]], projection[face[1]], projection[face[2]], projection[face[0]]])
        for i in projection_:
            vertex = []
            for j in i: 
                x, y, a, b = np.dot(M_VV3DV, j)
                vertex.append([x, y, j[2]])
            graph.append(vertex)
    else:
        projection = []
        z = []
        Nper = np.dot(M, np.dot(Sper,np.dot(SHpar,np.dot(TPRP,np.dot(R,TVRP)))))
        for i in vertices:
            projection.append(np.dot(Nper, i))
            z.append(projection[-1][2])
            projection[-1] /= projection[-1][3]
        graph = []
        projection_ = []
        z_ = []
        for face in faces:
            projection_.append([projection[face[0]], projection[face[1]], projection[face[2]], projection[face[0]]])
            z_.append([z[face[0]], z[face[1]], z[face[2]], z[face[0]]])
        for i in range(len(projection_)):
            vertex = []
            for j in range(len(projection_[i])): 
                x, y, a, b = np.dot(M_VV3DV, projection_[i][j])
                vertex.append([x, y, z_[i][j]])
            graph.append(vertex)
    return graph

def depth_cueing(pz):
    near = 0
    far = -1
    return str(int(Maxval*(pz-far)/(near-far)))

def scanfill(polygon, color, F, Z):
    edge = {}
    for y in range(0, 501):
        edge[y] = []
        for i in range(len(polygon)-1):
            x1, y1, z1 = polygon[i]
            x2, y2, z2 = polygon[i+1]
            if int(y1) == int(y2):
                continue
            elif y >= min(y1, y2) and y < max(y1, y2):
                x = ((x1*y2-y1*x2)*(-1-502)-(x1-x2)*(-1*y-y*502))/(-(y1-y2)*(-1-502))
                z = z1-((z1-z2)*(y1-y)/(y1-y2))
                if x1 == x2:
                    x = x1
                edge[y].append((int(x), z))
    for y in edge:
        if len(edge[y]) <= 0:
            continue
        val = edge[y]
        val.sort(key=lambda x: x[0])
        x1, x2 = val[0][0], val[1][0]
        z1, z2 = val[0][1], val[1][1]
        for x in range(x1, x2 + 1):
            if x == x1:
                pz = z1
            elif x == x2:
                pz = z2
            else:
                pz = z2-(z2-z1)*((x2-x)/(x2-x1))
            if pz < 0 and pz > Z[y][x]:
                Z[y][x] = pz
                if color == "red":
                    F[500 - y][x] = "{} 00 00".format(depth_cueing(pz))
                elif color == "green":
                    F[500 - y][x] = "00 {} 00".format(depth_cueing(pz))
                elif color == "blue":
                    F[500 - y][x] = "00 00 {}".format(depth_cueing(pz))
    return F, Z

def graph_with_scan_line(graph1, graph2, graph3):
    F = [["00 00 00"]*501 for i in range(501)]
    Z = [[-1]*501 for i in range(501)]
    for i in range(len(graph1)):
        F, Z = scanfill(graph1[i], "red", F, Z)
    if len(graph2) != 0:
        for i in range(len(graph2)):
            F, Z = scanfill(graph2[i], "green", F, Z)
    if len(graph3) != 0:
        for i in range(len(graph3)):
            F, Z = scanfill(graph3[i], "blue", F, Z)
    return F

if __name__=='__main__':
    print("P3\n501 501\n{}".format(Maxval))

    # if paraPro:
    #     graph1 = parallel_projection(vertices1)
    # else:
    #     graph1 = perspective_projection(vertices1)
    graph1 = mapping(vertices1, faces1)
    
    graph2 = []
    graph3 = []
    if fileName2 != ' ':
        file2 = open(fileName2, 'r')
        vertices2, faces2 = read_file(file2)
        # if paraPro:
        #     graph2 = parallel_projection(vertices2)
        # else:
        #     graph2 = perspective_projection(vertices2)
        graph2 = mapping(vertices2, faces2)

    if fileName3 != ' ':
        file3 = open(fileName3, 'r')
        vertices3, faces3 = read_file(file3)
        # if paraPro:
        #     graph3 = parallel_projection(vertices3)
        # else:
        #     graph3 = perspective_projection(vertices3)
        graph3 = mapping(vertices3, faces3)

    graph = graph_with_scan_line(graph1, graph2, graph3)  
    for line in graph:
        print(*line)