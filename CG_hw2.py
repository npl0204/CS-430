#!/usr/bin/python3
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str)
parser.add_argument('-a', type=int)
parser.add_argument('-b', type=int)
parser.add_argument('-c', type=int)
parser.add_argument('-d', type=int)
parser.add_argument('-s', type=float)
parser.add_argument('-m', type=int)
parser.add_argument('-n', type=int)
parser.add_argument('-r', type=int)

args = parser.parse_args()

fileName = args.f if args.f else 'hw2_a.ps'
lowerBoundx = args.a if args.a else 0
lowerBoundy = args.b if args.b else 0
upperBoundx = args.c if args.c else 499
upperBoundy = args.d if args.d else 499
scalingFactor = args.s if args.s else 1.0
xTranslation = args.m if args.m else 0
yTranslation = args.n if args.n else 0
rotation = args.r if args.r else 0

graph = []
file1 = open(fileName, 'r')
Lines = file1.readlines()

for line in Lines:
    line = line.split(' ')
    try:
        int(line[0])
        graph.append([int(line[0]), int(line[1])])
    except:
        continue

def graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation):
    graph_after_transformation = []
    for i in graph:
        x0 = i[0]*scalingFactor
        y0 = i[1]*scalingFactor
        x0_ = x0*np.cos(np.radians(rotation))-y0*np.sin(np.radians(rotation))+xTranslation
        y0_ = x0*np.sin(np.radians(rotation))+y0*np.cos(np.radians(rotation))+yTranslation
        graph_after_transformation.append([int(x0_), int(y0_)])
    return graph_after_transformation

def clip_each_edge(graph, x1, y1, x2, y2):
    new_graph = []
    for i in range(len(graph)):
        ix = graph[i][0]
        iy = graph[i][1]
        if i == len(graph) - 1:
            jx = graph[0][0]
            jy = graph[0][1]
        else:
            jx = graph[i+1][0]
            jy = graph[i+1][1]

        # check vi and v(i+1) wrt the clip edge. Comparing the gradient of point i or j with and point (x1, y1) wrt to line (x1, y1) to (x2, y2)
        iWRTedge = (iy-y1)*(x2-x1)-(ix-x1)*(y2-y1)
        jWRTedge = (jy-y1)*(x2-x1)-(jx-x1)*(y2-y1)

        # case in->in
        if iWRTedge < 0 and jWRTedge < 0:
            new_graph.append([int(ix), int(iy)])
            #new_graph.append([int(jx), int(jy)])
        # case out->out
        elif iWRTedge >= 0 and jWRTedge >= 0:
            continue
        # case in->out
        elif iWRTedge < 0 and jWRTedge >= 0:
            new_graph.append([int(ix), int(iy)])
            newx = ((x1*y2-y1*x2)*(ix-jx)-(x1-x2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
            newy = ((x1*y2-y1*x2)*(iy-jy)-(y1-y2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
            new_graph.append([int(newx), int(newy)])
        # case out->in
        else: 
            newx = ((x1*y2-y1*x2)*(ix-jx)-(x1-x2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
            newy = ((x1*y2-y1*x2)*(iy-jy)-(y1-y2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
            new_graph.append([int(newx), int(newy)])
    return new_graph

def graph_after_cohen(graph):
    edges = [[lowerBoundx, lowerBoundy], [lowerBoundx, upperBoundy], [upperBoundx, upperBoundy], [upperBoundx, lowerBoundy]]
    for i in range(len(edges)):
        x1 = edges[i][0]
        y1 = edges[i][1]
        if i == len(edges) - 1:
            x2 = edges[0][0]
            y2 = edges[0][1]
        else:
            x2 = edges[i+1][0]
            y2 = edges[i+1][1]
        graph = clip_each_edge(graph, x1, y1, x2, y2)
    return graph

if __name__=='__main__':
    graph_after_transformation = graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation)
    graph_after_cohen = graph_after_cohen(graph_after_transformation)
    
    print("%!PS\n")
    print("0.1 setlinewidth")
    print("%%BeginSetup")
    print("  << /PageSize [" + str(upperBoundx-lowerBoundx+1), str(upperBoundy-lowerBoundy+1) + "] >> setpagedevice")
    print("%%EndSetup\n")
    print("%%%BEGIN")
    
    if len(graph_after_cohen) > 0:
        print(graph_after_cohen[0][0]-lowerBoundx, graph_after_cohen[0][1]-lowerBoundy, "moveto")
        for i in range(1, len(graph_after_cohen)):
            print(graph_after_cohen[i][0]-lowerBoundx, graph_after_cohen[i][1]-lowerBoundy, "lineto")
        print(graph_after_cohen[0][0]-lowerBoundx, graph_after_cohen[0][1]-lowerBoundy, "lineto")
    else:
        print("0 0 moveto")
        print("0 0 lineto")
    print("stroke")
    print("%%%END")