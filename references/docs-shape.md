# docs.json shape (Claude writes this after reading each document with vision)

```json
{
  "tax_year": "2027",
  "taxpayer": "Demo Taxpayer",
  "items": [
    {"kind": "salary", "source": "salary_certificate_demo_employer.pdf", "amount": 1200000, "tax_withheld": 60000, "reference": "certificate no."},
    {"kind": "bank_profit", "source": "bank_profit_certificate.pdf", "amount": 80000, "tax_withheld": 12000},
    {"kind": "withholding_certificate", "source": "cert.pdf", "amount": 0, "tax_withheld": 4000, "reference": "section on the certificate"},
    {"kind": "freelance_remittance", "source": "remittance_1.png", "amount": 500000, "tax_withheld": 0, "reference": "PRC number"}
  ]
}
```

- `kind`: salary, bank_profit, withholding_certificate, freelance_remittance. Other kinds are listed with "place it by hand".
- `amount` in rupees, as printed. For a foreign-currency remittance write the rupee amount shown on the PRC.
- Copy figures exactly. Leave a field out if you cannot read it. Never guess.
- `source` is the file name of the document the figure came from. The worksheet shows it next to each figure.

# notice.json shape

```json
{"section": "114(4)", "tax_year": "2024", "date_issued": "2026-11-10", "deadline": "2026-12-05",
 "notice_no": "as printed", "office": "RTO or CTO name", "taxpayer_name": "", "ntn": "", "demand": null}
```
Dates as YYYY-MM-DD. `demand` in rupees or null.
