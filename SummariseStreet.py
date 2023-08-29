import geopandas as gpd
from shapely.geometry import LineString
import math
import matplotlib.pyplot as plt
from config import shp_file_path, angle
import random


class CreateStreets:
    def __init__(self):
        self.lines = list()
        self.open_shp()
        self.deleting_list = []

    def open_shp(self):
        gdf = gpd.read_file(shp_file_path)
        self.lines = [LineString(line.coords) for line in gdf.geometry]

    @staticmethod
    def get_all_intersections(lines):
        intersecting_lines = {}
        for i, line1 in enumerate(lines):
            start_intersecting_lines = []
            end_intersecting_lines = []
            for j, line2 in enumerate(lines):
                if i != j:
                    if line1.coords[0] == line2.coords[0] or \
                       line1.coords[0] == line2.coords[-1]:
                        start_intersecting_lines.append(j)
                    if line1.coords[-1] == line2.coords[0] or \
                       line1.coords[-1] == line2.coords[-1]:
                        end_intersecting_lines.append(j)
                    intersecting_lines[i] = start_intersecting_lines, end_intersecting_lines
        return intersecting_lines

    def dot(self, vA, vB):
        return vA[0] * vB[0] + vA[1] * vB[1]

    def check_angle(self, lineA, lineB):
        # Get nicer vector form
        vA = [(lineA[0][0] - lineA[1][0]), (lineA[0][1] - lineA[1][1])]
        vB = [(lineB[0][0] - lineB[1][0]), (lineB[0][1] - lineB[1][1])]
        # Get dot prod
        dot_prod = self.dot(vA, vB)
        # Get magnitudes
        magA = self.dot(vA, vA) ** 0.5
        magB = self.dot(vB, vB) ** 0.5
        # Get cosine value
        cos_ = dot_prod / magA / magB
        # Get angle in radians and then convert to degrees
        angle = math.acos(dot_prod / magB / magA)
        # Basically doing angle <- angle mod 360
        ang_deg = math.degrees(angle) % 360

        if ang_deg - 180 >= 0:
            # As in if statement
            return 360 - ang_deg
        else:
            return ang_deg

    def find_the_smallest_angle(self, key, values):
        smallest_result = None
        last_id = None
        for i, value in enumerate(values):
            result = self.check_angle(self.lines[key].coords[:], self.lines[value].coords[:])
            if smallest_result:
                if result < smallest_result:
                    smallest_result = result
                    last_id = value
            else:
                smallest_result = result
                last_id = value
        if last_id and smallest_result < angle:
            return last_id
        else:
            return None

    def collect_all_unique_values(self, dct, key, visited_numbers):
        res = [key]
        if key in dct:
            values = dct.pop(key)
            for value in values:
                if value is not None and value not in visited_numbers:
                    visited_numbers.add(value)
                    res.extend(self.collect_all_unique_values(dct, value, visited_numbers))
        return res

    def remove_duplicates(self, lst):
        seen = set()
        res = []
        for num in lst:
            if num not in seen:
                seen.add(num)
                res.append(num)
        return res

    def calculate_vectors(self, vectors, res={}):
        if not vectors:
            return None
        else:
            for key_id, values_id in vectors.items():
                res[key_id] = [self.find_the_smallest_angle(key_id, values_id[0]), self.find_the_smallest_angle(key_id, values_id[1])]
            return res

    def union_all_geometry(self, lines):
        line_geoms = [self.lines[coords].coords[:] for coords in lines]
        return line_geoms

    def visual_view(self, lines_list):
        new_lines = []
        colors = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(len(lines_list))]

        for i, lines in enumerate(lines_list):
            for line_coords in lines:
                new_line = LineString(line_coords)
                new_lines.append((new_line, colors[i]))

        gdf = gpd.GeoDataFrame(geometry=[line for line, _ in new_lines], columns=['geometry'])
        gdf['color'] = [color for _, color in new_lines]

        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color=gdf['color'])
        # plt.savefig('output_image.png', dpi=300)
        plt.show()


if __name__ == '__main__':
    # Init class
    createStreet = CreateStreets()
    # Intersect all lines
    intersects_lines = createStreet.get_all_intersections(createStreet.lines)

    # get lists with the smallest angle to other lines
    check = dict()
    for i, n in enumerate(createStreet.lines):
        check[i] = n.coords[:]
    get_the_smallest_angle = createStreet.calculate_vectors(intersects_lines)

    # Recurse through list
    result_without_dublicates = []
    unique_number = set()
    while get_the_smallest_angle:
        key_smallest = next(iter(get_the_smallest_angle))
        result = createStreet.collect_all_unique_values(get_the_smallest_angle, key_smallest, unique_number)
        result_without_dublicates.append(createStreet.remove_duplicates([num for num in result if num is not None]))

    # Union geometry coords line
    data_frame_all_geometry = []
    print(result_without_dublicates)
    for line in result_without_dublicates:
        data_frame_all_geometry.append(createStreet.union_all_geometry(line))

    # Make view
    createStreet.visual_view(data_frame_all_geometry)
