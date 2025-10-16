#!/usr/bin/env python3
# defensive_stack/domain_similarity_detector.py
import difflib

def normalize(domain: str) -> str:
    d = domain.lower().strip()
    # common visual substitutions
    for a,b in [('0','o'),('1','l'),('5','s'),('!','i')]:
        d = d.replace(a,b)
    return d.replace('.','').replace('-','')

def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def is_similar(candidate: str, canonical_list: list, threshold: float = 0.85):
    """
    Returns (bool, score, matching_canonical) - True if any canonical domain
    is similar enough to candidate.
    """
    for canon in canonical_list:
        sc = similarity(candidate, canon)
        if sc >= threshold:
            return True, sc, canon
    return False, 0.0, None

if __name__ == "__main__":
    # basic quick test
    print(is_similar("gmai1.com", ["gmail.com"]))
