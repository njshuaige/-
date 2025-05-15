# ai_helper.py

def check_winner(grid):
    """
    检查九宫格映射中是否有胜利者
    :param grid: 3x3 的九宫格列表
    :return: 1（玩家1胜利），-1（玩家2胜利），0（无胜利者）
    """
    for row in grid:
        if row[0] == row[1] == row[2] and row[0] != 0:
            return row[0]
    for col in range(3):
        if grid[0][col] == grid[1][col] == grid[2][col] and grid[0][col] != 0:
            return grid[0][col]
    if grid[0][0] == grid[1][1] == grid[2][2] and grid[0][0] != 0:
        return grid[0][0]
    if grid[0][2] == grid[1][1] == grid[2][0] and grid[0][2] != 0:
        return grid[0][2]
    return 0

def help_move(grid, player):
    """
    计算当前棋盘 grid 上 player 的最佳下一步
    :param grid: 3x3 棋盘状态
    :param player: 当前玩家（1 或 -1）
    :return: 推荐落子位置坐标 (i, j)，或 None
    """
    opponent = -player

    # 1. 检查是否能直接赢
    for i in range(3):
        for j in range(3):
            if grid[i][j] == 0:
                grid[i][j] = player
                if check_winner(grid) == player:
                    grid[i][j] = 0
                    return (i, j)
                grid[i][j] = 0

    # 2. 阻止对手赢
    for i in range(3):
        for j in range(3):
            if grid[i][j] == 0:
                grid[i][j] = opponent
                if check_winner(grid) == opponent:
                    grid[i][j] = 0
                    return (i, j)
                grid[i][j] = 0

    # 3. 占据中心
    if grid[1][1] == 0:
        return (1, 1)

    # 4. 占据角落
    for i, j in [(0, 0), (0, 2), (2, 0), (2, 2)]:
        if grid[i][j] == 0:
            return (i, j)

    # 5. 占据边缘
    for i, j in [(0, 1), (1, 0), (1, 2), (2, 1)]:
        if grid[i][j] == 0:
            return (i, j)

