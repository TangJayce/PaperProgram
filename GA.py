"""
遗传算法实现
编码方式：二进制编码
"""

import random

populations = 100   # 种群规模
pc = 0.7            # 交叉概率
pm = 0.05           # 变异概率
iterations = 200    # 迭代次数


def check(chromosome: list) -> bool:
    """判断染色体是否合理，也就是判断是否全部为0，如果全为0则不合理"""
    for gene in chromosome:
        if gene > 0:
            return True
    return False


def init(genes: int, chromosomes: int) -> list:
    """初始化种群
    :param genes: 这个种群的基因数量
    :param chromosomes: 这个种群有多少个个体
    :return: 整个种群的染色体
    """
    population = []
    i = 0
    while i < chromosomes:
        chromosome = []
        for j in range(genes):
            chromosome.append(random.randint(0, 1))
        if check(chromosome):
            population.append(chromosome)
            i += 1
        else:
            continue
    return population


def cal_pop_fitness(population: list, func, size: int) -> list:
    fitness = cal_fitness(population, func)
    s = []
    for index, value in enumerate(fitness):
        s.append([index, value])
    s.sort(key=(lambda x: x[1]), reverse=True)
    pop_fitness = []
    for i in range(size):
        index = s[i][0]
        pop_fitness.append(population[index])
    return pop_fitness


def cal_fitness(population: list, func) -> list:
    """计算适应度函数"""
    fitness = []
    for chromosome in population:
        fitness.append(1 / func(chromosome))
    return fitness


def select(population: list, fitness: list, func) -> list:
    """遗传选择"""
    # 计算累积概率
    p = []
    s = 0
    total = sum(fitness)
    for i in fitness:
        s += i
        p.append(s / total)
    # 轮盘赌法进行选择
    size = 5
    new_population = cal_pop_fitness(population, func, size)
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
    pos = random.randint(1, len(population[0]) - 1)
    for i in range(m):
        for j in range(i + 1, m):
            dad = list(chromosomes[i])
            mom = list(chromosomes[j])
            new_chromosome = dad[:pos] + mom[pos:]
            new_population.append(new_chromosome)
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
