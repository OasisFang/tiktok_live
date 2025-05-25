import logging
from flask import Flask, render_template, jsonify, send_from_directory
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.types.events import ConnectEvent, GiftEvent, ViewerCountUpdateEvent  # 导入 ViewerCountUpdateEvent
from pyngrok import ngrok
import threading
import datetime

# 创建 Flask 应用实例
app = Flask(__name__, template_folder='/content/drive/MyDrive/tiktok_live/templates/')

# 禁用 Flask 的开发日志输出
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 初始化 TikTok 客户端
client: TikTokLiveClient = TikTokLiveClient(unique_id="@mpl.id.official")

# 用于存储最新礼物和观众人数的全局变量
latest_data = {
    "viewer_count": 0,
    "gift_info": {}
}

# 处理连接事件
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")

# 处理观众人数更新事件，使用 ViewerCountUpdateEvent 而不是字符串
@client.on(ViewerCountUpdateEvent)
async def on_viewer_count_update(event: ViewerCountUpdateEvent):
    current_time = datetime.datetime.now()
    viewer_count = event.viewerCount

    # 更新最新的观众人数
    latest_data["viewer_count"] = viewer_count
    print(f"{current_time.strftime('%H:%M:%S')}: {viewer_count} 人正在观看")

# 处理礼物事件
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift_message = ""

    if event.gift.streakable and not event.streaking:
        gift_message = f"{event.user.unique_id} ({event.user.nickname}) 送出了 {event.repeat_count}x \"{event.gift.name}\""
        latest_data["gift_info"]["repeat_count"] = event.repeat_count  # 存储连击的次数
    elif not event.gift.streakable:
        gift_message = f"{event.user.unique_id} ({event.user.nickname}) 送出了 \"{event.gift.name}\""
        latest_data["gift_info"]["repeat_count"] = 1  # 非连击礼物默认为1
    
    if gift_message:
        latest_data["gift_info"]["user"] = event.user.nickname  # 使用用户昵称
        latest_data["gift_info"]["gift"] = event.gift.name
        print(f"最新礼物信息: {gift_message}")

# 首页路由，展示静态页面
@app.route('/')
def index():
    return render_template('index.html')

# 获取最新的礼物和观众人数信息
@app.route('/get_latest_data')
def get_latest_data():
    return jsonify(latest_data)

# 提供静态文件
@app.route('/goat.gif')
def serve_gif():
    return send_from_directory('/content/drive/MyDrive/tiktok_live/anime', 'goat.gif')

# 启动 ngrok 隧道
def start_ngrok():
    public_url = ngrok.connect(5000)
    print(f"ngrok 公共URL: {public_url}")

# 启动 Flask 服务
def start_flask():
    app.run(port=5000)

# 主程序入口
if __name__ == '__main__':
    # 启动 ngrok 隧道和 Flask 应用
    threading.Thread(target=start_ngrok).start()
    threading.Thread(target=start_flask).start()
    
    # 设置日志级别并运行 TikTok 客户端
    client.logger.setLevel(LogLevel.INFO.value)
    client.run()
