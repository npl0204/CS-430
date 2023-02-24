#!/usr/bin/python3
import argparse
import numpy as np
from numpy import linalg as LA
import re 
import sys
parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str)
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

fileName = args.f if args.f else 'bound-lo-sphere.smf'
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

file1 = open(fileName, 'r')
Lines = file1.readlines()
vertices = []
faces = []

for line in Lines:
    line = re.split(r'\s{1,}', line.strip())
    if str(line[0]) == 'v':
        vertices.append([float(line[1]), float(line[2]), float(line[3]), 1])
    else:
        faces.append([int(line[1])-1, int(line[2])-1, int(line[3])-1])

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

def parallel_projection(vertices):
    parallel_projection = []
    Npar = np.dot(Spar,np.dot(Tpar,np.dot(SHpar,np.dot(R,TVRP))))
    for i in vertices:
        parallel_projection.append(np.dot(Npar, i))
    return parallel_projection

def perspective_projection(vertices):
    perspective_projection = []
    Nper = np.dot(M, np.dot(Sper,np.dot(SHpar,np.dot(TPRP,np.dot(R,TVRP)))))
    for i in vertices:
        perspective_projection.append(np.dot(Nper, i))
        perspective_projection[-1] /= perspective_projection[-1][3]
    return perspective_projection

window = 0 #bit 4 is 0000 
WL = 1 #bit 4 is 0001 - window left
WR = 2 #bit 4 is 0010 - window right
WB = 4 #bit 4 is 0100 - window bottom
WT = 8 #bit 4 is 1000 - window top

def clipRegion(x, y):
    code = window 
    if y > 1:
        code |= WT 
    elif y < -1:
        code |= WB 
    if x > 1:
        code |= WR
    elif x < -1:
        code |= WL
    return code

def cohenSutherlandClip(x0, y0, x1, y1): 
    while True: 
        region0 = clipRegion(x0, y0) 
        region1 = clipRegion(x1, y1)
        # both inside window
        if region0 == 0 and region1 == 0: 
            return [x0, y0, x1, y1]
        # both outside window
        elif (region0 & region1) != 0: 
            return [0, 0, 0, 0]
        # one of the point outside window
        else: 
            if region0 != 0: 
                out = region0 
            else: 
                out = region1 
            if out & WT != 0: # & is bitwise, cannot use and
                x = (1 - y0)*(x1 - x0)/(y1 - y0) + x0
                y = 1 
            elif out & WB != 0: 
                x = (-1 - y0)*(x1 - x0)/(y1 - y0) + x0
                y = -1 
            elif out & WR != 0: 
                y = (1 - x0)*(y1 - y0)/(x1 - x0) + y0
                x = 1 
            else: 
                y = (-1 - x0)*(y1 - y0)/(x1 - x0) + y0
                x = -1 
            if out == region0: 
                x0 = x
                y0 = y
            else: 
                x1 = x
                y1 = y

def clipping(projection, faces):
    graph_after_cohen = []
    for face in faces:
        a = cohenSutherlandClip(projection[face[0]][0], projection[face[0]][1], projection[face[1]][0], projection[face[1]][1])
        if a == [0, 0, 0, 0]:
            continue
        else:
            x1, y1, x2, y2  = a[0], a[1], a[2], a[3]
        a = cohenSutherlandClip(projection[face[0]][0], projection[face[0]][1], projection[face[2]][0], projection[face[2]][1])
        if a == [0, 0, 0, 0]:
            continue
        else:
            x1, y1, x3, y3  = a[0], a[1], a[2], a[3]
        vertex = [[x1, y1, projection[face[0]][2], 1], [x2, y2, projection[face[1]][2], 1], [x3, y3, projection[face[2]][2], 1]]
        graph_after_cohen.append(vertex)
    return graph_after_cohen

def mapping(projection):
    graph = []
    T1 = [[1,0,0,lowerVPx],[0,1,0,lowerVPy],[0,0,1,1],[0,0,0,1]]
    S = [[(upperVPx-lowerVPx)/2,0,0,0],[0,(upperVPy-lowerVPy)/2,0,0],[0,0,1,0],[0,0,0,1]]
    T2 = [[1,0,0,1],[0,1,0,1],[0,0,1,1],[0,0,0,1]]
    M_VV3DV = np.dot(T1, np.dot(S, T2))
    for i in projection:
        vertex = []
        for j in i:
            vertex.append(np.dot(M_VV3DV, j))
        graph.append(vertex)
    return graph

if __name__=='__main__':
    if paraPro:
        projection = parallel_projection(vertices)
    else:
        projection = perspective_projection(vertices)
    graph = clipping(projection, faces)
    graph = mapping(graph)

    print("%!PS\n")
    print("0.1 setlinewidth")
    print("%%BeginSetup")
    print("  << /PageSize [" + str(500+1), str(500+1) + "] >> setpagedevice")
    print("%%EndSetup\n")
    print("%%%BEGIN")
    
    for i in graph:
        print(i[0][0], i[0][1], "moveto")
        print(i[1][0], i[1][1], "lineto")
        print(i[2][0], i[2][1], "lineto")
        print(i[0][0], i[0][1], "lineto")
        print("stroke")
    print("%%%END")