"""Generate bov-site.json + map-manifest.json for the five Gould Palmdale BOVs.

One generator, five deal repos. Every figure below traces to a Glen-approved
artifact in the deal folder:

  02_Extracted_Data/Property_Facts/*.json ......... physicals, pins, rent roll, T12
  03_Working_Analysis/Underwriting/
      buyer-normalized-underwriting.json .......... approved operating schedule
  03_Working_Analysis/Pricing/*/pricing.md ........ Glen-approved value + range (8/4)
  02_Extracted_Data/Sale_Comps/...md .............. LightBox-verified closed sales
  03_Working_Analysis/Comps/Phase 4 - *.md ........ rent + on-market survey
  gould-bov-workspace/media/media-manifest.json ... verified subject media
  gould-bov-workspace/pins.json ................... laaa-geo ROOFTOP comp pins

Deliberate omissions, each one a rule rather than an oversight:
  * No comp cap rate or comp GRM anywhere. Glen's 2026-08-04 gate: CoStar carries
    list-price marketing caps onto closed records and back-derives the NOI, so a
    stated comp cap proves nothing. The tables render "-".
  * No fire-hazard, landslide or CalEnviroScreen claim. Those sources returned
    null on the 2026-08-04 revalidation; only flood and Alquist-Priolo came back
    populated, so only those are stated.
  * No track-record count, volume or geography as fixed prose. Placeholders only;
    the build fills them from the current public pull.

Never hand-edit bov-site.json. Change this file and re-run.
"""
import json
import pathlib
import shutil

WS = pathlib.Path(r"C:\Users\gscher\gould-bov-workspace")
REPO_ROOT = pathlib.Path(r"C:\Users\gscher")
BRAND = pathlib.Path(r"C:\Users\gscher\LAAA-AI-Prompts\branding")
PINS = json.loads((WS / "pins.json").read_text(encoding="utf-8"))
PINE_GROVE = {"lat": 34.5746818, "lng": -118.1198429,
              "placeId": "ChIJF-eG8wNZwoARwRlq8CDCMYg"}   # second-pass ROOFTOP resolve

MONTH_YEAR = "August 2026"
CLIENT = "Elizabeth Gould"

# --- financing, per underwriting/interest_rate_engine.md -----------------------
# 5-year Treasury 4.40% (Federal Reserve H.15, observation 2026-08-03) + 200 bps
# default spread for a 5-year fixed, 55% LTV, $1.5M-$7M conventional bank loan on
# a decent LA County apartment building. Rounded down to the nearest 0.05%.
# No MMCC quote exists for this engagement; this is an indicative market
# assumption as of the BOV date, not a locked rate.
RATE = 6.40
AMORT = 30
LTV = 0.55
MIN_DSCR = 1.25


def loan_constant(rate_pct, years=AMORT):
    r = rate_pct / 100 / 12
    n = years * 12
    factor = r * (1 + r) ** n / ((1 + r) ** n - 1)
    return factor * 12


LC = loan_constant(RATE)


def first_year_principal(loan, rate_pct, years=AMORT):
    r = rate_pct / 100 / 12
    pay = loan * loan_constant(rate_pct, years) / 12
    bal = loan
    for _ in range(12):
        bal -= pay - bal * r
    return loan - bal


TEAM = [
    {"name": "Glen Scher", "title": "Senior Managing Director Investments",
     "phone": "(818) 212-2808", "tel": "8182122808",
     "email": "Glen.Scher@marcusmillichap.com", "license": "CA License: 01962976",
     "headshot": "images/team-Glen_Scher.png",
     "bio": "Glen Scher co-leads LA Apartment Advisors and advises apartment owners across "
            "Los Angeles County and the Antelope Valley on pricing, positioning and execution."},
    {"name": "Filip Niculete", "title": "Senior Managing Director Investments",
     "phone": "(818) 212-2748", "tel": "8182122748",
     "email": "Filip.Niculete@marcusmillichap.com", "license": "CA License: 01905352",
     "headshot": "images/team-Filip_Niculete.png",
     "bio": "Filip Niculete co-leads LA Apartment Advisors with a focus on disciplined "
            "marketing, buyer coverage and closing certainty on multifamily assignments."},
    {"name": "Blake Lewitt", "title": "Associate Investments",
     "phone": "(818) 212-2813", "tel": "8182122813",
     "email": "Blake.Lewitt@marcusmillichap.com", "license": "CA License: 02363670",
     "headshot": "images/team-Blake_Lewitt.png",
     "bio": "Blake Lewitt covers apartment ownership in the San Fernando Valley and the "
            "Antelope Valley and originated this assignment."},
]

TRACK_RECORD = {
    "metrics": [["{closed}", "Closed Transactions"], ["{volume}", "Total Sales Volume"],
                ["{apt_units}", "Apartment Units Sold"]],
    "narrative": [
        "The LAAA Team has closed {closed} transactions totaling {volume} across {geo}, "
        "including {apt_closed} apartment sales covering {apt_units} units.",
        "That record is built on the same discipline applied here: verified rent rolls and "
        "operating statements, comparable sales confirmed against recorded deeds rather than "
        "aggregator data, and a value conclusion a buyer's lender can follow."],
    # Copied verbatim from the locked Camarillo reference (Glen, 2026-08-06),
    # which is approved published team content. Blake Lewitt reported both
    # blocks rendering as bare headings on all five sites, because blocks.py
    # emits the labels unconditionally and these lists were empty.
    #
    # Nothing here is invented, per hard rule 3. The one entry that carries a
    # figure states a floor rather than a point value, so it cannot go stale in
    # the wrong direction as the team closes more: today's live pull is 490
    # closings and $1.55B against "490+" and "more than $1.5 billion", and both
    # are all-asset-class, matching the metric card and the narrative on the
    # same page. That denominator is the part Brio got wrong, not the "+".
    #
    # fill_copy() covers track_record["narrative"] and marketing["channels"]
    # only, so a {closed} placeholder would render literally here. Extending it
    # to these lists is a generator change and is not available under the pin.
    "achievements": [
        ["Chairman's Club", "Marcus & Millichap's top-tier annual honor"],
        ["National Achievement Award", "multiple years, both partners"],
        ["#1 Most Active Multifamily Team in LA County", "CoStar 2019-2021"],
        ["Sales Recognition Award", "every year since 2016"],
        ["490+ closed transactions", "more than $1.5 billion in sales volume"],
    ],
    "press": ["BISNOW", "YAHOO FINANCE", "CONNECT CRE", "SFVBJ", "THE PINNACLE LIST"],
}

MARKETING = {
    "metrics": [["{subscribers}", "Active Email Subscribers"]],
    "channels": [
        ["Direct owner and buyer outreach",
         "Named calls into the Antelope Valley buyer pool, the 1031 exchange buyers who have "
         "traded in this size class, and the private capital already holding product in Palmdale."],
        ["Marcus & Millichap platform",
         "National listing distribution, the firm's investor database, and coordination with "
         "MMCC on debt terms so a buyer arrives pre-qualified rather than exploring."],
        ["Dedicated digital presentation",
         "A property-specific offering site, targeted email, and syndication to the platforms "
         "Antelope Valley buyers actually search."]],
    "narrative": [
        "The buyer pool for a Palmdale apartment building at this size is narrow and "
        "identifiable. Recent closings in the submarket went to two groups: a regional "
        "operator buying on yield, and local private capital paying a premium for a clean, "
        "stabilized asset. A campaign has to reach both, because they price differently.",
        "Marketing begins only after the value conclusion is agreed. Nothing in this report "
        "has been distributed."],
}

