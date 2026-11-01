"""Generate a synthetic FY2025 general ledger (P&L accounts) for a fictional
Duluth, MN landscaping company, with 15 planted quality-of-earnings adjustments
and a set of decoys (legitimate items that look suspicious).

Outputs: ledger.json, answer_key.json
"""
import json, random, datetime as dt

random.seed(20251031)
rows = []
tid = [1000]

def add(date, account, atype, payee, memo, amount):
    tid[0] += 1
    rows.append({"id": f"T{tid[0]}", "date": date.isoformat(), "account": account,
                 "type": atype, "payee": payee, "memo": memo, "amount": round(amount, 2)})

def d(m, day):
    return dt.date(2025, m, min(day, 28 if m == 2 else 30 if m in (4, 6, 9, 11) else 31))

def jitter(x, pct=0.08):
    return x * (1 + random.uniform(-pct, pct))

SEASON = [4, 5, 6, 7, 8, 9, 10, 11]
SNOW = [1, 2, 3, 12]
season_w = {4: .08, 5: .16, 6: .17, 7: .15, 8: .15, 9: .13, 10: .11, 11: .05}

# ---------------- Revenue ----------------
clients_install = ["Lakeside Residence - Olson", "Park Point Residence - Kowalski", "Hartley Townhomes HOA",
                   "Essentia Clinic - Hermantown", "Congdon Residence - Pierce", "UMD Facilities",
                   "Glen Avon Residence - Strand", "Canal Park Lodge", "Woodland Residence - Haugen",
                   "Duluth Pack Store", "Lester River Residence - Nelson", "St. Luke's Annex",
                   "Hunters Park Residence - Moe", "Bayfront Condos HOA", "Kenwood Residence - Lind",
                   "Proctor Schools", "Hermantown Retail Center", "Chester Park Residence - Dahl"]
inst_total = 1_140_000
for m in SEASON:
    n = random.randint(4, 8)
    month_amt = inst_total * season_w[m]
    parts = [random.random() for _ in range(n)]
    s = sum(parts)
    for p in parts:
        c = random.choice(clients_install)
        add(d(m, random.randint(1, 28)), "Revenue - Design & Installation", "Revenue", c,
            random.choice(["Patio & retaining wall - progress billing", "Landscape install - final invoice",
                           "Design-build - progress billing", "Paver walkway & plantings", "Irrigation install"]),
            month_amt * p / s)

maint_clients = ["Hartley Townhomes HOA", "Bayfront Condos HOA", "Essentia Clinic - Hermantown",
                 "Canal Park Lodge", "Hermantown Retail Center", "St. Luke's Annex", "UMD Facilities",
                 "Residential maintenance plans (batch)"]
maint_monthly = {"Hartley Townhomes HOA": 6200, "Bayfront Condos HOA": 7400, "Essentia Clinic - Hermantown": 5100,
                 "Canal Park Lodge": 3900, "Hermantown Retail Center": 4300, "St. Luke's Annex": 5600,
                 "UMD Facilities": 8800, "Residential maintenance plans (batch)": 18900}
for m in SEASON:
    for c in maint_clients:
        add(d(m, 1), "Revenue - Maintenance Contracts", "Revenue", c, f"Maintenance contract - {dt.date(2025,m,1):%b} 2025",
            jitter(maint_monthly[c], .03))

snow_clients = ["Hartley Townhomes HOA", "Bayfront Condos HOA", "Essentia Clinic - Hermantown",
                "Hermantown Retail Center", "St. Luke's Annex", "Canal Park Lodge"]
for m in SNOW:
    for c in snow_clients:
        add(d(m, 5), "Revenue - Snow Removal", "Revenue", c, "Seasonal snow contract - monthly", jitter(5650, .1))

# PLANTED 9: one-time storm debris contract (non-recurring revenue) + its subcontractor cost
add(d(7, 22), "Revenue - Design & Installation", "Revenue", "City of Duluth",
    "Storm debris removal - July 2025 derecho event - phase 1", 52000)
add(d(8, 19), "Revenue - Design & Installation", "Revenue", "City of Duluth",
    "Storm debris removal - July 2025 derecho event - phase 2 (final)", 33000)
add(d(7, 25), "Subcontractors", "COGS", "Superior Tree & Crane", "Sub - storm debris haul & crane", 24500)
add(d(8, 21), "Subcontractors", "COGS", "Superior Tree & Crane", "Sub - storm debris haul & crane (final)", 16500)

