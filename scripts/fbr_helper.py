"""FBR helper: (a) notice mode and (b) return-sheet mode. Never logs in anywhere.

  python3 scripts/fbr_helper.py notice --notice notice.json [--lang en|roman|ur] [--today YYYY-MM-DD] [--letter reply.txt]
  python3 scripts/fbr_helper.py return-sheet --docs docs.json [--lang en|roman|ur] [--csv worksheet.csv] [--slabs FILE]
Stdlib only, python 3.9+.
"""
import argparse, csv, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")
NOTICE = {"en": "This is a helper, not professional advice. Check the figures before you act.",
          "roman": "Yeh sirf madadgar tool hai, professional mashwara nahin. Amal se pehle hisaab khud check karein.",
          "ur": "یہ صرف مددگار ٹول ہے، پیشہ ورانہ مشورہ نہیں۔ عمل سے پہلے حساب خود چیک کریں۔"}
IRIS = {"en": "File through IRIS yourself; this tool never logs in.",
        "roman": "IRIS par khud file karein; yeh tool kabhi login nahin karta.",
        "ur": "IRIS پر خود فائل کریں؛ یہ ٹول کبھی لاگ ان نہیں کرتا۔"}
L = {
 "days": {"en": "Days left: {n}", "roman": "Baqi din: {n}", "ur": "باقی دن: {n}"},
 "overdue": {"en": "OVERDUE by {n} days", "roman": "{n} din ki derr ho chuki hai", "ur": "{n} دن کی تاخیر ہو چکی ہے"},
 "today": {"en": "Deadline is TODAY", "roman": "Aakhri tareekh AAJ hai", "ur": "آخری تاریخ آج ہے"},
 "soon": {"en": "Less than 8 days left. Start now, or ask for more time in writing.", "roman": "8 din se kam baqi hain. Abhi shuru karein ya likh kar mazeed waqt maangein.",
          "ur": "8 دن سے کم باقی ہیں۔ ابھی شروع کریں یا تحریری طور پر مزید وقت مانگیں۔"},
 "section": {"en": "Section", "roman": "Section", "ur": "سیکشن"},
 "plain": {"en": "What it means", "roman": "Matlab", "ur": "مطلب"},
 "resp": {"en": "Typical response", "roman": "Aam jawab", "ur": "عام جواب"},
 "pen": {"en": "Penalty", "roman": "Jurmana", "ur": "جرمانہ"},
 "docs": {"en": "Documents to gather", "roman": "Jama karne wale kaghzaat", "ur": "جمع کرنے والے کاغذات"},
 "notin": {"en": "Section {s} is NOT IN THE TABLE. Read the notice and the Income Tax Ordinance 2001 yourself or ask a tax professional. No explanation is given.",
           "roman": "Section {s} TABLE MEIN NAHIN hai. Notice aur Income Tax Ordinance 2001 khud parhein ya tax professional se poochein. Koi wazahat nahin di gayi.",
           "ur": "سیکشن {s} ٹیبل میں موجود نہیں۔ نوٹس اور انکم ٹیکس آرڈیننس 2001 خود پڑھیں یا ٹیکس ماہر سے پوچھیں۔ کوئی وضاحت نہیں دی گئی۔"},
 "parent": {"en": "Sub-section {s} is not in the table; showing the parent section {p}.", "roman": "Sub-section {s} table mein nahin; parent section {p} dikhaya ja raha hai.",
            "ur": "ذیلی دفعہ {s} ٹیبل میں نہیں؛ اصل سیکشن {p} دکھایا جا رہا ہے۔"},
 "unv": {"en": "UNVERIFIED RULE: check {src}", "roman": "UNVERIFIED RULE: check {src}", "ur": "UNVERIFIED RULE: check {src}"},
}


def lg(k, lang, **kw):
    return L[k][lang].format(**kw)


def norm_section(s):
    s = str(s).lower().replace("section", "").replace("u/s", "").replace(" ", "")
    return s.strip(".")


def lookup(sections, raw):
    k = norm_section(raw)
    if k in sections:
        return k, sections[k], None
    base = re.match(r"\d+[a-z]?", k)
    if base and base.group(0) in sections and "(" in k:
        return base.group(0), sections[base.group(0)], base.group(0)
    return None, None, None


def parse_date(s):
    return dt.date.fromisoformat(str(s)[:10])


