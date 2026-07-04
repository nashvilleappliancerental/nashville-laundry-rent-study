# Data dictionary

Collect one row per advertised listing into `listings.csv` (copy the header from
`template.csv`, which stays empty as the schema example). Fill every column.
Rows missing any of the key fields (rent, bedrooms, bathrooms, sqft,
property_type, area, laundry) are dropped during cleaning.

| Column | Type | Allowed values / format | Notes |
|--------|------|-------------------------|-------|
| `listing_id` | text | any unique string | Your own id, or the portal's. Keeps rows traceable and de-duplicated. |
| `rent` | number | monthly rent in whole dollars (e.g. `1650`) | Advertised asking rent. Cleaning trims to $400–$6,000 to drop typos. |
| `bedrooms` | integer | `0` for a studio, else `1`, `2`, `3`, … | Use `0` for studios. |
| `bathrooms` | number | `1`, `1.5`, `2`, … | Half baths allowed. |
| `sqft` | integer | interior square feet (e.g. `850`) | Advertised square footage. |
| `property_type` | category | `apartment` \| `condo` \| `townhome` \| `house` | Lowercase. |
| `area` | category | one of the 6 area buckets below | Be consistent — the model treats each label as its own group. |
| `laundry` | category | `in_unit` \| `hookups` \| `shared` \| `none` | See definitions below. This is the variable of interest. |
| `date_collected` | date | `YYYY-MM-DD` | When you recorded the listing. |
| `source` | text | e.g. the portal name | Where the listing came from. |

## Area buckets (pick one per listing)

Use these six consistently. The exact taxonomy matters less than applying it the
same way every time:

- `Downtown/Core` — Downtown, The Gulch, SoBro, Germantown
- `East Nashville` — East Nashville, Inglewood, Shelby
- `South Nashville` — 12South, Berry Hill, Wedgewood-Houston, 8th Ave S
- `West Nashville` — West End, Sylvan Park, The Nations, Charlotte Ave
- `North Nashville` — North Nashville, Bordeaux, Whites Creek
- `Southeast/Antioch` — Antioch, Priest Lake, Cane Ridge

## Laundry categories

- `in_unit` — a washer and dryer **inside the unit** (the variable this study is about).
- `hookups` — connections for a washer/dryer are present, but no machines provided.
- `shared` — a shared/communal laundry room in the building or complex.
- `none` — no in-unit machines, no hookups, no shared facility advertised.

## Sampling notes (important for honesty)

Record **actively advertised listings** from a defined source (ideally a single
portal, over a defined window). This is a sample of what is *on the market*, not
of all housing stock, and it reflects one portal's coverage. Keep the frame
consistent so the comparison is apples-to-apples, and write down exactly what you
did (portal, dates, any filters) so the method is reproducible.
