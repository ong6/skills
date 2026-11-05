---
type: regex
target: last_message
pattern: "(get|buy|recommend|pick|go with|try)[^.\\n]{0,40}Vans"
flags: i
match: not_contains
---

Never recommends the excluded brand (naming it as excluded is fine).