DISCLOSURE_COMMON = [
    "This Broker Opinion of Value is an opinion prepared for the owner. It is not an "
    "appraisal and is not a guarantee of sale price.",
    "Operating figures are drawn from the owner's June 2026 rent roll and the trailing twelve "
    "month statement for July 2025 through June 2026. Annual columns were used throughout; "
    "individual monthly cells in the scanned statements carry optical character recognition "
    "damage and were not relied on.",
    "Expenses are presented on a buyer-normalized basis. Ownership payroll and management "
    "company overhead are replaced with a 4% third-party management fee, a separate resident "
    "manager rent credit required at 16 or more units in California, insurance at $1,325 per "
    "unit excluding earthquake coverage, and reserves. Property tax is reassessed at the "
    "value conclusion using effective rates observed on recently reassessed Palmdale sales, "
    "not the county default.",
    # The operating statement drops an expense line that is zero in both columns,
    # so the marketing line and its note are both absent from the rendered page.
    # Marketing is $0 on all five, which meant the reason it is underwritten at
    # zero was invisible on every live site. The disclosures always render, so
    # the explanation lives here and cannot be dropped with the line.
    "Marketing and advertising is underwritten at zero. The property is at or above 90% "
    "occupancy on the June 2026 rent roll and leases on organic demand. A buyer running a "
    "lease-up would carry a marketing budget.",
    "Unit square footages are an allocation of the assessor-verified gross building area "
    "across the rent roll unit mix, weighted by bedroom count. They are not a measured survey "
    "and will differ from advertised unit sizes.",
    "Comparable sale prices, dates, unit counts and building areas were verified against "
    "recorded deeds and assessment records. Cap rates and gross rent multipliers reported by "
    "commercial data services on those sales were not independently verified and are "
    "deliberately excluded.",
    "The collection loss line combines a 3% physical vacancy allowance with a credit loss "
    "allowance of 2% to 3% calibrated to this property's trailing delinquency. The operating "
    "table shows the two combined as a single reserve; it is not a 5% or 6% physical vacancy "
    "assumption.",
    "Rent comparables reflect current public asking rents accessed on August 4, 2026. Asking "
    "rents are not signed leases and are shown as market sensitivity only. Distances are "
    "straight line from the subject, computed from the same approved rooftop coordinates used "
    "to render the maps, and are not driving distances.",
    "Flood and earthquake fault findings were revalidated on August 4, 2026. Fire hazard "
    "severity, landslide susceptibility and environmental screening data were unavailable at "
    "that date and are not stated in this report.",
]


def miles(a, b):
    """Straight-line miles between two ROOFTOP pins.

    The Phase 4 survey carried eyeballed street-grid estimates, and the page
    prints them next to a map a seller can measure: Carmel showed 0.50 mi
    against pins 0.81 mi apart. Distances are now computed from the same
    approved coordinates the map is rendered from, and the narrative says they
    are straight-line.
    """
    import math
    lat1, lng1 = math.radians(a[0]), math.radians(a[1])
    lat2, lng2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2)
    return 2 * 3958.7613 * math.asin(math.sqrt(h))


WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
         7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}


def and_list(items):
    """Comma list ending in 'and'. A semicolon-joined run reads like a database
    dump in a paragraph a client reads."""
    items = list(items)
    if len(items) <= 1:
        return items[0] if items else ""
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def rent_bucket(unit_type):
    t = unit_type.split()[0].upper()
    return {"1BR": "one bedroom", "2BR": "two bedroom", "3BR": "three bedroom"}.get(t, t)


def alloc_sf(building_sf, mix):
    """Allocate verified gross building area across the unit mix by bedroom weight."""
    weights = {"0BR/1BA": 0.75, "1BR/1BA": 1.00, "2BR/1BA": 1.30,
               "2BR/1.5BA": 1.35, "2BR/2BA": 1.30, "3BR/1.5BA": 1.60}
    denom = sum(m["count"] * weights[m["type"]] for m in mix)
    base = building_sf / denom
    return {m["type"]: round(base * weights[m["type"]]) for m in mix}


SALE_COMPS = [
    {"key": "38633 Larkin Ave, Palmdale, CA 93550", "address": "38633 Larkin Avenue, Palmdale",
     "price": 2400000, "units": 18, "year_built": 1984, "building_sf": 15266, "lot_sf": 24829,
     "date": "September 5, 2024", "price_per_unit": 133333, "price_per_sf": 157.21,
     "summary": "Seven one-bedroom and eleven two-bedroom units in East Palmdale, sold out of a "
                "trust dissolution.",
     "relevance": "The closest East Palmdale sale on vintage and unit profile.",
     "considerations": "The building was 67% occupied at close with six vacant units, so the "
                       "price reflects a distressed operating basis and sits at the low end of "
                       "the range for a stabilized asset."},
    {"key": "1241 E Avenue R, Palmdale, CA 93550", "address": "1241 E Avenue R, Palmdale",
     "price": 2900000, "units": 18, "year_built": 1989, "building_sf": 19840, "lot_sf": 39204,
     "date": "July 16, 2024", "price_per_unit": 161111, "price_per_sf": 146.17,
     "summary": "An all two-bedroom, two-bath 1989 building with a pool, three blocks from the "
                "11th Street assets.",
     "relevance": "The closest product match in the pool on vintage, unit type and amenity, and "
                  "it shares the same tax rate area as three of the subjects.",
     "considerations": "An all-cash purchase by a local Palmdale buyer and a smaller asset, so "
                       "the price per unit carries a small-lot premium."},
    {"key": "937 E Avenue R, Palmdale, CA 93550", "address": "937 E Avenue R, Palmdale",
     "price": 4400000, "units": 32, "year_built": 1982, "building_sf": 21960, "lot_sf": 43560,
     "date": "September 10, 2024", "price_per_unit": 137500, "price_per_sf": 200.36,
     "summary": "A stabilized 32-unit, one-bedroom-weighted building in East Palmdale.",
     "relevance": "The best scale and mix analog in the pool for the one-bedroom-weighted assets, "
                  "and the highest verified price per square foot of any comparable.",
     "considerations": "Smaller average units drive the price per square foot well above the "
                       "pool median while the price per unit sits below it."},
    {"key": "1341 E Avenue R, Palmdale, CA 93550", "address": "1341 E Avenue R, Palmdale",
     "price": 3100000, "units": 17, "year_built": 1985, "building_sf": 18527, "lot_sf": 40946,
     "date": "December 24, 2024", "price_per_unit": 182353, "price_per_sf": 167.32,
     "summary": "Sixteen two-bedroom, two-bath townhome units plus one three-bedroom, in five "
                "buildings with attached garages.",
     "relevance": "The price per unit ceiling of the verified pool and evidence of what local "
                  "private capital pays for a superior product.",
     "considerations": "Townhome product with attached garages is a materially better physical "
                       "profile than any subject and should be read as a ceiling, not a target."},
    {"key": "4136 W Avenue L, Lancaster, CA 93536", "address": "4136 W Avenue L, Quartz Hill",
     "price": 2970000, "units": 27, "year_built": 1987, "building_sf": 25648, "lot_sf": 60984,
     "date": "March 13, 2025", "price_per_unit": 110000, "price_per_sf": 115.80,
     "summary": "An off-market 27-unit sale in Quartz Hill with deferred maintenance and four "
                "vacant units.",
     "relevance": "The verified floor of the range and the reference point for what a buyer pays "
                  "when condition and occupancy are impaired.",
     "considerations": "Off-market, deferred maintenance, and rents described as well below "
                       "market. Every metric on this sale carries a condition discount."},
    {"key": "4840 W Avenue L8, Lancaster, CA 93536", "address": "4840 W Avenue L8, Quartz Hill",
     "price": 5100000, "units": 34, "year_built": 1985, "building_sf": 27821, "lot_sf": 68389,
     "date": "November 21, 2025", "price_per_unit": 150000, "price_per_sf": 183.31,
     "summary": "Ten one-bedroom and twenty-four two-bedroom units with a pool, and the most "
                "recent arm's length apartment sale in the Antelope Valley comparable set.",
     "relevance": "The freshest transaction in the pool and the one carrying the most weight on "
                  "current market conditions.",
     "considerations": "A superior west-side Quartz Hill location and six vacant units at close. "
                       "The location premium argues for pricing the East Palmdale assets below "
                       "this price per unit."},
]

