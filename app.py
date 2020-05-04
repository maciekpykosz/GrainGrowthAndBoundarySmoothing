import itertools
import random
import copy
import numpy as np
import neighborhood as nh

from collections import Counter
from math import exp
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

x_size = 0
y_size = 0
grid = None
mc_grid = None
rectangle_size = 5
begin_id = None
colors = {}
seed_id = 0


class Cell:
    def __init__(self, i, j):
        x = j * 5 + 2
        y = i * 5 + 2
        self.id = 0
        self.color = 'white'
        self.next_state = 0
        self.energy = 0
        self.position_in_canvas = (x, y)
        self.position_in_matrix = (i, j)

    def switch_state(self):
        self.id = self.next_state

    def clean_cell(self):
        self.id = 0
        self.next_state = 0
        self.color = 'white'
        self.draw_cell(gui.canvas)

    def draw_cell(self, canvas):
        x, y = self.position_in_canvas
        color = self.color
        canvas.create_rectangle(x, y, x + rectangle_size, y + rectangle_size, fill=color)

    def draw_cell_energy(self, canvas, color):
        x, y = self.position_in_canvas
        canvas.create_rectangle(x, y, x + rectangle_size, y + rectangle_size, fill=color)


class GUI(Tk):
    def __init__(self):
        Tk.__init__(self, className=' Cellular Automata 2D Grain Growth + Monte Carlo Grain Boundary Smoothing')
        self.minsize(800, 626)

        self.ca_frame = Frame(self)
        self.ca_frame.pack()
        self.mc_frame = Frame(self)
        self.mc_frame.pack()
        self.canvas_frame = Frame(self)
        self.canvas_frame.pack()

        # CA frame
        self.ca_lab = Label(self.ca_frame, text='CA:  ')
        self.ca_lab.pack(side=LEFT)

        self.start_butt = Button(self.ca_frame, text='Start', fg='white', bg='#263D42', width=10, command=self.start)
        self.start_butt.pack(side=LEFT)

        self.stop_butt = Button(self.ca_frame, text='Stop', fg='white', bg='#263D42', width=10, command=self.stop)
        self.stop_butt.pack(side=LEFT)

        self.size_lab = Label(self.ca_frame, text='Size (x,y): (')
        self.size_lab.pack(side=LEFT)
        self.default_x_size = IntVar(value=250)
        self.x_size_ent = Entry(self.ca_frame, width=4, textvariable=self.default_x_size)
        self.x_size_ent.pack(side=LEFT)
        self.colon_lab = Label(self.ca_frame, text=',')
        self.colon_lab.pack(side=LEFT)
        self.default_y_size = IntVar(value=150)
        self.y_size_ent = Entry(self.ca_frame, width=4, textvariable=self.default_y_size)
        self.y_size_ent.pack(side=LEFT)
        self.bracket_lab = Label(self.ca_frame, text=') ')
        self.bracket_lab.pack(side=LEFT)
        self.size_butt = Button(self.ca_frame, text='Change size/Clear', fg='white', bg='#263D42', width=16,
                                command=self.build_grid)
        self.size_butt.pack(side=LEFT)

        self.condition_lab = Label(self.ca_frame, text='Condition: ')
        self.condition_lab.pack(side=LEFT)
        self.default_condition = StringVar(value='Periodic')
        self.condition_combo = ttk.Combobox(self.ca_frame, width=10, values=['Periodic', 'Absorbing'],
                                            textvariable=self.default_condition)
        self.condition_combo.pack(side=LEFT)

        self.nucleation_lab = Label(self.ca_frame, text='Nucleation: ')
        self.nucleation_lab.pack(side=LEFT)
        self.default_nucleation = StringVar(value='Random')
        self.nucleation_combo = ttk.Combobox(self.ca_frame, width=15, textvariable=self.default_nucleation,
                                             value=['Homogeneous', 'With a radius', 'Random'])
        self.nucleation_combo.pack(side=LEFT)
        self.nucleation_combo.bind('<<ComboboxSelected>>', self.nucleation_handler)

        self.number_rand_lab = Label(self.ca_frame, text='Number of random: ')
        self.number_rand_lab.pack(side=LEFT)
        self.default_num_rand = IntVar(value=100)
        self.number_rand_ent = Entry(self.ca_frame, width=5, textvariable=self.default_num_rand)
        self.number_rand_ent.pack(side=LEFT)

        self.neighborhood_lab = Label(self.ca_frame, text='Neighborhood: ')
        self.neighborhood_lab.pack(side=LEFT)
        self.default_neighborhood = StringVar(value='Moore')
        self.neighborhood_combo = ttk.Combobox(self.ca_frame, width=15, textvariable=self.default_neighborhood,
                                               value=['Moore', 'Von Neumann', 'Pentagonal-random', 'Hexagonal-left',
                                                      'Hexagonal-right', 'Hexagonal-random', 'With a radius'])
        self.neighborhood_combo.pack(side=LEFT)
        self.neighborhood_combo.bind('<<ComboboxSelected>>', self.neighborhood_handler)

        self.radius_lab = Label(self.ca_frame, text='Radius: ')
        self.radius_lab.pack(side=LEFT)
        self.default_radius = IntVar(value=10)
        self.radius_ent = Entry(self.ca_frame, width=4, textvariable=self.default_radius)
        self.radius_ent.pack(side=LEFT, padx=(0, 40))

        # MC frame
        self.mc_lab = Label(self.mc_frame, text='MC:  ')
        self.mc_lab.pack(side=LEFT)

        self.smooth_butt = Button(self.mc_frame, text='Smooth boundaries', fg='white', bg='#263D42', width=20,
                                  state=DISABLED,
                                  command=self.smooth_boundaries)
        self.smooth_butt.pack(side=LEFT)

        self.iter_lab = Label(self.mc_frame, text='Iterations: ')
        self.iter_lab.pack(side=LEFT)
        self.default_iter = IntVar(value=10)
        self.iter_ent = Entry(self.mc_frame, width=4, textvariable=self.default_iter)
        self.iter_ent.pack(side=LEFT)

        self.kt_lab = Label(self.mc_frame, text='kt: ')
        self.kt_lab.pack(side=LEFT)
        self.default_kt = IntVar(value=1)
        self.kt_spin = Spinbox(self.mc_frame, width=4, from_=0.1, to=6.0, increment=0.1, textvariable=self.default_kt)
        self.kt_spin.pack(side=LEFT)

        self.energy_view_butt = Button(self.mc_frame, text='Show energy view', fg='white', bg='#263D42', width=25,
                                       state=DISABLED,
                                       command=self.show_energy_view)
        self.energy_view_butt.pack(side=RIGHT, padx=(0, 730))

        # Canvas frame
        self.canvas = Canvas(self.canvas_frame, width=1251, height=751)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', switch_cell_state_on_click)

    def build_grid(self):
        global x_size
        global y_size
        global grid
        x_size = int(self.x_size_ent.get())
        y_size = int(self.y_size_ent.get())
        grid = np.array([[Cell(i, j) for j in range(x_size)] for i in range(y_size)], dtype=object)
        draw_grid(self.canvas)

    def start(self):
        neighborhood = self.neighborhood_handler(event=None)
        condition = self.condition_combo.get()
        empty_cells_counter = change_states_in_grid(neighborhood, condition)
        if empty_cells_counter != 0:
            draw_cells_change_state(self.canvas)
            global begin_id
            begin_id = self.canvas.after(100, self.start)
        else:
            self.stop()
            messagebox.showinfo('Good info!', 'Completed successfully!')
            self.smooth_butt.config(state=NORMAL)

    def stop(self):
        self.canvas.after_cancel(begin_id)

    def nucleation_handler(self, event):
        values = ['Homogeneous', 'With a radius', 'Random']
        current = self.nucleation_combo.current()
        value = values[current]
        func_map = {
            'Homogeneous': homogeneous,
            'With a radius': with_radius,
            'Random': rand
        }
        func = func_map.get(value)
        func()

    def neighborhood_handler(self, event):
        current = self.neighborhood_combo.current()
        neighborhood = nh.choose_neighborhood(current)
        return neighborhood

    def smooth_boundaries(self):
        global grid
        global mc_grid
        mc_canvas = self.create_new_window()
        draw_grid(mc_canvas)
        draw_cells(grid, mc_canvas)
        mc_canvas.update()
        current = self.neighborhood_combo.current()
        neighborhood = nh.choose_neighborhood(current)
        condition = self.condition_combo.get()
        mc_grid = copy.deepcopy(grid)
        iterations = int(self.iter_ent.get())
        try:
            for i in range(iterations):
                calculate_energy_in_grid(neighborhood, condition)
                draw_cells(mc_grid, mc_canvas)
                mc_canvas.update()
            messagebox.showinfo('Good info!', 'Completed successfully!')
            self.energy_view_butt.config(state=NORMAL)
        except ZeroDivisionError:
            messagebox.showerror('Error!', 'You can not divide by zero!')

    def create_new_window(self):
        mc_root = Toplevel(self)
        mc_canvas = Canvas(mc_root, width=1251, height=751)
        mc_canvas.pack()
        return mc_canvas

    def show_energy_view(self):
        energy_canvas = self.create_new_window()
        draw_grid(energy_canvas)
        energy_level = {
            0: '#1e00ff',
            1: '#00aeff',
            2: '#ccff00',
            3: '#fff700',
            4: '#ff6f00',
            5: '#ff0000',
            6: '#a30000',
            7: '#470000',
            8: '#000000'
        }
        for i in range(y_size):
            for j in range(x_size):
                cell_energy = mc_grid[i][j].energy
                if cell_energy in energy_level.keys():
                    color = energy_level[cell_energy]
                    mc_grid[i][j].draw_cell_energy(energy_canvas, color)


