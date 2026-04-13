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
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            body = json.loads(raw)
        except Exception as e:
            return self._json(400, {"error": f"Invalid JSON body: {e}"})

        prompt = body.get("prompt", "").strip()
        style  = body.get("style", "Photorealistic")
        mood   = body.get("mood", "Cinematic")

        if not prompt:
            return self._json(400, {"error": "prompt is required"})

        api_key = os.environ.get("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", "")
        if not api_key:
            return self._json(500, {"error": "NVIDIA_API_KEY environment variable is not set"})

        user_msg = f"Concept: {prompt}\nArt style: {style}\nMood/atmosphere: {mood}"

        payload = json.dumps({
            "model": "google/gemma-4-31b-it",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
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
                "Content-Type":  "application/json",
                "Accept":        "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8")
            return self._json(e.code, {"error": f"NVIDIA API error: {detail}"})
        except Exception as e:
            return self._json(502, {"error": f"Upstream error: {str(e)}"})

        result = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage  = data.get("usage", {})
        return self._json(200, {"result": result, "usage": usage})

    def _json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, *args):
        pass
