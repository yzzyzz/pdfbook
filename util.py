def genNumberSeqByA4Page(m):
    """
    生成A4纸张的页面排列顺序
    
    输入：A4纸张数量 m
    逻辑：m张A4纸张横向叠放后对折，形成一个A5大小的册子
    每张A4纸包含4个A5页面，总共 4*m 个页面
    输出：按照册子翻阅顺序 1->4*m 的页面在A4纸上的排列顺序
    
    示例：
    1张纸：4-1-2-3
    2张纸：8-1-2-7, 6-3-4-5
    
    参数:
        m (int): A4纸张数量
    
    返回:
        list: 每张A4纸上的4个页面编号列表
    """
    if m <= 0:
        return []
    
    total_pages = 4 * m  # 总页面数
    result = []
    
    # 对于每张A4纸
    for sheet in range(m):
        # 计算当前sheet的4个页面编号
        # 按照书籍折页的规律：
        # 第1张纸：背面外侧(4), 正面外侧(1), 正面内侧(2), 背面内侧(3)
        # 第2张纸：背面外侧(8), 正面外侧(5), 正面内侧(6), 背面内侧(7)
        
        # 背面外侧（从后往前数）
        back_outside = total_pages - sheet * 2
        # 正面外侧（从前往后数）
        front_outside = sheet * 2 + 1
        # 正面内侧
        front_inside = sheet * 2 + 2
        # 背面内侧（从后往前数）
        back_inside = total_pages - sheet * 2 - 1
        
        # A4纸上的页面顺序：背面外侧, 正面外侧, 正面内侧, 背面内侧
        sheet_pages = [back_outside, front_outside, front_inside, back_inside]
        result.append(sheet_pages)
    
    return result

# 测试函数
if __name__ == "__main__":
    # 测试1张纸的情况
    print("1张纸:", genNumberSeqByA4Page(1))  # 应该输出 [[4, 1, 2, 3]]
    
    # 测试2张纸的情况
    print("2张纸:", genNumberSeqByA4Page(2))  # 应该输出 [[8, 1, 2, 7], [6, 3, 4, 5]]
    
    print("6张纸:", genNumberSeqByA4Page(6))  # 应该输出 [[8, 1, 2, 7], [6, 3, 4, 5]]