# ---------------- COGS ----------------
for m in SEASON:
    for vendor, share, memo in [("Hedberg Landscape Supply", .45, "Pavers, block, aggregate"),
                                ("Bailey Nurseries", .25, "Trees, shrubs & perennials"),
                                ("Northland Rain Bird Supply", .12, "Irrigation parts"),
                                ("Home Depot", .08, "Job materials"),
                                ("Duluth Ready Mix", .10, "Concrete & base")]:
        for _ in range(random.randint(2, 4)):
            add(d(m, random.randint(1, 28)), "Materials & Plants", "COGS", vendor, memo,
                jitter(418000 * season_w[m] * share / 3, .35))

for m in SEASON:
    add(d(m, 15), "Subcontractors", "COGS", random.choice(["Arrowhead Electric", "North Shore Masonry"]),
        "Sub - specialty work", jitter(7200, .3))

for m in range(1, 13):
    for _ in range(4 if m in SEASON else 3):
        add(d(m, random.randint(1, 28)), "Fuel", "COGS", "Holiday Stationstores", "Fleet fuel",
            jitter(1450 if m in SEASON else 1100, .2))
    add(d(m, random.randint(1, 28)), "Equipment Repairs & Maintenance", "COGS", "Lakehead Equipment",
        random.choice(["Mower service", "Skid steer hydraulic repair", "Plow blade repair", "Tires - trailer"]),
        jitter(3100, .4))
    if m in SEASON:
        add(d(m, 20), "Dump & Disposal Fees", "COGS", "WLSSD Yard Waste Site", "Green waste disposal", jitter(1150, .2))

# ---------------- Payroll ----------------
paydates = [dt.date(2025, 1, 3) + dt.timedelta(days=14 * i) for i in range(26)]
def in_season(pd):
    return dt.date(2025, 4, 1) <= pd <= dt.date(2025, 11, 30)

payroll_gross = {}
def pay(pd, account, atype, name, role, amount, hrs=None):
    memo = f"Payroll - {name} ({role})" + (f" {hrs:.1f} hrs" if hrs is not None else " salary")
    add(pd, account, atype, name, memo, amount)
    payroll_gross[pd] = payroll_gross.get(pd, 0) + amount

for pd in paydates:
    # PLANTED 1: owner salary well above market for a GM
    pay(pd, "Officer Salaries", "OpEx", "Dale Brandt", "President", 160000 / 26)
    # PLANTED 2: spouse on payroll, salaried, overlapping office role
    pay(pd, "Office Salaries", "OpEx", "Karen Brandt", "Office", 52000 / 26)
    pay(pd, "Office Salaries", "OpEx", "Linda Ortiz", "Office Manager", 48500 / 26)
    pay(pd, "Field Labor", "COGS", "Miguel Santos", "Foreman", 64000 / 26)
    hrs = 80.0 if in_season(pd) else random.choice([56.0, 64.0, 72.0])
    pay(pd, "Field Labor", "COGS", "Tom Lindgren", "Crew Lead", 24.0 * hrs, hrs)
    if in_season(pd):
        # PLANTED 15: owner's son as crew lead at half the market rate
        pay(pd, "Field Labor", "COGS", "Jake Brandt", "Crew Lead", 12.0 * 80, 80.0)
        pay(pd, "Field Labor", "COGS", "Ana Reyes", "Crew Lead", 23.5 * 80, 80.0)
        for nm in ["Chris Hall", "Devon Price", "Sam Kuehn", "Eli Novak", "Marcus Bell", "Ty Larsen"]:
            h = random.choice([72.0, 76.0, 80.0, 80.0, 84.0])
            pay(pd, "Field Labor", "COGS", nm, "Laborer", 18.0 * h, h)
    else:
        for nm in ["Chris Hall", "Devon Price"]:
            h = random.choice([40.0, 48.0, 56.0])
            pay(pd, "Field Labor", "COGS", nm, "Laborer", 18.0 * h, h)

for pd, g in payroll_gross.items():
    add(pd, "Payroll Taxes", "OpEx", "EFTPS / MN Revenue", "Employer FICA, FUTA, SUTA", g * 0.0805)

for m in range(1, 13):
    add(d(m, 1), "Employee Benefits", "OpEx", "Medica", "Group health premium", 6150)

# PLANTED 10: workers comp premiums stop after June (coverage gap / under-recorded cost)
for m in range(1, 7):
    add(d(m, 10), "Insurance", "OpEx", "SFM Mutual Insurance", "Workers comp premium - policy WC-55821", 1550)
for m in range(1, 13):
    add(d(m, 10), "Insurance", "OpEx", "West Bend Insurance", "GL & commercial auto - monthly installment", 2000)