def letter(n, ent, lang, left):
    sec, ty, issued, dl = n.get("section"), n.get("tax_year", "[tax year]"), n.get("date_issued", "[date]"), n.get("deadline", "[deadline]")
    no, off = n.get("notice_no", "[notice no.]"), n.get("office", "[tax office]")
    docs = "\n".join(f"- {d}" for d in (ent["documents"] if ent else ["[documents listed in the notice]"]))
    if lang == "ur":
        t = (f"بخدمت: {off}\n\nموضوع: نوٹس نمبر {no} بابت سیکشن {sec}، ٹیکس سال {ty}\n\nمحترم جناب،\n\n"
             f"مجھے {issued} کو جاری ہونے والا نوٹس موصول ہوا ہے جس کی آخری تاریخ {dl} ہے۔ میں مطلوبہ کاغذات جمع کر رہا/رہی ہوں:\n\n{docs}\n\n"
             "میں مقررہ تاریخ تک جواب جمع کراؤں گا/گی۔ اگر کاغذات مکمل کرنے کے لیے مزید وقت درکار ہوا تو براہ کرم [تاریخ] تک مہلت عطا فرمائیں۔ "
             "مجھے سماعت کا موقع دیا جائے۔\n\nشکریہ\n[نام]\n[این ٹی این / شناختی کارڈ]\n[فون]\n")
    elif lang == "roman":
        t = (f"Bakhidmat: {off}\n\nMauzu: Notice no. {no} babat section {sec}, tax year {ty}\n\nMuhtaram janab,\n\n"
             f"Mujhe {issued} ko jari hone wala notice mila hai jis ki aakhri tareekh {dl} hai. Main darj-e-zail kaghzaat jama kar raha/rahi hun:\n\n{docs}\n\n"
             "Main muqarrara tareekh tak jawab jama karaunga/karaungi. Agar kaghzaat mukammal karne ke liye mazeed waqt chahiye hua to meherbani karke [tareekh] tak mohlat dein. "
             "Mujhe sunwai ka mauqa diya jaye.\n\nShukriya\n[Naam]\n[NTN / CNIC]\n[Phone]\n")
    else:
        t = (f"To: {off}\n\nSubject: Notice no. {no} under section {sec}, tax year {ty}\n\nDear Sir or Madam,\n\n"
             f"I received the notice issued on {issued} with the deadline {dl}. I am collecting the documents below:\n\n{docs}\n\n"
             "I will submit my reply by the due date. If I need more time to complete the documents, please allow an extension until [date]. "
             "Please give me an opportunity to be heard.\n\nThank you\n[Name]\n[NTN / CNIC]\n[Phone]\n")
    return t + "\n" + NOTICE[lang] + "\n" + IRIS[lang] + "\n"


def cmd_notice(a):
    n = json.load(open(a.notice, encoding="utf-8"))
    sections = json.load(open(os.path.join(REF, "sections.json"), encoding="utf-8"))["sections"]
    today = parse_date(a.today) if a.today else dt.date.today()
    lang = a.lang
    print(f"{lg('section', lang)}: {n.get('section')}   Tax year: {n.get('tax_year', '?')}   Issued: {n.get('date_issued', '?')}   Deadline: {n.get('deadline', '?')}")
    left = None
    if n.get("deadline"):
        left = (parse_date(n["deadline"]) - today).days
        if left < 0:
            print(lg("overdue", lang, n=-left))
        elif left == 0:
            print(lg("today", lang))
        else:
            print(lg("days", lang, n=left))
            if left <= 7:
                print(lg("soon", lang))
    else:
        print("No deadline in notice.json. Read it from the notice.")
    if n.get("demand") is not None:
        print(f"Demand: Rs {n['demand']:,}")
    key, ent, parent = lookup(sections, n.get("section", ""))
    if ent is None:
        print(lg("notin", lang, s=n.get("section")))
    else:
        if parent:
            print(lg("parent", lang, s=n["section"], p=parent))
        print(f"{ent['title']}")
        print(f"{lg('plain', lang)}: {ent['plain']}")
        print(f"{lg('resp', lang)}: {ent['typical_response']}")
        print(f"{lg('pen', lang)}: {ent['penalty']}")
        print(f"{lg('docs', lang)}:")
        for d in ent["documents"]:
            print(f"  - {d}")
        if not ent["verified"]:
            print(lg("unv", lang, src=ent["source_url"]))
    if a.letter:
        open(a.letter, "w", encoding="utf-8").write(letter(n, ent, lang, left))
        print("Reply letter written:", a.letter)
    print(NOTICE[lang])
    print(IRIS[lang])


def money(x):
    return f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.2f}"


