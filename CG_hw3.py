#!/usr/bin/python3
import argparse
import numpy as np
import re 

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
parser.add_argument('-j', type=int)
parser.add_argument('-k', type=int)
parser.add_argument('-o', type=int)
parser.add_argument('-p', type=int)

args = parser.parse_args()

fileName = args.f if args.f else 'hw3.ps'
lowerBoundx = args.a if args.a else 0
lowerBoundy = args.b if args.b else 0
upperBoundx = args.c if args.c else 499
upperBoundy = args.d if args.d else 499
scalingFactor = args.s if args.s else 1.0
xTranslation = args.m if args.m else 0
yTranslation = args.n if args.n else 0
rotation = args.r if args.r else 0
lowerVPx = args.j if args.j else 0
lowerVPy = args.k if args.k else 0
upperVPx = args.o if args.o else 200
upperVPy = args.p if args.p else 200

graph = []
file1 = open(fileName, 'r')
Lines = file1.readlines()
polygon = []

for line in Lines:
    line = re.split(r'\s{1,}', line.strip())
    try:
        int(line[0]) or int(line[1])
        if str(line[0]) == '':
            polygon.append([int(line[1]), int(line[2])])
        else:
            polygon.append([int(line[0]), int(line[1])])
    except:
        if str(line[0]) == "stroke":
            graph.append(polygon)
            polygon = []
        continue

def graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation):
    graph_after_transformation = []
    for polygon in graph:
        polygon_after_transformation = []
        for i in polygon:
            x0 = i[0]*scalingFactor
            y0 = i[1]*scalingFactor
            x0_ = x0*np.cos(np.radians(rotation))-y0*np.sin(np.radians(rotation))+xTranslation
            y0_ = x0*np.sin(np.radians(rotation))+y0*np.cos(np.radians(rotation))+yTranslation
            polygon_after_transformation.append([int(x0_), int(y0_)])
        graph_after_transformation.append(polygon_after_transformation)
    return graph_after_transformation

def clip_each_edge(graph, x1, y1, x2, y2):
    new_graph = []
    for polygon in graph:
        new_polygon = []
        for i in range(len(polygon)):
            ix = polygon[i][0]
            iy = polygon[i][1]
            if i == len(polygon) - 1:
                jx = polygon[0][0]
                jy = polygon[0][1]
            else:
                jx = polygon[i+1][0]
                jy = polygon[i+1][1]

            # check vi and v(i+1) wrt the clip edge. Comparing the gradient of point i or j with and point (x1, y1) wrt to line (x1, y1) to (x2, y2)
            iWRTedge = (iy-y1)*(x2-x1)-(ix-x1)*(y2-y1)
            jWRTedge = (jy-y1)*(x2-x1)-(jx-x1)*(y2-y1)

            # case in->in
            if iWRTedge < 1 and jWRTedge < 1:
                new_polygon.append([int(ix), int(iy)])
                #new_graph.append([int(jx), int(jy)])
            # case out->out
            elif iWRTedge >= 1 and jWRTedge >= 1:
                continue
            # case in->out
            elif iWRTedge < 1 and jWRTedge >= 1:
                new_polygon.append([int(ix), int(iy)])
                newx = ((x1*y2-y1*x2)*(ix-jx)-(x1-x2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
                newy = ((x1*y2-y1*x2)*(iy-jy)-(y1-y2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
                new_polygon.append([int(newx), int(newy)])
            # case out->in
            else: 
                newx = ((x1*y2-y1*x2)*(ix-jx)-(x1-x2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
                newy = ((x1*y2-y1*x2)*(iy-jy)-(y1-y2)*(ix*jy-iy*jx))/((x1-x2)*(iy-jy)-(y1-y2)*(ix-jx))
                new_polygon.append([int(newx), int(newy)])
        new_graph.append(new_polygon)
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

def graph_after_viewports(graph):
    graph_after_viewports = []
    for polygon in graph:
        polygon_after_viewports = []
        for i in polygon:
            x = lowerVPx+(i[0]-lowerBoundx)*(upperVPx+1-lowerVPx)/(upperBoundx-lowerBoundx)
            y = lowerVPy+(i[1]-lowerBoundy)*(upperVPy+1-lowerVPy)/(upperBoundy-lowerBoundy)
            polygon_after_viewports.append([int(x), int(y)])
        graph_after_viewports.append(polygon_after_viewports)
    return graph_after_viewports

def scan_fill(polygon):
    bucket = {}
    for i in range(len(polygon)):
        x1 = polygon[i][0]
        y1 = polygon[i][1]
        if i == len(polygon) - 1:
            x2 = polygon[0][0]
            y2 = polygon[0][1]
        else:
            x2 = polygon[i+1][0]
            y2 = polygon[i+1][1]
        for j in range(min(y1,y2), max(y1,y2)):
            try: 
                x = ((x1*y2-y1*x2)*(-1-502)-(x1-x2)*(-1*j-j*502))/(-(y1-y2)*(-1-502))
                try:
                    bucket[500-j].append(int(x))
                except:
                    bucket[500-j] = []
                    bucket[500-j].append(int(x))
            except:
                continue
    return bucket

def graph_with_scan_line(graph):
    graph_to_pbm = []
    for i in range(501):
        graph_to_pbm.append([0]*501)
    for polygon in graph:
        bucket = scan_fill(polygon)
        for i in bucket:
            bucket[i].sort()
            for j in range(0, len(bucket[i]), 2):
                try:
                    for k in range(bucket[i][j], bucket[i][j+1]+1):
                        graph_to_pbm[i][k] = 1
                except:
                    continue
    return graph_to_pbm
    
if __name__=='__main__':
    graph_after_transformation = graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation)
    graph_after_cohen = graph_after_cohen(graph_after_transformation)
    graph_after_viewports = graph_after_viewports(graph_after_cohen)
    graph_with_scan_line = graph_with_scan_line(graph_after_viewports)

    print("P1\n501 501")
    for line in graph_with_scan_line:
        print(print(*line))