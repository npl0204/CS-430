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

fileName = args.f if args.f else 'hw1.ps'
lowerBoundx = args.a if args.a else 0
lowerBoundy = args.b if args.b else 0
upperBoundx = args.c if args.c else 499
upperBoundy = args.d if args.d else 499
scalingFactor = args.s if args.s else 1
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
        graph.append([int(line[0]), int(line[1]), int(line[2]), int(line[3])])
    except:
        continue  

def graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation):
    graph_after_transformation = []
    for i in graph:
        x0 = i[0]*scalingFactor
        y0 = i[1]*scalingFactor
        x1 = i[2]*scalingFactor
        y1 = i[3]*scalingFactor

        x0_ = x0*np.cos(np.radians(rotation))-y0*np.sin(np.radians(rotation))+xTranslation
        y0_ = x0*np.sin(np.radians(rotation))+y0*np.cos(np.radians(rotation))+yTranslation
        x1_ = x1*np.cos(np.radians(rotation))-y1*np.sin(np.radians(rotation))+xTranslation
        y1_ = x1*np.sin(np.radians(rotation))+y1*np.cos(np.radians(rotation))+yTranslation

        graph_after_transformation.append([x0_, y0_, x1_, y1_])
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
            return [int(x0), int(y0), int(x1), int(y1)]
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
                x0 = int(x) 
                y0 = int(y) 
            else: 
                x1 = int(x)
                y1 = int(y)

def graph_after_cohen(graph):
    graph_after_cohen = []
    for i in graph:
        graph_after_cohen.append(cohenSutherlandClip(i[0], i[1], i[2], i[3]))
    return graph_after_cohen
    
if __name__=='__main__':
    graph_after_transformation = graph_after_transformation(graph, scalingFactor, xTranslation, yTranslation, rotation)
    graph_after_cohen = graph_after_cohen(graph_after_transformation)
    
    print("%!PS\n")
    print("/m {moveto} bind def")
    print("/l {lineto} bind def")
    print("/cp {closepath} bind def")
    print("/s {stroke} bind def")
    print("/sg {setgray} bind def")
    print("0.1 setlinewidth")
    print("%%BeginSetup")
    print("  << /PageSize [" + str(upperBoundx-lowerBoundx+1), str(upperBoundy-lowerBoundy+1) + "] >> setpagedevice")
    print("%%EndSetup\n")
    print("%%%BEGIN")

    for i in graph_after_cohen:
        print(i[0]-lowerBoundx, i[1]-lowerBoundy, "m")
        print(i[2]-lowerBoundx, i[3]-lowerBoundy, "l") 
        print("s")

    print("0 sg")
    print("%%%END")