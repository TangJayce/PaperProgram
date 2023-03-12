import GA

l = 2   # 上级供应点数量
m = 3   # 配送中心数量
n = 12  # 需求点数量

Qi = [3550, 3050]  # 供应点供应量
Qk = [350, 550, 400, 370, 580, 420, 470, 320, 530, 290, 500, 430]  # 需求点需求量

fj = [1900000, 2100000, 2000000]    # 各备选配送中心年分摊固定成本
dij = [     # 供应点与备选配送中心的距离
    [34.4, 39.2, 23.2],
    [47.6, 42.4, 68.8]
]
djk = [     # 备选配送中心与客户需求点的距离
    [10.8, 12.2, 10.4, 12.4, 17.2, 23.8, 20.6, 21.4, 23.4, 31.6, 23, 24.6],
    [19.6, 13.4, 9.8, 5.2, 8.4, 17.6, 9, 11.8, 15.4, 20.1, 6.6, 8],
    [24, 21.4, 24.6, 26.4, 19.4, 10.2, 18, 15.2, 12.8, 10.2, 30.4, 29.6]
]
Tk = [      # 期望配送时间
    [10, 30],
    [10, 40],
    [30, 60],
    [20, 30],
    [15, 45],
    [20, 30],
    [20, 50],
    [30, 40],
    [25, 35],
    [40, 50],
    [30, 50],
    [20, 60]
]

g1 = 1          # 运输阶段的单位运输费率（元/吨公里）
g2 = 2          # 配送阶段的单位运输费率（元/吨公里）
alpha = 200     # 单位制冷成本（元/吨）
h = 100         # 单位仓储成本h（元/吨）
epsilon1 = 5    # 时间惩罚系数1（元/吨*小时）
epsilon2 = 10   # 时间惩罚系数2（元/吨*小时）
theta = 0.004   # 单位距离新鲜度损耗率
gamma = 1.2     # 新鲜度每下降一个百分点需求量对应下降的百分点
P = 10000       # 水产品单位成本（元/吨）
beta = 150      # 单位预处理成本（元/吨）
delta1 = 15     # 单位消毒成本（元/吨）
delta2 = 10     # 单位检验成本（元/吨）
v = 30          # 车辆行驶速度v（公里/小时）


def get_fixed_cost(chromosome: list) -> float:
    """
    获取固定成本
    :param chromosome: 染色体
    :return: 固定成本C1
    """
    s = 0
    for index, gene in enumerate(chromosome):
        if gene > 0:
            s += fj[index]
    return s


def get_transport_cost(chromosome: list, q_ij: list, q_jk: list) -> float:
    """
    获取运输成本
    :param chromosome: 染色体
    :param q_ij: 供应点向配送中心的运输量
    :param q_jk: 配送中心向需求点的运输量
    :return: 运输成本C2
    """
    s = 0
    # 累计供应点到配送中心的运输成本
    for i in range(l):
        for j in range(m):
            s += dij[i][j] * q_ij[i][j] * g1 * chromosome[j]
    # 累计配送中心到客户需求点的运输成本
    for j in range(m):
        for k in range(n):
            s += djk[j][k] * q_jk[j][k] * g2 * chromosome[j]
    return s


def get_refrigeration_cost(chromosome: list, q_ij: list, q_jk: list) -> float:
    """获取制冷成本"""
    s = 0
    for i in range(l):
        for j in range(m):
            t_ij = dij[i][j] / v
            s += q_ij[i][j] * t_ij * chromosome[j]
    for j in range(m):
        for k in range(n):
            t_jk = djk[j][k] / v
            s += q_jk[j][k] * t_jk * chromosome[j]
    return s * alpha


def get_storage_cost(chromosome: list, q_ij: list) -> float:
    """获取仓储成本"""
    s = 0
    for i in range(l):
        for j in range(m):
            s += q_ij[i][j] * chromosome[j]
    return s * h


def get_penalty_cost(chromosome: list, q_jk: list) -> float:
    """获取惩罚成本"""
    s = 0
    for j in range(m):
        for k in range(n):
            t_jk = djk[j][k] / v
            ET = Tk[k][0] / 60
            LT = Tk[k][1] / 60
            F = epsilon1 * max(ET - t_jk, 0) + epsilon2 * max(t_jk - LT, 0)
            M = P * Qk[k]
            s += min(F, M) * q_jk[j][k] * chromosome[j]
    return s


def get_damage_cost(Dk: list) -> float:
    """获取货损成本"""
    s = 0
    for k in range(n):
        phi_k = (1 - theta) ** Dk[k]
        if phi_k < 0.3:
            s += Qk[k]
        elif phi_k < 0.9:
            s += Qk[k] * (1 - phi_k) * gamma
    return s * P


def get_pretreatment_cost(chromosome: list, q_ij: list) -> float:
    """获取预处理成本"""
    s = 0
    for i in range(l):
        for j in range(m):
            s += q_ij[i][j] * chromosome[j]
    return s * beta


def get_inspection_cost(chromosome: list, q_ij: list) -> float:
    """获取安全检验成本"""
    s = 0
    for i in range(l):
        for j in range(m):
            s += (delta1 + delta2) * q_ij[i][j] * chromosome[j]
    return s


