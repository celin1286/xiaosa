#!/usr/bin/env python3
import json
import time
import os
import requests
import warnings
import re
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

# 站点映射关系
site_mappings = {
    '立播': 'libo',
    '闪电': 'shandian',
    '欧哥': 'ouge',
    '小米': 'xiaomi',
    '多多': 'duoduo',
    '蜡笔': 'labi',
    '至臻': 'zhizhen',
    '木偶': 'mogg',
    '六趣': 'liuqu',
    '虎斑': 'huban',
    '下饭': 'xiafan',
    '玩偶': 'wogg',
    '星剧社': 'star2'
}

buye_mappings = {
    '立播': 'libo',
    '闪电': 'sd',
    '欧哥': 'ouge',
    '小米': 'xmi',
    '多多': 'duo',
    '蜡笔': 'labi',
    '至臻': 'zhiz',
    '木偶': 'muo',
    '六趣': 'liuq',
    '虎斑': 'hub',
    '下饭': 'xiaf',
    '玩偶': 'wogg',
    '星剧社': 'star2'
}

def test_url(url):
    """测试URL是否可用"""
    try:
        response = requests.get(url.strip(), timeout=5, verify=False)
        return response.status_code == 200
    except:
        return False

def get_best_url(urls):
    """从多个URL中选择最佳的一个"""
    if not isinstance(urls, list):
        return urls
    
    if len(urls) == 1:
        return urls[0].strip()
    
    # 每次测试两个链接
    for i in range(0, len(urls), 2):
        test_urls = urls[i:i+2]
        for url in test_urls:
            if test_url(url):
                return url.strip()
    
    return None

def get_star2_real_url(source_url):
    """从源站获取星剧社真实链接"""
    try:
        response = requests.get(source_url, timeout=5, verify=False)
        if response.status_code == 200:
            match = re.search(r'https?://[^"\'\s<>]+?star2\.cn[^"\'\s<>]*', response.text)
            if match:
                real_url = match.group(0).strip()
                print(f"从源站获取到星剧社真实链接: {real_url}")
                return real_url
    except Exception as e:
        print(f"获取星剧社真实链接失败: {str(e)}")
    return None

def process_urls(existing_urls):
    """处理所有URL数据"""
    url_data = {}
    buye_data = {}
    
    try:
        if not os.path.exists('yuan.json'):
            print("yuan.json 文件不存在")
            return False
            
        with open('yuan.json', 'r', encoding='utf-8') as f:
            yuan_data = json.load(f)
            
        # 处理所有站点链接
        base_data = {}
        for cn_name, urls in yuan_data.items():
            if urls:
                if cn_name == '星剧社':
                    # 特殊处理星剧社链接
                    source_url = get_best_url(urls if isinstance(urls, list) else [urls])
                    if source_url:
                        real_url = get_star2_real_url(source_url)
                        if real_url:
                            base_data[cn_name] = real_url
                            print(f"添加 {cn_name} 链接: {real_url}")
                        elif cn_name in site_mappings and site_mappings[cn_name] in existing_urls:
                            base_data[cn_name] = existing_urls[site_mappings[cn_name]]
                            print(f"保持 {cn_name} 原有链接")
                else:
                    # 处理其他站点链接
                    best_url = get_best_url(urls if isinstance(urls, list) else [urls])
                    if best_url:
                        base_data[cn_name] = best_url
                        print(f"添加 {cn_name} 链接: {best_url}")
                    elif cn_name in site_mappings and site_mappings[cn_name] in existing_urls:
                        base_data[cn_name] = existing_urls[site_mappings[cn_name]]
                        print(f"保持 {cn_name} 原有链接")
        
        # 映射到两种格式
        for cn_name, url in base_data.items():
            if cn_name in site_mappings:
                url_data[site_mappings[cn_name]] = url
            if cn_name in buye_mappings:
                buye_data[buye_mappings[cn_name]] = url
        
        if url_data:
            # 保存文件
            with open('url.json', 'w', encoding='utf-8') as f:
                json.dump(url_data, f, ensure_ascii=False, indent=2)
            with open('buye.json', 'w', encoding='utf-8') as f:
                json.dump(buye_data, f, ensure_ascii=False, indent=2)
            print(f"成功更新 url.json 和 buye.json")
            return True
        
        print("没有新的有效数据")
        return False
        
    except Exception as e:
        print(f"处理出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始更新 URL...")
    
    # 读取现有的 url.json
    existing_urls = {}
    try:
        if os.path.exists('url.json'):
            with open('url.json', 'r', encoding='utf-8') as f:
                existing_urls = json.load(f)
    except Exception as e:
        print(f"读取 url.json 失败: {str(e)}")

    # 处理并保存URL
    if process_urls(existing_urls):
        print("更新完成")
    else:
        print("更新失败，保持文件不变")

def get_redirect_data():
    """
    token必须为管理员的token
    查看映射关系：http://ip:port:3000/redirect/?token=abc123
    """
    res = requests.get('http://47.79.86.9:8080/redirect/', params={'token':'cdcd890204'}, timeout=5, verify=False)
    res.raise_for_status()
    return res.json() # data为t4后台配置的重定向数据

def post_redirect_data(data):
    """
    提交数据，data为需要更新的映射关系数据
    """
    res = requests.post('http://47.79.86.9:8080/redirect/', params={'token':'cdcd890204'}, json=data, timeout=5, verify=False)
    res.raise_for_status()
    print("更新t4重定向数据成功！")

if __name__ == "__main__":
    main()
