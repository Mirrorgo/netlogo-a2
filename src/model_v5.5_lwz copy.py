import random
import math
import matplotlib.pyplot as plt
from enum import Enum


class EntityType(Enum):
    AGENT = 'Agent'
    COP = 'Cop'


class Turtle:
    def __init__(self, agent_id, type, vision, risk_aversion=None, hardship=None):
        self.agent_id = agent_id
        self.type = type
        self.vision = vision
        self.risk_aversion = risk_aversion
        self.hardship = hardship
        self.grievance = None
        self.active = False
        self.jail_term = 0
        self.position = (None, None)

    def __repr__(self):
        return f"{self.type}{self.agent_id}"


class Model:
    def __init__(self, agent_density, cop_density, vision, k, gov_legitimacy, max_jail_term):
        if agent_density + cop_density > 100:
            raise ValueError("The sum of agent_density and cop_density should not exceed 100%")
        self.width = 40
        self.height = 40
        self.vision = vision
        self.grid = [[{'cops': False, 'active_agents': False} for _ in range(self.width)] for _ in range(self.height)]
        self.k = k
        self.gov_legitimacy = gov_legitimacy
        self.max_jail_term = max_jail_term
        self.entities = []  # 统一存储所有实体
        self.total_cells = self.width * self.height
        self.num_agents = int((agent_density / 100) * self.total_cells)
        self.num_cops = int((cop_density / 100) * self.total_cells)
        self.neighborhoods = [[[] for _ in range(self.height)] for _ in range(self.width)]
        self.compute_neighborhoods()
        self.data = {'quiet': [self.num_agents], 'jail': [0], 'active': [0]}
        self.create_entities(self.num_agents,self.num_cops)

    def compute_neighborhoods(self):
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

    def place_entities_randomly(self):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        for entity in self.entities:
            entity.position = random.sample(positions, 1)[0]
            x, y = entity.position
            if entity.type == EntityType.COP:
                self.grid[x][y]['cops'] = True
            elif entity.type == EntityType.AGENT and entity.active:
                self.grid[x][y]['active_agents'] = True
            positions.remove(entity.position) 


    def create_entities(self, num_agents, num_cops):
        # 从0到num_agents-1是agent, num_agents到num_agents+num_cops-1是cops
        for i in range(num_agents):
            agent = Turtle(i, EntityType.AGENT, self.vision, random.random(), random.random())
            self.entities.append(agent)
        for i in range(num_cops):
            cop = Turtle(num_agents + i, EntityType.COP, self.vision)
            self.entities.append(cop)
        self.place_entities_randomly()

  

    def step(self):
        quiet_count = jail_count = active_count = 0
        for entity in self.entities:
            if entity.type == EntityType.AGENT:
                if entity.jail_term > 0:
                    entity.jail_term -= 1
                    continue
                if entity.grievance is None:
                    entity.grievance = entity.hardship * (1 - self.gov_legitimacy)
                self.move_agent(entity)
                self.determine_behavior(entity)
            elif entity.type == EntityType.COP:
                self.move_agent(entity)
                self.enforce(entity)
        # 统计不同状态的agent数量
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

    def move_agent(self, agent):
        if agent.jail_term > 0:
            return  # Jailed agents do not move
        valid_positions = []
        x, y = agent.position
        # for all neighborhood
        neighborhood = self.neighborhoods[x][y]
        for nx, ny in neighborhood:
            if (not self.grid[nx][ny]['cops']) and (not self.grid[nx][ny]['active_agents']):
                valid_positions.append((nx, ny))
        if valid_positions:  # 检查是否有可选位置
            agent.position = random.choice(valid_positions)
            newx, newy = agent.position
            if agent.type == EntityType.AGENT and agent.active == True:
                self.grid[x][y]['active_agents'] = False
                self.grid[newx][newy]['active_agents'] = True
            elif agent.type == EntityType.COP:
                self.grid[x][y]['cops'] = False
                self.grid[newx][newy]['cops'] = True

    def determine_behavior(self, agent):
        arrest_probability = self.estimate_arrest_probability(agent.position)
        x,y = agent.position
        if agent.grievance - (agent.risk_aversion * arrest_probability) > 0.1:
            agent.active = True
            self.grid[x][y]['active_agents'] = True
        else:
            agent.active = False

    def estimate_arrest_probability(self, position):
        x, y = position
        cops_count = 0
        active_agents_count = 0
        neighborhood = self.neighborhoods[x][y]
        for nx, ny in neighborhood:
            if self.grid[nx][ny]['cops']:
                cops_count += 1
            if self.grid[nx][ny]['active_agents']:
                active_agents_count += 1
        arrest_prob = 1 - math.exp(-self.k * math.floor(cops_count / (active_agents_count + 1)))
        return arrest_prob

    def enforce(self, cop):
        x, y = cop.position
        active_agents = []
        neighborhood = self.neighborhoods[x][y]
        for nx, ny in neighborhood:
            if self.grid[nx][ny]['active_agents']:
                for agent in self.entities[:self.num_agents]:
                    if agent.position == (nx, ny):
                        active_agents.append(agent)
                        # 是否break以及去掉找到过的

        # Randomly select one active agent to arrest
        if active_agents:
            selected_agent = random.choice(active_agents)
            cop.position = selected_agent.position
            new_x,new_y = cop.position
            
            selected_agent.active = False
            selected_agent.jail_term = random.randint(0, self.max_jail_term)
            
            # Move cop to the position of the arrested agent
            self.grid[x][y]['cops'] = False
            self.grid[new_x][new_y]['cops'] = True
            self.grid[new_x][new_y]["active_agents"] = False
            

# 实例化并运行模型
AGENT_DENSITY = 70
COP_DENSITY = 3
VISION = 7
K = 2.3
GOV_LEGITIMACY = 0.3
MAX_JAIL_TERM = 30
model = Model(AGENT_DENSITY, COP_DENSITY, VISION, K, GOV_LEGITIMACY, MAX_JAIL_TERM)
for _ in range(200):
    model.step()

# 绘制结果
plt.figure(figsize=(10, 6))
plt.plot(model.data['quiet'], label='Quiet Agents', color="green")
plt.plot(model.data['jail'], label='Jailed Agents',color="black")
plt.plot(model.data['active'], label='Active Agents',color="red")
plt.xlabel('Time Steps')
plt.ylabel('Number of Agents')
plt.title('Agent Status Over Time')
plt.legend()
plt.show()


