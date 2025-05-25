import logging
from flask import Flask, render_template, jsonify, send_from_directory
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, GiftEvent
from pyngrok import ngrok
import threading

# 创建 Flask 应用实例
app = Flask(__name__, template_folder='/content/drive/MyDrive/tiktok_live/templates/')

# 禁用 Flask 的开发日志输出
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 初始化 TikTok 客户端
client: TikTokLiveClient = TikTokLiveClient(unique_id="@realomizu")

# 用于存储最新礼物事件的全局变量
latest_gift_info = {}

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")


# @client.on(GiftEvent)
# async def on_gift(event: GiftEvent):
#     gift_message = ""

#     if event.gift.streakable and not event.streaking:
#         gift_message = f"{event.user.unique_id} 送出了 {event.repeat_count}x \"{event.gift.name}\""
#         latest_gift_info["repeat_count"] = event.repeat_count  # 存储连击的次数
#     elif not event.gift.streakable:
#         gift_message = f"{event.user.unique_id} 送出了 \"{event.gift.name}\""
#         latest_gift_info["repeat_count"] = 1  # 非连击礼物默认为1
    
#     if gift_message:
#         latest_gift_info["user"] = event.user.unique_id
#         latest_gift_info["gift"] = event.gift.name
#         print(f"最新礼物信息: {gift_message}")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift_message = ""

    if event.gift.streakable and not event.streaking:
        gift_message = f"{event.user.unique_id} ({event.user.nickname}) 送出了 {event.repeat_count}x \"{event.gift.name}\""
        latest_gift_info["repeat_count"] = event.repeat_count  # 存储连击的次数
    elif not event.gift.streakable:
        gift_message = f"{event.user.unique_id} ({event.user.nickname}) 送出了 \"{event.gift.name}\""
        latest_gift_info["repeat_count"] = 1  # 非连击礼物默认为1
    
    if gift_message:
        latest_gift_info["user"] = event.user.nickname  # 使用用户昵称
        latest_gift_info["gift"] = event.gift.name
        print(f"最新礼物信息: {gift_message}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_gift_info')
def get_gift_info():
    # 只返回最新的礼物信息
    return jsonify(latest_gift_info)

@app.route('/goat.gif')
def serve_gif():
    return send_from_directory('/content/drive/MyDrive/tiktok_live/anime', 'goat.gif')

def start_ngrok():
    public_url = ngrok.connect(5000)
    print(f"ngrok 公共URL: {public_url}")

def start_flask():
    app.run(port=5000)

if __name__ == '__main__':
    # 启动 ngrok 隧道和 Flask 应用
    threading.Thread(target=start_ngrok).start()
    threading.Thread(target=start_flask).start()
    
    # 设置日志级别并运行 TikTok 客户端
    client.logger.setLevel(LogLevel.INFO.value)
    client.run()
