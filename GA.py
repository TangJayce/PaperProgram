"""
遗传算法实现
编码方式：二进制编码
"""

import random

populations = 100   # 种群规模
pc = 0.7            # 交叉概率
pm = 0.05           # 变异概率
iterations = 200    # 迭代次数
pr = 0.1            # 保留前10%最优秀的个体


def check(chromosome: list) -> bool:
    """判断染色体是否合理，也就是判断是否全部为0，如果全为0则不合理"""
    for gene in chromosome:
        if gene > 0:
            return True
    return False


def init(genes: int) -> list:
    """初始化种群
    :param genes: 这个种群的基因数量
    :return: 整个种群的染色体
    """
    population = []
    i = 0
    while i < populations:
        chromosome = []
        for j in range(genes):
            chromosome.append(random.randint(0, 1))
        if check(chromosome):
            population.append(chromosome)
            i += 1
        else:
            continue
    return population


def cal_pop_fitness(population: list, fitness: list, size: int) -> list:
    s = []
    for index, value in enumerate(fitness):
        s.append([index, value])
    s.sort(key=(lambda x: x[1]), reverse=True)
    pop_chromosome = []
    for i in range(size):
        index = s[i][0]
        if index < len(population):
            pop_chromosome.append(population[index])
        else:
            pop_chromosome.append([])
    return pop_chromosome


def cal_fitness(population: list, func) -> list:
    """计算适应度函数"""
    fitness = []
    for chromosome in population:
        fitness.append(1 / (func(chromosome) - 10_0000))
    return fitness


def select(population: list, fitness: list) -> list:
    """遗传选择"""
    # 计算累积概率
    p = []
    s = 0
    total = sum(fitness)
    for i in fitness:
        s += i
        p.append(s / total)
    # 轮盘赌法进行选择
    size = int(len(fitness) * pr)
    new_population = cal_pop_fitness(population, fitness, size)
    for i in range(populations - size):
        r = random.random()
        for index, value in enumerate(p):
            if value <= r:
                new_population.append(population[index])
                break
    return new_population


def crossover(population: list) -> list:
    """遗传交叉"""
    new_population = []
    chromosomes = []
    r = random.random()
    for value in population:
        if r < pc:
            chromosomes.append(value)
        else:
            new_population.append(value)
    m = len(chromosomes)
    for i in range(0, m - 1, 2):
        pos = random.randint(1, len(population[0]) - 1)
        j = i + 1
        dad = list(chromosomes[i])
        mom = list(chromosomes[j])
        new_population.append(dad[:pos] + mom[pos:])
        new_population.append(mom[:pos] + dad[pos:])
    return new_population


def mutation(population: list) -> list:
    """遗传变异"""
    new_population = []
    l = len(population[0])
    for value in population:
        tmp = random.random()
        if tmp < pm:
            pos = random.randint(0, l - 1)
            if value[pos] > 0:
                value[pos] = 0
            else:
                value[pos] = 1
        if check(value):
            new_population.append(value)
    return new_population
