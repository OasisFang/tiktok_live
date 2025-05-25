import logging
from flask import Flask, render_template, jsonify, send_from_directory
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, GiftEvent
from pyngrok import ngrok
import threading

# Create Flask application instance
app = Flask(__name__, template_folder='/content/drive/MyDrive/tiktok_live/templates/')

# Disable Flask development log output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Initialize TikTok client
client: TikTokLiveClient = TikTokLiveClient(unique_id="@oasis_fang")

# Global variable to store latest gift event
latest_gift_info = {}

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    gift_message = ""

    if event.gift.streakable and not event.streaking:
        gift_message = f"{event.user.unique_id} ({event.user.nickname}) sent {event.repeat_count}x \"{event.gift.name}\""
        latest_gift_info["repeat_count"] = event.repeat_count  # Store streak count
    elif not event.gift.streakable:
        gift_message = f"{event.user.unique_id} ({event.user.nickname}) sent \"{event.gift.name}\""
        latest_gift_info["repeat_count"] = 1  # Non-streakable gifts default to 1
    
    if gift_message:
        latest_gift_info["user"] = event.user.nickname  # Use user nickname
        latest_gift_info["gift"] = event.gift.name
        print(f"Latest gift info: {gift_message}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_gift_info')
def get_gift_info():
    # Return only the latest gift information
    return jsonify(latest_gift_info)

@app.route('/goat.gif')
def serve_gif():
    return send_from_directory('/content/drive/MyDrive/tiktok_live/anime', 'goat.gif')

def start_ngrok():
    public_url = ngrok.connect(5000)
    print(f"ngrok public URL: {public_url}")

def start_flask():
    app.run(port=5000)

if __name__ == '__main__':
    # Start ngrok tunnel and Flask application
    threading.Thread(target=start_ngrok).start()
    threading.Thread(target=start_flask).start()
    
    # Set log level and run TikTok client
    client.logger.setLevel(LogLevel.INFO.value)
    client.run()
