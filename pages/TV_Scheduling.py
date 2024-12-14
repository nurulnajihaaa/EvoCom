import streamlit as st
import csv
import random

def read_csv_to_dict(file):
    """
    Read a CSV file from a Streamlit upload widget and parse it into a program ratings dictionary.
    """
    program_ratings = {}
    file_content = file.read().decode('utf-8').splitlines()
    reader = csv.reader(file_content)
    header = next(reader)
    for row in reader:
        program = row[0]
        ratings = [float(x) for x in row[1:]]
        program_ratings[program] = ratings
    return program_ratings

# Fitness function
def fitness_function(schedule, ratings):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

# Crossover function
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# Mutation function
def mutate(schedule, all_programs):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

# Genetic Algorithm
def genetic_algorithm(initial_schedule, ratings, all_programs, generations, population_size, crossover_rate, mutation_rate, elitism_size):
    population = [initial_schedule]

    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        new_population = []

        # Elitism
        population.sort(key=lambda schedule: fitness_function(schedule, ratings), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1, all_programs)
            if random.random() < mutation_rate:
                child2 = mutate(child2, all_programs)

            new_population.extend([child1, child2])

        population = new_population

    return population[0]

# Streamlit UI
st.title("Optimal TV Program Scheduling using Genetic Algorithm")

# File upload
uploaded_file = st.file_uploader("Upload CSV file with Program Ratings", type=["csv"])

if uploaded_file:
    # Read CSV data
    program_ratings = read_csv_to_dict(uploaded_file)
    all_programs = list(program_ratings.keys())
    all_time_slots = list(range(6, 24))  # Time slots from 6 AM to 11 PM

    # User inputs for Genetic Algorithm
    st.sidebar.header("Genetic Algorithm Parameters")
    generations = st.sidebar.number_input("Generations", min_value=10, max_value=1000, value=100, step=10)
    population_size = st.sidebar.number_input("Population Size", min_value=10, max_value=500, value=50, step=10)
    crossover_rate = st.sidebar.slider("Crossover Rate", min_value=0.0, max_value=0.95, value=0.8)
    mutation_rate = st.sidebar.slider("Mutation Rate", min_value=0.0, max_value=1.0, value=0.2)
    elitism_size = st.sidebar.number_input("Elitism Size", min_value=0.01, max_value=0.05, value=2, step=1)

    # Generate initial brute-force best schedule
    st.write("### Generating Schedule...")
    
    initial_best_schedule = all_programs.copy()
    random.shuffle(initial_best_schedule)
    rem_t_slots = len(all_time_slots) - len(initial_best_schedule)

    # Run Genetic Algorithm
    optimal_schedule = genetic_algorithm(
        initial_best_schedule,
        program_ratings,
        all_programs,
        generations,
        population_size,
        crossover_rate,
        mutation_rate,
        elitism_size
    )

    final_schedule = initial_best_schedule + optimal_schedule[:rem_t_slots]

    # Display final schedule
    st.write("### Final Optimal Schedule")
    schedule_display = []
    for time_slot, program in enumerate(final_schedule):
        schedule_display.append(f"{all_time_slots[time_slot]}:00 - {program}")
        st.write(f"**{all_time_slots[time_slot]}:00**: {program}")

    # Display total ratings
    total_ratings = fitness_function(final_schedule, program_ratings)
    st.write(f"### Total Ratings: **{total_ratings}**")
