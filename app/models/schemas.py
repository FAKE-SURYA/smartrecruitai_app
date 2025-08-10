"""Pydantic Models and Schemas for SmartRecruitAI API

Defines all input/output data models for API endpoints with validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator, EmailStr


class ScoreLevel(str, Enum):
    """Score level enumeration."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class FileFormat(str, Enum):
    """Supported file formats."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    IMAGE = "image"


# === Resume Parsing Models ===

class ResumeSection(BaseModel):
    """Individual resume section."""
    title: str = Field(..., description="Section title (e.g., 'Experience', 'Education')")
    content: str = Field(..., description="Section content text")
    order: int = Field(..., description="Section order in resume")


class ParsedResume(BaseModel):
    """Parsed resume output."""
    text: str = Field(..., description="Full extracted text")
    skills: List[str] = Field(default_factory=list, description="Extracted skills")
    sections: List[ResumeSection] = Field(default_factory=list, description="Resume sections")
    contact_info: Optional[Dict[str, Any]] = Field(None, description="Contact information")
    experience_years: Optional[int] = Field(None, description="Estimated years of experience")
    education: Optional[str] = Field(None, description="Education summary")
    file_format: FileFormat = Field(..., description="Original file format")
    parsing_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Parsing confidence score")


class ParseResumeRequest(BaseModel):
    """Request for resume parsing."""
    file_content: Optional[str] = Field(None, description="Base64 encoded file content")
    file_url: Optional[str] = Field(None, description="URL to file")
    file_format: FileFormat = Field(..., description="File format")
    extract_skills: bool = Field(True, description="Whether to extract skills")
    extract_sections: bool = Field(True, description="Whether to extract sections")

    @validator('file_content', 'file_url')
    def at_least_one_source(cls, v, values):
        if not v and not values.get('file_content') and not values.get('file_url'):
            raise ValueError('Either file_content or file_url must be provided')
        return v


# === Analysis Models ===

class SkillMatch(BaseModel):
    """Individual skill match."""
    skill: str = Field(..., description="Skill name")
    matched: bool = Field(..., description="Whether skill is matched")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    category: Optional[str] = Field(None, description="Skill category")


class AnalysisGap(BaseModel):
    """Analysis gap or improvement suggestion."""
    category: str = Field(..., description="Gap category (e.g., 'skills', 'experience')")
    description: str = Field(..., description="Gap description")
    severity: ScoreLevel = Field(..., description="Gap severity")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class JobTitleSuggestion(BaseModel):
    """Job title suggestion."""
    title: str = Field(..., description="Job title")
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score")
    rationale: str = Field(..., description="Why this title matches")
    level: str = Field(..., description="Job level (e.g., 'Entry', 'Mid', 'Senior')")


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall match score (0-100)")
    score_level: ScoreLevel = Field(..., description="Score level category")
    skill_matches: List[SkillMatch] = Field(default_factory=list, description="Skill analysis")
    gaps: List[AnalysisGap] = Field(default_factory=list, description="Identified gaps")
    job_titles: List[JobTitleSuggestion] = Field(default_factory=list, description="Job title suggestions")
    rationale: str = Field(..., description="Overall analysis rationale")
    score_breakdown: Dict[str, float] = Field(default_factory=dict, description="Score breakdown by category")


class AnalyzeMatchRequest(BaseModel):
    """Request for resume-job match analysis."""
    resume_content: Optional[str] = Field(None, description="Resume text content")
    resume_id: Optional[str] = Field(None, description="Previously parsed resume ID")
    job_description: Optional[str] = Field(None, description="Job description text")
    job_url: Optional[str] = Field(None, description="Job posting URL")
    analysis_depth: str = Field("detailed", description="Analysis depth: 'quick' or 'detailed'")
    include_suggestions: bool = Field(True, description="Include improvement suggestions")

    @validator('resume_content', 'resume_id')
    def resume_source_required(cls, v, values):
        if not v and not values.get('resume_content') and not values.get('resume_id'):
            raise ValueError('Either resume_content or resume_id must be provided')
        return v

    @validator('job_description', 'job_url')
    def job_source_required(cls, v, values):
        if not v and not values.get('job_description') and not values.get('job_url'):
            raise ValueError('Either job_description or job_url must be provided')
        return v


# === Bullet Point Rewriting Models ===

class BulletPoint(BaseModel):
    """Original bullet point."""
    text: str = Field(..., description="Original bullet point text")
    category: Optional[str] = Field(None, description="Bullet point category")


class RewrittenBullet(BaseModel):
    """Rewritten bullet point."""
    original: str = Field(..., description="Original text")
    rewritten: str = Field(..., description="Rewritten text")
    improvements: List[str] = Field(default_factory=list, description="List of improvements made")
    score_improvement: float = Field(0.0, description="Estimated score improvement")


class RewriteBulletsRequest(BaseModel):
    """Request for bullet point rewriting."""
    bullets: List[BulletPoint] = Field(..., description="Bullet points to rewrite")
    job_context: Optional[str] = Field(None, description="Job description context")
    tone: str = Field("professional", description="Writing tone: 'professional', 'dynamic', 'technical'")
    focus_keywords: List[str] = Field(default_factory=list, description="Keywords to emphasize")
    max_length: Optional[int] = Field(None, description="Maximum length per bullet")


class RewriteBulletsResponse(BaseModel):
    """Response for bullet point rewriting."""
    rewrites: List[RewrittenBullet] = Field(..., description="Rewritten bullet points")
    overall_improvement: str = Field(..., description="Overall improvement summary")
    suggested_additions: List[str] = Field(default_factory=list, description="Suggested additional bullets")


# === Export Models ===

class ExportRequest(BaseModel):
    """Request for document export."""
    resume_text: str = Field(..., description="Resume content")
    rewrites: Optional[List[RewrittenBullet]] = Field(None, description="Applied rewrites")
    format: str = Field("docx", description="Export format: 'docx' or 'pdf'")
    template: str = Field("modern", description="Template style")
    include_analysis: bool = Field(False, description="Include analysis results")


class ExportResponse(BaseModel):
    """Response for document export."""
    download_url: str = Field(..., description="Download URL")
    file_size: int = Field(..., description="File size in bytes")
    expires_at: datetime = Field(..., description="URL expiration time")
    format: str = Field(..., description="Export format")


# === Report Models ===

class AnalysisReport(BaseModel):
    """Complete analysis report."""
    id: str = Field(..., description="Report ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    resume_summary: str = Field(..., description="Resume summary")
    analysis: AnalysisResult = Field(..., description="Analysis results")
    recommendations: List[str] = Field(default_factory=list, description="Key recommendations")
    status: str = Field("completed", description="Report status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# === Error Models ===

class ErrorDetail(BaseModel):
    """Error detail."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused error")


class APIError(BaseModel):
    """API error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: List[ErrorDetail] = Field(default_factory=list, description="Error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


# === Health and Status Models ===

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency status")


class APIInfo(BaseModel):
    """API information response."""
    message: str = Field(..., description="API message")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints")
    version: str = Field(..., description="API version")
    documentation: str = Field(..., description="Documentation URL")
