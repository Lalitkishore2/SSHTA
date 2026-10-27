import re

with open('full_paper_paragraphs.txt', 'r', encoding='utf-8') as f:
    text = f.read()

paras = text.split('\n\n')
print(f"Total paragraphs: {len(paras)}")

# Check for math or equation patterns
math_patterns = [
    r'(\w+_\w+)', # identifiers with underscore like h_2, L_2, PAC_table, page_ID
    r'([A-Za-z]\s*=\s*[\d\.\+]+)', # expressions like L_2 = 40.0 ns, alpha = 0.85
    r'(\(\d\))', # equation numbers like (1), (2), (3)
    r'(\b[A-Za-z]\s+[0-9]\b)', # broken subscripts like 'h 2', 'L 2', 'L 3'
    r'(\b[A-Za-z]\s+[a-z]{3,}\b)', # broken terms like 'L serviced', 'L eff'
    r'(NmigrationsNaccesses)', # squashed fraction
]

print("=== PARAGRAPHS WITH BROKEN SUBSCRIPTS OR UNFORMATTED MATH ===")
for p in paras:
    if any(re.search(pat, p) for pat in [r'\bh 2\b', r'\bL 2\b', r'\bL 3\b', r'\bL serviced\b', r'\bL eff\b', r'NmigrationsNaccesses', r'h_2', r'L_2', r'L_3', r'L_eff', r'L_serviced', r'theta =', r'alpha =']):
        print(p[:200])
        print("---")
