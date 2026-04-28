from pydantic import BaseModel, model_validator, Field
from typing import Literal, Optional, Union
from datetime import datetime

# Global objects
AnswerOptions = Literal["A", "B", "C", "D"]
QuestionAnswerOptions = Union[AnswerOptions, str] 
WasUserCorrect = Literal["Correct", "Incorrect", "Neutral"]

class QuestionBase(BaseModel):
    questionText: Optional[str] = Field(default=None, max_length=2000)
    questionImgRef: Optional[str] = None

    @model_validator(mode="after")
    def check_question_content(self):
        if not self.questionText and not self.questionImgRef:
            raise ValueError("A question must have either text or an image reference.")

        return self

# Request from user
class SolveRequest(QuestionBase):
    userAnswer: Optional[QuestionAnswerOptions] = None
    requestedAt: datetime = Field(default_factory=datetime.now)

# Question & Trap Structure
QuestionTypesEnglish = Literal[
    "grammar",
    "transition",
    "rhetoric",
    "inference",
    "vocabulary",
    "notes",
    "main_idea"
]

QuestionTypesMath = Literal[
    "algebra",
    "linear",
    "quadratic",
    "geometry",
    "trigonometry",
    "probability",
    "statistics",
    "word_problem"
]

QuestionTypes = Union[QuestionTypesEnglish, QuestionTypesMath]

TrapTypesEnglish = Literal[
    "scope_mismatch",
    "too_broad",
    "too_specific",
    "grammar_boundary_error",
    "transition_logic_error",
    "vocabulary_tone_mismatch",
]

TrapTypesMath = Literal[
    "sign_error",
    "wrong_formula",
    "unit_mistake",
    "extraneous_solution",
    "misread_question",
]

TrapTypes = Union[TrapTypesEnglish, TrapTypesMath]

# Response from platform
Sections = Literal["english", "math"]

class SolveResult(BaseModel):
    section: Sections
    questionType: QuestionTypes
    correctChoice: QuestionAnswerOptions = Field(..., description="Clean answer only.")
    explanation: str = Field(..., max_length=500)
    wasUserCorrect: WasUserCorrect
    trapType: TrapTypes
    confidence: int = Field(..., ge=0, le=100)

# Attempts
class Attempt(QuestionBase):
    id: int
    createdAt: datetime = Field(default_factory=datetime.now)
    userAnswer: Optional[QuestionAnswerOptions] = None
    correctChoice: QuestionAnswerOptions = Field(..., description="Clean answer only.")
    wasUserCorrect: WasUserCorrect
    section: Sections
    questionType: QuestionTypes
    trapType: TrapTypes
    explanation: str = Field(..., max_length=500)
    confidence: int = Field(..., ge=0, le=100)

class AttemptPreview(BaseModel):
    id: int
    createdAt: datetime
    questionType: QuestionTypes
    correctChoice: QuestionAnswerOptions = Field(..., description="clean answer without any unnecessary details.")
    userAnswer: Optional[QuestionAnswerOptions] = None
    wasUserCorrect: WasUserCorrect
    confidence: int = Field(..., ge=0, le=100)