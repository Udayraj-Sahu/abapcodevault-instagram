# English voiceover guide (living document)

Voiceovers are in **English** since 12 Nov 2026 (before that they were Hinglish).
Read this before writing any `voiceover` / `spoken` line. The daily run improves it on "script" work:
add glossary rows, fix awkward phrasings found in recent reels, and note the source of anything learned.

## Voice (`voiceover`, spoken by Kokoro hm_psi, `"voice_lang": "en"`)
- Clear, conversational English, like a senior developer explaining to a colleague. Not a textbook.
- Short sentences (5-14 words). One idea per sentence. Commas and full stops where a speaker breathes.
- Contractions are good ("it's", "don't", "here's"). Active voice ("Activate it", not "It should be activated").
- Start with a hook in ≤ 2 s: a question ("Is your report slow?") or a bold claim ("This one line can read your entire table.").
- No code symbols (`@`, `=`, `->`, `#( )`); say them in words ("the VALUE operator", "the arrow", "equals").
- Numbers the natural way ("ten thousand calls", "seven forty syntax").
- Acronyms / T-codes / table names are pronounced via the `SAY` table in `generate.py`; add new ones there.
- **Do not say "ABAP"** (the voice mispronounces it; user feedback 12 Nov). Say "code", "report", "seven forty syntax",
  "developer" instead. "ABAP" on screen and in captions is fine. Lift this rule only after a voice improvement makes it sound right.

## Subtitles (`spoken`, shown on screen)
- Exactly the same text as `voiceover`, so subtitles match the audio word for word.
- Technical words keep their normal casing: SELECT, LOOP, ALV, BAPI, SE38, internal table.

## Glossary: how developers actually say it
| Term | In voiceover | Notes |
| --- | --- | --- |
| internal table | internal table | |
| work area | work area | |
| field symbol | field symbol | |
| SELECT SINGLE | SELECT SINGLE | |
| FOR ALL ENTRIES | FOR ALL ENTRIES | |
| sy-subrc | S Y subrc | add to SAY if missing |
| ABAP 7.40 | seven forty syntax | never "ABAP" in voice |
| transport request | transport | |
| short dump | dump | "you get a dump" |
| SE11 | S E eleven | via SAY |

## Phrases that sound natural (use) vs. stiff (avoid)
| Natural | Stiff |
| --- | --- |
| "Read the data once, then look it up in memory." | "It is recommended to retrieve the data in a single database access." |
| "Save this." | "Kindly save this post for future reference." |
| "Interviewers ask this a lot." | "This question is frequently asked in interviews." |
| "Program still behaving the old way? Check that you activated it." | "If the program exhibits the previous behavior, verify activation." |
