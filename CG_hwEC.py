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
parser.add_argument('-N', type=int)

args = parser.parse_args()

fileName = args.f if args.f else 'ExtraCredit.ps'
lowerBoundx = args.a if args.a else 0
lowerBoundy = args.b if args.b else 0
upperBoundx = args.c if args.c else 250
upperBoundy = args.d if args.d else 250
scalingFactor = args.s if args.s else 1.0
xTranslation = args.m if args.m else 0
yTranslation = args.n if args.n else 0
rotation = args.r if args.r else 0
lowerVPx = args.j if args.j else 0
lowerVPy = args.k if args.k else 0
upperVPx = args.o if args.o else 200
upperVPy = args.p if args.p else 200
numLine = args.N if args.N else 20

graph = []
file1 = open(fileName, 'r')
Lines = file1.readlines()
curve = []

for line in Lines:
    line = re.split(r'\s{1,}', line.strip())
    try:
        int(line[0])
        if str(line[-1]) == "moveto":
            curve.append([int(line[0]), int(line[1])])
        elif str(line[-1]) == "curveto":
            curve = curve + [[int(line[0]), int(line[1])], [int(line[2]), int(line[3])], [int(line[4]), int(line[5])]]
        else:
            graph.append([[int(line[0]), int(line[1])], [int(line[2]), int(line[3])]])
    except:
        if str(line[0]) == "stroke":
            graph.append(curve)
            curve = []
        continue  

def bezier(graph, numLine):
    graph_after_bezier = []
    for polygon in graph:
        polygon_after_bezier = []
        if len(polygon) == 4:
            x0, x1, x2, x3 = polygon[0][0], polygon[1][0], polygon[2][0], polygon[3][0]
            y0, y1, y2, y3 = polygon[0][1], polygon[1][1], polygon[2][1], polygon[3][1]
            i = 0
            while i <= 1:
                xi = ((1-i)**3)*x0+3*i*((1-i)**2)*x1+3*(i**2)*(1-i)*x2+(i**3)*x3
                yi = ((1-i)**3)*y0+3*i*((1-i)**2)*y1+3*(i**2)*(1-i)*y2+(i**3)*y3
                polygon_after_bezier.append([xi, yi])
                i = round((i+1/numLine), 8)
            graph_after_bezier.append(polygon_after_bezier)
        else:
            graph_after_bezier.append(polygon)
    return graph_after_bezier

def graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation):
    graph_after_transformation = []
    for polygon in graph:
        polygon_after_transformation = []
        for i in polygon:
            x0 = i[0]*scalingFactor
            y0 = i[1]*scalingFactor
            x0_ = x0*np.cos(np.radians(rotation))-y0*np.sin(np.radians(rotation))+xTranslation
            y0_ = x0*np.sin(np.radians(rotation))+y0*np.cos(np.radians(rotation))+yTranslation
            polygon_after_transformation.append([x0_, y0_])
        graph_after_transformation.append(polygon_after_transformation)
    return graph_after_transformation

window = 0 #bit 4 is 0000 
WL = 1 #bit 4 is 0001 - window left
WR = 2 #bit 4 is 0010 - window right
WB = 4 #bit 4 is 0100 - window bottom
WT = 8 #bit 4 is 1000 - window top

def clipRegion(x, y):
    code = window 
    if y > upperBoundy:
        code |= WT 
    elif y < lowerBoundy:
        code |= WB 
    if x > upperBoundx:
        code |= WR
    if x < lowerBoundx:
        code |= WL
    return code 

def cohenSutherlandClip(x0, y0, x1, y1): 
    while True: 
        region0 = clipRegion(x0, y0) 
        region1 = clipRegion(x1, y1)
        # both inside window
        if region0 == 0 and region1 == 0: 
            return x0, y0, x1, y1
        # both outside window
        elif (region0 & region1) != 0: 
            return None
        # one of the point outside window
        else: 
            if region0 != 0: 
                out = region0 
            else: 
                out = region1 
            if out & WT != 0: # & is bitwise, cannot use and
                x = (upperBoundy - y0)*(x1 - x0)/(y1 - y0) + x0
                y = upperBoundy 
            elif out & WB != 0: 
                x = (lowerBoundy - y0)*(x1 - x0)/(y1 - y0) + x0
                y = lowerBoundy 
            elif out & WR != 0: 
                y = (upperBoundx - x0)*(y1 - y0)/(x1 - x0) + y0
                x = upperBoundx 
            else: 
                y = (lowerBoundx - x0)*(y1 - y0)/(x1 - x0) + y0
                x = lowerBoundx 
            if out == region0: 
                x0 = x 
                y0 = y
            else: 
                x1 = x
                y1 = y

def graph_after_cohen(graph):
    graph_after_cohen = []
    for polygon in graph:
        polygon_after_cohen = []
        for i in range(len(polygon)-1):
            if cohenSutherlandClip(polygon[i][0], polygon[i][1], polygon[i+1][0], polygon[i+1][1]) == None:
                continue
            else:
                x1, y1, x2, y2 = cohenSutherlandClip(polygon[i][0], polygon[i][1], polygon[i+1][0], polygon[i+1][1])
                polygon_after_cohen.append([x1, y1])
                polygon_after_cohen.append([x2, y2])
        graph_after_cohen.append(polygon_after_cohen)    
    return graph_after_cohen

def graph_after_viewports(graph):
    graph_after_viewports = []
    for polygon in graph:
        polygon_after_viewports = []
        for i in polygon:
            x = lowerVPx+(i[0]-lowerBoundx)*(upperVPx-lowerVPx)/(upperBoundx-lowerBoundx)
            y = lowerVPy+(i[1]-lowerBoundy)*(upperVPy-lowerVPy)/(upperBoundy-lowerBoundy)
            polygon_after_viewports.append([x, y])
        graph_after_viewports.append(polygon_after_viewports)
    return graph_after_viewports
    
if __name__=='__main__':
    bezier = bezier(graph, numLine)
    graph_after_transformation = graph_after_transformation(bezier, scalingFactor, xTranslation, yTranslation, rotation)
    graph_after_cohen = graph_after_cohen(graph_after_transformation)
    graph_after_viewports = graph_after_viewports(graph_after_cohen)
    
    print("%!PS\n")
    print("0.1 setlinewidth")
    print("%%BeginSetup")
    print("  << /PageSize [" + str(500+1), str(500+1) + "] >> setpagedevice")
    print("%%EndSetup\n")
    print("%%%BEGIN")
    
    for polygon in graph_after_viewports:
        for i in range(0, len(polygon)-1, 2):
            print(polygon[i][0], polygon[i][1], "moveto")
            print(polygon[i+1][0], polygon[i+1][1], "lineto")
            print("stroke")
    print("%%%END")