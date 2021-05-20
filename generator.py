import geneticalgorithms as ga
import realtimeviewer as rtv
from shipsims import drone
from shipsims import gimbaldrone
from shipsims import ship
from shipsims import spinship
# population, generation = run_evolution(
#     populate_func=partial(generate_population, size=10, layer_sizes=layer_sizes),
#     fitness_limit = 50000,
#     generation_limit = 200
# )
ls = [5,3,2]
sim_class = drone.Drone
ps = 1/30.0
population, generation = ga.run_evolution(
    # populate_func=partial(read_population),
    sim_class = sim_class,
    pop_mode = "read",# Gravity
    #pop_file = "savedgenome.txt",
    max_time = 15,
    fitness_limit = 50000,
    generation_limit = 500,
    layer_sizes = ls
)
view = rtv.RealtimeViewer(population[0], ls, sim_class, ps)
view.start()