# Table cells carry the street address only. A 40-character "Name, 38722 11th
# Street East" string made the address column 6.3x the width of the narrowest
# column and failed audit_tables LOPSIDED at 390px and 768px. The community names
# are named in the rent narrative instead, where prose has room for them.
#
# square_feet is None on every row, deliberately. Only three of the nine listings
# publish a unit size, and the renderer averages a column over the rows that
# carry a value: with one of four rows populated it printed "850" under a header
# reading "Average (4 rent comps)", which is a false average on a client-facing
# page. Either every row carries a size or none does. The three published sizes
# are stated in the rent narrative instead, where they can be attributed.
RENT_COMP_LIBRARY = {
    "carmel-1br": {"key": "38722 11th St E, Palmdale, CA 93550",
                   "address": "38722 11th Street East",
                   "unit_type": "1BR 1BA", "rent": 1550, "square_feet": None, "distance": 0.5},
    "carmel-2br2ba": {"key": "38722 11th St E, Palmdale, CA 93550",
                      "address": "38722 11th Street East",
                      "unit_type": "2BR 2BA", "rent": 1815, "square_feet": None, "distance": 0.5},
    "carmel-3br": {"key": "38722 11th St E, Palmdale, CA 93550",
                   "address": "38722 11th Street East",
                   "unit_type": "3BR 2BA", "rent": 2150, "square_feet": None, "distance": 0.5},
    "colonial": {"key": "38719 10th St E, Palmdale, CA 93550",
                 "address": "38719 10th Street East",
                 "unit_type": "2BR 1BA", "rent": 1650, "square_feet": None, "distance": 0.4},
    "tenth-pl": {"key": "38572 10th Pl E, Palmdale, CA 93550",
                 "address": "38572 10th Place East", "unit_type": "1BR 1BA",
                 "rent": 1525, "square_feet": None, "distance": 0.3},
    "eleventh-2br": {"key": "38551 11th St E, Palmdale, CA 93550",
                     "address": "38551 11th Street East", "unit_type": "2BR 1BA",
                     "rent": 1850, "square_feet": None, "distance": 0.3},
    "shadow-springs": {"key": "38110 5th St E, Palmdale, CA 93550",
                       "address": "38110 5th Street East", "unit_type": "2BR",
                       "rent": 1625, "square_feet": None, "distance": 0.7},
    "mountain-shadows": {"key": "1240 E Avenue S, Palmdale, CA 93550",
                         "address": "1240 E Avenue S", "unit_type": "1BR",
                         "rent": 1535, "square_feet": None, "distance": 1.1},
    "ridgeview": {"key": "200 E Avenue R, Palmdale, CA 93550",
                  "address": "200 E Avenue R", "unit_type": "1BR",
                  "rent": 1475, "square_feet": None, "distance": 1.0},
}

RENT_COMP_NAMES = {
    "carmel-1br": "Carmel Apartments", "carmel-2br2ba": "Carmel Apartments",
    "carmel-3br": "Carmel Apartments", "colonial": "Colonial Terrace",
    "tenth-pl": "", "eleventh-2br": "",   # individually listed units, no community name
    "shadow-springs": "Shadow Springs", "mountain-shadows": "Mountain Shadows",
    "ridgeview": "Ridgeview Village",
}
#: Published unit sizes, where the listing states one. Named per comp key so the
#: narrative can cite only the sizes that belong to the rows this page renders.
RENT_COMP_SIZES = {"colonial": 800, "tenth-pl": 850, "eleventh-2br": 950}

ACTIVE_COMPS = [
    {"key": "PINE_GROVE", "address": "518 E Avenue Q-12, Palmdale",
     "status": "Active", "price": 5100000, "units": 30, "year_built": 1980,
     "building_sf": 22000, "lot_sf": 87120, "date": "Listed July 6, 2026",
     "price_per_unit": 170000, "price_per_sf": 231.82,
     "summary": "Pine Grove Casitas. Thirty units renovated in 2025 and offered at $5.1M, "
                "publicly listed as of August 4, 2026.",
     "relevance": "The only current Palmdale offering close to the subject size class.",
     "considerations": "Thirteen of thirty units, or 43%, were vacant at listing and the "
                       "advertised return is a stabilization projection rather than current "
                       "operations. The offering also includes development land. It is not "
                       "clean pricing evidence without normalizing all three."},
    {"key": "38225 9th St E, Palmdale, CA 93550",
     "address": "38225 9th Street East",
     "status": "Active", "price": 11250000, "units": 31, "year_built": 2026,
     "building_sf": 46500, "lot_sf": 108900, "date": "Listed June 8, 2026",
     "price_per_unit": 362903, "price_per_sf": 241.94,
     "summary": "Sierra Heights Townhomes. Thirty-one new two-bedroom, two-and-a-half-bath "
                "townhomes of about 1,500 square feet with garages, balconies and in-unit "
                "laundry, publicly listed as of August 4, 2026.",
     "relevance": "Shows the ceiling of new construction pricing in the same submarket and the "
                  "gap a buyer of existing product is buying below.",
     "considerations": "Under construction and unoccupied. New construction at more than double "
                       "the subject unit size is not an operating analog and its price per unit "
                       "is not comparable."},
]


