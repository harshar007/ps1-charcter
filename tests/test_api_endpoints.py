"""
Integration tests for FastAPI endpoints.
"""

import os
import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient

import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "RetroMorph AI" in response.json()["message"]


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["ml_model_loaded"] is True


def test_samples_endpoint():
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.json()
    assert "samples" in data


def test_quality_check_endpoint():
    # Create test JPEG in memory
    img = Image.new("RGB", (512, 512), color=(140, 100, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/check-quality",
        files={"image": ("test.jpg", buf, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "confidence" in data
    assert "features" in data


def test_generate_character_endpoint():
    # Submit generation request
    img = Image.new("RGB", (512, 512), color=(140, 100, 80))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    response = client.post(
        "/api/generate",
        files={"image": ("test_char.jpg", buf, "image/jpeg")},
        data={
            "gender": "female",
            "outfit": "formal",
            "polygon_level": "low",
            "texture_size": "128",
            "pose": "standing"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    job_id = data["job_id"]

    # Poll status
    status_resp = client.get(f"/api/jobs/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["job_id"] == job_id
