import cv2
import math
import sys
import skimage, skimage.morphology
from skimage import measure
from scipy.spatial import distance
import numpy as np
import threading

# mesh = Mesh2D("dataset/Airplane/61_silhouette.png")

class Mesh2D:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pixels = cv2.imread(filepath)
        self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_BGR2GRAY)
        _, self.pixels= cv2.threshold(self.pixels, 127, 255, 0)
        self.area = self.get_area()
        self.perimeter_pixels = self.get_perimeter()
        self.perimeter = len(self.perimeter_pixels)
        self.bounding_box = self.get_bounding_box()
        self.diameter = self.get_diameter()
        self.rectangularity = self.get_rectangularity()
        self.compactness = self.get_compactness()
        self.skeleton = self.get_skeleton()
        self.skeleton_length = self.get_other_skeleton_length()

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

    def threading_area(self):
        self.area = np.count_nonzero(skimage.util.invert(self.pixels))

    def threading_perimeter(self):
        self.perimeter_pixels = self.get_contour()

    def threading_bbox(self):
        self.bounding_box = self.get_bounding_box()

    def threading_diameter(self):
        self.diameter = self.get_diameter()

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
                     [0, -1],
                     [1, 1],
                     [-1, -1],
                     [1, -1],
                     [-1, 1]]
        for x, line in enumerate(self.pixels):
            for y, pixel in enumerate(line):
                if pixel == 0:
                    for dx, dy in neighbors:
                        if x+dx>0 and y+dy>0 and x+dx<len(self.pixels) and y+dy<len(self.pixels[0]):
                            if self.pixels[x+dx][y+dy] != 0:
                                perimeter_pixels.append([x, y])
                                break
        return perimeter_pixels

    def get_contour(self):
        contours, hierarchy = cv2.findContours(self.pixels, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        ret_list = []
        for pixel in contours[1]:
            ret_list.append([pixel[0][0], pixel[0][1]])
        return ret_list

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

    def get_other_skeleton_length(self):
        max_dist = 0
        # skeleton_pixels = []
        # for i, p1 in enumerate(self.skeleton):
        #     for j, p2 in enumerate(p1):
        #         if p2:
        #             skeleton_pixels.append([i, j])
        skeleton_pixels = np.transpose(np.nonzero(self.skeleton))
        for p1 in skeleton_pixels:
            for p2 in skeleton_pixels:
                dist = (p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1])
                if dist > max_dist: max_dist = dist

        return max_dist

def main():
    import database_classes as db
    from main import getpngfiles


    # files = getpngfiles('dataset')
    m2D = Mesh2D('dataset/Airplane/80_silhouette.png')
    img = np.zeros((1200, 1200), dtype=np.uint8)

    for p in np.transpose(np.nonzero(m2D.skeleton)):
        img[p[0]][p[1]] = 255
    for p in m2D.perimeter_pixels:
        img[p[0]][p[1]] = 255

    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # for file in files:
    #     m2D = Mesh2D(file)
    #     mesh = db.session.query(db.Mesh).filter(db.Mesh.filename==file[:file.index('_')]+".off").first()
    #     mesh.skeletonToPerimeterRatio2D = m2D.skeleton_length
    #
    # db.session.commit()




if __name__=="__main__":
    main()