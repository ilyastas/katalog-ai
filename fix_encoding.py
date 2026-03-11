#!/usr/bin/env python3
import re, os

# Mojibake -> clean text replacements
REPLACEMENTS = [
    # em-dash
    ('вЂ"', '--'),
    ('вЂ"', '--'),
    # quotes
    ('вЂ™', "'"),
    ('вЂ˜', "'"),
    ('вЂœ', '"'),
    ('вЂ', '"'),
    # checkmark -> [+]
    ('вњ…', '[+]'),
    # cross -> [-]
    ('вќЊ', '[-]'),
    # warning
    ('вљ пёЏ', '[!]'),
    ('вљ', '[!]'),
    # arrows
    ('\u0432\u0402\u201c>', '->'),
    ('\u0432\u2020"', '->'),
    # bullets / numbers with emoji
    ('1пёЏвѓЈ', '1.'),
    ('2пёЏвѓЈ', '2.'),
    ('3пёЏвѓЈ', '3.'),
    ('4пёЏвѓЈ', '4.'),
    ('5пёЏвѓЈ', '5.'),
    ('6пёЏвѓЈ', '6.'),
    ('7пёЏвѓЈ', '7.'),
    # Cyrillic-looking mojibake emoji prefixes (рџ...)
    # just strip the whole emoji cluster - replace common ones
    ('рџ¤–', ''),     # 🤖
    ('рџ§ ', ''),     # 🧠
    ('рџЋЇ', ''),    # 🎯
    ('рџ"Љ', ''),    # 📊
    ('рџ"‹', ''),    # 📋
    ('рџ"—', ''),    # 🔗
    ('рџ"ђ', ''),    # 📒
    ('рџ"ќ', ''),    # 📝
    ('рџ"ј', ''),    # 📴
    ('рџ"ЅпёЏ', ''), # 🔅
    ('рЄ', ''),
    ('рњ', ''),
    ('рЏ', ''),
    ('рЋ', ''),
]

TARGET_FILES = [
    'README.md',
    'ai.txt',
    'llms.txt',
    'START_HERE_FOR_AI.txt',
    'LLM_GUARDRAILS.md',
    'LLM_QUERY_TEMPLATES.md',
    'CATALOG_STATUS_POLICY.md',
    'COMPANIES.txt',
]

def clean(text):
    for bad, good in REPLACEMENTS:
        text = text.replace(bad, good)
    # Remove any remaining mojibake Cyrillic clusters that are not real Cyrillic
    # Pattern: sequences like рџXX or вXX that are broken emoji
    text = re.sub(r'[рвдЃЂљњЋЌ][^\s\w]{0,4}', '', text)
    return text

for fname in TARGET_FILES:
    if not os.path.exists(fname):
        print(f'SKIP: {fname}')
        continue
    with open(fname, 'r', encoding='utf-8') as f:
        original = f.read()
    fixed = clean(original)
    if fixed != original:
        with open(fname, 'w', encoding='utf-8', newline='\n') as f:
            f.write(fixed)
        print(f'FIXED: {fname}')
    else:
        print(f'CLEAN: {fname}')
