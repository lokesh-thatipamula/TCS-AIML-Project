"""
Vercel Serverless Entry Point
Insurance Automated Risk Profile Summarizer - Single-Agent GenAI Underwriting System
"""

import json
import os
import sys
import mimetypes

# Ensure the project root is on sys.path so agent/ and data/ are importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent.risk_agent import RiskAgent
from agent.llm_client import LLMClient

STATIC_DIR = os.path.join(ROOT, "static")
DATA_DIR = os.path.join(ROOT, "data")

# Module-level singleton — shared across warm invocations
_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = RiskAgent()
    return _agent


def _send(status, body, content_type="application/json"):
    headers = {
        "Content-Type": content_type,
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return {"statusCode": status, "headers": headers, "body": body}


def _json(status, data):
    return _send(status, json.dumps(data, indent=2))


def handler(request, context=None):
    """Vercel serverless handler — compatible with both legacy dict and new Request formats."""

    method = request.get("method", "GET").upper()
    path = request.get("path", "/").split("?")[0]
    body_raw = request.get("body", "") or ""

    # ─── CORS preflight ────────────────────────────────────────────────────────
    if method == "OPTIONS":
        return _send(204, "", "text/plain")

    # ─── GET routes ────────────────────────────────────────────────────────────
    if method == "GET":
        if path == "/api/health":
            return _json(200, {
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
                    return _json(200, json.load(f))
            return _json(404, {"error": "Profiles file not found."})

        if path == "/api/schema":
            p = os.path.join(DATA_DIR, "schema.json")
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    return _json(200, json.load(f))
            return _json(404, {"error": "Schema file not found."})

        if path == "/api/llm/config":
            status = get_agent().synthesizer.llm_client.get_status()
            return _json(200, status)

        # Serve static files (HTML / CSS / JS)
        if path in ["", "/"]:
            file_name = "index.html"
        else:
            file_name = path.lstrip("/")

        file_path = os.path.join(STATIC_DIR, file_name)
        if os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
            with open(file_path, "rb") as f:
                content = f.read()
            try:
                body = content.decode("utf-8")
                return _send(200, body, content_type)
            except UnicodeDecodeError:
                import base64
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": content_type},
                    "body": base64.b64encode(content).decode("ascii"),
                    "isBase64Encoded": True,
                }

        return _json(404, {"error": f"Not found: {path}"})

    # ─── POST routes ───────────────────────────────────────────────────────────
    if method == "POST":
        if path == "/api/summarize":
            if not body_raw:
                return _json(400, {"error": "Empty request body."})
            try:
                payload = json.loads(body_raw)
            except json.JSONDecodeError as e:
                return _json(400, {"error": f"Invalid JSON: {e}"})
            try:
                result = get_agent().process(payload)
                return _json(200, result)
            except Exception as e:
                return _json(500, {"error": f"Agent failed: {e}"})

        if path == "/api/evaluate":
            try:
                # Run lightweight benchmark inline
                from tests.benchmark import run_benchmark
                results = run_benchmark()
                return _json(200, results)
            except Exception as e:
                return _json(500, {"error": str(e)})

        if path == "/api/llm/config":
            try:
                payload = json.loads(body_raw) if body_raw else {}
                provider = payload.get("provider", "local")
                updated = get_agent().synthesizer.llm_client.update_config(provider, **payload)
                return _json(200, updated)
            except Exception as e:
                return _json(400, {"error": str(e)})

        if path == "/api/llm/test":
            success, msg = get_agent().synthesizer.llm_client.test_connection()
            return _json(200, {
                "success": success,
                "message": msg,
                "provider": get_agent().synthesizer.llm_client.active_provider
            })

        return _json(404, {"error": f"POST endpoint '{path}' not found."})

    return _json(405, {"error": f"Method '{method}' not allowed."})
