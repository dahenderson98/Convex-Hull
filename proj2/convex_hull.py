from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()

		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		def getXValue(point):
			return point.x()

		points.sort(key = getXValue)

		t2 = time.time()

		t3 = time.time()

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

			finalHull = [leftHull[topTangentLeftIndex], rightHull[topTangentRightIndex]]

			if topTangentRightIndex % len(rightHull) != bottomTangentRightIndex % len(rightHull):
				i = (topTangentRightIndex + 1) % len(rightHull)
				while i % len(rightHull) != bottomTangentRightIndex % len(rightHull):
					finalHull.append(rightHull[i % len(rightHull)])
					i += 1

			# If right hulls is size 1, its bottom tangent right point was already added as the top right point
			if len(rightHull) > 1 and topTangentRightIndex % len(rightHull) != bottomTangentRightIndex % len(rightHull):
				finalHull.append(rightHull[bottomTangentRightIndex % len(rightHull)])
			if len(leftHull) > 1 and topTangentLeftIndex % len(leftHull) != bottomTangentLeftIndex % len(leftHull):
				finalHull.append(leftHull[bottomTangentLeftIndex % len(leftHull)])

			if topTangentLeftIndex % len(leftHull) != bottomTangentLeftIndex % len(leftHull):
				i = (bottomTangentLeftIndex + 1) % len(leftHull)
				while i % len(leftHull) != topTangentLeftIndex % len(leftHull) and i % len(
						leftHull) != bottomTangentLeftIndex % len(leftHull):
					finalHull.append(leftHull[i % len(leftHull)])
					i += 1

			return finalHull

		def getSlope(point1, point2):
			return (point2.y()-point1.y()) / (point2.x()-point1.x())

		hullPoints = solveConvexHull(points)
		polygon = [QLineF(hullPoints[i],hullPoints[(i+1)%len(hullPoints)]) for i in range(len(hullPoints))]

		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.12f} sec'.format(t4-t3))


