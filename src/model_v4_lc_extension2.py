# 添加了扩展，增加了一个neighborhood的不满程度可以影响到个人的不满程度。可以通过调节社会不满程度 的百分比来调节
import random
import math
import matplotlib.pyplot as plt
from enum import Enum

import numpy as np
from scipy.signal import find_peaks


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
        self.adjusted_hardship = hardship  # 新增属性，初始化时与hardship相同
        self.active = False
        self.jail_term = 0
        self.position = (None, None)

    def __repr__(self):
        return f"{self.type}{self.agent_id}"


class Model:
    def __init__(self, agent_density, cop_density, vision, k, gov_legitimacy, max_jail_term,
                 neighbor_influence_percentage):
        if agent_density + cop_density > 100:
            raise ValueError("The sum of agent_density and cop_density should not exceed 100%")
        self.width = 40
        self.height = 40
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        self.vision = vision
        self.k = k
        self.gov_legitimacy = gov_legitimacy
        self.max_jail_term = max_jail_term
        self.entities = []  # 统一存储所有实体
        self.total_cells = self.width * self.height
        self.neighborhoods = [[[] for _ in range(self.height)] for _ in range(self.width)]
        self.compute_neighborhoods()
        self.create_entities(int((agent_density / 100) * self.total_cells), int((cop_density / 100) * self.total_cells))
        self.data = {'quiet': [], 'jail': [], 'active': []}
        self.neighbor_influence_percentage = neighbor_influence_percentage  # 新增全局参数

    # Modification in v3:  consider the boundary condition
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

    # 计算受到邻居的hardship影响之后的新的hardship
    def compute_adjusted_hardship(self):
        for agent in self.entities:
            if agent.type == EntityType.AGENT:
                x, y = agent.position
                neighborhood = self.neighborhoods[x][y]
                total_hardship = 0
                count = 0
                for nx, ny in neighborhood:
                    neighbor = self.grid[nx][ny]
                    if isinstance(neighbor, Turtle) and neighbor.type == EntityType.AGENT:
                        total_hardship += neighbor.hardship
                        count += 1
                if count > 0:
                    average_hardship = total_hardship / count
                    agent.adjusted_hardship = (
                        average_hardship * self.neighbor_influence_percentage +
                        agent.hardship * (1 - self.neighbor_influence_percentage)
                    )

    def create_entities(self, num_agents, num_cops):
        for i in range(num_agents):
            agent = Turtle(i, EntityType.AGENT, self.vision, random.random(), random.random())
            self.place_entity_randomly(agent)
            self.entities.append(agent)
        for i in range(num_cops):
            cop = Turtle(num_agents + i, EntityType.COP, self.vision)
            self.place_entity_randomly(cop)
            self.entities.append(cop)

    def place_entity_randomly(self, entity):
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        while self.grid[x][y] is not None:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        self.grid[x][y] = entity
        entity.position = (x, y)

    def step(self):
        self.compute_adjusted_hardship()
        # 增加了shuffle每一轮都打乱顺序
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
        # 每次都是前面执行结束之后才跑统计方法
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
        x, y = agent.position
        grievance = agent.adjusted_hardship * (1 - self.gov_legitimacy)
        arrest_probability = self.estimate_arrest_probability((x, y))
        if grievance - (agent.risk_aversion * arrest_probability) > 0.1:
            agent.active = True
        else:
            agent.active = False

    def estimate_arrest_probability(self, position):
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

    # Modification: collect all active agents at first and then randomly select one to jail
    def enforce(self, cop):
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
            selected_agent.jail_term = random.randint(0, self.max_jail_term)
            # Move cop to the position of the arrested agent
            self.grid[x][y] = None  # Remove cop from current position
            self.grid[nx][ny] = cop  # Move cop to new position
            cop.position = (nx, ny)


def run_experiment(neighbor_influence_percentage):
    # 假设 Model 类和其他相关设置已经按照前面的讨论正确配置
    model = Model(
        agent_density=70,
        cop_density=4,
        vision=7,
        k=2.3,
        gov_legitimacy=0.82,
        max_jail_term=30,
        neighbor_influence_percentage=neighbor_influence_percentage
    )

    for _ in range(500):  # 模拟500步
        model.step()
    return model.data['active']


def analyze_peaks(active_data):
    active_data = np.array(active_data)  # 确保active_data是NumPy数组
    peaks, _ = find_peaks(active_data, height=0)  # 可以通过height参数调整峰值识别的灵敏度
    peak_values = active_data[peaks]  # 现在可以正确使用peaks进行索引
    return peak_values.mean() if len(peak_values) > 0 else 0


# 实验参数
neighbor_influence_percentages = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

# 收集结果
average_peak_values = []
for nip in neighbor_influence_percentages:
    active_data = run_experiment(nip)
    average_peak = analyze_peaks(active_data)
    average_peak_values.append(average_peak)
    print(average_peak)
# 绘制结果
plt.figure(figsize=(10, 6))
plt.plot(neighbor_influence_percentages, average_peak_values, marker='o')
plt.xlabel('Neighbor Influence Percentage')
plt.ylabel('Average Peak Active Agents')
plt.title('Average Peak of Active Agents vs. Neighbor Influence Percentage')
plt.grid(True)
plt.show()
plt.savefig(f'Average_peak.png')


#     # 绘制结果
#     plt.figure(figsize=(10, 6))
#     plt.plot(model.data['quiet'], label='Quiet Agents')
#     plt.plot(model.data['jail'], label='Jailed Agents')
#     plt.plot(model.data['active'], label='Active Agents')
#     plt.xlabel('Time Steps')
#     plt.ylabel('Number of Agents')
#     plt.title(f'Agent Status Over Time with NIP {neighbor_influence_percentage}')
#     plt.legend()
#     plt.savefig(f'results_{neighbor_influence_percentage}.png')  # 保存图像
#     plt.close()  # 关闭图形窗口以释放资源
#
#
# # 实验参数
# neighbor_influence_percentages = [0.1, 0.3, 0.5, 0.7, 0.9]
#
# # 运行实验
# for nip in neighbor_influence_percentages:
#     run_experiment(nip)


