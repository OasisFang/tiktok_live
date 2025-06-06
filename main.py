import subprocess
import sys
import threading
import signal
import os
from flask import Flask, render_template, jsonify, request
from datetime import datetime

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
    'comments': [],
    'room_info': {}  # 添加房间信息
}
monitor_proc = None

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
        'start_time': stream_data['start_time'],
        'room_info': stream_data['room_info']  # 添加房间信息
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
    for key in ['current_viewers', 'total_viewers', 'total_likes', 'total_shares', 
                'total_follows', 'total_gifts', 'is_live', 'start_time', 'room_info']:
        if key in data:
            stream_data[key] = data[key]
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
    stream_data['total_gifts'] += gift_data.get('gift_count', 1)
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
    if len(stream_data['comments']) > 100:
        stream_data['comments'] = stream_data['comments'][-100:]
    return jsonify({'status': 'success'})

@app.route('/start_monitor', methods=['POST'])
def start_monitor():
    global monitor_proc
    data = request.json
    room_id = data.get('room_id')
    if not room_id:
        return jsonify({'status': 'error', 'message': '缺少房间ID参数'}), 400
    
    # 停止已有监控进程
    stop_monitor_process()
    
    # 启动新的监控进程
    monitor_proc = subprocess.Popen([sys.executable, 'monitor.py', room_id])
    print(f"已启动子进程监控房间: {room_id}，进程ID: {monitor_proc.pid}")
    
    return jsonify({'status': 'success'})

@app.route('/stop_monitor', methods=['POST'])
def stop_monitor():
    """停止当前监控进程"""
    if stop_monitor_process():
        return jsonify({'status': 'success', 'message': '监控已停止'})
    return jsonify({'status': 'success', 'message': '没有正在运行的监控'})

def stop_monitor_process():
    """停止监控进程的辅助函数"""
    global monitor_proc
    if monitor_proc and monitor_proc.poll() is None:
        # 在Windows上使用taskkill，在Unix上使用kill
        try:
            if os.name == 'nt':  # Windows
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(monitor_proc.pid)])
            else:  # Unix
                os.kill(monitor_proc.pid, signal.SIGTERM)
            monitor_proc.wait(timeout=5)  # 等待进程结束
            print(f"已终止监控进程 {monitor_proc.pid}")
        except Exception as e:
            print(f"终止进程失败: {e}")
        monitor_proc = None
        return True
    return False

if __name__ == '__main__':
    # 确保程序退出时关闭子进程
    import atexit
    atexit.register(stop_monitor_process)
    
    # 正常启动网页服务
    print("启动 TikTok Live 监控服务，请访问 http://localhost:5000/")
    app.run(debug=True) 