from pydantic import BaseModel, Field

# 定义客户端需要提交的数据
class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    job_description: str = Field(min_length=1)


# 定义接口需要返回的数据结构
class AnalyzeResponse(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]


class SkillExtraction(BaseModel):
    required_skills: list[str]
    resume_skills: list[str]
    evidence: list[str]

