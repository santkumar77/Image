from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


SYSTEM_PROMPT = """You are an elite visual artist and image prompt engineer.
When given a concept or idea, generate ONE extraordinary, richly detailed image prompt.
Include: subject details, lighting, atmosphere, color palette, composition, camera/lens style, and art style.
Output ONLY the prompt (150-200 words). No preamble, no labels, no explanations."""


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except Exception:
            self._error(400, "Invalid JSON body")
            return

        prompt = body.get("prompt", "").strip()
        style = body.get("style", "Photorealistic")
        mood = body.get("mood", "Cinematic")

        if not prompt:
            self._error(400, "prompt is required")
            return

        api_key = os.environ.get("NVIDIA_API_KEY", "")
        if not api_key:
            self._error(500, "NVIDIA_API_KEY not configured")
            return

        user_msg = f"Concept: {prompt}\nArt style: {style}\nMood/atmosphere: {mood}"

        payload = json.dumps({
            "model": "google/gemma-4-31b-it",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "max_tokens": 512,
            "temperature": 1.0,
            "top_p": 0.95,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8")
            self._error(e.code, f"NVIDIA API error: {detail}")
            return
        except Exception as e:
            self._error(502, f"Upstream error: {str(e)}")
            return

        result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})

        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"result": result, "usage": usage}).encode())

    def _error(self, code, msg):
        self.send_response(code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode())

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        pass  # suppress default logging
