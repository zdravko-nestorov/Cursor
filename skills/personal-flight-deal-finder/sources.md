# Sources and lookup templates

Reference for `personal-flight-deal-finder`. Everything here is a starting point.
Confirm every number on the live page. Never quote a price from this file.

## Deep-link templates

Replace `SOF`, `NBO`, and the dates. Keep the date format each site uses.

| Site | Template | Date format |
| --- | --- | --- |
| Google Flights | `https://www.google.com/travel/flights?q=Flights%20to%20NBO%20from%20SOF%20on%202026-09-08%20through%202026-09-19` | `YYYY-MM-DD` |
| Google Flights, month | `https://www.google.com/travel/flights?q=flights%20from%20SOF%20to%20NBO%20in%20September%202026` | words |
| Kayak | `https://www.kayak.com/flights/SOF-NBO/2026-09-08/2026-09-19?sort=price_a` | `YYYY-MM-DD` |
| Kayak, flexible | `https://www.kayak.com/flights/SOF-NBO/2026-09-08-flexible/2026-09-19-flexible` | `YYYY-MM-DD` |
| Momondo | `https://www.momondo.com/flight-search/SOF-NBO/2026-09-08/2026-09-19` | `YYYY-MM-DD` |
| Skyscanner | `https://www.skyscanner.net/transport/flights/sof/nbo/260908/260919/` | `YYMMDD`, lowercase codes |
| Kiwi.com | `https://www.kiwi.com/en/search/results/sofia-bulgaria/nairobi-kenya/2026-09-08/2026-09-19` | `YYYY-MM-DD` |

Notes:

- Kayak, Momondo, Cheapflights and HotelsCombined belong to one company. They
  count as one source, never as two.
- Kiwi.com is the best place to find self-transfer combinations. It is also the
  place where the split-ticket risks in Step 6 apply hardest.
- Use a site's local domain when one exists, so prices come back in the origin
  country's currency instead of USD.
- If a template stops working, run one search by hand and copy the real URL the
  site produced. Then reuse that shape.

## Tools that need a human

Give these to the user as links when a page will not load for you. Do not claim
any number from them unless you actually read it.

- ITA Matrix, `https://matrix.itasoftware.com/`. Best calendar of lowest fares
  and best routing control. Needs a real browser.
- Azair, `https://www.azair.eu/`. Strong for flexible-date low-cost combinations
  inside Europe. Useful for the first leg of a split ticket.
- Google Flights Explore, `https://www.google.com/travel/explore`. Price map for
  a flexible destination.

## Carrier enumeration for Step 7

- `https://www.flightsfrom.com/SOF` and `https://www.flightsfrom.com/NBO` list
  every route and the airline flying it.
- The Wikipedia article for each airport has an "Airlines and destinations"
  table. It fetches reliably and is a good cross-check.
- The destination airport's own site publishes its airline list.

Airlines that commonly connect Europe to East Africa, so you have somewhere to
start the airline-direct price check: Turkish Airlines, Qatar Airways, Emirates,
Etihad, Ethiopian Airlines, Kenya Airways, EgyptAir, Saudia, flydubai, RwandAir,
Lufthansa, Swiss, Austrian, Air France, KLM, British Airways, ITA Airways.
Confirm which of them actually serve the route today. Do not assume.

## Price history for Step 5

- Google Flights prints a price graph, a date grid, and an insight line saying
  prices are low, typical, or high for the route. This is the single strongest
  source. Cite the insight line word for word.
- Kayak shows a price trend and a buy-or-wait forecast on the results page.
- Skyscanner's whole-month view shows the cheapest day per month, which gives a
  seasonal shape.
- Hopper publishes route and season research on its blog and press pages.

Only one of them loading means confidence is low. Say so.

## Fee traps to check before quoting a total

Read the price-breakdown panel on the results or fare page. It appears before any
passenger form. Never enter personal or card data to reveal a price.

| Source | What to look for |
| --- | --- |
| eDreams | Membership subscription added by default, service fee, card fee |
| Gotogate, Mytrip, Flightnetwork | Service fee, paid "flexible ticket" add-on |
| Kiwi.com | Self-transfer protection is a paid add-on, bags added at checkout |
| Trip.com | Some fees appear only at the final step |
| Any OTA | Currency shown differs from the card currency, so the bank converts |
| Low-cost carriers | Overhead cabin bag is paid, only an under-seat bag is free |

A fare brand can also hide cost. Check what the cheapest brand includes on the
airline's own fare-brand page, for example a light or basic economy fare with no
checked bag and no changes.

## Preset `sof-nbo-sep2026` nearby airports

Origin side, with rough distance from Sofia by road:

| Airport | City | Distance | Worth it when |
| --- | --- | --- | --- |
| PDV | Plovdiv | 150 km | Rarely, very few routes |
| INI | Nis | 170 km | A low-cost first leg beats the SOF fare |
| SKP | Skopje | 240 km | Same |
| SKG | Thessaloniki | 330 km | Direct bus, more long-haul connections |
| OTP | Bucharest | 380 km | Bus or train, a real hub with more carriers |
| BEG | Belgrade | 400 km | More long-haul options, longer ground leg |
| IST, SAW | Istanbul | 550 km | Only for a large gap, long bus ride |
| VAR, BOJ | Varna, Burgas | 400 to 470 km | Almost never for this direction |

Always add the ground cost and time to the total before comparing.

Destination side: Nairobi has no practical nearby international alternate. Wilson
airport is domestic only. Mombasa, Kilimanjaro, Entebbe and Dar es Salaam are
separate destinations, so use them only for an open-jaw idea, and add the onward
cost.

## Trip admin that changes the real cost

Mention these as conditions, not as prices, unless a source gives the fee.

- Destination entry rules. Kenya uses an online travel authorisation that every
  visitor applies for before travel.
- Transit rules of every layover country. A self-transfer that leaves the
  airside area needs entry permission for that country.
- Both apply per passport. Tell the user to check their own.
