import pandas as pd
import json
from datetime import datetime

def clean_data(df):
    # 1. 删除重复行
    df = df.drop_duplicates()
    
    # 2. 清理单价数据
    # 先移除可能存在的单位
    df['unit_price'] = df['unit_price'].astype(str).str.replace('元/m²', '').str.replace('元/㎡', '')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    # 添加单位
    df['unit_price_with_unit'] = df['unit_price'].astype(str) + '元/m²'
    
    # 3. 清理面积数据
    df['area'] = df['area'].str.replace('㎡', '').astype(float)
    
    # 4. 清理建造年份
    df['build_year'] = df['build_year'].str.extract('(\d{4})').astype(float)
    
    # 5. 清理总价数据
    # 先移除可能存在的单位
    df['total_price'] = df['total_price'].str.extract('(\d+\.?\d*)').astype(float)
    # 添加单位
    df['total_price_with_unit'] = df['total_price'].astype(str) + '万元'
    
    # 6. 处理缺失值
    df = df.dropna(subset=['unit_price', 'area', 'total_price'])
    
    # 7. 异常值处理
    Q1 = df['unit_price'].quantile(0.25)
    Q3 = df['unit_price'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['unit_price'] < (Q1 - 1.5 * IQR)) | (df['unit_price'] > (Q3 + 1.5 * IQR)))]
    
    # 8. 标准化区域名称
    df['district'] = df['district'].str.replace('区$', '')
    
    # 9. 添加建筑年龄
    current_year = datetime.now().year
    df['building_age'] = current_year - df['build_year']
    
    # 10. 数据验证
    calculated_total = df['unit_price'] * df['area'] / 10000
    df['price_difference'] = abs(calculated_total - df['total_price'])
    df = df[df['price_difference'] < df['total_price'] * 0.2]
    
    return df

if __name__ == "__main__":
    # 读取原始数据
    with open('anjuke_data_20250113_154904.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为DataFrame
    df = pd.DataFrame(data)
    
    # 清理数据
    df_cleaned = clean_data(df)
    
    # 打印清理报告
    print("数据清理报告:")
    print(f"原始数据行数: {len(df)}")
    print(f"清理后数据行数: {len(df_cleaned)}")
    print("\n缺失值统计:")
    print(df_cleaned.isnull().sum())
    print("\n基本统计信息:")
    print(df_cleaned.describe())
    
    # 保存清理后的数据 - 添加编码声明
    df_cleaned.to_csv('anjuke_data_cleaned.csv', index=False, encoding='utf_8_sig') 