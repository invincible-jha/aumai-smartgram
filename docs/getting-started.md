# Getting Started with aumai-smartgram

> **GOVERNANCE DISCLAIMER:** aumai-smartgram provides AI-assisted analysis tools only. All panchayat decisions must follow official Panchayati Raj guidelines and approved administrative channels. This tool does not replace elected representatives or government officials.

---

## Prerequisites

| Requirement | Minimum version |
|---|---|
| Python | 3.11 |
| pip | 22.0 |
| Operating system | Linux, macOS, or Windows |
| Network | Only required for installation; runs fully offline |

Verify Python version:

```bash
python --version
# Python 3.11.x or higher
```

---

## Installation

### From PyPI

```bash
pip install aumai-smartgram
```

Verify:

```bash
smartgram --version
# aumai-smartgram, version 0.1.0
```

### From source

```bash
git clone https://github.com/aumai-org/aumai-smartgram.git
cd aumai-smartgram
pip install -e ".[dev]"
```

### Virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
pip install aumai-smartgram
```

---

## Step-by-Step Tutorial

This tutorial uses a fictional gram panchayat (Sitapur GP, Uttar Pradesh) to walk through all five components.

### Step 1: Register a panchayat

Create a JSON file describing the panchayat.

**sitapur_gp.json:**
```json
{
  "panchayat_id": "UP-STR-001",
  "name": "Sitapur Gram Panchayat",
  "block": "Sitapur",
  "district": "Sitapur",
  "state": "Uttar Pradesh",
  "population": 4850,
  "households": 970,
  "area_sq_km": 28.4
}
```

Register it:

```bash
smartgram register --input sitapur_gp.json
```

Expected output:
```
Registered: Sitapur Gram Panchayat (UP-STR-001)
  Block: Sitapur, District: Sitapur, State: Uttar Pradesh
  Population: 4,850 | Households: 970
  Population density: 171/sq km
```

In Python:

```python
from aumai_smartgram.core import PanchayatRegistry
from aumai_smartgram.models import GramPanchayat

registry = PanchayatRegistry()
gp = GramPanchayat(
    panchayat_id="UP-STR-001",
    name="Sitapur Gram Panchayat",
    block="Sitapur",
    district="Sitapur",
    state="Uttar Pradesh",
    population=4850,
    households=970,
    area_sq_km=28.4,
)
registry.register(gp)

# Compute density
density = registry.population_density("UP-STR-001")
print(f"Population density: {density} persons/sq km")

# Retrieve the registered record
retrieved = registry.get("UP-STR-001")
assert retrieved is not None
print(f"Retrieved: {retrieved.name} in {retrieved.district}")
```

### Step 2: Create and track service requests

Create a service request JSON file.

**request_water.json:**
```json
{
  "request_id": "SR-2025-001",
  "panchayat_id": "UP-STR-001",
  "category": "water",
  "description": "Handpump at primary school has been non-functional for 3 weeks",
  "submitted_date": "2025-06-01",
  "priority": 1
}
```

Create it via CLI:

```bash
smartgram service --create request_water.json
```

View all pending requests:

```bash
smartgram service --status --panchayat UP-STR-001
```

In Python:

```python
from aumai_smartgram.core import ServiceTracker
from aumai_smartgram.models import ServiceRequest, ServiceCategory

tracker = ServiceTracker()

# Create several requests
for i, (cat, desc, priority) in enumerate([
    (ServiceCategory.WATER, "School handpump broken", 1),
    (ServiceCategory.ROADS, "Pothole at village entrance", 3),
    (ServiceCategory.SANITATION, "Community toilet locked, key missing", 2),
], start=1):
    tracker.create(ServiceRequest(
        request_id=f"SR-2025-{i:03d}",
        panchayat_id="UP-STR-001",
        category=cat,
        description=desc,
        submitted_date=f"2025-06-{i:02d}",
        priority=priority,
    ))

# Pending requests sorted by priority
pending = tracker.get_pending("UP-STR-001")
print(f"Pending: {len(pending)} requests")
for req in pending:
    print(f"  [P{req.priority}] {req.category.value}: {req.description}")

