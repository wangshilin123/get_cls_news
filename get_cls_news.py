import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def get_cls_telegraph():
    """获取财联社电报内容"""
    url = "https://www.cls.cn/nodeapi/telegraphList"
    
    # 定义请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=utf-8',
        'Referer': 'https://www.cls.cn/telegraph',
        'Origin': 'https://www.cls.cn',
        'Host': 'www.cls.cn'
    }
    
    # 构建请求参数
    params = {
        'app': 'CailianpressWeb',
        'os': 'web',
        'sv': '8.4.6',
        'sign': '7fbe61b974fb82107a9f9c5872bd2800',
        'rn': '20',  # 修改为只获取20条
        'hasFirstVipArticle': '1'
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(
            url, 
            params=params,
            timeout=10,
            verify=True
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求出错: {e}")
        return None

def format_telegraph_data(data, show_latest_only=False):
    """
    格式化输出电报数据
    show_latest_only: 是否只显示最新一条
    """
    if not data or 'data' not in data or 'roll_data' not in data['data']:
        print("没有获取到有效数据")
        return
    
    telegraphs = data['data']['roll_data']
    if not telegraphs:
        return
        
    print("\n" + "="*50 + " 财联社电报 " + "="*50)
    
    # 如果只显示最新一条，就只处理第一条数据
    items_to_show = [telegraphs[0]] if show_latest_only else telegraphs
    
    for idx, item in enumerate(items_to_show, 1):
        # 转换时间戳为可读格式
        timestamp = item.get('ctime', 0)
        date_time = datetime.fromtimestamp(timestamp)
        formatted_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取重要字段
        title = item.get('title', '')
        content = item.get('content', '无内容')
        category = item.get('category_name', '未分类')
        level = item.get('level', '')
        
        # 格式化输出
        print(f"\n📅 时间: {formatted_time}")
        if title:
            print(f"📌 标题: {title}")
        print(f"📝 内容: {content}")
        print(f"📊 分类: {category}")
        if level:
            print(f"⭐ 重要性: {level}")
        print("-" * 100)

def main():
    print("开始监控财联社电报内容...")
    print("程序将每30秒自动刷新一次")
    print("按 Ctrl+C 可以终止程序")
    
    # 记录上次获取的新闻ID，用于判断是否有新内容
    last_news_id = None
    
    try:
        while True:
            data = get_cls_telegraph()
            
            if data and 'data' in data and 'roll_data' in data['data']:
                telegraphs = data['data']['roll_data']
                
                if telegraphs:
                    # 获取最新新闻的ID
                    current_news_id = telegraphs[0].get('id')
                    
                    # 如果是第一次运行或有新内容，则显示
                    if last_news_id is None or current_news_id != last_news_id:
                        print("\n" + "="*30 + f" 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} " + "="*30)
                        format_telegraph_data(data, show_latest_only=True)  # 只显示最新一条
                        last_news_id = current_news_id
                    else:
                        print(f"\r上次更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 暂无新内容", end='')
            else:
                print("\n获取数据失败")
            
            # 等待30秒
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n程序已终止")
    except Exception as e:
        print(f"\n程序出错: {e}")

if __name__ == "__main__":
    main()
