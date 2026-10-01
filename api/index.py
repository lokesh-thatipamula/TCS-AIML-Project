"""
Vercel Serverless Entry Point — class-based BaseHTTPRequestHandler format
Insurance Automated Risk Profile Summarizer
"""

import json
import os
import sys
import mimetypes
from http.server import BaseHTTPRequestHandler

# Ensure the project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent.risk_agent import RiskAgent

STATIC_DIR = os.path.join(ROOT, "static")
DATA_DIR = os.path.join(ROOT, "data")

_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = RiskAgent()
    return _agent


class handler(BaseHTTPRequestHandler):

    def _cors_headers(self, content_type="application/json"):
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status, data):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self._cors_headers("application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status, body_str, content_type="text/html; charset=utf-8"):
        body = body_str.encode("utf-8") if isinstance(body_str, str) else body_str
        self.send_response(status)
        self._cors_headers(content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers("text/plain")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/api/health":
            return self._send_json(200, {
                "status": "healthy",
                "service": "Insurance Automated Risk Profile Summarizer",
                "version": "1.0.0",
                "engine": "Single-Agent GenAI Architecture",
                "sla_target_speed": "< 20.0s",
                "sla_target_accuracy": ">= 85%"
            })

        if path == "/api/profiles":
            p = os.path.join(DATA_DIR, "synthetic_profiles.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    return self._send_json(200, json.load(f))
            return self._send_json(404, {"error": "Profiles file not found."})

        if path == "/api/schema":
            p = os.path.join(DATA_DIR, "schema.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    return self._send_json(200, json.load(f))
            return self._send_json(404, {"error": "Schema file not found."})

        if path == "/api/llm/config":
            status = get_agent().synthesizer.llm_client.get_status()
            return self._send_json(200, status)

        # Serve static files
        if path in ["", "/"]:
            file_name = "index.html"
        elif path.startswith("/static/"):
            file_name = path[len("/static/"):]
        else:
            file_name = path.lstrip("/")

        file_path = os.path.join(STATIC_DIR, file_name)
        if os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self._cors_headers(content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        return self._send_json(404, {"error": f"Not found: {path}"})

    def do_POST(self):
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode("utf-8") if length else ""

        if path == "/api/summarize":
            if not body_raw:
                return self._send_json(400, {"error": "Empty request body."})
            try:
                payload = json.loads(body_raw)
            except json.JSONDecodeError as e:
                return self._send_json(400, {"error": f"Invalid JSON: {e}"})
            try:
                result = get_agent().process(payload)
                return self._send_json(200, result)
            except Exception as e:
                return self._send_json(500, {"error": f"Agent failed: {e}"})

        if path == "/api/llm/config":
            try:
                payload = json.loads(body_raw) if body_raw else {}
                provider = payload.get("provider", "local")
                updated = get_agent().synthesizer.llm_client.update_config(provider, **payload)
                return self._send_json(200, updated)
            except Exception as e:
                return self._send_json(400, {"error": str(e)})

        if path == "/api/llm/test":
            success, msg = get_agent().synthesizer.llm_client.test_connection()
            return self._send_json(200, {
                "success": success,
                "message": msg,
                "provider": get_agent().synthesizer.llm_client.active_provider
            })

        if path == "/api/evaluate":
            try:
                from tests.benchmark import run_benchmark
                results = run_benchmark()
                return self._send_json(200, results)
            except Exception as e:
                return self._send_json(500, {"error": str(e)})

        return self._send_json(404, {"error": f"POST endpoint '{path}' not found."})
