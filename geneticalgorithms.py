import random
from typing import List, Callable, Tuple
import numpy as np
from collections import namedtuple
from functools import partial, lru_cache
from shipsims import ship as shipsim
import neuralnetwork as nn
import realtimeviewer as rtv
import csv
import sys
import time
#layer_sizes=[4,3,2]
width, height = 1920, 1080
PHYSICS_STEP = 1.0/30.0
MAX_TIME = 15.
#layer_sizes=[8,10,10,2] means genome_length is 200!!!
Genome = Tuple[int]
#Specimen = List[Genome, int, float]
Population = List[Genome]


FitnessFunc = Callable[[Genome], int]
#fitnessFunc takes a genome and spits back it's fitness value
PopulateFunc = Callable[[], Population]
#populateFunc takes nothing and spits out new solutions
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
#SelectionFunc takes a population, and a fitness function to select
#2 solutions to be the parents
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
#CrossoverFunc Takes 2 genomes and returns 2 new genomes
MutationFunc = Callable[[Genome], Genome]
#MutationFunc takes one genome and returns a modified one

def generate_genome(layer_sizes):
    weight_shapes = [(a,b) for a,b in zip(layer_sizes[1:], layer_sizes[:-1])]
    weights = [np.random.standard_normal(s)/s[1]**.5 for s in weight_shapes]
    return np.concatenate([item for sublist in weights for item in sublist])
#generating a population, called until is desired size
def generate_population(size: int, layer_sizes) -> Population:
    return [generate_genome(layer_sizes) for _ in range(size)]
#fitness function, shorter time is better
@lru_cache(maxsize = 20)
def fitness(genome : Genome, sim_class, layer_sizes):
    k = 1
    (goals, time_in, time_out, closest_dist) = run_simulation(genome, sim_class, layer_sizes)

    #fitness = max(0.01,100*time_in/3 + goals*100 + max(.01,(2000-closest_dist)**2/400000) ) #(max(1,(2000-closest_dist)/2)  + 2000*goals)
    fitness = (max(0,(1 + 2 * time_in)/(1.0 + time_out)) + max(0, goals*10/(1.0 + time_out))
            + max(0, 1/(1+(closest_dist/1000))))
    #if it takes longer than 60 seconds it is culled
    if time_in + time_out<60.:
        return [fitness, time_in, time_out, goals, closest_dist]
    else:
        return 0.

def read_population(file = "savedgenome.txt", layer_sizes = [9,9,9]):
    pop = []
    with open(file, "r") as file1:
        for line in file1.readlines():
            # Each of these is a genome
            line = line[:-2]
            genome = [float(i) for i in line.split(',')]
            pop.append(genome)
    return pop

def selection_pair(population: Population, fitness_func: FitnessFunc, sim_class, layer_sizes) -> Population:
    return random.choices(
        population = population,
        weights = [fitness(tuple(genome), sim_class, tuple(layer_sizes))[0] for genome in population],
        k = 2
        )

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("genomes a and b must be of same length")

    length = len(a)
    if length<2:
        return a, b
        print("Genomes are less than length 2")

    p = random.randint(1, length -1)
    return np.append(a[0:p], b[p:]), np.append(b[0:p], a[p:])

def mutation(genome: Genome, num: int = 1, probability: float = 0.05) -> Genome:
    for _ in range(num):
        index = random.randrange(len(genome))
        genome[index] = genome[index] + np.random.standard_normal()
    return genome

def run_simulation(genome, sim_class, layer_sizes):
    # Create a ship object
    ship = sim_class(width/2, height/2, width, height, max_time = MAX_TIME)
    # Create a neural network controller object with genome
    net = nn.NeuralNetwork(layer_sizes)

    net.import_genome(genome, layer_sizes)
    # Simulate physics
    while(1):
        inputs = ship.get_inputs()
        outputs = net.predict(inputs)
        status = ship.status()
        if status[0] == 0:
            # simulation over
            break
        ship.set_controls(controls = outputs)
        ship.update(PHYSICS_STEP)
        if (ship.timer >= MAX_TIME):
            break
    # return results

    #print("\rGOALS: {} TIME: {} DIST: {}".format(ship.goal_counter,  round(ship.timer), round(ship.closest_to_goal)))
    #sys.stdout.flush()
    return (ship.goal_counter, ship.time_in, ship.time_out, ship.closest_to_goal)

def run_evolution(
        layer_sizes = [6,4,2],
        populate_func: PopulateFunc = partial(generate_population, size=10, layer_sizes=[6,4,2]),
        #fitness_func: FitnessFunc,
        pop_mode = "generate",
        pop_file = "savedgenomes/savedgenome.txt",
        fitness_limit: int = 1000,
        sim_class = shipsim.Ship,
        max_time = MAX_TIME,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        savefile = "savedgenomes/savedgenome.txt",
        generation_limit: int = 100) -> Tuple[Population, int]:
        #get the first generation by calling polulate func
        if pop_mode == "read":
            populate_func = partial(read_population, file = pop_file)
        population = populate_func(layer_sizes = layer_sizes)
        print(layer_sizes)
        MAX_TIME = max_time
        # MAIN LOOP
        start = time.time()
        for i in range(generation_limit):
            #first sort by descending fitness (best are first)
            population = sorted(
                population,
                key=lambda genome: fitness(tuple(genome), sim_class, tuple(layer_sizes))[0],
                reverse=True
            )
            #check if the best genome is above fitness limit
            fit_test = fitness(tuple(population[0]), sim_class, tuple(layer_sizes))
            best_fitness = fit_test[0]
            if best_fitness >= fitness_limit:
                break
            #keep the top 2 solutions for next generation
            next_generation = population[0:2]
            #generating next generation:
            for j in range(int(len(population)/2)-1):
                parents = selection_func(tuple(population), fitness, sim_class, tuple(layer_sizes))
                offspring_a, offspring_b = crossover_func(parents[0], parents[1])
                offspring_a = mutation_func(offspring_a)
                offspring_b = mutation_func(offspring_b)
                next_generation += [offspring_a, offspring_b]

            if i % 10 == 0:
                finish = time.time()
                dt = finish - start
                start = finish
                string = "GENERATION: {0} -- Highest Fitness: {1} | Time In: {2} | Goals: {3}".format(i, round(best_fitness, 2), round(fit_test[1], 2), fit_test[3])
                print(string, end='\n',flush = True)
            population = next_generation


        print("\nFinishing up...")


        population = sorted(
            population,
            key=lambda genome: fitness(tuple(genome), sim_class, tuple(layer_sizes))[0],
            reverse=True
        )

        f = open(savefile, 'w')
        for g in population:
            for i in g:
                f.write(str(i))
                f.write(",")
            f.write('\n')

        # Save best log

        print("Done.")
        return population, i

# population, generation = run_evolution(
#     populate_func=partial(generate_population, size=10, layer_sizes=layer_sizes),
#     fitness_limit = 50000,
#     generation_limit = 50
# )
# population, generation = run_evolution(
#     populate_func=partial(read_population),
#     fitness_limit = 50000,
#     generation_limit = 50
# )
# view = rtv.RealtimeViewer(population[0], layer_sizes)
# view.start()
#
# print(population[0]," \n", generation)

#print(f"number of generation: {generations}")
