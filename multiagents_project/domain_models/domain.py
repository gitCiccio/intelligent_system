from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SymptomReport:
    intensity_per_symptoms: Dict[str, int] = field(default_factory=dict)
    original_text_input: str = ""

@dataclass
class RawSymptomMatch:
    symptom: str
    area: Optional[str] = None
    intensity: int = 0
    negative: bool = False
    original_sentence: str = ""

@dataclass
class SymptomEntry:
    concept: str
    variants: List[str]

@dataclass
class AreaOfInterest:
    areas: Dict[str, List[str]]

@dataclass
class IntensityScale:
    scale: Dict[str, int]