import sys
import requests
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, DisconnectEvent, LikeEvent, JoinEvent, ShareEvent, FollowEvent
from TikTokLive.events import GiftEvent, CommentEvent
from datetime import datetime

if len(sys.argv) < 2:
    print("用法: python monitor.py <room_id>")
    sys.exit(1)
room_id = sys.argv[1]
# 确保 unique_id 带有 '@'
raw_id = room_id if room_id.startswith('@') else '@' + room_id

# 创建 TikTokLive 客户端
client = TikTokLiveClient(
    unique_id=raw_id,
    debug=True  # 启用调试模式，查看更多信息
)
print(f"[monitor.py] 开始监控房间: {raw_id}")

# 统计数据
stats = {
    'current_viewers': 0,
    'total_viewers': 0,
    'likes': 0,
    'shares': 0,
    'follows': 0,
    'room_info': {}
}

def update_summary():
    """更新前端的统计信息"""
    payload = {
        'current_viewers': stats['current_viewers'],
        'total_viewers': stats['total_viewers'],
        'total_likes': stats['likes'],
        'total_shares': stats['shares'],
        'total_follows': stats['follows'],
        'room_info': stats['room_info']
    }
    try:
        requests.post('http://localhost:5000/update_stream_data', json=payload)
    except Exception as e:
        print(f"更新数据失败: {e}")

# 连接事件
@client.on("connect")
async def on_connect(event: ConnectEvent):
    print(f"[monitor.py] 已连接到 {event.unique_id}，房间ID: {client.room_id}")
    
    # 更新房间信息
    stats['room_info'] = {
        'room_id': client.room_id,
        'room_title': getattr(client, 'room_info', {}).get('title', '未知'),
        'host_name': getattr(client, 'room_info', {}).get('owner', {}).get('nickname', '未知'),
        'avatar_url': getattr(client, 'room_info', {}).get('owner', {}).get('avatar_thumb', {}).get('url_list', [''])[0]
    }
    
    # 更新当前观众数
    try:
        stats['current_viewers'] = getattr(client, 'room_info', {}).get('user_count', 0)
    except Exception as e:
        print(f"获取观众数失败: {e}")
    
    # 发送连接状态到前端
    try:
        requests.post('http://localhost:5000/update_stream_data', json={
            'is_live': True, 
            'start_time': datetime.now().isoformat(),
            'room_info': stats['room_info']
        })
    except Exception as e:
        print(f"更新直播状态失败: {e}")

# 断开连接事件
@client.on("disconnect")
async def on_disconnect(event: DisconnectEvent):
    print(f"[monitor.py] 已断开与房间 {client.room_id} 的连接")
    try:
        requests.post('http://localhost:5000/update_stream_data', json={'is_live': False})
    except Exception as e:
        print(f"更新断开连接状态失败: {e}")

# 用户加入事件，更新观众数
@client.on("join")
async def on_join(event: JoinEvent):
    try:
        stats['current_viewers'] += 1
        stats['total_viewers'] += 1
        update_summary()
    except Exception as e:
        print(f"处理加入事件失败: {e}")

# 点赞事件
@client.on("like")
async def on_like(event: LikeEvent):
    try:
        # 在新版本中，可能没有 count 属性，默认按 1 计数
        count = getattr(event, 'count', 1)
        stats['likes'] += count
        update_summary()
    except Exception as e:
        print(f"处理点赞事件失败: {e}, 事件属性: {event.__dict__}")

# 分享事件
@client.on("share")
async def on_share(event: ShareEvent):
    stats['shares'] += 1
    update_summary()

# 关注事件
@client.on("follow")
async def on_follow(event: FollowEvent):
    stats['follows'] += 1
    update_summary()

# 礼物事件
@client.on("gift")
async def on_gift(event: GiftEvent):
    try:
        # 根据官方文档示例处理礼物事件
        gift_info = {
            'user': event.user.nickname,
            'gift_name': event.gift.name,
            'diamonds': event.gift.info.diamond_count * event.gift.count,
            'gift_count': event.gift.count,
            'timestamp': datetime.now().isoformat()
        }
        
        # 处理连击礼物
        if event.gift.streakable and not event.streaking:
            # 礼物连击结束
            print(f"[monitor.py] 礼物: {event.user.nickname} 送出了 {event.gift.count}x {event.gift.name}")
        elif not event.gift.streakable:
            # 非连击礼物
            print(f"[monitor.py] 礼物: {event.user.nickname} 送出了 {event.gift.name}")
        
        requests.post('http://localhost:5000/add_gift', json=gift_info)
    except Exception as e:
        print(f"处理礼物事件失败: {e}, 事件属性: {event.__dict__}")

# 评论事件
@client.on("comment")
async def on_comment(event: CommentEvent):
    try:
        comment_data = {
            'user': event.user.nickname,
            'comment': event.comment,
            'timestamp': datetime.now().isoformat()
        }
        requests.post('http://localhost:5000/add_comment', json=comment_data)
    except Exception as e:
        print(f"处理评论事件失败: {e}")

if __name__ == "__main__":
    # 使用同步方法连接并运行
    client.run() 