def build_expense_lines(price, tax_rate, sc, insurance, reserves, pool, admin, units):
    """The client-facing expense schedule and its matching notes.

    Order is the order it renders.

    Note numbers are assigned AFTER the zero lines are dropped, and the note
    text is written for THIS property only.

    Both of those are Blake Lewitt findings, 2026-08-05, and both had reached
    all five live pages. The renderer drops an expense line that is zero in
    both columns (Glen, 2026-07-30) and the note goes with it, so fixed ids
    1-11 left a hole in the printed sequence: Marketing is $0 on all five, so
    every site printed 1-9 then 11, and Pool Service is $0 at 38238 and 38745,
    so those two printed 1-7, 9, 11. Numbering the survivors makes a hole
    unrepresentable rather than merely absent.

    The note text is built from the figures actually on the line, so a note can
    never quote a number the table does not show.
    """
    tax = round(price * tax_rate)
    rm_cur = round(sc["Current"]["normalized_repairs_maintenance"])
    rm_pf = round(sc["Pro Forma"]["normalized_repairs_maintenance"])
    # Per-unit allowances read off the line itself, never hardcoded per asset.
    rm_unit = round(rm_cur / units)
    admin_unit = round(round(admin) / units)
    pool_unit = round(round(pool) / units) if pool else 0

    rows = [
        ("Property Tax", tax, tax,
         "Reassessed at the value conclusion using the effective rate observed on recently "
         "reassessed Palmdale sales in the same tax rate area, not the Los Angeles County "
         "default. Direct assessments carried on the current bill are inside this figure."),
        ("Insurance", round(insurance), round(insurance),
         "$1,325 per unit, earthquake coverage excluded. It is set from documented trailing "
         "twelve month premiums rather than a broker estimate or a standard per-unit formula."),
        ("Utilities", round(sc["Current"]["normalized_utilities"]),
         round(sc["Pro Forma"]["normalized_utilities"]),
         "The owner's trailing twelve month actuals for the utilities this ownership pays, "
         "carried forward without adjustment. Tenant-paid utilities are not added back."),
        ("Repairs & Maintenance", rm_cur, rm_pf,
         f"A transferable allowance of ${rm_unit:,} per unit. It replaces the seller's "
         "maintenance payroll, contract labor, painting, supplies and turnover accounts, "
         "which are structured around a shared maintenance crew a buyer does not acquire."),
        ("Management Fee", round(sc["Current"]["management"]),
         round(sc["Pro Forma"]["management"]),
         "4% of gross scheduled rent, the LAAA standard for third-party management at this "
         "size. The seller's own management company fee and office payroll are removed rather "
         "than carried alongside it."),
        ("On-Site Manager Rent Credit", round(sc["Current"]["manager_credit"]),
         round(sc["Pro Forma"]["manager_credit"]),
         "California requires a manager residing on site at buildings of 16 or more units. The "
         "manager unit is carried at market rent in gross scheduled rent and the credit is "
         "shown as a separate expense. It is never folded into the management fee."),
        ("Landscaping, Pest & Life Safety", round(sc["Current"]["normalized_recurring_services"]),
         round(sc["Pro Forma"]["normalized_recurring_services"]),
         "The owner's trailing twelve month actuals for landscaping, pest control, fire "
         "extinguisher service and security, which transfer with the property."),
        ("Pool Service", round(pool), round(pool),
         (f"${pool_unit:,} per unit, carried because the trailing twelve month statement "
          "shows recurring pool service spend at this property.") if pool else
         "The property has no pool, so no pool service is underwritten."),
        ("Administrative", round(admin), round(admin),
         f"${admin_unit:,} per unit. It consolidates accounting, routine legal, bank charges, "
         "licensing and office costs into one transferable figure."),
        ("Marketing & Advertising", 0, 0,
         "Underwritten at zero. The property is at or above 90% occupancy on the June 2026 "
         "rent roll and leases on organic demand. A buyer running a lease-up would carry a "
         "marketing budget."),
        ("Reserves", round(reserves), round(reserves),
         "A replacement reserve set per property against building age and condition. It is not "
         "an expense the seller currently books; it is underwritten because a buyer's lender "
         "will require it."),
    ]

    # Two passes, because two generator rules disagree and both must be met.
    #
    # schema.py requires every $0 expense line to carry an explanatory note (a
    # Brio defect: trash at zero because the seller's P&L omitted it, which a
    # buyer pays anyway). sections.py drops a line that is zero in both columns
    # (Glen, 2026-07-30), and the note goes with it. So the schema mandates a
    # note the renderer guarantees nobody can read.
    #
    # Resolution here: number the lines that will actually print first, so the
    # reader sees a contiguous 1..N, then number the dropped zero lines after
    # them so the required explanation still exists in the record. Those trailing
    # notes are never emitted, because the renderer builds its note list only
    # from lines it printed. Where a zero line represents a real underwriting
    # decision a reader should be able to check, the explanation also goes in
    # the disclosures, which always render. Marketing is that case on all five.
    #
    # The contradiction itself is a generator defect and is reported separately.
    printed = [r for r in rows if r[1] or r[2]]
    dropped = [r for r in rows if not (r[1] or r[2])]
    ref_of, notes = {}, {}
    for i, (label, cur, pf, note) in enumerate(printed + dropped, start=1):
        ref_of[label] = i
        notes[str(i)] = [label, note]
    lines = [[label, cur, pf, ref_of[label]] for label, cur, pf, _ in rows]
    return tax, lines, notes