# Resolve the highest priority issue
tracker.update_status("SR-2025-001", "resolved", resolved_date="2025-06-05")
print(f"Resolution rate: {tracker.resolution_rate('UP-STR-001')}%")
```

### Step 3: Analyse budget utilisation

Prepare your budget allocations file.

**budget_2024_25.json:**
```json
[
  {"panchayat_id": "UP-STR-001", "financial_year": "2024-25",
   "scheme_name": "MGNREGA", "allocated_amount": 900000, "utilized_amount": 810000},
  {"panchayat_id": "UP-STR-001", "financial_year": "2024-25",
   "scheme_name": "PMAY-Gramin", "allocated_amount": 390000, "utilized_amount": 120000},
  {"panchayat_id": "UP-STR-001", "financial_year": "2024-25",
   "scheme_name": "SBM-Gramin", "allocated_amount": 200000, "utilized_amount": 195000}
]
```

Analyse:

```bash
smartgram budget --input budget_2024_25.json --panchayat UP-STR-001 --year 2024-25
```

The output flags PMAY-Gramin at 30.8% utilisation with `!!` and recommends reallocating Rs 2,70,000 before year end.

In Python:

```python
from aumai_smartgram.core import BudgetAnalyzer
from aumai_smartgram.models import BudgetAllocation

analyzer = BudgetAnalyzer()
analyzer.add(BudgetAllocation(
    panchayat_id="UP-STR-001", financial_year="2024-25",
    scheme_name="PMAY-Gramin", allocated_amount=390_000, utilized_amount=120_000,
))

# Check if any funds are at risk of lapsing
under = analyzer.under_utilized("UP-STR-001", "2024-25", threshold=50.0)
print(f"Schemes below 50% utilisation: {len(under)}")
for alloc in under:
    print(f"  {alloc.scheme_name}: {alloc.utilization_pct:.0f}% utilised")
    print(f"  Unspent: Rs {alloc.allocated_amount - alloc.utilized_amount:,.0f}")
```

### Step 4: Record a gram sabha meeting

```python
from aumai_smartgram.core import MeetingManager
from aumai_smartgram.models import MeetingRecord

manager = MeetingManager()

meeting = MeetingRecord(
    panchayat_id="UP-STR-001",
    date="2025-05-26",
    attendees_count=142,
    agenda_items=[
        "Review of MGNREGA work status for April",
        "PMAY beneficiary selection for 2025-26",
        "School building repair proposal",
    ],
    decisions=[
        "MGNREGA targets to be met by 20 June",
        "PMAY list submitted to block office",
    ],
    action_items=[
        "Secretary to follow up with PHE on handpump repair",
        "Sarpanch to get school repair estimate from contractor",
    ],
)
manager.record(meeting)

# Get all pending action items
print("Pending action items:")
for item in manager.all_action_items("UP-STR-001"):
    print(f"  [ ] {item}")
```

### Step 5: Discover eligible central schemes

```bash
# See all 15 schemes
smartgram schemes

# Search for livelihood schemes
smartgram schemes --search "livelihood"

# Search for nutrition programmes
smartgram schemes --search "nutrition"
```

In Python:

```python
from aumai_smartgram.core import SchemeMapper

mapper = SchemeMapper()
all_schemes = mapper.all_schemes()
print(f"Total schemes: {len(all_schemes)}")

# Group by ministry
from collections import Counter
by_ministry = Counter(s.ministry for s in all_schemes)
for ministry, count in sorted(by_ministry.items(), key=lambda x: -x[1]):
    print(f"  {ministry}: {count} scheme(s)")
```

---

## Common Patterns and Recipes

### Recipe 1: Multi-panchayat block dashboard

```python
from aumai_smartgram.core import PanchayatRegistry, ServiceTracker
from aumai_smartgram.models import GramPanchayat, ServiceRequest, ServiceCategory

registry = PanchayatRegistry()
tracker = ServiceTracker()

# Register all panchayats in a block
block_panchayats = ["RJ-BLK-001", "RJ-BLK-002", "RJ-BLK-003"]

# Aggregate pending requests across the block
all_pending = tracker.get_pending()  # No panchayat filter = all
water_issues = [r for r in all_pending if r.category == ServiceCategory.WATER]
print(f"Block-wide water issues: {len(water_issues)}")

# Resolution rates across block
for pid in block_panchayats:
    rate = tracker.resolution_rate(pid)
    print(f"  {pid}: {rate:.0f}% resolution rate")
```

### Recipe 2: Financial year-end budget audit

```python
from aumai_smartgram.core import BudgetAnalyzer
from aumai_smartgram.models import BudgetAllocation

analyzer = BudgetAnalyzer()
# ... load all allocations ...

# Identify schemes at risk of lapsing (less than 30% used with < 2 months left)
critical_under = analyzer.under_utilized("UP-STR-001", "2024-25", threshold=30.0)
print(f"CRITICAL: {len(critical_under)} schemes below 30% utilisation")

