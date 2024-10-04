import asyncio
import psutil
import websockets

# 監視したいインターフェース名を指定
target_interface = "イーサネット"

# ネットワークの通信量を取得する関数
def get_network_usage():
    return psutil.net_io_counters(pernic=True)

async def send_network_usage(websocket, path):
    prev_stats = get_network_usage()
    
    while True:
        await asyncio.sleep(1)  # 1秒ごとに取得

        # 現在のネットワーク通信量を取得
        current_stats = get_network_usage()

        if target_interface in current_stats:
            # 送受信の差分を計算 (バイト)
            sent_diff = current_stats[target_interface].bytes_sent - prev_stats[target_interface].bytes_sent
            recv_diff = current_stats[target_interface].bytes_recv - prev_stats[target_interface].bytes_recv

            # バイトをビットに変換し、Mbpsに換算
            sent_mbps = (sent_diff * 8) / (1024 * 1024)
            recv_mbps = (recv_diff * 8) / (1024 * 1024)

            # クライアントに送信
            data = {
                'upload': sent_mbps,
                'download': recv_mbps
            }
            await websocket.send(f"{data['upload']:.2f},{data['download']:.2f}")
        
        # 次の計算のために現在のデータを保存
        prev_stats = current_stats

# WebSocketサーバーの起動
start_server = websockets.serve(send_network_usage, "0.0.0.0", 8765)

# イベントループを開始
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
