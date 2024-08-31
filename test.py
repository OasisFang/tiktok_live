import logging
from flask import Flask, render_template, jsonify
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, GiftEvent
from pyngrok import ngrok
import threading

# 创建 Flask 应用实例
app = Flask(__name__, template_folder='/content/templates')

# 禁用 Flask 的开发日志输出
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 初始化 TikTok 客户端
client: TikTokLiveClient = TikTokLiveClient(unique_id="@rr30678")

# 用于存储最新礼物事件的全局变量
latest_gift_info = []

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    client.logger.info("Received a gift!")
    
    gift_message = ""

    if event.gift.streakable and not event.streaking:
        gift_message = f"{event.user.unique_id} 送出了 {event.repeat_count}x \"{event.gift.name}\""
    elif not event.gift.streakable:
        gift_message = f"{event.user.unique_id} 送出了 \"{event.gift.name}\""
    
    if gift_message:
        latest_gift_info.append(gift_message)
        print(f"最新礼物信息: {latest_gift_info[-1]}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_gift_info')
def get_gift_info():
    return jsonify(latest_gift_info[-10:])

def start_ngrok():
    public_url = ngrok.connect(5000)
    print(f"ngrok 公共URL: {public_url}")

def start_flask():
    app.run()

if __name__ == '__main__':
    # 启动 ngrok 隧道和 Flask 应用
    threading.Thread(target=start_ngrok).start()
    threading.Thread(target=start_flask).start()
    
    # 设置日志级别并运行 TikTok 客户端
    client.logger.setLevel(LogLevel.INFO.value)
    client.run()
