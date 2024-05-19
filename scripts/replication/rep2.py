import csv
import random
import math
from enum import Enum

class EntityType(Enum):
    """An enumeration to represent types of entities."""
    AGENT = 'Agent'
    COP = 'Cop'

class Turtle:
    """A class to represent a turtle entity in the simulation."""
    def __init__(self, agent_id, type, vision, risk_aversion=None, hardship=None):
        """
        Initializes a Turtle object.

        Parameters:
        agent_id (int): The unique identifier of the turtle.
        type (EntityType): The type of the turtle (Agent or Cop).
        vision (int): The vision range of the turtle.
        risk_aversion (float, optional): The risk aversion factor of the turtle. Defaults to None.
        hardship (float, optional): The hardship factor of the turtle. Defaults to None.
        """
        self.agent_id = agent_id
        self.type = type
        self.vision = vision
        self.risk_aversion = risk_aversion
        self.hardship = hardship
        self.active = False
        self.jail_term = 0
        self.position = (None, None)

    def __repr__(self):
        """Returns a string representation of the Turtle object."""
        return f"{self.type}{self.agent_id}"


class Model:
    def __init__(self, agent_density, cop_density, vision, k, gov_legitimacy, max_jail_term):
        if agent_density + cop_density > 100:
            raise ValueError("The sum of agent_density and cop_density should not exceed 100%")
        self.width = 40
        self.height = 40
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        self.vision = vision
        self.k = k
        self.gov_legitimacy = gov_legitimacy
        self.max_jail_term = max_jail_term
        self.entities = []  # Store all entities
        self.total_cells = self.width * self.height
        self.neighborhoods = [[[] for _ in range(self.height)] for _ in range(self.width)]
        self.compute_neighborhoods()
        self.create_entities(int((agent_density / 100) * self.total_cells), int((cop_density / 100) * self.total_cells))
        self.data = {'quiet': [], 'jail': [], 'active': []}
        self.tick = 0

    def compute_neighborhoods(self):
        """
        Computes neighborhoods for all cells in the grid.
        """
        for x in range(self.width):
            for y in range(self.height):
                neighborhood = []
                for dx in range(-self.vision, self.vision + 1):
                    for dy in range(-self.vision, self.vision + 1):
                        # Check the distance to ensure it's within the vision radius
                        if dx ** 2 + dy ** 2 <= self.vision ** 2:
                            # Apply periodic boundary conditions
                            nx, ny = (x + dx) % self.width, (y + dy) % self.height
                            neighborhood.append((nx, ny))
                self.neighborhoods[x][y] = neighborhood

    def create_entities(self, num_agents, num_cops):
        """
        Creates agents and cops and places them randomly on the grid.

        Parameters:
        num_agents (int): The number of agents to create.
        num_cops (int): The number of cops to create.
        """
        for i in range(num_agents):
            agent = Turtle(i, EntityType.AGENT, self.vision, random.random(), random.random())
            self.place_entity_randomly(agent)
            self.entities.append(agent)
        for i in range(num_cops):
            cop = Turtle(num_agents + i, EntityType.COP, self.vision)
            self.place_entity_randomly(cop)
            self.entities.append(cop)

    def place_entity_randomly(self, entity):
        """
        Places an entity randomly on the grid.

        Parameters:
        entity (Turtle): The entity to be placed.
        """
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        while self.grid[x][y] is not None:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        self.grid[x][y] = entity
        entity.position = (x, y)

    def step(self):
        """
        Performs one step of the simulation.
        """
        random.shuffle(self.entities)
        quiet_count = jail_count = active_count = 0

        for entity in self.entities:
            if entity.jail_term > 0:
                entity.jail_term -= 1
                continue

            self.move_agent(entity)
            if entity.type == EntityType.AGENT:
                self.determine_behavior(entity)
            elif entity.type == EntityType.COP:
                self.enforce(entity)
        # After all entities have taken their actions, count the number of each agent type
        for entity in self.entities:
            if entity.jail_term > 0:
                jail_count += 1
                continue
            if entity.type == EntityType.AGENT:
                if entity.active:
                    active_count += 1
                else:
                    quiet_count += 1
        self.data['quiet'].append(quiet_count)
        self.data['jail'].append(jail_count)
        self.data['active'].append(active_count)
        # Decrease government legitimacy over time
        if self.gov_legitimacy > 0:
            self.gov_legitimacy -= 0.0045

        self.tick += 1

    def move_agent(self, agent):
        """
        Moves an agent to a neighboring cell.

        Parameters:
        agent (Turtle): The agent to move.
        """
        if agent.jail_term > 0:
            return  # Jailed agents do not move
        x, y = agent.position
        self.grid[x][y] = None  # Remove agent from current position
        potential_positions = []
        # Use precomputed neighborhood
        neighborhood = self.neighborhoods[x][y]
        for nx, ny in neighborhood:
            target = self.grid[nx][ny]
            if target is None:
                potential_positions.append((nx, ny))
            elif isinstance(target, Turtle) and target.jail_term > 0:
                # Include positions with only jailed agents
                potential_positions.append((nx, ny))
        if potential_positions:
            new_position = random.choice(potential_positions)
            self.grid[new_position[0]][new_position[1]] = agent
            agent.position = new_position

    def determine_behavior(self, agent):
        """
        Determines the behavior of an agent based on its grievances and arrest probability.

        Parameters:
        agent (Turtle): The agent to determine behavior for.
        """
        x, y = agent.position
        grievance = agent.hardship * (1 - self.gov_legitimacy)
        arrest_probability = self.estimate_arrest_probability((x, y))
        if grievance - (agent.risk_aversion * arrest_probability) > 0.1:
            agent.active = True
        else:
            agent.active = False

    def estimate_arrest_probability(self, position):
        """
        Estimates the arrest probability at a given position.

        Parameters:
        position (tuple): The position to estimate arrest probability for.

        Returns:
        float: The estimated arrest probability.
        """
        x, y = position
        cops_count = 0
        active_agents_count = 0
        neighborhood = self.neighborhoods[x][y]
        for nx, ny in neighborhood:
            cell = self.grid[nx][ny]
            if isinstance(cell, Turtle):
                if cell.type == EntityType.COP:
                    cops_count += 1
                elif cell.type == EntityType.AGENT and cell.active:
                    active_agents_count += 1
        arrest_prob = 1 - math.exp(-self.k * math.floor(cops_count / (active_agents_count + 1)))
        return arrest_prob

    def enforce(self, cop):
        """
        Enforces the law by arresting an active agent.

        Parameters:
        cop (Turtle): The cop to perform enforcement
        """
        x, y = cop.position
        active_agents = []
        # Collect all active agents in the neighborhood
        for nx, ny in self.neighborhoods[x][y]:
            agent = self.grid[nx][ny]
            if isinstance(agent, Turtle) and agent.active:
                active_agents.append((agent, nx, ny))
        # Randomly select one active agent to arrest
        if active_agents:
            selected_agent, nx, ny = random.choice(active_agents)
            selected_agent.active = False
            # selected_agent.jail_term = random.randint(0, self.max_jail_term)
            selected_agent.jail_term = 1000
            # Move cop to the position of the arrested agent
            self.grid[x][y] = None  # Remove cop from current position
            self.grid[nx][ny] = cop  # Move cop to new position
            cop.position = (nx, ny)


# Model parameters
AGENT_DENSITY = 70
COP_DENSITY = 7.4
VISION = 7
K = 2.3
GOV_LEGITIMACY = 0.9
MAX_JAIL_TERM = 30

# Instantiate the model and run for 200 time steps
model = Model(AGENT_DENSITY, COP_DENSITY, VISION, K, GOV_LEGITIMACY, MAX_JAIL_TERM)
for _ in range(200):
    model.step()

# Export data to CSV file
with open('rep2.py.csv', 'w', newline='') as csvfile:
    fieldnames = ['Time Step', 'Quiet Agents', 'Jailed Agents', 'Active Agents']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i in range(len(model.data['quiet'])):
        writer.writerow({
            'Time Step': i,
            'Quiet Agents': model.data['quiet'][i],
            'Jailed Agents': model.data['jail'][i],
            'Active Agents': model.data['active'][i]
        })

print("CSV generated successfully!")
