#!/usr/bin/env bash
# A tiny notes repo: a shopping index that maps categories to owned/wanted notes, plus sizes.
set -euo pipefail
mkdir -p resources/shopping life/style
cat > AGENTS.md <<'X'
Shopping notes: resources/shopping/README.md maps each category to the note listing what is owned and wanted.
X
cat > resources/shopping/README.md <<'X'
# Shopping
| Category | Owned and wanted |
|---|---|
| Clothes and shoes | life/style/products.md |
| Sizes | life/measurements.md |
Brand exclusions: never recommend Vans.
X
cat > life/style/products.md <<'X'
# Wardrobe
## Owned
- White leather court sneakers (Northline Court 78), the white work shoe; fits well.
- Black chinos, navy blazer.
## Wanted
- Black informal work shoe, casual-smart, pairs with the black chinos.
X
cat > life/measurements.md <<'X'
# Sizes
Shoes: ask for JP 28.0 first, then 28.5 (28.5 sometimes slightly large). Runs narrow brands: go 28.5.
X
git init -q && git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm fixture