# PLANTED 13: next year's policy paid & expensed in December (out-of-period)
add(d(12, 18), "Insurance", "OpEx", "West Bend Insurance",
    "GL & commercial auto - annual renewal 1/1/2026-12/31/2026 paid in full", 24000)

# ---------------- Occupancy ----------------
# PLANTED 3: rent to owner's LLC above market
for m in range(1, 13):
    add(d(m, 1), "Rent", "OpEx", "Brandt Properties LLC", "Rent - shop & yard, 4410 Industrial Pkwy", 8500)
for m in range(1, 13):
    add(d(m, 12), "Utilities", "OpEx", "Minnesota Power", "Electric - shop", jitter(780 if m in SNOW else 520, .15))
    add(d(m, 12), "Utilities", "OpEx", "ComfortSystems", "Gas & water - shop", jitter(640 if m in SNOW else 260, .15))
    add(d(m, 15), "Telephone & Internet", "OpEx", "Verizon Wireless", "Company cell plan - 9 lines", jitter(540, .03))
    add(d(m, 15), "Telephone & Internet", "OpEx", "Spectrum Business", "Office internet", 189)

# ---------------- Vehicles ----------------
for m in range(1, 13):
    for unit in ["#3", "#4", "#5"]:
        add(d(m, 5), "Vehicle Expense", "OpEx", "Ford Credit", f"Lease - F-250 crew truck {unit}", 865)
    # PLANTED 5: owner's personal luxury SUV lease
    add(d(m, 5), "Vehicle Expense", "OpEx", "Toyota Financial Services", "Lease - 2025 Lexus GX 550", 1200)

# ---------------- G&A ----------------
for m in range(1, 13):
    add(d(m, 20), "Software & Subscriptions", "OpEx", "Aspire Software", "Field service software", 425)
    add(d(m, 20), "Software & Subscriptions", "OpEx", "Intuit QuickBooks", "Accounting software", 90)
    # PLANTED 7: country club dues
    add(d(m, 3), "Dues & Subscriptions", "OpEx", "Northland Country Club", "Monthly dues", 800)
    add(d(m, 25), "Accounting Fees", "OpEx", "Clearwater CPA Group", "Monthly bookkeeping & payroll review", 800)
    add(d(m, 18), "Bank & Merchant Fees", "OpEx", "North Shore Bank", "Merchant & service fees", jitter(310, .3))
    add(d(m, 28), "Interest Expense", "Other", "North Shore Bank", "Interest - equipment term loan", 1780 - m * 12)
    add(d(m, 28), "Depreciation", "Other", "Internal", "Monthly depreciation - fleet & equipment", 5650)
    # PLANTED 14 + decoy: Costco household items on company card; Amazon legit office supplies
    add(d(m, random.randint(1, 28)), "Office Supplies", "OpEx", "Amazon", random.choice(
        ["Printer toner", "Office supplies", "Shop organizers", "Safety vests & gloves"]), jitter(160, .4))
for m, amt, memo in [(1, 520, "Costco - household items"), (2, 410, "Costco - household"), (3, 610, "Costco - home groceries & household"),
                     (4, 480, "Costco - household items"), (5, 560, "Costco - patio furniture (home)"),
                     (6, 700, "Costco - household"), (7, 540, "Costco - household items"), (8, 620, "Costco - home"),
                     (9, 480, "Costco - household"), (10, 590, "Costco - household items"), (11, 650, "Costco - home groceries"),
                     (12, 1020, "Costco - holiday gifts family")]:
    add(d(m, 14), "Office Supplies", "OpEx", "Costco Wholesale", memo, amt)

# Decoys: legitimate dues, training, legal, marketing, meals
add(d(1, 15), "Dues & Subscriptions", "OpEx", "Duluth Area Chamber of Commerce", "Annual membership", 650)
add(d(2, 1), "Dues & Subscriptions", "OpEx", "MN Nursery & Landscape Association", "Annual membership", 495)
add(d(3, 12), "Training & Education", "OpEx", "Hennepin Technical College", "Pesticide applicator certification - crew", 1350)
add(d(3, 20), "Training & Education", "OpEx", "ICPI", "Concrete paver installer certification - M. Santos", 1200)
# PLANTED 8: private-school tuition booked as training
add(d(1, 8), "Training & Education", "OpEx", "Marshall School", "Tuition - spring semester", 9000)
add(d(8, 15), "Training & Education", "OpEx", "Marshall School", "Tuition - fall semester", 9000)
for m in [2, 5, 9, 11]:
    add(d(m, 9), "Legal & Professional", "OpEx", "Arrowhead Legal Services", "Contract review - commercial bids", jitter(600, .2))