# Get total unspent for the panchayat
total_alloc = analyzer.total_allocation("UP-STR-001", "2024-25")
total_used = analyzer.total_utilized("UP-STR-001", "2024-25")
unspent = total_alloc - total_used
print(f"Total unspent: Rs {unspent:,.0f} (risk of lapse)")
```

### Recipe 3: Export meeting minutes as JSON

```python
import json
from aumai_smartgram.core import MeetingManager

manager = MeetingManager()
# ... record meetings ...

meetings = manager.get_meetings("UP-STR-001")
minutes_data = [m.model_dump() for m in meetings]

with open("meeting_minutes.json", "w", encoding="utf-8") as f:
    json.dump(minutes_data, f, indent=2, ensure_ascii=False)
print(f"Exported {len(minutes_data)} meeting records")
```

### Recipe 4: Scheme catalogue for awareness drives

```python
from aumai_smartgram.core import SchemeMapper
import csv

mapper = SchemeMapper()
schemes = mapper.all_schemes()

with open("schemes_for_awareness.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "ministry", "description", "allocation_type"])
    writer.writeheader()
    for scheme in schemes:
        writer.writerow(scheme.model_dump())
print(f"Exported {len(schemes)} schemes to CSV")
```

### Recipe 5: Cross-panchayat scheme gap analysis

Identify which panchayats in a district are NOT applying for eligible schemes:

```python
from aumai_smartgram.core import PanchayatRegistry, SchemeMapper
from aumai_smartgram.models import GramPanchayat

registry = PanchayatRegistry()
mapper = SchemeMapper()

# Find panchayats in a district
district_panchayats = registry.search_by_district("Sitapur")

# For each panchayat, check eligible schemes
target_scheme = "Jal Jeevan Mission"
for gp in district_panchayats:
    eligible = mapper.find_eligible(gp)
    eligible_names = [s.name for s in eligible]
    if target_scheme in eligible_names:
        print(f"  {gp.name} ({gp.panchayat_id}): eligible for {target_scheme}")
```

---

## Troubleshooting FAQ

**Q: `ValidationError` when loading a panchayat JSON**

Ensure all required fields are present and types are correct:
- `population` and `households` must be positive integers (`gt=0`)
- `area_sq_km` must be a positive float (`gt=0`)
- `panchayat_id`, `name`, `block`, `district`, `state` are all required strings

**Q: `ServiceCategory` value not recognised**

Use lowercase string values: `"infrastructure"`, `"welfare"`, `"agriculture"`, `"health"`, `"education"`, `"sanitation"`, `"water"`, `"roads"`. These are the `.value` of the `ServiceCategory` enum.

**Q: Budget percentages seem wrong**

`utilization_pct` is a computed property on `BudgetAllocation`: `(utilized_amount / allocated_amount) * 100`. Check that `allocated_amount > 0`. If `allocated_amount == 0`, `utilization_pct` returns `0.0` to avoid division by zero.

**Q: `find_eligible()` returns no results for a panchayat**

Without a `GramPanchayat` argument, `find_eligible(None)` returns all 15 schemes. With a panchayat, the filter checks specific criteria (population size, etc.). If your panchayat has `population <= 5000`, the `AMRUT 2.0` scheme is excluded. If population < 250, `PMGSY` (unconnected habitations) may be excluded. Most schemes are inclusive.

**Q: MeetingManager has no persistence — data is lost when the process exits**

By design — aumai-smartgram is a library, not a database. For persistence, serialise meeting records to JSON with `[m.model_dump() for m in manager.get_meetings(pid)]` and reload on the next run with `MeetingRecord.model_validate(data)`.

**Q: The scheme database does not include state-specific schemes**

The built-in database covers 15 central government (Union government) schemes only. State-specific schemes vary widely. You can add them at runtime:
```python
from aumai_smartgram.models import SchemeInfo
mapper._schemes.append(SchemeInfo(
    name="Dr. B.R. Ambedkar Awaas Navinikarn Yojana (HP)",
    ministry="Government of Himachal Pradesh",
    description="House renovation assistance for BPL SC families in HP",
    eligible_panchayats="all_bpl",
))
```

**Q: Why is there no `--output` flag for saving results to a file?**

Pipe the JSON output to a file using shell redirection:
```bash
smartgram schemes --search "water" > water_schemes.json
```

Or use the Python API directly and call `model_dump_json()`.
