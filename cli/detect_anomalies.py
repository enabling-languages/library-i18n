import regex
import icu
import el_internationalisation as eli
import unicodedataplus as ud

problem_chars_pattern = regex.compile(r'[\p{Bidi_Control}\p{Cs}\p{Co}\p{Cn}\u0333\u3013\uFFFD]')
problem_chars = ['\u0333', '\u3013', '\uFFFD']
problem_chars.extend(list(icu.UnicodeSet(r'\p{Bidi_Control}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Cs}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Co}')))
problem_chars.extend(list(icu.UnicodeSet(r'\p{Cn}')))

def detect_anomalies(text: str) -> set[str]:
    problematic = set()
    if regex.search(problem_chars_pattern, text):
        for char in problem_chars:
            if char in text:
                problematic.add(f"{eli.cp(char)} ({ud.name(char)})")
    return problematic

def register_anomalies(subfield: str):
    check = detect_anomalies(subfield)
    if check:
        print(*sorted(check), sep="\n", end="\n\n")
    return None

s1 = 'Thuo̳n̳jän̳ \ufffdathör tuen̳\u3013 ë kue̳n'
s2 = 'Thuo̳n̳jän̳ athör tuen̳ ë kue̳n'
s3 = "Hell, does it work?"

register_anomalies(s1)
register_anomalies(s2)
register_anomalies(s3)