def switch_cell_state_on_click(event):
    global seed_id
    x = (event.x + 2) - (event.x + 2) % 5
    y = (event.y + 2) - (event.y + 2) % 5
    try:
        one_element_structure = []
        j = int(x / 5 - 1)
        i = int(y / 5 - 1)
        if i == -1 or j == -1:
            raise IndexError
        if grid[i][j].id == 0:
            one_element_structure.append((j, i))
            seed_id += 1
            grid[i][j].id = seed_id
            draw_structure(one_element_structure)
        else:
            grid[i][j].clean_cell()
    except IndexError:
        return


def draw_grid(canv):
    canv.delete('all')
    global x_size
    global y_size
    for i in range(y_size):
        for j in range(x_size):
            grid[i][j].draw_cell(canv)


def draw_cells_change_state(canv):
    for i in range(y_size):
        for j in range(x_size):
            if grid[i][j].next_state != grid[i][j].id:
                grid[i][j].draw_cell(canv)
                grid[i][j].switch_state()


def change_states_in_grid(neighborhood_func, condition):
    empty_cells_counter = 0
    radius = int(gui.radius_ent.get())
    for i in range(y_size):
        for j in range(x_size):
            if grid[i][j].id == 0:
                if neighborhood_func != nh.with_radius:
                    neighborhood_struct = neighborhood_func(grid[i][j])
                else:
                    neighborhood_struct = neighborhood_func(grid[i][j], radius)
                calculate_state(grid[i][j], neighborhood_struct, condition)
                empty_cells_counter += 1
    return empty_cells_counter


