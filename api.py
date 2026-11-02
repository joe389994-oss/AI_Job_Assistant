from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from models import AnalyzeRequest,AnalyzeResponse,SkillExtraction

app = FastAPI(title="AI 求职助手")



# 模拟大模型提取技能
def extract_skills_mock(resume_text, job_description):
    # 暂时支持识别的技能关键词
    skill_library = [
        "Python",
        "FastAPI",
        "SQLite",
        "RAG",
        "大模型 API 调用"
    ]

    # 从招聘要求中提取技能
    required_skills = [
        skill for skill in skill_library
        if skill in job_description
    ]

    # 从简历中提取技能
    resume_skills = [
        skill for skill in skill_library
        if skill in resume_text
    ]

    return SkillExtraction(
        required_skills=required_skills,
        resume_skills=resume_skills,
        evidence=[]
    )


# 模拟大模型重试函数

def extract_with_retry(responses, max_attempts=2):
    last_error = None

    for attempt in range(min(max_attempts, len(responses))):
        try:
            data = responses[attempt]
            extraction = SkillExtraction(**data)
            return extraction

        except ValidationError as e:
            last_error = e
            print(f"第 {attempt + 1} 次验证失败：{e}")

    raise RuntimeError("技能提取失败，已达到最大尝试次数") from last_error




# 提取的技能进行对比
def compare_skills(extraction: SkillExtraction):
    required = set(extraction.required_skills)
    resume = set(extraction.resume_skills)

    matched_skills = sorted(required & resume)
    missing_skills = sorted(required - resume)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": [
            f"补充学习或项目实践：{skill}"
            for skill in missing_skills
        ]
    }



# 定义简历与职位匹配接口


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    # 第一步：暂时用模拟数据代替大模型的提取结果
    try:
        extraction = extract_skills_mock(
            request.resume_text,
            request.job_description
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=502,
            detail="技能提取暂时失败，请稍后重试"
        ) from e

    # 第二步：调用业务函数，计算匹配结果
    result = compare_skills(extraction)

    # 第三步：返回分析结果
    return result





if __name__ == "__main__":
    sample = SkillExtraction(
        required_skills=["Python", "FastAPI", "RAG"],
        resume_skills=["Python", "FastAPI", "SQLite"],
        evidence=["完成过库存管理 API 项目"]
    )

    print(compare_skills(sample))

# 大模型重试逻辑


responses = [
    {
        "required_skills": ["Python", "FastAPI"],
        "resume_skills": ["Python", 123],
        "evidence": []
    },
    {
        "required_skills": ["Python", "FastAPI"],
        "resume_skills": ["FastAPI", 123],
        "evidence": []
    }
]


# extract_with_retry(responses)