def get_parent_j(chromosome: list) -> list:
    """获取配送中心是由哪个供应点供应的"""
    parent_j = [-1 for _ in range(m)]
    for j in range(m):
        d = -1
        idx = -1
        for i in range(l):
            if chromosome[j] > 0:
                if d < 0 or dij[i][j] < d:
                    d = dij[i][j]
                    idx = i
        parent_j[j] = idx
    return parent_j


def get_parent_k(chromosome: list) -> list:
    """获取需求点是否哪个配送中心配送的"""
    parent_k = [-1 for _ in range(n)]
    for k in range(n):
        d = -1
        idx = -1
        for j in range(m):
            if chromosome[j] > 0:
                if d < 0 or djk[j][k] < d:
                    d = djk[j][k]
                    idx = j
        parent_k[k] = idx
    return parent_k


def get_q_jk(parent_k: list):
    """
    获取每一个配送中心到需求点的供应量
    :param parent_k: 需求点是否哪个配送中心配送的
    :return: q_ij表示配送中心到需求点的供应量, Tj表示配送中心的总需求量
    """
    q_jk = [[0 for k in range(n)] for j in range(m)]
    Tj = [0 for j in range(m)]

    for k in range(n):
        idx = parent_k[k]
        if idx >= 0:
            q_jk[idx][k] = Qk[k]
            Tj[idx] += Qk[k]
    return q_jk, Tj


def get_q_ij(parent_j: list, Tj: list) -> list:
    """
    获取每一个供应点到配送中心的供应量
    :param parent_j: 配送中心是由哪个供应点供应的
    :param Tj: 配送中心的总需求量
    :return: q_ij
    """
    q_ij = [[0 for j in range(m)] for i in range(l)]
    for j in range(m):
        idx = parent_j[j]
        if idx >= 0:
            q_ij[idx][j] = Tj[j]
    return q_ij


def get_cost(chromosome: list) -> float:
    s = 0
    parent_j = get_parent_j(chromosome)
    parent_k = get_parent_k(chromosome)
    [q_jk, Tj] = get_q_jk(parent_k)
    q_ij = get_q_ij(parent_j, Tj)

    Dk = []
    for k in range(n):
        j = parent_k[k]
        i = parent_j[j]
        Dk.append(dij[i][j] + djk[j][k])

    s += get_fixed_cost(chromosome)                         # 累计固定成本
    s += get_transport_cost(chromosome, q_ij, q_jk)         # 累计运输成本
    s += get_refrigeration_cost(chromosome, q_ij, q_jk)     # 累计制冷成本
    s += get_storage_cost(chromosome, q_ij)                 # 累计仓储成本
    s += get_penalty_cost(chromosome, q_jk)                 # 累计惩罚成本
    s += get_damage_cost(Dk)                                # 累计货损成本
    s += get_pretreatment_cost(chromosome, q_ij)            # 累计预处理成本
    s += get_inspection_cost(chromosome, q_ij)              # 累计安全检验成本
    return s


def show_cost_detail(chromosome: list):
    parent_j = get_parent_j(chromosome)
    parent_k = get_parent_k(chromosome)
    [q_jk, Tj] = get_q_jk(parent_k)
    q_ij = get_q_ij(parent_j, Tj)

    Dk = []
    for k in range(n):
        j = parent_k[k]
        i = parent_j[j]
        Dk.append(dij[i][j] + djk[j][k])

    print("固定成本: ", get_fixed_cost(chromosome))
    print("运输成本: ", get_transport_cost(chromosome, q_ij, q_jk))
    print("制冷成本: ", get_refrigeration_cost(chromosome, q_ij, q_jk))
    print("仓储成本: ", get_storage_cost(chromosome, q_ij))
    print("惩罚成本: ", get_penalty_cost(chromosome, q_jk))
    print("货损成本: ", get_damage_cost(Dk))
    print("预处理成本: ", get_pretreatment_cost(chromosome, q_ij))
    print("安全检验成本: ", get_inspection_cost(chromosome, q_ij))


def print_total():
    """显示每一种情况的成本"""
    for index in range(1 << m):
        chromosome = []
        for j in range(m):
            chromosome.append((index >> (m - j - 1)) & 1)
        print(chromosome, get_cost(chromosome))
        show_cost_detail(chromosome)
        print()


if __name__ == '__main__':
    population = GA.init(m)
    for i in range(GA.iterations):
        print("第", i + 1, "次迭代中初始种群数量：", len(population))

        fitness = GA.cal_fitness(population, get_cost)
        p = GA.cal_pop_fitness(population, fitness, 5)
        print("第", i + 1, "次迭代中最优的前五个基因：")
        for chromosome in p:
            print(chromosome, end='')
            print(get_cost(chromosome))

        selected_population = GA.select(population, fitness)
        print("第", i + 1, "次迭代中选择后种群数量：", len(selected_population))

        crossed_population = GA.crossover(selected_population)
        print("第", i + 1, "次迭代中交叉后种群数量：", len(crossed_population))

        mutated_population = GA.mutation(crossed_population)
        print("第", i + 1, "次迭代中变异后种群数量：", len(mutated_population))
        population = mutated_population
        print()

    fitness = GA.cal_fitness(population, get_cost)
    p = GA.cal_pop_fitness(population, fitness, 1)
    print("第", GA.iterations, "次迭代后最优的一个基因：")
    chromosome = p[0]
    print(chromosome)
    print("总成本为：", get_cost(chromosome))
    show_cost_detail(chromosome)
