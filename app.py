from flask import Flask, render_template, jsonify, request
from datetime import datetime
import threading
import time

app = Flask(__name__)

# 全局变量存储直播数据
stream_data = {
    'current_viewers': 0,
    'total_viewers': 0,
    'total_likes': 0,
    'total_shares': 0,
    'total_follows': 0,
    'total_gifts': 0,
    'is_live': False,
    'start_time': None,
    'gifts': [],
    'comments': []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_summary')
def get_summary():
    return jsonify({
        'current_viewers': stream_data['current_viewers'],
        'total_viewers': stream_data['total_viewers'],
        'total_likes': stream_data['total_likes'],
        'total_shares': stream_data['total_shares'],
        'total_follows': stream_data['total_follows'],
        'total_gifts': stream_data['total_gifts'],
        'is_live': stream_data['is_live'],
        'start_time': stream_data['start_time']
    })

@app.route('/get_stream_data')
def get_stream_data():
    return jsonify({
        'gifts': stream_data['gifts'],
        'comments': stream_data['comments']
    })

@app.route('/update_stream_data', methods=['POST'])
def update_stream_data():
    data = request.json
    stream_data['current_viewers'] = data.get('current_viewers', 0)
    stream_data['total_viewers'] = data.get('total_viewers', 0)
    stream_data['total_likes'] = data.get('total_likes', 0)
    stream_data['total_shares'] = data.get('total_shares', 0)
    stream_data['total_follows'] = data.get('total_follows', 0)
    stream_data['total_gifts'] = data.get('total_gifts', 0)
    stream_data['is_live'] = data.get('is_live', False)
    
    if data.get('is_live') and not stream_data['start_time']:
        stream_data['start_time'] = datetime.now().isoformat()
    elif not data.get('is_live'):
        stream_data['start_time'] = None
    
    return jsonify({'status': 'success'})

@app.route('/add_gift', methods=['POST'])
def add_gift():
    gift_data = request.json
    stream_data['gifts'].append({
        'user': gift_data['user'],
        'gift_name': gift_data['gift_name'],
        'gift_count': gift_data['gift_count'],
        'timestamp': datetime.now().isoformat()
    })
    # 只保留最近100条记录
    if len(stream_data['gifts']) > 100:
        stream_data['gifts'] = stream_data['gifts'][-100:]
    return jsonify({'status': 'success'})

@app.route('/add_comment', methods=['POST'])
def add_comment():
    comment_data = request.json
    stream_data['comments'].append({
        'user': comment_data['user'],
        'comment': comment_data['comment'],
        'timestamp': datetime.now().isoformat()
    })
    # 只保留最近100条记录
    if len(stream_data['comments']) > 100:
        stream_data['comments'] = stream_data['comments'][-100:]
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True) 