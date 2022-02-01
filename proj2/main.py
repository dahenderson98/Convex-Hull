
import math
import random
import signal
import sys
import time

from PyQt6.QtCore import *


if __name__ == '__main__':
    def solveConvexHull(points):
        size = len(points)

        # Base Case: Return leaf list when size is 1
        if size == 1:
            return points

        # Split left and right points by increasing x value, and recursively solve hulls for them
        halfSize = size // 2
        leftPoints = points[:halfSize]
        rightPoints = points[halfSize:]
        leftHull = solveConvexHull(leftPoints)
        rightHull = solveConvexHull(rightPoints)

        # If both children are of size 1, concatenate them and return the origin-slope-sorted product
        if len(leftHull) == 1 and len(rightHull) == 1:
            rightHull.extend(leftHull)
            return rightHull

        # Else, merge the final two hulls into a final hull and return it
        finalHull = mergeHulls(leftHull, rightHull)

        return finalHull

    def mergeHulls(leftHull, rightHull):
        leftHullStartPoint = max(leftHull, key=getXValue)
        rightHullStartPoint = min(rightHull, key=getXValue)
        leftHullStartIndex = leftHull.index(leftHullStartPoint) % len(leftHull)
        rightHullStartIndex = rightHull.index(rightHullStartPoint) % len(rightHull)
        originalLeftStartIndex = leftHullStartIndex
        originalRightStartIndex = rightHullStartIndex

        # Fixed-point iteration to find top tangent
        i_left = leftHull[leftHullStartIndex % len(leftHull)]
        i_right = rightHull[rightHullStartIndex % len(rightHull)]
        topTangentLeftIndex = leftHullStartIndex % len(leftHull)
        topTangentRightIndex = rightHullStartIndex % len(rightHull)
        delta = 1
        while delta > 0:
            delta = 0

            # Shift the right point up until slope stops increasing
            leftHullStartIndex = topTangentLeftIndex
            rightHullStartIndex = topTangentRightIndex
            i_left = leftHull[topTangentLeftIndex]
            i_right = rightHull[topTangentRightIndex]
            shift = 1
            slope1 = getSlope(i_left, i_right)
            proceed = True
            while proceed:
                proceed = False

                i_right = rightHull[(rightHullStartIndex + shift) % len(rightHull)]
                slope2 = getSlope(i_left, i_right)
                if slope2 <= slope1:
                    break
                else:
                    topTangentRightIndex = (rightHullStartIndex + shift) % len(rightHull)
                    slope1 = slope2
                    slope2 = 0.0
                    shift += 1
                    delta += 1
                    proceed = True

            # Shift the left point up until slope stops decreasing
            leftHullStartIndex = topTangentLeftIndex
            rightHullStartIndex = topTangentRightIndex
            i_left = leftHull[topTangentLeftIndex]
            i_right = rightHull[topTangentRightIndex]
            shift = 1
            slope1 = getSlope(i_left, i_right)
            proceed = True
            while proceed:
                proceed = False

                i_left = leftHull[(leftHullStartIndex - shift) % len(leftHull)]
                slope2 = getSlope(i_left, i_right)
                if slope2 >= slope1:
                    break
                else:
                    topTangentLeftIndex = (leftHullStartIndex - shift) % len(leftHull)
                    slope1 = slope2
                    slope2 = 0.0
                    shift += 1
                    delta += 1
                    proceed = True


        # Fixed-point iteration to find bottom tangent
        leftHullStartIndex = originalLeftStartIndex
        rightHullStartIndex = originalRightStartIndex
        i_left = leftHull[leftHullStartIndex % len(leftHull)]
        i_right = rightHull[rightHullStartIndex % len(rightHull)]
        bottomTangentRightIndex = rightHullStartIndex % len(rightHull)
        bottomTangentLeftIndex = leftHullStartIndex % len(leftHull)
        delta = 1
        while delta > 0:
            delta = 0

            leftHullStartIndex = bottomTangentLeftIndex
            rightHullStartIndex = bottomTangentRightIndex
            i_left = leftHull[bottomTangentLeftIndex]
            i_right = rightHull[bottomTangentRightIndex]
            # Shift the right point down until slope stops decreasing
            shift = 1
            slope1 = getSlope(i_left, i_right)
            proceed = True
            while proceed:
                proceed = False
                i_right = rightHull[(rightHullStartIndex - shift) % len(rightHull)]
                slope2 = getSlope(i_left, i_right)
                if slope2 >= slope1:
                    break
                else:
                    bottomTangentRightIndex = (rightHullStartIndex - shift) % len(rightHull)
                    slope1 = slope2
                    slope2 = 0.0
                    shift += 1
                    delta += 1
                    proceed = True

            # Shift the left point down until slope stops increasing
            leftHullStartIndex = bottomTangentLeftIndex
            rightHullStartIndex = bottomTangentRightIndex
            i_left = leftHull[bottomTangentLeftIndex]
            i_right = rightHull[bottomTangentRightIndex]
            slope1 = getSlope(i_left, i_right)
            shift = 1
            proceed = True
            while proceed:
                proceed = False
                i_left = leftHull[(leftHullStartIndex + shift) % len(leftHull)]
                slope2 = getSlope(i_left, i_right)
                if slope2 <= slope1:
                    break
                else:
                    bottomTangentLeftIndex = (leftHullStartIndex + shift) % len(leftHull)
                    slope1 = slope2
                    slope2 = 0.0
                    shift += 1
                    delta += 1
                    proceed = True

        # edge between right iterator and left iterator are bottom tangent

        finalHull = [leftHull[topTangentLeftIndex],rightHull[topTangentRightIndex]]

        if topTangentRightIndex%len(rightHull) != bottomTangentRightIndex%len(rightHull):
            i = (topTangentRightIndex + 1) % len(rightHull)
            while i % len(rightHull) != bottomTangentRightIndex%len(rightHull):
                finalHull.append(rightHull[i % len(rightHull)])
                i += 1

        # If right hulls is size 1, its bottom tangent right point was already added as the top right point
        if len(rightHull) > 1 and topTangentRightIndex%len(rightHull) != bottomTangentRightIndex%len(rightHull):
            finalHull.append(rightHull[bottomTangentRightIndex%len(rightHull)])
        if len(leftHull) > 1 and topTangentLeftIndex%len(leftHull) != bottomTangentLeftIndex%len(leftHull):
            finalHull.append(leftHull[bottomTangentLeftIndex%len(leftHull)])

        if topTangentLeftIndex%len(leftHull) != bottomTangentLeftIndex%len(leftHull):
            i = (bottomTangentLeftIndex + 1) % len(leftHull)
            while i % len(leftHull) != topTangentLeftIndex%len(leftHull) and i%len(leftHull) != bottomTangentLeftIndex%len(leftHull):
                finalHull.append(leftHull[i % len(leftHull)])
                i += 1

        return finalHull

    def getSlope(point1, point2):
        return (point2.y() - point1.y()) / (point2.x() - point1.x())


    def getXValue(point):
        return point.x()

    points = []
    points.append(QPointF(1.0, 5.0))
    points.append(QPointF(2.0, 4.0))
    points.append(QPointF(4.0, 1.0))
    points.append(QPointF(5.0, 7.0))
    points.append(QPointF(6.0, 2.0))

    points.sort(key = getXValue)
    print("Sorted: ",points)
    hullPoints = solveConvexHull(points)
    print("Hull: ",hullPoints)

