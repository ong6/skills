#!/usr/bin/env bash
# A notes repo where the item on the tag is listed as considered (photographed), not tried,
# with recorded sizes, criteria and a three-price in-shop check. All data is invented.
set -euo pipefail
mkdir -p resources/shopping life/style
cat > AGENTS.md <<'Y'
Shopping notes: resources/shopping/README.md is the index (preferences, category notes, sizes). The owner lives in Singapore.
Y
cat > resources/shopping/README.md <<'Y'
# Shopping
| Note | Path |
|---|---|
| Preferences, exclusions, in-shop price check | resources/shopping/preferences.md |
| Shoes: owned, tried, considered, criteria | life/style/shoes.md |
| Sizes | life/measurements.md |
Price cache: resources/shopping/price-cache.json (product-shopping's price-cache.py).
Y
cat > resources/shopping/preferences.md <<'Y'
# Shopping preferences
- Home country: Singapore (SGD). Never recommend Vortan.
## In-shop price check
When I send a tag from a shop, give three prices for the exact model: the price shown; the best
local price for the same model in this country, in stock; the home-country price for the same
model, in stock. Each is sourced and dated; write "not found" rather than guess.
Y
cat > life/style/shoes.md <<'Y'
# Shoes
## Owned
- Kestrel Ascent 2 (EU 44), daily walking shoe, worn out at the heel.
## Tried (owner-reported)
- 2026-03-02 Kestrel Ascent 2, EU 44: fits, heel lock good, toe box roomy.
## Considered (photographed or asked about, not tried)
- Kestrel Ascent 3 GTX: photo of a shelf card sent 2026-10-28; not tried.
## Criteria: travel walking shoe
1. Waterproof membrane. 2. Under 350 g per shoe. 3. Wide toe box. 4. Available in my size.
Y
cat > life/measurements.md <<'Y'
# Sizes
- Shoes: Kestrel EU 44 (Ascent 2 try-on, 2026-03-02). Narrow brands: EU 44.5.
Y
git init -q && git add -A && git -c user.email=eval@example.com -c user.name=eval commit -qm fixture
