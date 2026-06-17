#!/usr/bin/env python3
"""
微信公众号文章抓取器 — 绕过环境验证

当 r.jina.ai / markdown.new 被微信403时，
直接用HTTP请求 + Accept-Encoding: identity 绕过gzip，
然后从HTML中提取 #js_content 区域。

用法:
    python weixin_fetch.py <URL>

示例:
    python weixin_fetch.py https://mp.weixin.qq.com/s/xxxx
"""
import urllib.request
import ssl
import re
import sys
import gzip

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def fetch_weixin_article(url: str) -> str:
    """抓取微信公众号文章正文。"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; SM-S918B) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/120.0.6099.43 Mobile Safari/537.36 '
                       'MicroMessenger/8.0.47',
        'Accept': 'text/html',
        'Accept-Encoding': 'identity',  # 关键：不要gzip
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=20, context=ssl_context)
    raw = resp.read()

    # 尝试解压gzip
    try:
        html = gzip.decompress(raw).decode('utf-8', errors='ignore')
    except Exception:
        html = raw.decode('utf-8', errors='ignore')

    # 检查是否被验证挡
    if '环境异常' in html or '验证' in html:
        return f"ERROR:微信环境异常验证 - {url}"

    # 提取正文
    match = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
    if not match:
        return f"ERROR:未找到正文区域 - {url}"

    content = match.group(1)
    # 去掉HTML标签
    text = re.sub(r'<[^>]+>', '\n', content)
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python weixin_fetch.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    result = fetch_weixin_article(url)

    if result.startswith('ERROR:'):
        print(f"ERROR: {result}")
        sys.exit(1)

    print(result)
