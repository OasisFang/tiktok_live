import logging
from flask import Flask, render_template, jsonify, request
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, GiftEvent, LikeEvent, ShareEvent, FollowEvent
import threading
import json
from datetime import datetime
import os
import asyncio

# 创建Flask应用
app = Flask(__name__)

# 禁用Flask开发日志输出
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 初始化TikTok客户端
client = TikTokLiveClient(
    unique_id="@username",  # 替换为要监控的用户名
    **({"process_initial_data": True})
)

# 全局变量存储直播数据
stream_data = {
    "current_viewers": 0,
    "total_viewers": 0,
    "gifts": [],
    "comments": [],
    "likes": 0,
    "shares": 0,
    "follows": 0,
    "start_time": None,
    "is_live": False
}

# 创建数据目录
if not os.path.exists('data'):
    os.makedirs('data')

def save_data():
    """保存直播数据到JSON文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/stream_data_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(stream_data, f, ensure_ascii=False, indent=2)

@client.on("connect")
async def on_connect(_):
    print("已连接到直播间")
    stream_data["start_time"] = datetime.now().isoformat()
    stream_data["is_live"] = True
    save_data()

@client.on("disconnect")
async def on_disconnect(_):
    print("与直播间断开连接")
    stream_data["is_live"] = False
    save_data()

@client.on("viewer_count")
async def on_viewer_count(event):
    stream_data["current_viewers"] = event.viewer_count
    stream_data["total_viewers"] += 1
    save_data()

@client.on("like")
async def on_like(event: LikeEvent):
    stream_data["likes"] += event.like_count
    save_data()

@client.on("share")
async def on_share(event: ShareEvent):
    stream_data["shares"] += 1
    save_data()

@client.on("follow")
async def on_follow(event: FollowEvent):
    stream_data["follows"] += 1
    save_data()

@client.on("gift")
async def on_gift(event: GiftEvent):
    gift_info = {
        "user": event.user.nickname,
        "gift_name": event.gift.info.name,
        "gift_count": event.gift.count,
        "gift_value": event.gift.diamond_count,
        "timestamp": datetime.now().isoformat()
    }
    stream_data["gifts"].append(gift_info)
    save_data()

@client.on("comment")
async def on_comment(event: CommentEvent):
    comment_info = {
        "user": event.user.nickname,
        "comment": event.comment,
        "timestamp": datetime.now().isoformat()
    }
    stream_data["comments"].append(comment_info)
    save_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stream_data')
def get_stream_data():
    """返回当前直播数据"""
    return jsonify(stream_data)

@app.route('/get_summary')
def get_summary():
    """返回直播数据摘要"""
    summary = {
        "current_viewers": stream_data["current_viewers"],
        "total_viewers": stream_data["total_viewers"],
        "total_gifts": len(stream_data["gifts"]),
        "total_comments": len(stream_data["comments"]),
        "total_likes": stream_data["likes"],
        "total_shares": stream_data["shares"],
        "total_follows": stream_data["follows"],
        "is_live": stream_data["is_live"],
        "start_time": stream_data["start_time"]
    }
    return jsonify(summary)

def start_flask():
    app.run(port=5000)

if __name__ == '__main__':
    # 启动Flask应用
    threading.Thread(target=start_flask).start()
    
    # 设置日志级别并运行TikTok客户端
    client.logger.setLevel(logging.INFO)
    asyncio.run(client.start()) 