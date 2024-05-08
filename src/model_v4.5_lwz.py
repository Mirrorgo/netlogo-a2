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
        self.k = k
        self.gov_legitimacy = gov_legitimacy
        self.max_jail_term = max_jail_term
        self.entities = []  # 统一存储所有实体
        self.total_cells = self.width * self.height
        self.num_agents = int((agent_density / 100) * self.total_cells)
        self.num_cops = int((cop_density / 100) * self.total_cells)
        self.create_entities(self.num_agents,self.num_cops)
        self.data = {'quiet': [], 'jail': [], 'active': []}

    def place_entities_randomly(self):
        positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        for entity in self.entities:
            entity.position = random.sample(positions, 1)[0]
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
            if entity.jail_term > 0:
                entity.jail_term -= 1
                jail_count += 1
                continue
            self.move_agent(entity)

            if entity.type == EntityType.AGENT:
                self.determine_behavior(entity)
                if entity.active:
                    active_count += 1
                else:
                    quiet_count += 1
            elif entity.type == EntityType.COP:
                self.enforce(entity)

        self.data['quiet'].append(quiet_count)
        self.data['jail'].append(jail_count)
        self.data['active'].append(active_count)

    def move_agent(self, agent):
        if agent.jail_term > 0:
            return  # Jailed agents do not move
        def is_position_valid(new_x, new_y):
            for entity in self.entities:
                x, y = entity.position
                if new_x == x and new_y == y: 
                    if entity.type == EntityType.COP: # 新位置与已有实体的位置重合
                        return False
                    elif entity.type == EntityType.AGENT and entity.jail_term == 0:
                        return False
            return True 
        x, y = agent.position
        while True:
            dx = random.randint(-self.vision, self.vision)
            dy = random.randint(-self.vision, self.vision)
            # Update the agent's position, considering wrap-around
            new_x = (x + dx) % self.width
            new_y = (y + dy) % self.height
            if is_position_valid(new_x,new_y):
                break
        # Update the agent's position
        agent.position = (new_x, new_y)

       

    def determine_behavior(self, agent):
        grievance = agent.hardship * (1 - self.gov_legitimacy)
        arrest_probability = self.estimate_arrest_probability(agent.position)
        if grievance - (agent.risk_aversion * arrest_probability) > 0.1:
            agent.active = True
        else:
            agent.active = False

    def is_neighbor(self,x,y,j,k):
        dx = abs(x - j)
        dy = abs(y - k)
        distance_x = min(dx, self.width - dx)
        distance_y = min(dy, self.height - dy)
        return distance_x <= self.vision and distance_y <= self.vision


    def estimate_arrest_probability(self, position):
        x, y = position
        cops_count = 0
        active_agents_count = 0
        for entity in self.entities:
            cx,cy = entity.position
            if self.is_neighbor(x,y,cx,cy):
                if(entity.type == EntityType.COP):
                    cops_count += 1
                elif entity.type == EntityType.AGENT and entity.active:
                    active_agents_count += 1
        arrest_prob = 1 - math.exp(-self.k * math.floor(cops_count / (active_agents_count + 1)))
        return arrest_prob

    # TODO
    # Modification: collect all active agents at first and then randomly select one to jail
    def enforce(self, cop):
        x, y = cop.position
        active_agents = []
        for entity in self.entities[:self.num_agents]:
            ax,ay = entity.position
            if self.is_neighbor(x,y,ax,ay):
                if entity.type == EntityType.AGENT and entity.active == True:
                    active_agents.append(entity)
        # Randomly select one active agent to arrest
        if active_agents:
            selected_agent = random.choice(active_agents)
            selected_agent.active = False
            selected_agent.jail_term = random.randint(0, self.max_jail_term)
            # Move cop to the position of the arrested agent
            cop.position = selected_agent.position

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
plt.plot(model.data['quiet'], label='Quiet Agents')
plt.plot(model.data['jail'], label='Jailed Agents')
plt.plot(model.data['active'], label='Active Agents')
plt.xlabel('Time Steps')
plt.ylabel('Number of Agents')
plt.title('Agent Status Over Time')
plt.legend()
plt.show()


