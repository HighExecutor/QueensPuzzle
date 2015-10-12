__author__ = 'Mishanya'

import random
from deap import creator, base, tools, algorithms
from copy import deepcopy
import numpy
import time


#TODO change generation and mutation without 2 queens at one row

def draw_solution(n, sol, canvas, queen, queen_arr, line_arr):
    for q in queen_arr:
        canvas.delete(q)
    for line in line_arr:
        canvas.delete(line)
    queen_arr.clear()
    d = int(400 / n)
    for i in range(n):
        new_q = canvas.create_image(d/2+1 + d*i, d/2+1 + d*sol[i], image=queen)
        queen_arr.append(new_q)

    lines = []
    for i in range(len(sol)):
        for j in range(len(sol)):
            if i == j or (i, j) in lines or (j, i) in lines:
                continue
            if sol[i] == sol[j]:
                lines.append((i, j))
            if abs(sol[i] - sol[j]) == abs(i - j):
                lines.append((i, j))
    for line in lines:
        line_arr.append(canvas.create_line(d / 2 + 1 + d* line[0],
                           d / 2 + 1 + d* sol[line[0]],
                           d / 2 + 1 + d* line[1],
                           d / 2 + 1 + d* sol[line[1]],
                           fill='red', width=2))

def eval_fit(ind):
    res = 0
    used = []
    for i in range(len(ind)):
        for j in range(len(ind)):
            if i == j or (i, j) in used or (j, i) in used:
                continue
            if ind[i] == ind[j]:
                res += 1
                used.append((i, j))
            if abs(ind[i] - ind[j]) == abs(i - j):
                res += 1
                used.append((i, j))

    return res

def mutate(n, ind):
    #TODO try to change covered queens often
    if random.random() < 0.5:
        ind[random.randint(0, n-1)] = random.randint(0, n-1)
    else:
        idx1 = random.randint(0, n - 1)
        idx2 = random.randint(0, n - 1)
        ind[idx1], ind[idx2] = ind[idx2], ind[idx1]
    if random.random() < 0.5:
        repair(ind, n)
    pass

# if individual has several queens at one row -> replace on the not used rows
def repair(ind, n):
    indexes = dict()
    values = []
    for i, v in enumerate(ind):
        if v not in values:
            values.append(v)
            indexes[v] = list()
        indexes[v].append(i)
    not_used = [q for q in range(n) if q not in values]
    for v, ids in indexes.items():
        while len(ids) > 1:
            change_idx = ids[random.randint(0, len(ids) - 1)]
            change_val = not_used[random.randint(0, len(not_used) - 1)]
            ind[change_idx] = change_val
            not_used.remove(change_val)
            ids.remove(change_idx)

class GA_for_queens:

    def __init__(self, n, canvas, queen, values, b_start, ngen=10000, cxpb=0.5, mutpb=0.1, pop_size=30, delay=0.0):
        self.n = n
        self.ngen = ngen
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.pop_size = pop_size

        self.canvas = canvas
        self.queen = queen
        self.queen_arr = []
        self.line_arr = []
        self.e_best = values[0]
        self.e_worst = values[1]
        self.e_avg = values[2]
        self.delay = delay
        self.b_start = b_start

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()

        toolbox.register("pos_gen", random.randint, 0, n - 1)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.pos_gen, n)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("clone", deepcopy)

        toolbox.register("evaluate", eval_fit)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", mutate, n)
        toolbox.register("select", tools.selTournament, tournsize=3)

        pop = toolbox.population(pop_size)
        #repair
        for p in pop:
            repair(p, n)

        self.pop = pop
        self.toolbox = toolbox

        pass

    def __call__(self):

        pop = self.pop
        n = self.n
        cxpb = self.cxpb
        mutpb = self.mutpb
        ngen = self.ngen
        pop_size = self.pop_size
        toolbox = self.toolbox

        best = None

        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = (fit,)

        for g in range(ngen):
            if best is not None and best.fitness.values[0] == 0:
                break
            print("g = " + str(g) + " / " + str(ngen))
            # Select the next generation individuals
            if best is not None:
                pop.append(toolbox.clone(best))
            pop = toolbox.select(pop, pop_size)

            # Apply crossover on the offspring
            for parent1, parent2 in zip(pop[::2], pop[1::2]):
                if random.random() < cxpb:
                    child1 = toolbox.clone(parent1)
                    child2 = toolbox.clone(parent2)
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
                    pop.append(child1)
                    pop.append(child2)

            # Apply mutation on the offspring
            for mutant in pop:
                if random.random() < mutpb:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = list(map(toolbox.evaluate, invalid_ind))
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = (fit,)

            pop.sort(key=lambda x: x.fitness, reverse=True)

            if best is None or best.fitness < pop[0].fitness:
                best = toolbox.clone(pop[0])
                draw_solution(n, best, self.canvas, self.queen, self.queen_arr, self.line_arr)

            self.e_best.delete(0, 'end')
            self.e_worst.delete(0, 'end')
            self.e_avg.delete(0, 'end')
            self.e_best.insert(0, best.fitness.values[0])
            self.e_worst.insert(0, pop[-1].fitness.values[0])
            self.e_avg.insert(0, numpy.mean([ind.fitness.values[0] for ind in pop]))

            time.sleep(self.delay)
            print("Best fit = " + str(best.fitness.values[0]))
            pass

        self.b_start['state'] = 'normal'
        print("Finished")

    pass

pass