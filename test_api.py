from fastapi.testclient import TestClient
from api import app, SkillExtraction, compare_skills
from unittest.mock import patch

client=TestClient(app)

def test_analyze_success():
    response=client.post(
        "/analyze",
        json={
            "resume_text": "我掌握 Python、FastAPI 和 SQLite",
            "job_description": "招聘要求 Python、FastAPI 和大模型 API 调用经验"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "suggestions" in data
    assert set(data["matched_skills"]) == {"Python", "FastAPI"}




def test_analyze_missing_job_description():
    response = client.post(
        "/analyze",
        json={
            "resume_text": "我掌握 Python 和 FastAPI"
        }
    )

    assert response.status_code == 422


def test_analyze_invalid_type():
    response = client.post(
        "/analyze",
        json={
            "resume_text": 123,
            "job_description": "招聘 Python 开发工程师"
        }
    )

    assert response.status_code == 422


def test_compare_skills():
    sample = SkillExtraction(
        required_skills=["Python", "FastAPI", "RAG"],
        resume_skills=["Python", "FastAPI", "SQLite"],
        evidence=["完成过库存管理 API 项目"]
    )

    result = compare_skills(sample)

    assert result["matched_skills"] == ["FastAPI", "Python"]
    assert result["missing_skills"] == ["RAG"]
    assert result["suggestions"] == ["补充学习或项目实践：RAG"]



def test_analyze_extraction_error():
    with patch(
        "api.extract_skills_mock",
        side_effect=RuntimeError("模拟技能提取失败")
    ):
        response = client.post(
            "/analyze",
            json={
                "resume_text": "我会 Python",
                "job_description": "需要 Python 和 FastAPI"
            }
        )

    assert response.status_code == 502
    assert response.json()["detail"] == "技能提取暂时失败，请稍后重试"
