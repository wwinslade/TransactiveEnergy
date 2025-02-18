import asyncio
import cv2
import numpy as np
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route

class VideoStreamTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return np.array(frame)

async def index(request):
    return HTMLResponse("""
    <html>
    <body>
        <video id="video" autoplay playsinline></video>
        <script>
            const pc = new RTCPeerConnection();
            pc.ontrack = event => {
                document.getElementById("video").srcObject = event.streams[0];
            };
            fetch("/offer").then(response => response.json()).then(offer => {
                pc.setRemoteDescription(offer);
                return pc.createAnswer();
            }).then(answer => {
                pc.setLocalDescription(answer);
                return fetch("/answer", { method: "POST", body: JSON.stringify(answer) });
            });
        </script>
    </body>
    </html>
    """)

routes = [
    Route("/", endpoint=index),
]

app = Starlette(routes=routes)