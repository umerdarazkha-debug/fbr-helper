#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
PY="python3 scripts/fbr_helper.py"
F=tests/fixtures
OUT="$(mktemp -d)"
fail=0
expect() { if grep -qF -- "$3" <<<"$2"; then echo "ok   $1"; else echo "FAIL $1: missing '$3'"; fail=1; fi; }
refute() { if grep -qF -- "$3" <<<"$2"; then echo "FAIL $1: should not contain '$3'"; fail=1; else echo "ok   $1"; fi; }

# notice: 114(4) issued 10 Nov, deadline 5 Dec, today 26 Nov => 9 days left
out=$($PY notice --notice $F/notice_114_4.json --today 2026-11-26 --letter "$OUT/r.txt")
expect days "$out" "Days left: 9"
refute not-soon "$out" "Less than 8 days"
expect section-text "$out" "Notice to file a return (sub-section 4)"
expect unverified "$out" "UNVERIFIED RULE: check https://download1.fbr.gov.pk"
expect notice-line "$out" "This is a helper, not professional advice. Check the figures before you act."
expect never-logs-in "$out" "File through IRIS yourself; this tool never logs in."
expect letter "$(cat $OUT/r.txt)" "Subject: Notice no. DEMO/0001 under section 114(4), tax year 2024"
expect letter-docs "$(cat $OUT/r.txt)" "- CNIC / NTN"

# 3 days left triggers the warning; same day; overdue
out=$($PY notice --notice $F/notice_114_4.json --today 2026-12-02)
expect days3 "$out" "Days left: 3"
expect soon "$out" "Less than 8 days left"
out=$($PY notice --notice $F/notice_114_4.json --today 2026-12-05)
expect deadline-today "$out" "Deadline is TODAY"
out=$($PY notice --notice $F/notice_182_overdue.json --today 2026-11-26 --lang roman)
expect overdue "$out" "6 din ki derr ho chuki hai"
expect demand "$out" "Demand: Rs 25,000"
expect sec182 "$out" "Penalties"
out=$($PY notice --notice $F/notice_182_overdue.json --today 2026-11-26 --lang ur --letter "$OUT/u.txt")
expect urdu-overdue "$out" "6 دن کی تاخیر"
expect urdu-letter "$(cat $OUT/u.txt)" "بخدمت"

# unknown section must be reported as not in the table, with no made-up explanation
out=$($PY notice --notice $F/notice_unknown.json --today 2026-11-26)
expect unknown "$out" "Section 999 is NOT IN THE TABLE"
refute unknown-no-explain "$out" "What it means"

# sub-section not in table falls back to the parent and says so
sed 's/114(4)/114(2)/' $F/notice_114_4.json > "$OUT/n2.json"
out=$($PY notice --notice "$OUT/n2.json" --today 2026-11-26)
expect parent "$out" "Sub-section 114(2) is not in the table; showing the parent section 114."

# return sheet: salary 1,500,000 (60,000 withheld), bank 80,000 (12,000), cert 4,000, freelance 750,000
out=$($PY return-sheet --docs $F/docs.json --csv "$OUT/w.csv" --slabs $F/slabs_test.json | tr -s " ")
expect total-salary "$out" " salary 1,500,000 60,000"
expect total-freelance "$out" " freelance_remittance 750,000 0"
expect total-all "$out" " ALL 2,330,000 76,000"
expect source-col "$out" "salary_certificate_demo_employer.pdf"
expect iris-col "$out" "Salary section"
expect prc-warning "$out" "remittance_2.png: freelance remittance without PRC number"
# test-only slabs (verified): income 2,250,000 -> 20,000 + 0.2 x (2,250,000 - 300,000) = 410,000
expect indicative "$out" "INDICATIVE tax on salary + freelance income 2,250,000: 410,000"
csv=$(cat "$OUT/w.csv")
expect csv-source "$csv" "demo_bank_profit_certificate.pdf"
expect csv-total "$csv" "TOTAL salary"

# real slab file is unverified: no tax figure, UNVERIFIED printed
out=$($PY return-sheet --docs $F/docs_ty2027.json | tr -s " ")
refute no-tax "$out" "INDICATIVE"
expect unverified-slabs "$out" "Tax liability is NOT computed"
expect unverified-rule "$out" "UNVERIFIED RULE: check https://www.fbr.gov.pk (slab table for tax year 2027 not verified)"
expect sheet-totals "$out" " salary 1,500,000 60,000"

# bad input fails
$PY notice --notice /nonexistent.json >/dev/null 2>&1 && { echo "FAIL bad input accepted"; fail=1; } || echo "ok   bad-input rejected"

[ $fail -eq 0 ] && echo "ALL PASS" || { echo "FAILED"; exit 1; }