def periodic_condition(cell_co):
    y, x = cell_co
    if x < 0:
        x = x_size + x
    elif x >= x_size:
        x = x - x_size
    if y < 0:
        y = y_size + y
    elif y >= y_size:
        y = y - y_size
    return y, x


def calculate_energy(neighborhood_struct, cell, condition):
    energy = 0
    if condition == 'Absorbing':
        for cell_co in neighborhood_struct:
            y, x = cell_co
            if x < 0 or y < 0 or x >= x_size or y >= y_size:
                continue
            if mc_grid[y][x].id != cell.id:
                energy += 1
    elif condition == 'Periodic':
        for cell_co in neighborhood_struct:
            try:
                y, x = cell_co
                if mc_grid[y][x].id != cell.id:
                    energy += 1
            except IndexError:
                y, x = periodic_condition(cell_co)
                if mc_grid[y][x].id != cell.id:
                    energy += 1
    return energy


def random_new_cell(neighborhood_struct, cell, condition):
    x, y = random.choice(neighborhood_struct)
    if condition == 'Absorbing':
        try:
            new_cell = mc_grid[x][y]
        except IndexError:
            new_cell = cell
        return new_cell
    elif condition == 'Periodic':
        try:
            new_cell = mc_grid[y][x]
        except IndexError:
            y, x = periodic_condition(random.choice(neighborhood_struct))
            new_cell = mc_grid[y][x]
        return new_cell


def change_energy(rand_cell, new_cell, energy_after):
    rand_cell.energy = energy_after
    rand_cell.id = new_cell.id
    rand_cell.color = new_cell.color


