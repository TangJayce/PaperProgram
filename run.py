l = 2       # 上级供应点数量
m = 3       # 配送中心数量
n = 12      # 需求点数量

fj = [190, 210, 200]    # 各备选配送中心年分摊固定成本
dij = [                 # 供应点与备选配送中心的距离
    [17.2, 19.6, 11.6],
    [23.8, 21.2, 34.4]
]
djk = [                 # 备选配送中心与客户需求点的距离
    [5.4, 6.1, 5.2, 6.2, 8.6, 11.9, 10.3, 10.7, 11.7, 15.8, 11.5, 12.3],
    [8.8, 6.7, 4.9, 2.6, 4.2, 8.7, 4.5, 5.9, 7.2, 10.1, 3.3, 4],
    [12, 10.7, 12.3, 13.2, 9.7, 5.1, 9, 7.6, 6.4, 5.1, 15.2, 14.8]
]

g1 = 1          # 运输阶段的单位运输费率（元/吨公里）
g2 = 2          # 配送阶段的单位运输费率（元/吨公里）
alpha = 200     # 单位制冷成本（元/吨）
h = 100         # 单位仓储成本h（元/吨）
epsilon1 = 5    # 时间惩罚系数1（元/吨*小时）
epsilon2 = 10   # 时间惩罚系数2（元/吨*小时）
theta = 0.004   # 单位距离新鲜度损耗率
gamma = 2       # 新鲜度每下降一个百分点需求量对应下降的百分点
sigma = 0.85    # 下降的需求量中低价处理掉的百分比
b = 4000        # 未完全腐败所损失的价值（元/吨）
e = 10000       # 完全腐败所损失的价值（元/吨）
beta = 150      # 单位预处理成本（元/吨）
delta1 = 15     # 单位消毒成本（元/吨）
delta2 = 10     # 单位检验成本（元/吨）
v = 30          # 车辆行驶速度v（公里/小时）


def get_fixed_cost(chromosome: list):
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


def get_transport_cost(chromosome: list, q_ij: list, q_jk: list):
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


def get_refrigeration_cost(chromosome: list, q_ij: list, q_jk: list):
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


def get_storage_cost(chromosome: list, q_ij: list):
    """获取仓储成本"""
    # todo: 待修改
    s = 0
    for i in range(l):
        for j in range(m):
            s += q_ij[i][j] * chromosome[j]
    return s * h


def get_penalty_cost(chromosome: list, q_jk: list):
    """获取惩罚成本"""
    s = 0
    for j in range(m):
        for k in range(n):
            t_jk = djk[j][k] / v
            # todo: 获取ET和LT的值
            ET = 8
            LT = 10
            s += (epsilon1 * max(ET - t_jk, 0) + epsilon2 * max(t_jk - LT, 0)) * q_jk[j][k] * chromosome[j]
    return s


if __name__ == '__main__':
    print("hello world")
