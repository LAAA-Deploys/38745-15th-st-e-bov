"""Independent arithmetic verification of every published figure.

Reads each deployed bov-site.json and re-derives the numbers from first
principles, then compares. This does not trust the generator; it recomputes.
Also re-checks each figure against the Glen-approved Phase 5 pricing conclusions.
"""
import json
import pathlib
import re

SITES = ["38050-11th-st-e", "38220-11th-st-e", "38238-11th-st-e",
         "38745-15th-st-e", "38705-20th-st-e"]

APPROVED = {   # Glen, 2026-08-04
    "38050-11th-st-e": (4750000, 4450000, 4850000, 32, 26392),
    "38220-11th-st-e": (4450000, 4200000, 4550000, 36, 22170),
    "38238-11th-st-e": (4950000, 4750000, 5050000, 36, 24856),
    "38745-15th-st-e": (2800000, 2650000, 2900000, 22, 13188),
    "38705-20th-st-e": (9500000, 9000000, 9900000, 76, 56256),
}

fails, notes = [], []


def close(a, b, tol=1.0):
    return abs(a - b) <= tol


def main() -> int:
    for slug in SITES:
        root = pathlib.Path(rf"C:\Users\gscher\{slug}-bov")
        d = json.loads((root / "bov-site.json").read_text(encoding="utf-8"))
        p = d["properties"][0]
        html = (root / "index.html").read_text(encoding="utf-8")
        mf = json.loads((root / "map-manifest.json").read_text(encoding="utf-8"))
        op = p["operating"]
        price, low, high, units, sf = APPROVED[slug]
        say = lambda m: fails.append(f"{slug}: {m}")  # noqa: E731

        # 1. approved conclusion
        if p["price"] != price:
            say(f"price {p['price']:,} != approved {price:,}")
        if p["value_range"] != f"${low:,} to ${high:,}":
            say(f"value_range {p['value_range']!r} != approved ${low:,} to ${high:,}")
        if p["units"] != units or p["building_sf"] != sf:
            say(f"units/SF {p['units']}/{p['building_sf']} != verified {units}/{sf}")

        # 2. pay metrics
        if not close(p["price_per_unit"], price / units, 1):
            say(f"price_per_unit {p['price_per_unit']} != {price / units:.0f}")
        if not close(p["price_per_sf"], price / sf, 0.01):
            say(f"price_per_sf {p['price_per_sf']} != {price / sf:.2f}")

        # 3. unit mix reconciles to scheduled rent (the GRM divisor)
        mix_c = sum(u["monthly_current"] for u in p["unit_mix"])
        mix_m = sum(u["monthly_market"] for u in p["unit_mix"])
        if mix_c != p["scheduled_rent"][0]:
            say(f"unit mix current {mix_c:,} != scheduled_rent {p['scheduled_rent'][0]:,}")
        if mix_m != p["scheduled_rent"][1]:
            say(f"unit mix market {mix_m:,} != scheduled_rent[1] {p['scheduled_rent'][1]:,}")
        for u in p["unit_mix"]:
            if u["count"] * u["rent_current"] and abs(u["count"] * u["rent_current"]
                                                      - u["monthly_current"]) > u["count"]:
                say(f"unit row {u['type']}: {u['count']}x{u['rent_current']} strays from "
                    f"stated total {u['monthly_current']}")

        # 4. GRM divides by scheduled RENT, never gross income. Asserting it
        # against operating.sgi was wrong once sgi correctly included other
        # income; the divisor is the annualized unit mix.
        annual_rent = mix_c * 12
        if not close(p["grm_current"], price / annual_rent, 0.01):
            say(f"grm_current {p['grm_current']} != price/scheduled rent "
                f"{price / annual_rent:.2f}")
        if not close(p["grm_market"], price / (mix_m * 12), 0.01):
            say(f"grm_market {p['grm_market']} != price/market rent "
                f"{price / (mix_m * 12):.2f}")
        if close(p["grm_current"], price / op["sgi"][0], 0.005):
            say("grm_current equals price divided by gross income; that is a GIM, not a GRM")
        # the three rows the page asks a reader to add up must actually add up
        if p["monthly_sgi"][0] != p["scheduled_rent"][0] + p["additional_income"][0]:
            say(f"monthly SGI {p['monthly_sgi'][0]:,} != scheduled rent + additional income "
                f"{p['scheduled_rent'][0] + p['additional_income'][0]:,}")

        # 5. operating chain
        for i, label in ((0, "current"), (1, "market")):
            # sgi now carries other income, so the annual chain the page prints
            # is simply SGI - vacancy = GOI. Tolerance covers component rounding.
            goi = op["sgi"][i] - op["vacancy"][i]
            if not close(goi, op["goi"][i], 2):
                say(f"{label} GOI {op['goi'][i]:,} != sgi - vacancy + other = {goi:,.0f}")
            noi = op["goi"][i] - op["expenses"][i]
            if not close(noi, op["noi"][i], 2):
                say(f"{label} NOI {op['noi'][i]:,} != GOI - expenses = {noi:,.0f}")
            lines = sum(r[1 + i] for r in p["expense_lines"])
            if lines != op["expenses"][i]:
                say(f"{label} expense lines sum {lines:,} != expenses {op['expenses'][i]:,}")
            if not close(op["expense_ratio"][i], op["expenses"][i] / op["goi"][i] * 100, 0.1):
                say(f"{label} expense ratio {op['expense_ratio'][i]} != "
                    f"{op['expenses'][i] / op['goi'][i] * 100:.1f}")
            cap = op["noi"][i] / price * 100
            got = p["cap_current"] if i == 0 else p["cap_market"]
            if not close(got, cap, 0.02):
                say(f"{label} cap {got} != NOI/price = {cap:.2f}")
            if not (35 <= op["expense_ratio"][i] <= 55):
                notes.append(f"{slug}: {label} expense ratio {op['expense_ratio'][i]}% is "
                             f"outside the 35-55% band")

        # 6. property tax is reassessed at the concluded value
        tax = next(r[1] for r in p["expense_lines"] if r[0] == "Property Tax")
        if not close(tax, price * p["tax_rate"] / 100, 2):
            say(f"property tax {tax:,} != {p['tax_rate']}% of price "
                f"({price * p['tax_rate'] / 100:,.0f})")

        # 7. financing: loan constant, debt service, DCR, LTV
        fin = p["financing"]
        r_m = fin["rate"] / 100 / 12
        n = fin["amortization"] * 12
        lc = r_m * (1 + r_m) ** n / ((1 + r_m) ** n - 1) * 12
        ds = fin["loan_amount"] * lc
        if not close(ds, -op["loan_payments"][0], 2):
            say(f"debt service {-op['loan_payments'][0]:,} != loan x constant = {ds:,.0f}")
        if not close(fin["dcr"], op["noi"][0] / ds, 0.02):
            say(f"DCR {fin['dcr']} != NOI/DS = {op['noi'][0] / ds:.2f}")
        ltv = fin["loan_amount"] / price
        if ltv > 0.5501:
            say(f"LTV {ltv:.1%} exceeds the stated 55% maximum")
        if fin["dcr"] < 1.25:
            say(f"DCR {fin['dcr']} is below the 1.25x minimum")
        if not close(op["pretax_cf"][0], op["noi"][0] - ds, 2):
            say("pretax cash flow does not equal NOI minus debt service")

        # 8. no comp cap or GRM published anywhere
        for c in p["sale_comps"] + p["active_comps"]:
            if c.get("cap_rate") or c.get("grm"):
                say(f"comp {c['address']} publishes a cap rate or GRM")
            if not close(c["price_per_unit"], c["price"] / c["units"], 1):
                say(f"comp {c['address']} $/unit does not follow from price/units")
            if not close(c["price_per_sf"], c["price"] / c["building_sf"], 0.02):
                say(f"comp {c['address']} $/SF does not follow from price/SF")

        # 9. Price discipline. Truncating at #property-info, as the shipped gate
        # does, also skips #rent-comps, which sits between Buyer Profile and Sale
        # Comps. Excise only the property-info block and scan everything else
        # before the reveal.
        head = html.split('id="sale-comps"')[0]
        if 'id="property-info"' in head:
            before, rest = head.split('id="property-info"', 1)
            head = before + (rest.split('id="rent-comps"', 1)[1]
                             if 'id="rent-comps"' in rest else "")
        for token in (f"${price:,}", f"${p['price_per_unit']:,}", f"{p['cap_current']}%",
                      f"{p['grm_current']}"):
            if token in head:
                say(f"{token} appears before the Sale Comparables section")
        # 9b. Rent-comp distances must equal the straight-line distance between
        # the approved pins the map is drawn from. Eyeballed estimates printed
        # 0.50 mi against pins 0.81 mi apart.
        import math
        subj = next(e for e in mf["entries"] if e["category"] == "subject")
        rent_pins = sorted((e for e in mf["entries"] if e["category"] == "rent"),
                           key=lambda e: e["order"])
        for rc, pin in zip(p["rent_comps"], rent_pins):
            la1, lo1, la2, lo2 = map(math.radians, (subj["lat"], subj["lng"],
                                                    pin["lat"], pin["lng"]))
            hv = (math.sin((la2 - la1) / 2) ** 2
                  + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
            d = 2 * 3958.7613 * math.asin(math.sqrt(hv))
            if not close(rc["distance"], d, 0.01):
                say(f"rent comp {rc['address']} prints {rc['distance']} mi but its approved "
                    f"pin is {d:.2f} mi from the subject pin")

        # 9c. Every rent-comp asking rent quoted in the narrative must be
        # reproducible from the table on the same page.
        prose = " ".join(p["rent_narrative"])
        for amount in re.findall(r"\$(\d,\d{3})\b", prose):
            if int(amount.replace(",", "")) not in {c["rent"] for c in p["rent_comps"]}:
                say(f"rent narrative quotes ${amount}, which no row in the rent-comp table shows")

        # every expense superscript on the page must have a definition under it
        refs = {r[3] for r in p["expense_lines"] if len(r) > 3 and r[3] and (r[1] or r[2])}
        missing = sorted(str(r) for r in refs if str(r) not in p["expense_notes"])
        if missing:
            say(f"expense note reference(s) {missing} appear with no definition")

        # 10. images all resolve and the manifest binds every map
        for ref in re.findall(r'(?:src|href)="(images/[^"]+)"', html):
            if not (root / ref).exists():
                say(f"broken image reference {ref}")
        for kind, ref in p["maps"].items():
            if ref and ref.replace("\\", "/") not in mf["renders"]:
                say(f"map {kind} has no certified digest")

        # 11. No AFFIRMATIVE claim on a hazard source that came back empty on the
        # 2026-08-04 revalidation. Matching the bare words is wrong: the required
        # disclosure sentence names all three in order to say they are unavailable,
        # and an earlier version of this check failed the page for its own
        # disclosure. Match claim-shaped phrasing instead, and separately require
        # the disclosure to be present so the exemption cannot hide a deletion.
        low = html.lower()
        for banned in ("fire hazard severity zone", "very high fire",
                       "state responsibility area", "moderate fire hazard",
                       "landslide susceptibility is", "low landslide",
                       "calenviroscreen score", "calenviroscreen percentile",
                       "minimal flood risk", "no flood risk"):
            if banned in low:
                say(f"page makes the affirmative claim {banned!r}; that source returned "
                    f"empty on the 2026-08-04 revalidation")
        if "fire hazard severity, landslide susceptibility and environmental screening " \
           "data were unavailable" not in " ".join(html.split()).lower():
            say("the unavailable-hazard-source disclosure is missing")
        for required in ("flood zone x", "alquist-priolo"):
            if required not in low:
                say(f"the verified hazard finding {required!r} is not stated")

        # 12. No cross-property language on a single-asset report.
        #
        # Blake Lewitt, 2026-08-05: expense notes 4 and 9 named another property
        # ("or $800 at the 1971 asset", "or $75 at the 76 unit asset"), so 38050
        # carried a sentence about Avalon Park and Avalon referred to itself in
        # the third person. A sweep of the same class found a third, note 2,
        # quoting a $1,329 per unit average "across the five properties".
        #
        # This class had already been found once, in the rent narrative, and was
        # not swept into the expense notes. That is exactly how it survived to
        # five live pages, so the sweep is now an assertion.
        #
        # The relative constructions below are banned outright rather than
        # per-property: "the 1971 asset" is meaningless on a report that renders
        # one building, including on that building's own page. The deliberate
        # Investment Overview disclaimer ("one of five individual opinions of
        # value prepared for the ownership") is a scope statement, not portfolio
        # boilerplate, and none of these patterns match it.
        text = " ".join(re.sub(r"<[^>]+>", " ", html).split())
        for label, pattern in (
            ("year-of-another-asset", r"\b(?:18|19|20)\d{2}\s+asset\b"),
            ("unit-count-of-another-asset", r"\b\d{1,4}\s+unit\s+asset\b"),
            ("aggregate-across-the-set", r"\bacross\s+the\s+(?:five|other)\b"),
            ("the-other-assets", r"\bthe\s+other\s+(?:four|five|propert|asset)"),
            ("at-the-sibling", r"\bor\s+\$[\d,]+\s+at\s+the\b"),
        ):
            m = re.search(pattern, text, re.I)
            if m:
                say(f"cross-property language on a single-asset report "
                    f"[{label}]: {m.group(0)!r}")

        # 13. Expense note numbering is contiguous, and every superscript has a
        # body. The renderer drops an expense line that is zero in both columns,
        # which took its fixed note id out of the sequence with it: all five
        # printed 1-9 then 11 because Marketing is $0, and 38238 and 38745 also
        # skipped 8 because they have no pool. Numbers are now assigned after
        # the drop, so a gap is unrepresentable.
        supers = [int(n) for n in re.findall(r'class="note-ref">\[(\d+)\]</span>', html)]
        bodies = [int(n) for n in re.findall(
            r'class="note-ref">\[(\d+)\]</span>\s*<strong>', html)]
        refs = sorted(set(supers) - set(bodies))
        if sorted(set(bodies)) != list(range(1, len(set(bodies)) + 1)):
            say(f"expense note numbers are not contiguous from 1: {sorted(set(bodies))}")
        if refs:
            say(f"expense superscript(s) {refs} have no note body")
        orphans = sorted(set(bodies) - set(supers))
        if orphans:
            say(f"expense note(s) {orphans} have no superscript on any line")

        print(f"  {slug:18s} ${price:>10,}  {op['expense_ratio'][0]:>4.1f}% opex  "
              f"cap {p['cap_current']}%/{p['cap_market']}%  GRM {p['grm_current']}/"
              f"{p['grm_market']}  DCR {fin['dcr']}  LTV {ltv:.0%}")

    print()
    for n in notes:
        print("  NOTE  " + n)
    if fails:
        print(f"\n{len(fails)} FAILURES")
        for f in fails:
            print("  FAIL  " + f)
        return 1
    print(f"\nALL CHECKS PASS across {len(SITES)} sites.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
