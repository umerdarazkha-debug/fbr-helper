# fbr-helper

Two helpers for FBR income tax paperwork in Pakistan. English, Roman Urdu and Urdu script.

1. **Notice mode**: read a notice into `notice.json`, get days left, a plain explanation of the section, the documents to gather and a draft reply letter.
2. **Return-sheet mode**: turn salary, bank profit, withholding certificates and freelance remittance (PRC) figures into a worksheet that shows the source file and where each figure goes in IRIS.

## Install
Copy this folder to `~/.claude/skills/fbr-helper`. Standard library only (Python 3.9 or newer).

## Not included
- It never logs in to IRIS or any FBR system. You file yourself.
- It does not compute final tax. Slabs for tax year 2027 are not in `references/slabs.json` because no official table was retrieved. Add them from the Finance Act or FBR website to get an indicative figure.
- Section explanations are plain-language and marked UNVERIFIED with a source link. Read the section before you rely on it.

## Tests
`bash tests/run.sh` (offline, fake names and numbers).

This is a helper, not professional advice. Check the figures before you act.

## Install

```bash
git clone https://github.com/umerdarazkha-debug/fbr-helper ~/.claude/skills/fbr-helper
```

## License

MIT
