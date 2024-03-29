#! /usr/bin/env python

from __future__ import division

import math

import os
import random
import time


def deg_to_rad(deg):
    return deg * 180 / math.pi


class Coord(object):
    def __init__(self, uid, coord):
        self._uid = uid
        self._x, self._y = coord

    def set_coords(self, coord):
        self._x, self._y = coord

    def get_coords(self):
        return (self._x, self._y)

    def move(self, time, velocity, direction):
        v = time * velocity
        self._x += v * math.cos(direction)
        self._y += v * math.sin(direction)


class Axis(object):
    def __init__(self):
        self._items = {}
        self._sorted_items = []

    def sort(self):
        items = []
        for k, v in self._items.iteritems():
            items.append(v)
        self._sorted_items = sorted(items, key=lambda k: k['v'])

    def insert(self, v, index):
        item = {'v': v, 'i': index}
        self._items[index] = item
        return item

    def inject(self, v, index):
        new_item = self.insert(v, index)
        pivot = self.quick_find(v)
        pivot_item = self.at(pivot)
        if v < pivot_item['v']:
            if pivot is 0:
                pivot = 1
            self._sorted_items[pivot - 1:pivot - 1] = new_item
        else:
            self._sorted_items[pivot:pivot] = new_item

    def quick_find(self, x, start = 0, end = 0):
        items = len(self._sorted_items)

        if end is 0:
            end = items

        if start is end or (end - start) < 3:
            return start

        pivot = start + ((end - start) // 2)
        item = self._sorted_items[pivot]['v']
        if item is x:
            return pivot
        if item > x:
            return self.quick_find(x, start, pivot)
        else:
            return self.quick_find(x, pivot, end)

    def query(self, start, end):
        start_index = self.quick_find(start)
        end_index = self.quick_find(end)
        return (start_index, end_index)

    def at(self, index):
        return self._sorted_items[index]['i']


# Reduce
class Grid(object):
    def __init__(self, coord, vector):
        self._x_axis = Axis()
        self._y_axis = Axis()
        self._cx, self._cy = coord
        self._width, self._height = vector

    def insert(self, coord, uid):
        x, y = coord.get_coords()
        self._x_axis.insert(x, coord._uid)
        self._y_axis.insert(y, coord._uid)

    def inject(self, coord, uid):
        x, y = coord.get_coords()
        self._x_axis.inject(x, coord._uid)
        self._y_axis.inject(y, coord._uid)

    def get_outliers(self):
        pass

    def query(self, coord, vector):
        width, height = vector
        width = width // 2
        height = height // 2

        cx, cy = coord
        xbs, xbe = self._x_axis.query(cx - width, cx + width)
        ybs, ybe = self._y_axis.query(cy - height, cy + height)

        x_items = []
        y_items = []
        for i in range(xbe - xbs):
            x_items.append(self._x_axis.at(xbs + i))
        for i in range(ybe - ybs):
            y_items.append(self._y_axis.at(ybs + i))

        x_set = set(x_items)
        return x_set.intersection(y_items)

    def sort(self):
        self._x_axis.sort()
        self._y_axis.sort()


# Map
class SpatialDB(object):
    ''' TOOD: change _coords to _items.
        Create a Grid object that is like Axis.
        Create a _grids property for the list of grids.
        create a map_rect() function that maps a query_rect() to a list of
        applicable grids--return combined results.
        create a map_point() function to get the grid responsible for a
        point for add() and inject().
        add() and inject() insert into the proper grid.
        clean() function to inspect the edges of a grid for items that
        belong elsewhere.
    '''
    def __init__(self):
        self._uid = 0
        self._coords = {}
        self._grid = Grid((0, 0), (0, 0))

    ''' TODO: pass in a generated coord, return uid.'''
    def _generate_coord(self, coord):
        self._uid += 1
        c = Coord(self._uid, coord)
        self._coords[self._uid] = c
        return c

    ''' TODO: see _generate_coord().'''
    def add_coord(self, coord=(0, 0)):
        c = self._generate_coord(coord)
        self._grid.insert(c, c._uid)
        return c

    '''TODO: see _generate_coord().'''
    def inject_coord(self, coord):
        c = self._genereate_coord(coord)
        self._grid.inject(c, c._uid)
        return c

    ''' TODO: change to get_item().'''
    def get_coord(self, uid):
        return self._coords[uid]

    def sort(self):
        self._grid.sort()

    ''' TODO: change to items. '''
    def query(self, coord, vector):
        shared_items = self._grid.query(coord, vector)
        bounded_coords = []
        for uid in shared_items:
            bounded_coords.append(self._coords[uid])
        return bounded_coords


def generate_random_grid(ps, dp, mult):
    npcs_to_players = 60
    points = ps * npcs_to_players * mult
    grid_size = ps * mult * dp

    random.seed(os.urandom(5))

    uids = []
    sdb = SpatialDB()
    for i in range(points):
        rx = random.randint(0, grid_size)
        ry = random.randint(0, grid_size)
        coord = sdb.add_coord((rx, ry))
        uids.append(coord._uid)

    sdb.sort()
    return (sdb, uids)

if __name__ == '__main__':
    mult = 1
    players = 1000
    gw = 5000 * mult
    gh = 5000 * mult

    start = time.time()
    sdb, uids = generate_random_grid(players, 250, mult)
    end = time.time()
    print 'elapsed time:', end - start

    start = time.time()
    for i in range(players):
        x, y = sdb.get_coord(uids[i]).get_coords()
        ret = sdb.query((x, y), (gw, gh))
    end = time.time()

    print ret
    print 'in', (x - gw // 2, y - gh // 2), (x + gw // 2, y + gh // 2)
    print 'total', len(ret)
    print 'elapsed time:', end - start
