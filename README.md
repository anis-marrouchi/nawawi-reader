# Nawawi reader

Al-Arba'in an-Nawawiyya (Nawawi's 40 hadith) side by side with Ibn Rajab's commentary,
*Jami' al-'Ulum wa-l-Hikam*. Arabic, right to left, and it works on a phone.

- Every commentary paragraph shows its volume and page in the printed edition.
- Search across the whole commentary works with or without harakat.
- The "انسخ للمساعد" button copies the hadith and its full commentary, with page numbers,
  plus an instruction to answer only from that text and cite volume and page. Paste it into
  any AI assistant. There is no AI inside the app, and the app writes nothing of its own.

It is a reading and finding aid. It does not give tafsir or fatwas.

## Run it

```
python3 -m http.server
```

Then open http://localhost:8000/#/1. `#/n/i` jumps to hadith n, paragraph i.
`python3 build.py` rebuilds `data.json` from `sources/` and stops if any of the 42
commentary sections does not open with its expected ordinal.

## Sources

- **Matn:** vocalised Arabic text from sunnah.com, via
  [AhmedBaset/hadith-json](https://github.com/AhmedBaset/hadith-json).
- **Commentary:** Ibn Rajab al-Hanbali (d. 795 AH), *Jami' al-'Ulum wa-l-Hikam*, ed. Shu'ayb
  al-Arna'ut and Ibrahim Bajis, Mu'assasat al-Risala, Beirut, 7th printing 1422/2001, 2 vols.
  Text from the [OpenITI](https://openiti.org) corpus,
  `0795IbnRajabHanbali.JamicCulumWaHikam.Shamela0004268-ara1`.

## Known issues

- In hadith 1, the sunnah.com text leaves Imam Muslim out of the line saying who
  narrated it. Ibn Rajab's own copy reads "رواه البخاري ومسلم". The source text is
  shown as it is.
- Page numbers come from OpenITI page markers and have not yet been checked against a printed copy.
  Corrections are welcome.

## Licence

Code (`index.html`, `build.py`): MIT. The OpenITI text is distributed under OpenITI's
terms (CC BY-NC-SA 4.0). Keep the attribution and use it non-commercially.
