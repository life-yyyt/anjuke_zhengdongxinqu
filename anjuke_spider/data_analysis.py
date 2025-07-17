import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
from matplotlib.font_manager import FontProperties

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']  # 添加多个字体选项
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('seaborn-v0_8')

# 尝试加载中文字体
try:
    font = FontProperties(fname=r"C:\Windows\Fonts\SimHei.ttf")  # Windows系统中的黑体字体
except:
    try:
        font = FontProperties(fname=r"C:\Windows\Fonts\msyh.ttc")  # Windows系统中的雅黑字体
    except:
        font = None

class ZhengdongAnalyzer:
    """郑东新区房价分析器"""
    
    def __init__(self, df):
        self.df = df
        self.zhengdong_df = df[df['district'] == '郑东新区']
        self.font = font
    
    def save_json(self, data, filename):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_plot(self, filename, dpi=300):
        """保存并关闭图表"""
        # 设置所有文字的字体
        if self.font:
            for text in plt.gca().texts + [plt.gca().title] + \
                       [plt.gca().xaxis.label] + [plt.gca().yaxis.label]:
                text.set_fontproperties(self.font)
            
            # 设置刻度标签的字体
            plt.gca().tick_params(labelsize=10)
            for label in plt.gca().get_xticklabels() + plt.gca().get_yticklabels():
                label.set_fontproperties(self.font)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        plt.close()
    
    def _set_plot_font(self, title, xlabel=None, ylabel=None):
        """设置图表字体"""
        if self.font:
            plt.title(title, fontproperties=self.font)
            if xlabel:
                plt.xlabel(xlabel, fontproperties=self.font)
            if ylabel:
                plt.ylabel(ylabel, fontproperties=self.font)
    
    def analyze_communities(self):
        """分析小区房价排名和统计概况"""
        # 计算小区统计信息
        stats = self.zhengdong_df.groupby('community').agg({
            'unit_price': ['mean', 'count', 'min', 'max', 'std'],
            'total_price': 'mean',
            'area': 'mean'
        }).round(2)
        
        stats.columns = ['avg_price', 'house_count', 'min_price', 'max_price', 
                        'price_std', 'avg_total_price', 'avg_area']
        stats = stats.sort_values('avg_price', ascending=False)
        
        # 生成分析结果
        result = {
            "统计概况": {
                "小区总数": len(stats),
                "最贵小区": self._get_community_info(stats.iloc[0]),
                "最便宜小区": self._get_community_info(stats.iloc[-1])
            },
            "房价排名": {
                community: self._get_community_info(row)
                for community, row in stats.iterrows()
            }
        }
        
        self.save_json(result, 'zhengdong_analysis_summary.json')
        return result
    
    def _get_community_info(self, row):
        """生成小区信息字典"""
        return {
            "名称": row.name,
            "平均单价": f"{row['avg_price']}元/m²",
            "最低单价": f"{row['min_price']}元/m²",
            "最高单价": f"{row['max_price']}元/m²",
            "价格标准差": f"{row['price_std']}元/m²",
            "平均总价": f"{row['avg_total_price']}万元",
            "平均面积": f"{row['avg_area']}m²",
            "房源数量": int(row['house_count'])
        }
    
    def analyze_age_impact(self):
        """分析建造时间对房价的影响"""
        valid_data = self.zhengdong_df.dropna(subset=['build_year', 'unit_price'])
        
        # 创建年龄分组
        age_ranges = pd.cut(valid_data['building_age'], 
                          bins=[-np.inf, 5, 10, 15, 20, np.inf],
                          labels=['5年内', '5-10年', '10-15年', '15-20年', '20年以上'])
        
        # 计算年龄段统计
        age_stats = valid_data.groupby(age_ranges).agg({
            'unit_price': ['mean', 'count', 'std', 'min', 'max'],
            'total_price': ['mean', 'min', 'max'],
            'area': 'mean'
        }).round(2)
        
        # 生成分析结果
        result = self._format_age_stats(age_stats)
        self.save_json(result, 'zhengdong_age_analysis.json')
        
        # 绘制年龄相关图表
        self._plot_age_price_relation(valid_data, age_ranges)
        
        return result
    
    def _format_age_stats(self, stats):
        """格式化年龄统计数据"""
        stats.columns = ['avg_price', 'house_count', 'price_std', 'min_price', 'max_price',
                        'avg_total_price', 'min_total_price', 'max_total_price', 'avg_area']
        return {
            age: {
                "平均单价": f"{stats.loc[age, 'avg_price']}元/m²",
                "价格标准差": f"{stats.loc[age, 'price_std']}元/m²",
                "最低单价": f"{stats.loc[age, 'min_price']}元/m²",
                "最高单价": f"{stats.loc[age, 'max_price']}元/m²",
                "平均总价": f"{stats.loc[age, 'avg_total_price']}万元",
                "最低总价": f"{stats.loc[age, 'min_total_price']}万元",
                "最高总价": f"{stats.loc[age, 'max_total_price']}万元",
                "平均面积": f"{stats.loc[age, 'avg_area']}m²",
                "房源数量": int(stats.loc[age, 'house_count'])
            }
            for age in stats.index
        }
    
    def create_visualizations(self):
        """创建所有可视化图表"""
        self._plot_price_distribution()
        self._plot_area_price_relation()
        self._plot_total_price_distribution()
        self._plot_area_distribution()
        self._plot_build_year_distribution()
        self._plot_price_trends()
    
    def _plot_price_distribution(self):
        """绘制房价分布饼图"""
        plt.figure(figsize=(10, 8))
        price_ranges = pd.cut(self.zhengdong_df['unit_price'], 
                            bins=[0, 10000, 15000, 20000, 25000, float('inf')],
                            labels=['1万以下', '1-1.5万', '1.5-2万', '2-2.5万', '2.5万以上'])
        price_dist = price_ranges.value_counts()
        
        # 绘制饼图
        patches, texts, autotexts = plt.pie(price_dist, labels=price_dist.index, 
                                          autopct='%1.1f%%', textprops={'fontproperties': self.font})
        
        self._set_plot_font('郑东新区房价区间分布')
        self.save_plot('zhengdong_price_distribution_pie.png')
    
    def _plot_area_price_relation(self):
        """绘制面积与房价关系图"""
        plt.figure(figsize=(12, 8))
        plt.scatter(self.zhengdong_df['area'], self.zhengdong_df['unit_price'], alpha=0.5)
        
        # 添加趋势线
        z = np.polyfit(self.zhengdong_df['area'], self.zhengdong_df['unit_price'], 1)
        p = np.poly1d(z)
        plt.plot(self.zhengdong_df['area'], p(self.zhengdong_df['area']), "r--", alpha=0.8)
        
        self._set_plot_font('郑东新区面积与单价关系', 
                           '面积(平方米)', 
                           '单价(元/平方米)')
        self.save_plot('zhengdong_area_price_scatter.png')
    
    def _plot_total_price_distribution(self):
        """绘制总价分布直方图"""
        plt.figure(figsize=(12, 8))
        plt.hist(self.zhengdong_df['total_price'], bins=30, edgecolor='black')
        plt.title('郑东新区房屋总价分布')
        plt.xlabel('总价(万元)')
        plt.ylabel('数量')
        self.save_plot('zhengdong_total_price_hist.png')
    
    def _plot_area_distribution(self):
        """绘制面积分布饼图"""
        plt.figure(figsize=(10, 8))
        area_ranges = pd.cut(self.zhengdong_df['area'], 
                           bins=[0, 90, 120, 150, 200, float('inf')],
                           labels=['90㎡以下', '90-120㎡', '120-150㎡', '150-200㎡', '200㎡以上'])
        area_dist = area_ranges.value_counts()
        plt.pie(area_dist, labels=area_dist.index, autopct='%1.1f%%')
        plt.title('郑东新区房屋面积分布')
        self.save_plot('zhengdong_area_distribution_pie.png')
    
    def _plot_build_year_distribution(self):
        """绘制建造年份分布图"""
        plt.figure(figsize=(12, 6))
        valid_years = self.zhengdong_df['build_year'].dropna()
        plt.hist(valid_years, bins=20, edgecolor='black')
        plt.title('郑东新区房屋建造年份分布')
        plt.xlabel('建造年份')
        plt.ylabel('数量')
        plt.xticks(rotation=45)
        self.save_plot('zhengdong_build_year_hist.png')
    
    def _plot_age_price_relation(self, valid_data, age_ranges):
        """绘制房龄与价格关系图"""
        plt.figure(figsize=(12, 8))
        sns.boxplot(x=age_ranges, y=valid_data['unit_price'])
        plt.title('郑东新区不同房龄价格分布')
        plt.xlabel('房屋年龄')
        plt.ylabel('单价(元/平方米)')
        plt.xticks(rotation=45)
        self.save_plot('zhengdong_age_price_box.png')
    
    def _plot_price_trends(self):
        """绘制房价趋势折线图"""
        # 1. 按建造年份的房价趋势
        year_stats = self.zhengdong_df.groupby('build_year').agg({
            'unit_price': ['mean', 'count'],
            'total_price': 'mean'
        }).round(2)
        
        year_stats.columns = ['avg_price', 'house_count', 'avg_total_price']
        year_stats = year_stats.sort_index()
        
        # 创建双轴图表
        fig, ax1 = plt.subplots(figsize=(15, 8))
        ax2 = ax1.twinx()
        
        # 绘制平均单价折线（主坐标轴）
        line1 = ax1.plot(year_stats.index, year_stats['avg_price'], 
                        'b-', label='平均单价', linewidth=2, marker='o')
        
        # 设置主坐标轴标签
        if self.font:
            ax1.set_xlabel('建造年份', fontproperties=self.font)
            ax1.set_ylabel('平均单价(元/平方米)', color='b', fontproperties=self.font)
        else:
            ax1.set_xlabel('建造年份')
            ax1.set_ylabel('平均单价(元/平方米)', color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        
        # 绘制房源数量柱状图（次坐标轴）
        bars = ax2.bar(year_stats.index, year_stats['house_count'], 
                      alpha=0.3, color='gray', label='房源数量')
        
        # 设置次坐标轴标签
        if self.font:
            ax2.set_ylabel('房源数量(套)', color='gray', fontproperties=self.font)
            plt.title('郑东新区房价趋势(按建造年份)', fontproperties=self.font)
        else:
            ax2.set_ylabel('房源数量(套)', color='gray')
            plt.title('郑东新区房价趋势(按建造年份)')
        ax2.tick_params(axis='y', labelcolor='gray')
        
        # 设置图例
        lines = line1 + [bars]
        labels = [l.get_label() for l in lines]
        if self.font:
            ax1.legend(lines, labels, loc='upper left', prop=self.font)
        else:
            ax1.legend(lines, labels, loc='upper left')
        
        # 设置x轴标签旋转
        plt.xticks(year_stats.index, rotation=45)
        
        # 保存趋势图
        plt.tight_layout()
        self.save_plot('zhengdong_price_trend_by_year.png')
        plt.close()
        
        # 2. 按小区均价排名的前20名趋势
        community_stats = self.zhengdong_df.groupby('community')['unit_price'].mean().sort_values(ascending=False)
        top20_communities = community_stats.head(20)
        
        # 创建新的图表
        plt.figure(figsize=(15, 8))
        bars = plt.bar(range(len(top20_communities)), top20_communities.values)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', rotation=0)
        
        plt.xticks(range(len(top20_communities)), top20_communities.index, rotation=45, ha='right')
        
        self._set_plot_font('郑东新区房价最高的20个小区',
                            '小区名称',
                            '平均单价(元/平方米)')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        self.save_plot('zhengdong_top20_communities_price.png')
        plt.close()

def main():
    # 读取数据
    df = pd.read_csv('anjuke_data_cleaned.csv')
    
    # 创建分析器实例
    analyzer = ZhengdongAnalyzer(df)
    
    # 执行分析
    analyzer.analyze_communities()
    analyzer.analyze_age_impact()
    analyzer.create_visualizations()

if __name__ == "__main__":
    main() 