def slab_tax(slabs, income):
    for s in slabs:
        if s.get("up_to") is None or income <= s["up_to"]:
            return s["fixed"] + max(income - s["over"], 0) * s["rate"]
    return None


def cmd_sheet(a):
    d = json.load(open(a.docs, encoding="utf-8"))
    imap = json.load(open(os.path.join(REF, "iris-map.json"), encoding="utf-8"))["kinds"]
    slabs_all = json.load(open(a.slabs or os.path.join(REF, "slabs.json"), encoding="utf-8"))["tax_years"]
    lang, ty = a.lang, str(d.get("tax_year", ""))
    rows, warns, tot = [], [], {}
    for it in d["items"]:
        k = it.get("kind")
        m = imap.get(k)
        amt, tw = float(it.get("amount") or 0), float(it.get("tax_withheld") or 0)
        note = ""
        if m is None:
            note = "kind not in IRIS map: place it by hand"
            warns.append(f"{it.get('source', '?')}: unknown kind '{k}'")
        if not it.get("source"):
            warns.append(f"An item of kind {k} has no source document")
        if k == "freelance_remittance" and not it.get("reference"):
            note = "PRC number missing"
            warns.append(f"{it.get('source', '?')}: freelance remittance without PRC number. Get the PRC from your bank before filing.")
        if tw > amt and amt > 0:
            warns.append(f"{it.get('source', '?')}: tax withheld is more than the amount. Check the figure.")
        rows.append({"kind": k, "source": it.get("source", ""), "reference": it.get("reference", ""), "amount": amt, "tax_withheld": tw,
                     "iris_location": (m or {}).get("iris", ""), "note": note})
        t = tot.setdefault(k, [0.0, 0.0])
        t[0] += amt
        t[1] += tw
    print(f"Return worksheet, tax year {ty}, {d.get('taxpayer', '')}")
    hdr = f"{'kind':24}{'amount':>14}{'tax withheld':>14}  source | where it goes in IRIS"
    print(hdr)
    for r in rows:
        print(f"{r['kind']:24}{money(r['amount']):>14}{money(r['tax_withheld']):>14}  {r['source']} | {r['iris_location']}" + (f"  [{r['note']}]" if r["note"] else ""))
    print("Totals by kind:")
    for k, (x, y) in tot.items():
        print(f"  {k:24}{money(x):>14}{money(y):>14}")
    print(f"  {'ALL':24}{money(sum(v[0] for v in tot.values())):>14}{money(sum(v[1] for v in tot.values())):>14}")
    for w in warns:
        print("WARNING:", w)
    if any(not m.get("verified") for m in imap.values()):
        print("UNVERIFIED RULE: check the current IRIS screens (the 'where it goes' column is a guide, not official).")
    sl = slabs_all.get(ty)
    if sl and sl.get("verified") and sl.get("slabs"):
        taxable = tot.get("salary", [0, 0])[0] + tot.get("freelance_remittance", [0, 0])[0]
        tx = slab_tax(sl["slabs"], taxable)
        credit = sum(v[1] for v in tot.values())
        print(f"INDICATIVE tax on salary + freelance income {money(taxable)}: {money(tx)} (slabs: {sl['source_url']}, checked {sl['checked']}). "
              f"Withholding already shown: {money(credit)}. Final liability depends on final-tax items, exemptions, credits and rebates. Not computed here.")
    else:
        print(f"UNVERIFIED RULE: check {sl['source_url'] if sl else 'https://www.fbr.gov.pk'} (slab table for tax year {ty} not verified). "
              "Tax liability is NOT computed. Only the organised figures are shown.")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
            for k, (x, y) in tot.items():
                w.writerow({"kind": "TOTAL " + k, "source": "", "reference": "", "amount": x, "tax_withheld": y, "iris_location": "", "note": ""})
        print("Worksheet CSV written:", a.csv)
    print(NOTICE[lang])
    print(IRIS[lang])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("notice")
    n.add_argument("--notice", required=True)
    n.add_argument("--today")
    n.add_argument("--letter")
    r = sub.add_parser("return-sheet")
    r.add_argument("--docs", required=True)
    r.add_argument("--csv")
    r.add_argument("--slabs")
    for p in (n, r):
        p.add_argument("--lang", default="en", choices=["en", "roman", "ur"])
    a = ap.parse_args()
    try:
        (cmd_notice if a.cmd == "notice" else cmd_sheet)(a)
    except (OSError, ValueError, KeyError) as e:
        sys.exit(f"Input problem: {e!r}")


if __name__ == "__main__":
    main()
