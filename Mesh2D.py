import cv2
import math
import sys
import skimage, skimage.morphology

# mesh = Mesh2D("dataset/Airplane/61_silhouette.png")

class Mesh2D:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pixels = cv2.imread(filepath)
        self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_BGR2GRAY)
        self.area_pixels, self.perimeter_pixels = self.get_area_perimeter()
        self.area, self.perimeter = len(self.area_pixels), len(self.perimeter_pixels)
        self.bounding_box = self.get_bounding_box()
        self.rectangularity = self.get_rectangularity()
        self.compactness = self.get_compactness()
        self.diameter = self.get_diameter()
        self.skeleton = self.get_skeleton()
        self.skeleton_length = self.get_skeleton_length()


    def get_area_perimeter(self):
        # TODO implement database update
        neighborhood = [
                        [-1, -1],
                        [-1, 0],
                        [-1, 1],
                        [0, -1],
                        [0, 0],
                        [0, 1],
                        [1, -1],
                        [1, 0],
                        [1, 1],
                        ]
        area, perimeter = [], []
        for x in range(len(self.pixels)):
            for y in range(len(self.pixels[0])):
                if self.pixels[x][y] == 0:
                    area.append([x, y])
                    for dx, dy in neighborhood:
                        if x+dx > 0 and y+dy > 0 and x+dx < len(self.pixels) and y+dy < len(self.pixels[0]):
                            if self.pixels[x+dx][y+dy] == 255:
                                perimeter.append([x, y])
                                break

        return (area, perimeter)

    def get_compactness(self):
        return pow(self.perimeter, 2)/(4*math.pi*self.area)

    def get_bounding_box(self):
        max_x, max_y = 0, 0
        min_x, min_y = sys.maxsize, sys.maxsize
        for x in range(len(self.pixels)):
            for y in range(len(self.pixels[0])):
                if self.pixels[x][y] == 0:
                    if x > max_x: max_x = x
                    if y > max_y: max_y = y
                    if x < min_x: min_x = x
                    if y < min_y: min_y = y

        return (min_x, max_x, min_y, max_y)

    def get_rectangularity(self):
        min_x, max_x, min_y, max_y, = self.bounding_box
        return self.area/(max_x-min_x)*(max_y-min_y)

    def get_diameter(self):
        max_dist = 0
        for p1 in self.perimeter_pixels:
            for p2 in self.perimeter_pixels:
                dist = pow(p1[0]-p2[0], 2)+pow(p1[1]-p2[1], 2)
                if max_dist < dist: max_dist = dist
        return max_dist

    def get_eccentricity(self):
        pass
        # TODO fill

    def get_skeleton(self):
        image = skimage.util.invert(self.pixels/255)
        return skimage.morphology.skeletonize(image)

    def get_skeleton_length(self):
        count = 0
        for line in self.skeleton:
            for pixel in line:
                if pixel == 1: count += 1
        return count


