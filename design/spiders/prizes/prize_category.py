
if __name__ == '__main__':
    import xlrd
    workbook = xlrd.open_workbook('产品CMF(3).xlsx')
    sheet2 = workbook.sheet_by_name('产品分类关联 - IDEA设计奖')
    rows = 2
    category_list = []
    while rows <= sheet2.nrows-1:
        row = sheet2.row_values(rows)  # 获取第n行内容
        if row[0]:
            category = row[0]
        if row[1]:
            category_list.append({
                'name': row[2],
                'tag':row[1],
                'opalus_id':0,
                'category':category
            })
        print(row)
        rows += 1

    print(category_list)