def calculate_energy_in_grid(neighborhood_func, condition):
    draw_set = list(mc_grid.ravel())
    kt = float(gui.kt_spin.get())
    radius = int(gui.radius_ent.get())
    for rand_cell in range(len(draw_set)):
        rand_cell = np.random.choice(draw_set)
        draw_set.remove(rand_cell)
        if neighborhood_func != nh.with_radius:
            neighborhood_struct = neighborhood_func(rand_cell)
        else:
            neighborhood_struct = neighborhood_func(rand_cell, radius)
        energy_before = calculate_energy(neighborhood_struct, rand_cell, condition)
        rand_cell.energy = energy_before
        new_cell = random_new_cell(neighborhood_struct, rand_cell, condition)
        energy_after = calculate_energy(neighborhood_struct, new_cell, condition)
        energy_modification = energy_after - energy_before
        if energy_modification <= 0:
            change_energy(rand_cell, new_cell, energy_after)
        else:
            probability = exp(energy_modification / kt)
            rand_prob = random.random()
            if probability < rand_prob:
                change_energy(rand_cell, new_cell, energy_after)


def draw_cells(any_grid, canv):
    for i in range(y_size):
        for j in range(x_size):
            any_grid[i][j].draw_cell(canv)


def clean_cells(x_size, y_size):
    for i in range(y_size):
        for j in range(x_size):
            grid[i][j].clean_cell()


def prepare_to_do_nucleation():
    global x_size
    global y_size
    global seed_id
    structure = []
    clean_cells(x_size, y_size)
    return x_size, y_size, seed_id, structure


def draw_structure(structure):
    s = 0
    while s < len(structure):
        x_pos, y_pos = structure[s]
        color = f'#{random.randrange(0x1000000):06x}'
        if color not in colors.values():
            colors[grid[y_pos][x_pos].id] = color
            grid[y_pos][x_pos].color = color
            grid[y_pos][x_pos].draw_cell(gui.canvas)
            s += 1
        else:
            s -= 1


def homogeneous():
    x_size, y_size, seed_id, structure = prepare_to_do_nucleation()
    for x in itertools.islice(range(x_size), 1, x_size - 1, 10):
        for y in itertools.islice(range(y_size), 1, y_size - 1, 10):
            structure.append((x, y))
            seed_id += 1
            grid[y][x].id = seed_id
    draw_structure(structure)


def is_clear_within_radius(radius, x, y):
    x_start = x - radius
    y_start = y - radius
    for i in range(x_start, x_start + radius * 2 + 1):
        for j in range(y_start, y_start + radius * 2 + 1):
            if x_start == x and y_start == y:
                continue
            try:
                if grid[j][i].id != 0:
                    return False
            except IndexError:
                pass
    return True


def with_radius():
    x_size, y_size, seed_id, structure = prepare_to_do_nucleation()
    s = 0
    radius = int(gui.radius_ent.get())
    number_of_random_cells = int(gui.number_rand_ent.get())
    while s < number_of_random_cells:
        x = random.randint(0, x_size - 1)
        y = random.randint(0, y_size - 1)
        s += 1
        if grid[y][x].id == 0 and is_clear_within_radius(radius, x, y):
            structure.append((x, y))
            seed_id += 1
            grid[y][x].id = seed_id
    draw_structure(structure)


def rand():
    x_size, y_size, seed_id, structure = prepare_to_do_nucleation()
    s = 0
    number_of_random_cells = int(gui.number_rand_ent.get())
    if number_of_random_cells > x_size * y_size:
        messagebox.showerror('Error', 'Number of random cells is greater than cell number!')
        return
    while s < number_of_random_cells:
        x = random.randint(0, x_size - 1)
        y = random.randint(0, y_size - 1)
        s += 1
        if grid[y][x].id == 0:
            structure.append((x, y))
            seed_id += 1
            grid[y][x].id = seed_id
        else:
            s -= 1
    draw_structure(structure)


def most_frequent(id_list):
    occurrence_count = Counter(id_list)
    return occurrence_count.most_common(1)[0][0]


def calculate_state(cell, neighborhood_struct, condition):
    id_list = []
    if condition == 'Absorbing':
        for cell_co in neighborhood_struct:
            y, x = cell_co
            if x < 0 or y < 0 or x >= x_size or y >= y_size:
                continue
            if grid[y][x].id != 0:
                id_list.append(grid[y][x].id)
    elif condition == 'Periodic':
        for cell_co in neighborhood_struct:
            try:
                y, x = cell_co
                if grid[y][x].id != 0:
                    id_list.append(grid[y][x].id)
            except IndexError:
                y, x = periodic_condition(cell_co)
                if grid[y][x].id != 0:
                    id_list.append(grid[y][x].id)
    if len(id_list) != 0:
        most = most_frequent(id_list)
        cell.next_state = most
        cell.color = colors[most]


gui = GUI()
gui.build_grid()
gui.mainloop()