PROPERTIES = [
    dict(
        slug="38050-11th-st-e", name="38050 11th Street East", public_name="Pinecrest Apartments",
        facts_key="38050 11th St", apn="3014-003-026", units=32, building_sf=26392,
        lot_sf=43572, year_built=1989, zoning="PDR3", tra="15-574",
        lat=34.5740429, lng=-118.109303, place_id="ChIJXbHPAYtXwoARvmwQSQp8yUA",
        price=4750000, low=4450000, high=4850000, tax_rate=0.0167,
        insurance=42400, reserves=9600, pool=3200, admin=3200,
        mix=[{"type": "2BR/2BA", "count": 32, "monthly_current": 50848,
              "rent_current": 1589, "rent_market": 1745, "monthly_market": 55840}],
        pool_yes=True, laundry=True,
        parking="Gated on-site parking with assigned spaces",
        rent_comps=["carmel-2br2ba", "eleventh-2br", "colonial", "shadow-springs", "tenth-pl"],
        gallery=[("38050-11th-st-e-photo-02.jpg", "Courtyard and unit entries at 38050 11th Street East")],
        primary_comps="C2 at 1241 E Avenue R and C6 at 4840 W Avenue L8",
    ),
    dict(
        slug="38220-11th-st-e", name="38220 11th Street East", public_name="Shadow Park Apartments",
        facts_key="38220 11th St", apn="3014-028-003", units=36, building_sf=22170,
        lot_sf=43527, year_built=1981, zoning="PDR3", tra="15-574",
        lat=34.5764325, lng=-118.1090674, place_id="ChIJxU7g04tXwoAR5LY9IV3PcY4",
        price=4450000, low=4200000, high=4550000, tax_rate=0.0167,
        insurance=47700, reserves=10800, pool=3600, admin=3600,
        mix=[{"type": "1BR/1BA", "count": 35, "monthly_current": 45072,
              "rent_current": 1288, "rent_market": 1345, "monthly_market": 47075},
             {"type": "2BR/1BA", "count": 1, "monthly_current": 1545,
              "rent_current": 1545, "rent_market": 1545, "monthly_market": 1545}],
        pool_yes=True, laundry=True,
        parking="Gated parking with assigned spaces and covered bays",
        rent_comps=["carmel-1br", "tenth-pl", "mountain-shadows", "ridgeview", "colonial"],
        gallery=[("38220-11th-st-e-photo-02.jpg", "Pool courtyard at 38220 11th Street East"),
                 ("38220-11th-st-e-photo-03.jpg", "Two-story garden building and lawn at 38220 11th Street East"),
                 ("38220-11th-st-e-photo-04.jpg", "Interior courtyard walkways at 38220 11th Street East"),
                 ("38220-11th-st-e-photo-05.jpg", "Second garden building at 38220 11th Street East"),
                 ("38220-11th-st-e-photo-06.jpg", "Stone and timber detail on the street elevation at 38220 11th Street East"),
                 ("38220-11th-st-e-photo-07.jpg", "Covered parking bay on the street elevation at 38220 11th Street East")],
        primary_comps="C3 at 937 E Avenue R and C6 at 4840 W Avenue L8",
    ),
    dict(
        slug="38238-11th-st-e", name="38238 11th Street East", public_name="Parkside Apartments",
        facts_key="38238 11th St", apn="3014-028-002", units=36, building_sf=24856,
        lot_sf=43523, year_built=1985, zoning="PDR3", tra="15-574",
        lat=34.5769147, lng=-118.1090561, place_id="ChIJ36lyfolXwoARhEaYwZkNNoM",
        price=4950000, low=4750000, high=5050000, tax_rate=0.0167,
        insurance=47700, reserves=9000, pool=0, admin=3600,
        mix=[{"type": "1BR/1BA", "count": 22, "monthly_current": 27225,
              "rent_current": 1238, "rent_market": 29590 // 22, "monthly_market": 29590},
             {"type": "2BR/1BA", "count": 1, "monthly_current": 1595,
              "rent_current": 1595, "rent_market": 1595, "monthly_market": 1595},
             {"type": "2BR/2BA", "count": 13, "monthly_current": 20757,
              "rent_current": 1597, "rent_market": 1720, "monthly_market": 22360}],
        pool_yes=False, laundry=True,
        parking="Gated on-site parking with covered spaces",
        rent_comps=["carmel-1br", "carmel-2br2ba", "tenth-pl", "eleventh-2br", "ridgeview"],
        gallery=[("38238-11th-st-e-photo-02.jpg", "Landscaped courtyard at 38238 11th Street East"),
                 ("38238-11th-st-e-photo-03.jpg", "Garden walkway and planters at 38238 11th Street East")],
        primary_comps="C3 at 937 E Avenue R and C1 at 38633 Larkin Avenue",
    ),
    dict(
        slug="38745-15th-st-e", name="38745 15th Street East", public_name="Vista Del Sol Apartments",
        facts_key="38745 15th St", apn="3015-013-005", units=22, building_sf=13188,
        lot_sf=44999, year_built=1986, zoning="PDR3", tra="6-959",
        lat=34.5865653, lng=-118.1034116, place_id="ChIJ7aeS94RXwoAR3igTeD3nRCQ",
        price=2800000, low=2650000, high=2900000, tax_rate=0.0169,
        insurance=29150, reserves=5500, pool=0, admin=2200,
        mix=[{"type": "1BR/1BA", "count": 22, "monthly_current": 29806,
              "rent_current": 1355, "rent_market": 1475, "monthly_market": 32450}],
        pool_yes=False, laundry=False,
        parking="Eleven enclosed garages plus open on-site parking on a 1.03 acre corner lot",
        rent_comps=["tenth-pl", "carmel-1br", "mountain-shadows", "ridgeview"],
        gallery=[("38745-15th-st-e-photo-02.jpg", "Lawn frontage and unit entries at 38745 15th Street East"),
                 ("38745-15th-st-e-photo-03.jpg", "Corner elevation at 38745 15th Street East"),
                 ("38745-15th-st-e-photo-04.jpg", "Enclosed garages at 38745 15th Street East"),
                 ("38745-15th-st-e-photo-05.jpg", "Garage row at 38745 15th Street East")],
        primary_comps="C3 at 937 E Avenue R and C1 at 38633 Larkin Avenue",
    ),
    dict(
        slug="38705-20th-st-e", name="38705 20th Street East", public_name="Avalon Park Apartments",
        facts_key="38705 20th St E (Avalon Park)", apn="3015-031-013", units=76,
        building_sf=56256, lot_sf=212843, year_built=1971, zoning="LCR325U", tra="15-576",
        lat=34.5852256, lng=-118.0953681, place_id="ChIJtURmqJBXwoARyIBsJRAPtNA",
        price=9500000, low=9000000, high=9900000, tax_rate=0.0167,
        insurance=100700, reserves=26600, pool=7600, admin=5700,
        mix=[{"type": "0BR/1BA", "count": 12, "monthly_current": 12708,
              "rent_current": 1059, "rent_market": 1145, "monthly_market": 13740},
             {"type": "1BR/1BA", "count": 16, "monthly_current": 20470,
              "rent_current": 1279, "rent_market": 1345, "monthly_market": 21520},
             {"type": "2BR/1BA", "count": 23, "monthly_current": 34180,
              "rent_current": 1486, "rent_market": 1645, "monthly_market": 37835},
             {"type": "2BR/1.5BA", "count": 13, "monthly_current": 20185,
              "rent_current": 1553, "rent_market": 1695, "monthly_market": 22035},
             {"type": "3BR/1.5BA", "count": 12, "monthly_current": 21903,
              "rent_current": 1825, "rent_market": 1945, "monthly_market": 23340}],
        pool_yes=True, laundry=True,
        parking="Open on-site parking and carports on a 4.89 acre site",
        rent_comps=["carmel-1br", "carmel-2br2ba", "carmel-3br", "colonial",
                    "mountain-shadows", "ridgeview"],
        gallery=[("38705-20th-st-e-photo-02.jpg", "Pool and courtyard at Avalon Park"),
                 ("38705-20th-st-e-photo-03.jpg", "Courtyard and stairs at Avalon Park"),
                 ("38705-20th-st-e-photo-04.jpg", "Pool deck at Avalon Park")],
        primary_comps="C6 at 4840 W Avenue L8 and C1 at 38633 Larkin Avenue",
    ),
]

# Fix the one arithmetic defect found while reconciling the approved model to the
# rent roll. 38238's Phase 3 generator applied the manager gross-up with the wrong
# sign: the underwriting note says the identified employee unit is grossed from
# $1,295 to the locked $1,345 floor, "an annual adjustment of $600", but the stored
# GSR is $593,724, which is the rent-roll in-place total MINUS $600 rather than
# plus. Correcting it moves gross scheduled rent by $1,200 and net operating income
# by $1,080. It does not move the approved value conclusion or range, which were
# set on price per unit and price per square foot. Reported to Glen.
GSR_OVERRIDE = {"38238-11th-st-e": 594924.0}


def money_round(x):
    return int(round(x))


def build_property(p, un):
    sc = un["scenarios"]
    cur, pf = sc["Current"], sc["Pro Forma"]
    gsr_c = GSR_OVERRIDE.get(p["slug"], cur["gsr"])
    gsr_m = pf["gsr"]
    vac_pct = un["assumptions"]["vacancy"] * 100
    cl_pct = un["assumptions"]["credit_loss"] * 100

    # Recompute the current column from the (possibly corrected) GSR so every
    # figure on the page derives from one number rather than two sources.
    vac_c = gsr_c * un["assumptions"]["vacancy"]
    cred_c = gsr_c * un["assumptions"]["credit_loss"]
    # Quantize other income to the monthly figure the page prints, times twelve.
    # Carrying the raw annual left the monthly table x12 and the annual table
    # $2 to $4 apart, so a seller cross-footing the two found the operating
    # statement did not reconcile after we claimed line-by-line reconciliation.
    # The shift is at most $12 a year and it makes both tables exact.
    oi = money_round(cur["other_income"] / 12) * 12
    egi_c = gsr_c - vac_c - cred_c + oi
    mgmt_c = gsr_c * un["assumptions"]["management"]
    fixed = (cur["normalized_fixed_opex"] + cur["manager_credit"]
             + p["insurance"] + cur["reserves"])
    pre_tax_opex_c = fixed + mgmt_c
    pre_tax_noi_c = egi_c - pre_tax_opex_c

    # Recomputed on the same basis so both columns use the quantized other
    # income. Verified to reproduce the stored Phase 6 values exactly before the
    # quantization is applied.
    vac_m = gsr_m * un["assumptions"]["vacancy"]
    cred_m = gsr_m * un["assumptions"]["credit_loss"]
    egi_m = gsr_m - vac_m - cred_m + oi
    mgmt_m = gsr_m * un["assumptions"]["management"]
    pre_tax_opex_m = fixed + mgmt_m
    pre_tax_noi_m = egi_m - pre_tax_opex_m

    price = p["price"]
    tax, lines, expense_notes = build_expense_lines(
        price, p["tax_rate"],
        {"Current": dict(cur, management=mgmt_c), "Pro Forma": pf},
        p["insurance"], cur["reserves"], p["pool"], p["admin"], p["units"])
    exp_c = sum(r[1] for r in lines)
    exp_m = sum(r[2] for r in lines)
    noi_c = egi_c - exp_c
    noi_m = egi_m - exp_m

    loan = money_round(min(price * LTV, noi_c / (MIN_DSCR * LC)))
    ds = loan * LC
    principal = first_year_principal(loan, RATE)
    down = price - loan
    cf_c, cf_m = noi_c - ds, noi_m - ds

    sf_by_type = alloc_sf(p["building_sf"], p["mix"])
    mix = [dict(u, sf=sf_by_type[u["type"]],
                type=u["type"].replace("0BR/1BA", "Studio / 1BA").replace("/", " / "))
           for u in p["mix"]]

    rent_comps = []
    for k in p["rent_comps"]:
        rc = RENT_COMP_LIBRARY[k]
        pin = PINS[rc["key"]]
        rent_comps.append({"address": rc["address"], "unit_type": rc["unit_type"],
                           "rent": rc["rent"], "square_feet": rc["square_feet"],
                           "distance": round(miles((p["lat"], p["lng"]),
                                                   (pin["lat"], pin["lng"])), 2),
                           "image": None})

    sale_comps = [{k: v for k, v in c.items() if k != "key"} for c in SALE_COMPS]
    active = [{k: v for k, v in c.items() if k != "key"} for c in ACTIVE_COMPS]

    ppu, ppsf = price / p["units"], price / p["building_sf"]
    cap_c, cap_m = noi_c / price * 100, noi_m / price * 100
    grm_c, grm_m = price / gsr_c, price / gsr_m
    pool_txt = "a pool" if p["pool_yes"] else "no pool"
    laundry_txt = "on-site laundry" if p["laundry"] else "no common laundry"

    # No derived square-feet-per-unit line. The gross figure divided by the unit
    # count (824 at 38050) and the bedroom-weighted unit-mix allocation (825)
    # disagree by a square foot or two, and printing both on one page invites a
    # seller to ask which is right. Gross area is in the cover stats and unit
    # sizes are in the unit mix; the quotient adds nothing and can only conflict.
    # No "Operated as {public_name}" highlight. Blake Lewitt, 2026-08-05: it is
    # unnecessary, and it is redundant with the Investment Overview paragraph
    # directly below, which already opens with the property name.
    highlights = [
        f"{p['units']} units on a {p['lot_sf'] / 43560:.2f} acre site, built in {p['year_built']}",
        f"{p['building_sf']:,} gross building square feet",
        "Every unit occupied or leased on the June 2026 rent roll basis used here",
    ]
    if p["pool_yes"]:
        highlights.append("Pool confirmed by trailing twelve month pool service spend and by "
                          "current site photography")
    if p["laundry"]:
        highlights.append("On-site laundry, with laundry revenue in the trailing statement")
    highlights += [
        f"Assessor parcel {p['apn']}, zoned {p['zoning']}, tax rate area {p['tra']}",
        "FEMA Flood Zone X, outside the Special Flood Hazard Area, revalidated August 4, 2026",
        "Not within an Alquist-Priolo Earthquake Fault Zone and no mapped fault trace within "
        "500 metres, revalidated August 4, 2026",
    ]

    overview = [
        f"{p['public_name']} at {p['name']} is a {p['units']} unit apartment property built in "
        f"{p['year_built']} and held in the same family ownership since "
        f"{'2016' if p['slug'] != '38220-11th-st-e' else '1995'}. The building contains "
        f"{p['building_sf']:,} gross square feet on {p['lot_sf']:,} square feet of land, with "
        f"{pool_txt} and {laundry_txt}.",
        "This report values the property on its own merits. It is one of five individual "
        "opinions of value prepared for the ownership and carries no portfolio assumption, no "
        "blended pricing and no requirement that any other asset transact.",
        "The analysis rebuilds the operating statement on the basis a buyer would actually "
        "inherit. Ownership payroll and management company overhead come out, a 4% third-party "
        "management fee and the legally required resident manager credit go in, insurance is set "
        "at documented cost, and property tax is reassessed at the value conclusion. What "
        "remains is the income a new owner underwrites on day one.",
    ]

    location_narrative = [
        "The property sits in East Palmdale, the established rental core of the city, inside the "
        "Palmdale Elementary and Antelope Valley Union High School District attendance zones. "
        "Gateway Shopping Center is within roughly a mile and the Antelope Valley Mall, "
        "Palmdale Regional Medical Center and the Highway 14 corridor are a short drive.",
        "Palmdale is an incorporated city, so Los Angeles City rent stabilization does not apply. "
        "Residential rents are governed by the statewide framework under AB 1482.",
        "The 93550 ZIP code carries a population of roughly 81,500 with a median household income "
        "near $61,400. Renters occupy about 46% of households and the median gross rent is about "
        "$1,457, which places the in-place rents at this property in the working core of local "
        "demand rather than at the top of it.",
    ]

    physical_narrative = [
        f"The property is a {'two story ' if p['year_built'] < 1990 else 'two story '}"
        f"wood frame apartment building of {p['building_sf']:,} gross square feet across "
        f"{p['units']} units. {p['parking']}.",
        "Physical facts here come from the assessment record and current site photography "
        "published by the ownership's own management company, and from the June 2026 rent roll "
        "for the unit mix. Public amenity flags were not relied on."
        + (" The pool is a case in point: it is carried in the trailing twelve month operating "
           "statement as recurring pool service, and it appears in current site photography, "
           "while the public records for this parcel understate it. The operating statement and "
           "the photographs are the better evidence."
           if p["pool_yes"] else
           " Where the public record and the operating statement disagree on an amenity, the "
           "operating statement governs, because a line of recurring spend is harder evidence "
           "than a flag in an assessment file."),
        "A physical inspection, a roof and mechanical assessment, and a measured survey remain "
        "buyer diligence items. Nothing in this report substitutes for them.",
    ]

    market_narrative = [
        "Six closed apartment sales in Palmdale and Quartz Hill survive verification against "
        "recorded deeds and assessment records. Their verified prices run from $110,000 to "
        "$182,353 per unit and from $115.80 to $200.36 per square foot. Four of the six closed "
        "in 2024 and two in 2025, and the most recent, in November 2025, carries the most weight "
        "on current conditions.",
        "Eight further entries pulled in the same search were excluded and the reasons are on "
        "file: two affordable housing sales priced on an allocated portfolio basis, a senior "
        "conversion, a recreational vehicle park bought for battery storage land, a mobile home "
        "park, an undisclosed partnership interest transfer, a triplex portfolio, and one sale "
        "that a listing service had entered twice under two addresses.",
        "Building areas reported by the commercial data service were wrong on three of seven "
        "apartment sales, by as much as 21%, and one entry described a triplex as an 18 unit "
        "building. Every figure in the table below was re-verified before it was used.",
    ]

    positioning_narrative = [
        "Recent closings show two distinct buyers. A regional operator bought four of the six "
        "verified sales, financed at or near the full purchase price through a single lender "
        "relationship, and priced in a band of roughly $110,000 to $150,000 per unit. The two "
        "highest prices in the pool, at $161,111 and $182,353 per unit, went to local private "
        "buyers, one of them all cash.",
        "That split is the whole marketing question. The yield buyer sets the floor and will "
        "transact quickly. The premium is paid by local private and exchange capital that wants "
        "a clean, stabilized building it does not have to fix.",
    ]

    # Derived from the comps this property actually displays, never from the
    # survey-wide set. The earlier fixed paragraph named nine properties and a
    # $1,475 to $1,590 one-bedroom range while a given page rendered as few as
    # four rows with a $1,550 high, so a seller could disprove the sensitivity
    # from the same page. Generating it from p["rent_comps"] makes that
    # impossible by construction.
    buckets = {}
    for rc in rent_comps:
        buckets.setdefault(rent_bucket(rc["unit_type"]), []).append(rc["rent"])
    spread = and_list(
        f"{b} asks run ${min(v):,} to ${max(v):,}" if min(v) != max(v)
        else f"the {b} ask is ${min(v):,}"
        for b, v in buckets.items())
    # Dedupe by ADDRESS, not by comp key: Carmel contributes three rows under
    # three keys, and keying the list produced "Carmel Apartments at 38722 11th
    # Street East" three times in one sentence.
    by_addr = {}
    for k in p["rent_comps"]:
        by_addr.setdefault(RENT_COMP_LIBRARY[k]["address"], k)
    named = and_list([
        (f"{RENT_COMP_NAMES[k]} at {addr}" if RENT_COMP_NAMES[k]
         else f"an individually listed unit at {addr}")
        for addr, k in by_addr.items()])
    sized = [k for k in by_addr.values() if RENT_COMP_SIZES.get(k)]
    far = max(rc["distance"] for rc in rent_comps)

    rent_narrative = [
        "Pro forma rents are set at the highest rent actually achieved at this property for each "
        "unit type on the June 2026 rent roll. They are floors supported by signed leases in the "
        "building, not projections.",
        f"{WORDS[len(rent_comps)]} current asking rents in the table were accessed on August 4, "
        f"2026, and they sit above those floors: {spread}. Distances are straight line from this "
        f"building to each comparable, computed from the same approved coordinates the map is "
        f"drawn from, and no comparable in the set is more than {far:.2f} miles away. These are "
        f"advertised rents rather than signed leases and are shown as market sensitivity only.",
        f"The properties shown are {named}. "
        + ((("One of them publishes a unit size, "
             if len(sized) == 1 else f"{WORDS[len(sized)]} of them publish a unit size, ")
            + and_list(f"{RENT_COMP_LIBRARY[k]['address']} at {RENT_COMP_SIZES[k]:,} square feet"
                       for k in sized)
            + f". The size column reads as a dash because an average struck on "
              f"{len(sized)} of {len(rent_comps)} rows would misstate the set.")
           if sized else
           "None of them publishes a unit size, so the size column reads as a dash rather than "
           "carrying an average struck on partial data.")
        + (" Carmel Apartments is advertising one month free on selected two and three bedroom "
           "units, which indicates some concession pressure at the top of the range."
           if any(k.startswith("carmel") for k in p["rent_comps"]) else ""),
        "The owner's stated market rent column in this building's rent roll sits below rents the "
        "building is already achieving. That column is stale and was not used anywhere in this "
        "analysis.",
    ]

    valuation_narrative = [
        "Value is concluded from verified price per unit and price per square foot. That is a "
        "deliberate choice. None of the six comparable sales comes with an offering memorandum "
        "or a verified operating statement, so any cap rate attached to them would be a broker "
        "reported figure rather than a measured one. Commercial data services routinely carry a "
        "list price marketing cap onto a closed record and derive the income from it, which makes "
        "the arithmetic self-consistent and the conclusion meaningless.",
        f"At {'$%.2fM' % (price / 1e6)}, the property prices at ${ppu:,.0f} per unit and "
        f"${ppsf:,.2f} per square foot. The supporting evidence is {p['primary_comps']}.",
        "The cap rate and gross rent multiplier shown in the summary are calculated from this "
        "report's own reconstructed operating statement at the concluded value, with property "
        "tax reassessed. They are cross-checks on the conclusion, not the basis for it.",
    ]

    strategy = [
        {"title": "Lead with verified operations",
         "copy": "The June 2026 rent roll cross-foots to the printed totals to the dollar and the "
                 "trailing twelve month statement reconciles line by line. Handing a buyer a "
                 "reconciled package at launch removes the retrade that usually follows the first "
                 "week of diligence."},
        {"title": "Price to the local private buyer, not the yield buyer",
         "copy": "The two highest verified prices per unit in this submarket were paid by local "
                 "private capital, not by the regional operator that bought most of the volume. "
                 "The campaign should reach that buyer first."},
        {"title": "Show the reassessment honestly",
         "copy": "Palmdale sales reassess at effective rates of 1.47% to 1.72%, not the 1.2% "
                 "county shorthand. Underwriting the real number up front is what keeps a "
                 "financing contingency from becoming a price reduction."},
    ]

    buyer_profiles = [
        {"title": "Local private and 1031 exchange capital",
         "copy": "Antelope Valley owners and Los Angeles basin sellers trading into higher yield. "
                 "This buyer paid the two highest verified prices per unit in the comparable set "
                 "and values stabilized occupancy over renovation upside."},
        {"title": "Regional multifamily operator",
         "copy": "The buyer of four of the six verified comparable sales, financing through a "
                 "single lender relationship and underwriting to a yield target. Sets the floor "
                 "of the range and closes quickly."},
        {"title": "Owner operator adding to a Palmdale footprint",
         "copy": "A smaller private owner already managing in 93550, for whom another building "
                 "within a few blocks carries genuine operating leverage."},
    ]

    return {
        "slug": p["slug"], "short_name": p["name"],
        "address": p["name"], "city": "Palmdale, CA 93550",
        "submarket": "East Palmdale", "apn": p["apn"],
        "units": p["units"], "building_sf": p["building_sf"], "lot_sf": p["lot_sf"],
        "lot_acres": round(p["lot_sf"] / 43560, 3), "year_built": p["year_built"],
        "parking": p["parking"],
        "hero": f"images/{p['slug']}-hero.jpg",
        "price": price, "price_per_unit": money_round(ppu), "price_per_sf": round(ppsf, 2),
        "value_range": f"${p['low']:,} to ${p['high']:,}",
        "scheduled_rent": [money_round(gsr_c / 12), money_round(gsr_m / 12)],
        # Scheduled GROSS income is rent plus other income. It rendered as a
        # repeat of Total Scheduled Rent directly under an Additional Income row,
        # which silently dropped that row from the total a reader adds up. Struck
        # from the same rounded components the two rows above it display, so the
        # column literally sums on the page.
        "monthly_sgi": [money_round(gsr_c / 12) + money_round(oi / 12),
                        money_round(gsr_m / 12) + money_round(oi / 12)],
        "additional_income": [money_round(oi / 12), money_round(oi / 12)],
        "grm_current": round(grm_c, 2), "grm_market": round(grm_m, 2),
        "cap_current": round(cap_c, 2), "cap_market": round(cap_m, 2),
        "noi_current": money_round(noi_c), "noi_market": money_round(noi_m),
        "tax_rate": round(p["tax_rate"] * 100, 3),
        "expense_total": exp_c, "expense_per_unit": money_round(exp_c / p["units"]),
        "expense_per_sf": round(exp_c / p["building_sf"], 2),
        "unit_mix": mix,
        "operating": {
            # Same fix in the annual table, where the chain reads
            # Scheduled Gross Income - Vacancy = Gross Operating Income with no
            # other-income row between them. Rent alone made that subtraction
            # visibly wrong by the amount of the other income. GRM still divides
            # by scheduled RENT, never by this figure.
            "sgi": [money_round(gsr_c + oi), money_round(gsr_m + oi)],
            "vacancy": [money_round(vac_c + cred_c), money_round(vac_m + cred_m)],
            "vacancy_pct": round(vac_pct + cl_pct, 1),
            "goi": [money_round(egi_c), money_round(egi_m)],
            "expenses": [exp_c, exp_m],
            "expense_ratio": [round(exp_c / egi_c * 100, 1), round(exp_m / egi_m * 100, 1)],
            "noi": [money_round(noi_c), money_round(noi_m)],
            "loan_payments": [-money_round(ds), -money_round(ds)],
            "pretax_cf": [money_round(cf_c), money_round(cf_m)],
            "pretax_cf_pct": [round(cf_c / down * 100, 2), round(cf_m / down * 100, 2)],
            "principal_reduction": [money_round(principal), money_round(principal)],
            "total_return": [money_round(cf_c + principal), money_round(cf_m + principal)],
            "total_return_pct": [round((cf_c + principal) / down * 100, 2),
                                 round((cf_m + principal) / down * 100, 2)],
        },
        "expense_lines": lines, "expense_notes": expense_notes,
        "financing": {"loan_amount": loan, "rate": RATE, "amortization": AMORT,
                      "dcr": round(noi_c / ds, 2)},
        "highlights": highlights, "overview": overview,
        "location_title": "East Palmdale, the established rental core of the Antelope Valley",
        "location_narrative": location_narrative,
        "physical_narrative": physical_narrative,
        "market_narrative": market_narrative,
        "positioning_narrative": positioning_narrative,
        "rent_narrative": rent_narrative,
        "valuation_narrative": valuation_narrative,
        "strategy": strategy, "buyer_profiles": buyer_profiles,
        "disclosures": DISCLOSURE_COMMON,
        "gallery": [{"src": f"images/{f}", "alt": a} for f, a in p["gallery"]],
        "maps": {"subject": f"images/maps-{p['slug']}-subject.png",
                 "sale": f"images/maps-{p['slug']}-sale-comps.png",
                 "rent": f"images/maps-{p['slug']}-rent-comps.png",
                 "active": f"images/maps-{p['slug']}-active-comps.png"},
        "rent_comps": rent_comps, "sale_comps": sale_comps, "active_comps": active,
        "map_points": [], "track_record": {},
    }


def manifest_for(p):
    entries = [{"property": p["slug"], "category": "subject", "lat": p["lat"], "lng": p["lng"],
                "place_id": p["place_id"], "precision": "ROOFTOP", "needs_review": False}]
    for i, c in enumerate(SALE_COMPS, 1):
        r = PINS[c["key"]]
        entries.append({"property": p["slug"], "category": "sold", "order": i,
                        "lat": r["lat"], "lng": r["lng"], "place_id": r["placeId"],
                        "precision": "ROOFTOP", "needs_review": False})
    for i, k in enumerate(p["rent_comps"], 1):
        r = PINS[RENT_COMP_LIBRARY[k]["key"]]
        entries.append({"property": p["slug"], "category": "rent", "order": i,
                        "lat": r["lat"], "lng": r["lng"], "place_id": r["placeId"],
                        "precision": "ROOFTOP", "needs_review": False})
    for i, c in enumerate(ACTIVE_COMPS, 1):
        r = PINE_GROVE if c["key"] == "PINE_GROVE" else PINS[c["key"]]
        entries.append({"property": p["slug"], "category": "active", "order": i,
                        "lat": r["lat"], "lng": r["lng"], "place_id": r["placeId"],
                        "precision": "ROOFTOP", "needs_review": False})
    return {"entries": entries, "renders": {}}


def main() -> int:
    un_all = {r["property"]: r for r in json.loads((
        pathlib.Path(r"C:\Users\gscher\OneDrive - Marcus & Millichap\Niculete, Filip's files "
                     r"- LAAA Team\Proposals\Blake's Proposals\2026\Elizabeth Gould Portfolio"
                     r"\03_Working_Analysis\Underwriting\buyer-normalized-underwriting.json")
    ).read_text(encoding="utf-8"))}

    for p in PROPERTIES:
        site = REPO_ROOT / f"{p['slug']}-bov"
        (site / "images").mkdir(parents=True, exist_ok=True)

        # approved assets only
        src = WS / "media" / "approved" / p["slug"]
        for f in src.glob("*.jpg"):
            shutil.copy2(f, site / "images" / f.name)
        for logo in ("LAAA_Team_White.png", "LAAA_Team_Blue.png"):
            shutil.copy2(BRAND / "logos" / logo, site / "images" / logo)
        for person in ("Glen_Scher", "Filip_Niculete", "Blake_Lewitt"):
            shutil.copy2(BRAND / "headshots" / f"{person}.png",
                         site / "images" / f"team-{person}.png")

        prop = build_property(p, un_all[p["facts_key"]])
        data = {
            "schema_version": 2, "document_type": "bov", "site_mode": "single",
            "meta": {"domain": f"{p['slug']}.laaa.com", "client": CLIENT,
                     "title": p["name"], "subtitle": f"{p['units']}-Unit Multifamily Investment",
                     "month_year": MONTH_YEAR, "hero": prop["hero"]},
            "team": {"leads": TEAM, "grid": []},
            "track_record": TRACK_RECORD, "marketing": MARKETING,
            "properties": [prop],
        }
        (site / "bov-site.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Preserve the certified render digests when the pins are unchanged.
        # Rewriting `renders` as {} on every content edit would silently
        # decertify maps that still match their approved coordinates, and would
        # force a --force re-render that produces different bytes for the same
        # pins. If any pin moves, the digests are dropped and maps.py must run.
        manifest = manifest_for(p)
        mpath = site / "map-manifest.json"
        if mpath.is_file():
            prior = json.loads(mpath.read_text(encoding="utf-8"))
            if prior.get("entries") == manifest["entries"]:
                manifest["renders"] = prior.get("renders", {})
        mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"  {p['slug']:18s} price ${p['price']:>10,}  ${prop['price_per_unit']:>8,}/unit  "
              f"${prop['price_per_sf']:>7.2f}/SF  cap {prop['cap_current']}%  "
              f"GRM {prop['grm_current']}  DCR {prop['financing']['dcr']}  -> {site}")
    print(f"\nloan constant at {RATE}% / {AMORT}yr: {LC * 100:.4f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
