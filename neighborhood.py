import random


def moore(cell):
    x, y = cell.position_in_matrix
    neighborhood = ((x - 1, y - 1),
                    (x, y - 1),
                    (x + 1, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x - 1, y + 1),
                    (x, y + 1),
                    (x + 1, y + 1))
    return neighborhood


def von_neumann(cell):
    x, y = cell.position_in_matrix
    neighborhood = ((x, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x, y + 1))
    return neighborhood


def pentagonal_random(cell):
    x, y = cell.position_in_matrix
    left_neighborhood = ((x, y - 1),
                         (x + 1, y - 1),
                         (x + 1, y),
                         (x, y + 1),
                         (x + 1, y + 1))
    right_neighborhood = ((x - 1, y - 1),
                          (x, y - 1),
                          (x - 1, y),
                          (x - 1, y + 1),
                          (x, y + 1))
    top_neighborhood = ((x - 1, y),
                        (x + 1, y),
                        (x - 1, y + 1),
                        (x, y + 1),
                        (x + 1, y + 1))
    bottom_neighborhood = ((x - 1, y - 1),
                           (x, y - 1),
                           (x + 1, y - 1),
                           (x - 1, y),
                           (x + 1, y))
    neighborhood_list = [left_neighborhood, right_neighborhood, top_neighborhood, bottom_neighborhood]
    random_neighborhood = random.choice(neighborhood_list)
    return random_neighborhood


def hexagonal_left(cell):
    x, y = cell.position_in_matrix
    neighborhood = ((x, y - 1),
                    (x + 1, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x - 1, y + 1),
                    (x, y + 1))
    return neighborhood


def hexagonal_right(cell):
    x, y = cell.position_in_matrix
    neighborhood = ((x - 1, y - 1),
                    (x, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x, y + 1),
                    (x + 1, y + 1))
    return neighborhood


def hexagonal_random(cell):
    x, y = cell.position_in_matrix
    left_neighborhood = ((x, y - 1),
                         (x + 1, y - 1),
                         (x - 1, y),
                         (x + 1, y),
                         (x - 1, y + 1),
                         (x, y + 1))
    right_neighborhood = ((x - 1, y - 1),
                    (x, y - 1),
                    (x - 1, y),
                    (x + 1, y),
                    (x, y + 1),
                    (x + 1, y + 1))
    neighborhood_list = [left_neighborhood, right_neighborhood]
    random_neighborhood = random.choice(neighborhood_list)
    return random_neighborhood


def with_radius(cell, radius):
    x, y = cell.position_in_matrix
    x_start = x - radius
    y_start = y - radius
    neighborhood = []
    for i in range(x_start, x_start + radius * 2 + 1):
        for j in range(y_start, y_start + radius * 2 + 1):
            if x_start == x and y_start == y:
                continue
            neighborhood.append((i, j))
    return neighborhood


def choose_neighborhood(current):
    values = ['Moore',
              'Von Neumann',
              'Pentagonal-random',
              'Hexagonal-left',
              'Hexagonal-right',
              'Hexagonal-random',
              'With a radius']
    value = values[current]
    func_map = {
        'Moore': moore,
        'Von Neumann': von_neumann,
        'Pentagonal-random': pentagonal_random,
        'Hexagonal-left': hexagonal_left,
        'Hexagonal-right': hexagonal_right,
        'Hexagonal-random': hexagonal_random,
        'With a radius': with_radius
    }
    return func_map.get(value)