# PLANTED 4: one-time lawsuit settlement and related litigation fees
for m, amt in [(2, 3200), (3, 4100), (4, 2900), (5, 4300)]:
    add(d(m, 22), "Legal & Professional", "OpEx", "Lindqvist & Moe PLLC", "Litigation - Hansen v. Birchline (retaining wall failure)", amt)
add(d(6, 10), "Legal & Professional", "OpEx", "Lindqvist & Moe PLLC", "Settlement payment - Hansen v. Birchline, full & final", 38000)
for m in range(1, 13):
    add(d(m, 7), "Advertising & Marketing", "OpEx", "Google Ads", "Search ads", jitter(950 if m in SEASON else 300, .2))
for m in [3, 4]:
    add(d(m, 18), "Advertising & Marketing", "OpEx", "Duluth Home & Garden Show", "Booth - spring show", 1450)
for m in SEASON:
    for _ in range(2):
        add(d(m, random.randint(1, 28)), "Meals", "OpEx", random.choice(["Pizza Luce", "Jimmy John's", "Duluth Grill"]),
            "Crew lunch - job site", jitter(185, .3))
# PLANTED 6: family vacation booked as client development
add(d(2, 11), "Travel", "OpEx", "Delta Air Lines", "Client development - MSP-OGG x4", 3800)
add(d(2, 24), "Travel", "OpEx", "Wailea Beach Resort", "Client development - lodging 7 nights", 8000)
add(d(10, 8), "Travel", "OpEx", "Hilton Minneapolis", "NLA trade conference - lodging", 690)

# ---------------- Other income ----------------
# PLANTED 11: ERC refund (prior-year, non-recurring)
add(d(4, 16), "Other Income", "Other Income", "IRS - US Treasury", "Employee Retention Credit refund - Q3 2021", 46000)
# PLANTED 12: gain on sale of equipment
add(d(9, 30), "Other Income", "Other Income", "Lakehead Equipment", "Gain on sale - 2016 Bobcat S650 (traded)", 18500)
add(d(12, 31), "Other Income", "Other Income", "North Shore Bank", "Interest earned - operating account", 410)

rows.sort(key=lambda r: (r["date"], r["id"]))

def gk(acct, payee):
    return f"{acct}|{payee}"

