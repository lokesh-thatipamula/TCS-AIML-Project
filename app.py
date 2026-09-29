"""
Insurance Automated Risk Profile Summarizer - Web Application & REST API Server.
Zero-dependency implementation utilizing Python standard library (http.server).
"""

import json
import os
import sys
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.risk_agent import RiskAgent
from tests.benchmark import run_benchmark

PORT = int(os.environ.get("PORT", 8080))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

agent = RiskAgent()


class RiskSummarizerHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Concise logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def _send_json(self, status_code: int, data: Any):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_path = self.path.split("?")[0]

        # REST API Routes
        if parsed_path == "/api/health":
            self._send_json(200, {
                "status": "healthy",
                "service": "Insurance Automated Risk Profile Summarizer",
                "version": "1.0.0",
                "engine": "Single-Agent GenAI Synthesis Architecture",
                "sla_target_speed": "< 20.0s",
                "sla_target_accuracy": ">= 85%"
            })
            return

        elif parsed_path == "/api/profiles":
            profiles_file = os.path.join(DATA_DIR, "synthetic_profiles.json")
            if os.path.exists(profiles_file):
                with open(profiles_file, "r", encoding="utf-8") as f:
                    profiles = json.load(f)
                self._send_json(200, profiles)
            else:
                self._send_json(404, {"error": "Profiles file not found."})
            return

        elif parsed_path == "/api/schema":
            schema_file = os.path.join(DATA_DIR, "schema.json")
            if os.path.exists(schema_file):
                with open(schema_file, "r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                self._send_json(200, schema_data)
            else:
                self._send_json(404, {"error": "Schema file not found."})
            return

        # Static Web File Serving
        if parsed_path in ["", "/"]:
            file_name = "index.html"
        else:
            file_name = parsed_path.lstrip("/")

        file_path = os.path.join(STATIC_DIR, file_name)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self._send_json(404, {"error": f"Resource '{parsed_path}' not found."})

    def do_POST(self):
        parsed_path = self.path.split("?")[0]

        if parsed_path == "/api/summarize":
            content_len = int(self.headers.get("Content-Length", 0))
            if content_len == 0:
                self._send_json(400, {"error": "Empty request body. JSON risk profile required."})
                return

            body = self.rfile.read(content_len).decode("utf-8")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError as e:
                self._send_json(400, {"error": f"Invalid JSON payload: {str(e)}"})
                return

            try:
                result = agent.process(payload)
                self._send_json(200, result)
            except Exception as e:
                self._send_json(500, {"error": f"Agent processing failed: {str(e)}"})
            return

        elif parsed_path == "/api/evaluate":
            try:
                benchmark_results = run_benchmark()
                self._send_json(200, benchmark_results)
            except Exception as e:
                self._send_json(500, {"error": f"Benchmark evaluation failed: {str(e)}"})
            return

        self._send_json(404, {"error": f"POST endpoint '{parsed_path}' not found."})


def run_server(port: int = PORT):
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, RiskSummarizerHandler)
    print("=" * 65)
    print(" TCS Technology Day - Insurance Automated Risk Profile Summarizer")
    print("=" * 65)
    print(f" Web UI Dashboard running at : http://localhost:{port}")
    print(f" REST API endpoint           : http://localhost:{port}/api/summarize")
    print(f" Benchmark API endpoint      : http://localhost:{port}/api/evaluate")
    print(f" Health Check endpoint       : http://localhost:{port}/api/health")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
