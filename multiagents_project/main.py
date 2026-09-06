import re
from typing import List
from data.lexicon import SEGMENT_SEPARATORS, SYMPTOM_ENTRIES, NEGATIONS, AREA_OF_INTEREST, INTENSITY_SCALE
from domain_models.domain import RawSymptomMatch


def to_logical_symbol(match: RawSymptomMatch) -> str:
    combinations = match.symptom
    if match.area:
        combinations = f"{match.symptom}_{match.area}"
    return combinations

# riconosce il sintomo
def apply_symptom_recognition(sentence: str) -> str:
    for symptom in SYMPTOM_ENTRIES:
        for variant in symptom.variants:
            if variant in sentence:
                return symptom.concept
    return ""



# riconosce l'area del corpo a cui si riferisce il sintomo
def apply_area_recognition(match: RawSymptomMatch):
    for area in AREA_OF_INTEREST.areas:
        for sub_area in AREA_OF_INTEREST.areas[area]:
            if sub_area in match.original_sentence:
                match.area = area

# riconosce la scala di intensità
def apply_scale_recognition(sentence: str) -> int:
    for scale in INTENSITY_SCALE.scale:
        if scale in sentence:
            return INTENSITY_SCALE.scale[scale]
    return 0


def parse_text(text: str) -> List[RawSymptomMatch]:
    text_to_analyze = text

    separators = "|".join(SEGMENT_SEPARATORS)
    #print(f"Separators regex: {separators}")

    filtered_text = re.split(separators, text_to_analyze)

    filtered_text = [segment.strip() for segment in filtered_text if segment.strip()]
    #print(f"Filtered text: {filtered_text}")

    matches: List[RawSymptomMatch] = []
    for segment in filtered_text:
        is_negative = any(negation in segment.split() for negation in NEGATIONS)
        matches.append(RawSymptomMatch(
            symptom="",
            negative=is_negative,
            original_sentence=segment
        ))
    latest_symptom = ""
    latest_intensity = 0
    for match in matches:
        found_it = apply_symptom_recognition(match.original_sentence)
        if found_it:
            match.symptom = found_it
            latest_symptom = found_it
        apply_area_recognition(match)
        if match.area:
            match.symptom = latest_symptom
        found_intensity = apply_scale_recognition(match.original_sentence)
        if found_intensity:
            match.intensity = found_intensity
            latest_intensity = found_intensity
        elif match.area:
            match.intensity = latest_intensity


    #print(f"matches: {matches}")

    return matches

if __name__ == '__main__':
    full_text = "Ho un fortissimo dolore al petto e alla schiena, ma non ho febbre. Inoltre, sento un po' di nausea."
    print(f"Input text: {full_text}")
    parse_text(full_text)