key = [
 {"n": 1, "title": "Owner salary above market for a general manager", "category": "Owner compensation", "direction": 1, "amount": 65000,
  "groups": [gk("Officer Salaries", "Dale Brandt")], "why": "Owner pays himself $160K; a hired GM for a ~$1.6M landscaping firm runs ~$95K."},
 {"n": 2, "title": "Owner's spouse on payroll alongside a full-time office manager", "category": "Related party", "direction": 1, "amount": 52000,
  "groups": [gk("Office Salaries", "Karen Brandt")], "why": "Salaried, no hours, role duplicates the office manager. Add back if she won't stay."},
 {"n": 3, "title": "Rent paid to owner's LLC above market", "category": "Related party", "direction": 1, "amount": 36000,
  "groups": [gk("Rent", "Brandt Properties LLC")], "why": "$8,500/mo to the owner's own entity vs ~$5,500 market; buyer will sign a new lease at market."},
 {"n": 4, "title": "One-time lawsuit settlement and litigation fees", "category": "Non-recurring expense", "direction": 1, "amount": 52500,
  "groups": [gk("Legal & Professional", "Lindqvist & Moe PLLC")], "why": "Hansen v. Birchline settled in June, full and final."},
 {"n": 5, "title": "Owner's personal Lexus lease", "category": "Personal expense", "direction": 1, "amount": 14400,
  "groups": [gk("Vehicle Expense", "Toyota Financial Services")], "why": "Fleet is F-250s; a Lexus GX is the owner's personal car."},
 {"n": 6, "title": "Hawaii trip booked as client development", "category": "Personal expense", "direction": 1, "amount": 11800,
  "groups": [gk("Travel", "Delta Air Lines"), gk("Travel", "Wailea Beach Resort")], "why": "Four tickets to Maui (OGG) in February for a Duluth landscaper."},
 {"n": 7, "title": "Country club dues", "category": "Personal expense", "direction": 1, "amount": 9600,
  "groups": [gk("Dues & Subscriptions", "Northland Country Club")], "why": "Discretionary owner perk."},
 {"n": 8, "title": "Private-school tuition booked as training", "category": "Personal expense", "direction": 1, "amount": 18000,
  "groups": [gk("Training & Education", "Marshall School")], "why": "Spring/fall semester tuition at a private K-12 school."},
 {"n": 9, "title": "One-time storm cleanup contract", "category": "Non-recurring revenue", "direction": -1, "amount": 44000,
  "groups": [gk("Revenue - Design & Installation", "City of Duluth"), gk("Subcontractors", "Superior Tree & Crane")],
  "why": "$85K of derecho cleanup revenue less $41K of subcontractor cost; won't repeat."},
 {"n": 10, "title": "Workers' comp premiums stop after June", "category": "Missing cost", "direction": -1, "amount": 9300,
  "groups": [gk("Insurance", "SFM Mutual Insurance")], "why": "Only 6 of 12 monthly premiums recorded; a full year of coverage costs ~$9.3K more."},
 {"n": 11, "title": "Employee Retention Credit refund", "category": "Non-recurring income", "direction": -1, "amount": 46000,
  "groups": [gk("Other Income", "IRS - US Treasury")], "why": "Refund for 2021 payroll; not part of 2025 earnings."},
 {"n": 12, "title": "Gain on sale of equipment", "category": "Non-recurring income", "direction": -1, "amount": 18500,
  "groups": [gk("Other Income", "Lakehead Equipment")], "why": "One-time gain on trading in a skid steer."},
 {"n": 13, "title": "Next year's insurance expensed this year", "category": "Out-of-period", "direction": 1, "amount": 24000,
  "groups": [gk("Insurance", "West Bend Insurance")], "why": "2026 policy paid and expensed in December 2025; belongs in prepaid."},
 {"n": 14, "title": "Household purchases on the company card", "category": "Personal expense", "direction": 1, "amount": 7200,
  "groups": [gk("Office Supplies", "Costco Wholesale")], "why": "Costco memos read household, home groceries, family gifts."},
 {"n": 15, "title": "Owner's son paid half the market rate", "category": "Missing cost", "direction": -1, "amount": 16320,
  "groups": [gk("Field Labor", "Jake Brandt")], "why": "$12/hr vs $23.50-$24/hr for the other crew leads; a replacement costs ~$16K more for the season."},
]
decoys = [gk("Vehicle Expense", "Ford Credit"), gk("Dues & Subscriptions", "Duluth Area Chamber of Commerce"),
          gk("Dues & Subscriptions", "MN Nursery & Landscape Association"), gk("Training & Education", "Hennepin Technical College"),
          gk("Training & Education", "ICPI"), gk("Legal & Professional", "Arrowhead Legal Services"),
          gk("Travel", "Hilton Minneapolis"), gk("Office Supplies", "Amazon"), gk("Accounting Fees", "Clearwater CPA Group"),
          gk("Advertising & Marketing", "Duluth Home & Garden Show"), gk("Office Salaries", "Linda Ortiz"),
          gk("Field Labor", "Tom Lindgren"), gk("Field Labor", "Ana Reyes")]

# reconcile Costco & Jake amounts to the actual ledger
costco = sum(r["amount"] for r in rows if r["payee"] == "Costco Wholesale")
key[13]["amount"] = round(costco, 0)
jake_hrs = sum(80 for r in rows if r["payee"] == "Jake Brandt")
key[14]["amount"] = round(jake_hrs * (23.75 - 12.0), 0)

json.dump(rows, open("ledger.json", "w"))
json.dump({"planted": key, "decoys": decoys}, open("answer_key.json", "w"), indent=1)

# Summary
from collections import defaultdict
by_type = defaultdict(float)
for r in rows:
    by_type[r["type"]] += r["amount"]
rev = by_type["Revenue"]; cogs = by_type["COGS"]; opex = by_type["OpEx"]; oi = by_type["Other Income"]
other = by_type["Other"]
ni = rev - cogs - opex + oi - other
da = sum(r["amount"] for r in rows if r["account"] == "Depreciation")
intr = sum(r["amount"] for r in rows if r["account"] == "Interest Expense")
ebitda = ni + da + intr
net_adj = sum(k["direction"] * k["amount"] for k in key)
print(f"rows={len(rows)} revenue={rev:,.0f} cogs={cogs:,.0f} GP={rev-cogs:,.0f} opex={opex:,.0f} other_inc={oi:,.0f}")
print(f"NI={ni:,.0f} D&A={da:,.0f} int={intr:,.0f} EBITDA={ebitda:,.0f} net_adj={net_adj:,.0f} adj_EBITDA={ebitda+net_adj:,.0f}")
print("costco", costco, "jake hrs", jake_hrs, "groups", len({gk(r['account'], r['payee']) for r in rows}))
