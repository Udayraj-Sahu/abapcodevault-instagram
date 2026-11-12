# Hinglish voiceover & caption guide (living document)

Read this before writing any `voiceover` / `spoken` line. The daily run improves it on "translation" days:
add glossary rows, fix awkward phrasings found in recent reels, and note the source of anything learned.

## Voice (`voiceover`, spoken by Kokoro hm_psi)
- Hindi words in **Devanagari**, English/technical words in **Latin**, exactly as an Indian developer says them out loud.
- Short sentences (4-10 words). One idea per sentence. Full stop or comma where a speaker would breathe.
- Conversational register: "आप" for the viewer in hooks, "करो" for instructions ("save कर लो", "check करो").
- Start with a hook in ≤ 2 s: a question ("आपकी report slow है?") or a bold claim ("ये एक line पूरी table पढ़ लेती है।").
- No code symbols in the voiceover (`@`, `=`, `->`, `#( )`); say them in words ("VALUE operator", "arrow", "equals").
- Numbers: say them the natural way ("दस हज़ार calls", "seven forty"), not digits glued to units.
- Acronyms / T-codes / table names are pronounced via the `SAY` table in `generate.py`; add new ones there.
- **Do not say "ABAP" in the voiceover** (the voice mispronounces it; user feedback 12 Nov). Say "code", "report",
  "seven forty syntax", "developer" instead. "ABAP" on screen and in captions is fine. A voice-day improvement may
  fix the SAY entry for ABAP; only lift this rule after it sounds right.

## Captions (`spoken`, shown on screen)
- The same sentence fully in **Roman Hinglish**, word for word, so captions match the audio.
- Consistent spellings (use these exactly):

| Say | Write in `spoken` |
| --- | --- |
| है / हैं | hai / hain |
| में | mein |
| नहीं | nahi |
| करो / कर लो | karo / kar lo |
| के अंदर | ke andar |
| के लिए | ke liye |
| सिर्फ | sirf |
| ज़रूरत | zaroorat |
| हज़ार | hazaar |
| पढ़ो / पढ़ना | padho / padhna |
| अपने आप | apne aap |
| जवाब | jawaab |
| पूछा | poocha |

- Technical words keep their normal casing in captions: SELECT, LOOP, ALV, BAPI, SE38, internal table.

## Glossary: how developers actually say it
| Term | In voiceover | Notes |
| --- | --- | --- |
| internal table | internal table | never "आंतरिक तालिका" |
| work area | work area | |
| field symbol | field symbol | |
| SELECT SINGLE | SELECT SINGLE | |
| FOR ALL ENTRIES | FOR ALL ENTRIES | |
| sy-subrc | S Y subrc | already in SAY? add if missing |
| ABAP 7.40 | ABAP seven forty | |
| transport request | transport | |
| short dump | dump | "dump आ गया" |

## Phrases that sound natural (use) vs. stiff (avoid)
| Natural | Stiff |
| --- | --- |
| "एक बार में पढ़ो, फिर memory से उठाओ।" | "डेटा को एक बार में पढ़ें और फिर मेमोरी से प्राप्त करें।" |
| "Save कर लो।" | "कृपया इसे सहेजें।" |
| "Interview में ये ज़रूर पूछते हैं।" | "साक्षात्कार में यह प्रश्न पूछा जाता है।" |
