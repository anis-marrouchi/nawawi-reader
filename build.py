#!/usr/bin/env python3
"""Build data.json for the Nawawi reader.

Sources (both open, both cited in the app):
- sources/nawawi40.json: al-Arba'in an-Nawawiyya, vocalised Arabic only, from
  github.com/AhmedBaset/hadith-json (scraped from sunnah.com).
- sources/jamic.Shamela0004268.txt: Ibn Rajab, Jami' al-'Ulum wa-l-Hikam, ed. Shu'ayb
  al-Arna'ut and Ibrahim Bajis, Mu'assasat al-Risala, Beirut, 7th printing 1422/2001,
  2 vols. OpenITI 0795IbnRajabHanbali.JamicCulumWaHikam.Shamela0004268-ara1.

Each hadith section starts at its OpenITI heading ("### | [الحديث ...]").
Page numbers come from the OpenITI page markers (PageV01P058 = end of vol. 1, p. 58).
Nothing is generated: every word shown comes from these two files.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARH = HERE / "sources/jamic.Shamela0004268.txt"
END_OF_SENTENCE = tuple(".:؟!»\"")
UNITS = ["", "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع"]
TEENS = ["", "الحادي", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع"]
TENS = {2: "العشرون", 3: "الثلاثون", 4: "الأربعون", 5: "الخمسون"}


def ordinal(n):
    if n < 10:
        return UNITS[n]
    if n == 10:
        return "العاشر"
    if n < 20:
        return f"{TEENS[n - 10]} عشر"
    t, u = divmod(n, 10)
    return TENS[t] if u == 0 else f"{TEENS[u]} و{TENS[t]}"


def sections(raw):
    body = raw.split("#META#Header#End#", 1)[-1]
    parts = re.split(r"^### \| \[(.+?)\]\s*$", body, flags=re.M)
    # parts = [preface, title1, body1, title2, body2, ...]
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]


def paragraphs(text, start_page):
    """Return [{page, vol, text}] with paragraphs re-joined across page breaks."""
    text = re.sub(r"\bms\d+\s?", "", text)
    text = re.sub(r"</?span[^>]*>", "\n# ", text)
    text = re.sub(r"\n~~", " ", text)
    vol, page = start_page
    out, cur, cur_page = [], "", (vol, page)
    for token in re.split(r"(PageV\d+P\d+|\n#)", text):
        m = re.fullmatch(r"PageV(\d+)P(\d+)", token)
        if m:
            # marker closes a page; following text is on the next one
            vol, page = int(m.group(1)), int(m.group(2)) + 1
            continue
        if token == "\n#":
            if cur.strip().endswith(END_OF_SENTENCE):
                out.append({"vol": cur_page[0], "page": cur_page[1], "text": re.sub(r"\s+", " ", cur).strip()})
                cur = ""
            continue
        if not cur.strip():
            cur_page = (vol, page)
        cur += " " + token
    if cur.strip():
        out.append({"vol": cur_page[0], "page": cur_page[1], "text": re.sub(r"\s+", " ", cur).strip()})
    return [q for p in out if p["text"] for q in split_long(p)], (vol, page)


def split_long(p, limit=1400):
    """Split very long paragraphs at sentence ends so they stay readable."""
    if len(p["text"]) <= limit:
        return [p]
    pieces, cur = [], ""
    for sent in re.split(r"(?<=[.؟!])\s+", p["text"]):
        if cur and len(cur) + len(sent) > limit:
            pieces.append(cur.strip())
            cur = ""
        cur += " " + sent
    pieces.append(cur.strip())
    return [dict(p, text=t) for t in pieces if t]


def main():
    nawawi = json.loads((HERE / "sources/nawawi40.json").read_text())
    secs = sections(SHARH.read_text())
    titles = [t for t, _ in secs]
    assert titles[0].startswith("مقدمة"), titles[0]
    # page tracking needs every section, including the preface
    pos, parsed = (1, 1), []
    for title, body in secs:
        paras, pos = paragraphs(body, pos)
        parsed.append((title, paras))

    items = []
    for i, h in enumerate(nawawi["hadiths"]):
        title, paras = parsed[i + 1]
        title = re.sub(r"\bms\d+\s?", "", title)
        prefix = f"الحديث {ordinal(i + 1)} "
        if not title.startswith(prefix):
            raise SystemExit(f"section {i + 1} does not open with '{prefix}': {title}")
        items.append({
            "n": i + 1,
            "title": title,
            "short": title[len(prefix):],
            "arabic": h["arabic"].strip(),
            "english": (f'{h["english"]["narrator"]} {h["english"]["text"]}'.strip()
                        if h.get("english") else ""),
            "sharh": paras,
        })

    out = {
        "title": "الأربعون النووية مع جامع العلوم والحكم",
        "sources": {
            "matn": "متن الأربعين النووية للإمام يحيى بن شرف النووي (ت 676هـ)، النص المشكول من sunnah.com عبر github.com/AhmedBaset/hadith-json",
            "sharh": "جامع العلوم والحكم لابن رجب الحنبلي (ت 795هـ)، تحقيق شعيب الأرناؤوط وإبراهيم باجس، مؤسسة الرسالة، بيروت، ط7 1422هـ/2001م. النص من مشروع OpenITI (Shamela0004268)",
        },
        "hadiths": items,
    }
    (HERE / "data.json").write_text(json.dumps(out, ensure_ascii=False))
    for it in items:
        s = it["sharh"]
        print(f'{it["n"]:>2} v{s[0]["vol"]} p{s[0]["page"]}-{s[-1]["page"]} {len(s):>3} paras '
              f'| {it["title"][:55]}')


if __name__ == "__main__":
    main()
