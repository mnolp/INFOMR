import cv2
import math
import sys
import skimage, skimage.morphology
from skimage import measure
import numpy as np
import threading

# mesh = Mesh2D("dataset/Airplane/61_silhouette.png")

class Mesh2D:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pixels = cv2.imread(filepath)
        self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_BGR2GRAY)
        _, self.pixels= cv2.threshold(self.pixels, 127, 255, 0)
        self.flip_test()
        thread_area = threading.Thread(target=threading_area)
        thread_area.start()
        self.area = self.get_area()
        thread_perimeter = threading.Thread(target=threading_perimeter)
        thread_perimeter.start()
        self.perimeter_pixels = self.get_perimeter()
        self.perimeter = len(self.perimeter_pixels)
        thread_perimeter.join()
        thread_bbox = threading.Thread(target=threading_bbox)
        thread_bbox.start()
        self.bounding_box = self.get_bounding_box()
        self.rectangularity = self.get_rectangularity()
        self.compactness = self.get_compactness()
        thread_diameter = threading.Thread(target=threading_diameter)
        thread_area.start()
        self.diameter = self.get_diameter()
        self.skeleton = self.get_skeleton()
        self.skeleton_length = self.get_skeleton_length()
        thread_area.join()
        thread_bbox.join()
        thread_diameter.join()

    # def __init__(self, filepath):
    #     self.filepath = filepath
    #     self.pixels = cv2.imread(filepath)
    #     self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_BGR2GRAY)
    #     self.area = self.get_area()
    #     self.perimeter_pixels = self.get_perimeter()
    #     self.compactness = self.get_compactness()
    #     self.rectangularity = self.get_rectangularity()
    #     self.diameter = self.get_diameter()
    #     self.skeleton = self.get_skeleton()
    #     self.skeleton_length = self.get_skeleton_length()

    def flip_test(self):
        x_count, y_count = 0, 0

        for i, line in enumerate(self.pixels):
            for j, pixel in enumerate(line):
                if pixel == 0:
                    x_count += 1 if i < 600 else -1
                    y_count += 1 if j < 600 else -1

        if x_count < 0: self.pixels = np.flip(self.pixels, 0)
        if y_count < 0: self.pixels = np.flip(self.pixels, 1)

    def get_area(self):
        return np.count_nonzero(skimage.util.invert(self.pixels))

    def get_perimeter(self):
        perimeter_pixels = []
        neighbors = [[1, 0],
                     [0, 1],
                     [-1, 0],
                     [0, -1]]
        for x, line in enumerate(self.pixels):
            for y, pixel in enumerate(line):
                if pixel == 0:
                    for dx, dy in neighbors:
                        if x+dx>0 and y+dy>0 and x+dx<len(self.pixels) and y+dy<len(self.pixels[0]):
                            if self.pixels[x+dx][y+dy] != 0:
                                perimeter_pixels.append([x, y])
                                break
        return perimeter_pixels


    # def get_area(self):
    #     # img = cv2.imread(self.filepath)
    #     # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     # ret, thresh = cv2.threshold(img, 127, 255, 0)
    #
    #     ret_sum = 0
    #     for line in self.pixels:
    #         ret_sum += sum(1 for x in line if x==255)
    #     return ret_sum

    def get_compactness(self):
        return self.perimeter*self.perimeter/(4*math.pi*self.area)

    def get_bounding_box(self):
        max_x, max_y = 0, 0
        min_x, min_y = sys.maxsize, sys.maxsize
        for i in range(len(self.perimeter_pixels)):
            if self.perimeter_pixels[i][0] > max_x: max_x = self.perimeter_pixels[i][0]
            if self.perimeter_pixels[i][0] < min_x: min_x = self.perimeter_pixels[i][0]
            if self.perimeter_pixels[i][1] > max_y: max_y = self.perimeter_pixels[i][1]
            if self.perimeter_pixels[i][1] < min_y: min_y = self.perimeter_pixels[i][1]

        return (max_x-min_x, max_y-min_y)

    def get_rectangularity(self):
        dim_x, dim_y = self.bounding_box
        return self.area/(dim_x*dim_y)

    def get_diameter(self):
        max_dist = 0
        for p1 in self.perimeter_pixels:
            for p2 in self.perimeter_pixels:
                dist = ((p1[0]-p2[0])*(p1[0]-p2[0]))+((p1[1]-p2[1])*(p1[1]-p2[1]))
                if max_dist < dist: max_dist = dist
        return pow(max_dist, 1/2)

    def get_eccentricity(self):
        pass
        # TODO fill

    def get_skeleton(self):
        image = skimage.util.invert(self.pixels/255)
        return skimage.morphology.skeletonize(image)

    def get_skeleton_length(self):
        return np.count_nonzero(self.skeleton)


