# aumai-smartgram API Reference

AI-assisted administrative tool for gram panchayat governance. Provides
registries, trackers, budget analysis, meeting management, and government
scheme lookup for rural local self-government bodies.

> **Disclaimer:** This tool is an administrative aid. Verify all information
> with local gram panchayat officials. All decisions must follow official
> Panchayati Raj guidelines and be approved through proper administrative
> channels.

---

## Table of Contents

1. [Models](#models)
   - [PanchayatLevel](#panchayatlevel)
   - [ServiceCategory](#servicecategory)
   - [GramPanchayat](#grampanchayat)
   - [ServiceRequest](#servicerequest)
   - [BudgetAllocation](#budgetallocation)
   - [MeetingRecord](#meetingrecord)
   - [SchemeInfo](#schemeinfo)
2. [Core Classes](#core-classes)
   - [PanchayatRegistry](#panchayatregistry)
   - [ServiceTracker](#servicetracker)
   - [BudgetAnalyzer](#budgetanalyzer)
   - [MeetingManager](#meetingmanager)
   - [SchemeMapper](#schememapper)
3. [CLI Commands](#cli-commands)
4. [Built-in Schemes](#built-in-schemes)

---

## Models

All models are Pydantic `BaseModel` subclasses. Import from
`aumai_smartgram.models`.

---

### PanchayatLevel

String enumeration of administrative levels in the panchayat system.

```python
from aumai_smartgram.models import PanchayatLevel

level = PanchayatLevel.GRAM
print(level.value)  # "gram"
```

#### Members

| Member | Value | Description |
|---|---|---|
| `GRAM` | `"gram"` | Village-level panchayat. |
| `BLOCK` | `"block"` | Block-level panchayat samiti. |
| `DISTRICT` | `"district"` | District-level zila parishad. |

---

### ServiceCategory

String enumeration of service request categories.

```python
from aumai_smartgram.models import ServiceCategory

cat = ServiceCategory.WATER
print(cat.value)  # "water"
```

#### Members

| Member | Value |
|---|---|
| `INFRASTRUCTURE` | `"infrastructure"` |
| `WELFARE` | `"welfare"` |
| `AGRICULTURE` | `"agriculture"` |
| `HEALTH` | `"health"` |
| `EDUCATION` | `"education"` |
| `SANITATION` | `"sanitation"` |
| `WATER` | `"water"` |
| `ROADS` | `"roads"` |

---

### GramPanchayat

Represents a gram panchayat administrative unit.

```python
from aumai_smartgram.models import GramPanchayat

panchayat = GramPanchayat(
    panchayat_id="GP-MH-PUN-001",
    name="Shivajinagar Gram Panchayat",
    block="Haveli",
    district="Pune",
    state="Maharashtra",
    population=4500,
    households=890,
    area_sq_km=12.5,
)
```

#### Fields

| Field | Type | Required | Constraint | Description |
|---|---|---|---|---|
| `panchayat_id` | `str` | Yes | — | Unique identifier (e.g., e-Gram Swaraj ID or internal code). |
| `name` | `str` | Yes | — | Official name of the gram panchayat. |
| `block` | `str` | Yes | — | Block (taluka/tehsil) the panchayat belongs to. |
| `district` | `str` | Yes | — | District the panchayat belongs to. |
| `state` | `str` | Yes | — | State the panchayat belongs to. |
| `population` | `int` | Yes | `> 0` | Total population of the panchayat area. |
| `households` | `int` | Yes | `> 0` | Total number of households. |
| `area_sq_km` | `float` | Yes | `> 0` | Geographic area in square kilometres. |

---

### ServiceRequest

A citizen or panchayat service request, tracking status from submission
through resolution.

```python
from aumai_smartgram.models import ServiceRequest, ServiceCategory

request = ServiceRequest(
    request_id="SR-2024-0042",
    panchayat_id="GP-MH-PUN-001",
    category=ServiceCategory.WATER,
    description="Handpump at ward 3 not functioning since 2024-06-01",
    submitted_date="2024-06-10",
    status="pending",
    priority=1,
)
```

#### Fields

| Field | Type | Required | Constraint | Default | Description |
|---|---|---|---|---|---|
| `request_id` | `str` | Yes | — | — | Unique identifier for this request. |
| `panchayat_id` | `str` | Yes | — | — | ID of the panchayat this request belongs to. |
| `category` | `ServiceCategory` | Yes | — | — | Service category. |
| `description` | `str` | Yes | — | — | Detailed description of the request. |
| `submitted_date` | `str` | Yes | — | — | Submission date (ISO 8601 format recommended, e.g. `"2024-06-10"`). |
| `status` | `str` | No | — | `"pending"` | Current status. Conventional values: `"pending"`, `"in_progress"`, `"resolved"`. |
| `priority` | `int` | No | `1 <= x <= 5` | `3` | Priority level. `1` = highest priority, `5` = lowest. |
| `resolved_date` | `str \| None` | No | — | `None` | Resolution date, set when status becomes `"resolved"`. |

---

### BudgetAllocation

A budget allocation record for one scheme in one financial year for one
panchayat. The `utilization_pct` property is computed automatically.

```python
from aumai_smartgram.models import BudgetAllocation

allocation = BudgetAllocation(
    panchayat_id="GP-MH-PUN-001",
    financial_year="2024-25",
    scheme_name="MGNREGA",
    allocated_amount=500000.0,
    utilized_amount=320000.0,
)

print(allocation.utilization_pct)  # 64.0
```

#### Fields

| Field | Type | Required | Constraint | Description |
|---|---|---|---|---|
| `panchayat_id` | `str` | Yes | — | ID of the panchayat this allocation belongs to. |
| `financial_year` | `str` | Yes | — | Financial year identifier (e.g., `"2024-25"`). |
| `scheme_name` | `str` | Yes | — | Name of the government scheme. |
| `allocated_amount` | `float` | Yes | `>= 0` | Total amount allocated in rupees. |
| `utilized_amount` | `float` | Yes | `>= 0` | Amount actually utilised in rupees. |

#### Properties

##### `BudgetAllocation.utilization_pct`

```python
@property
def utilization_pct(self) -> float
```

Compute percentage of budget utilised. Returns `0.0` if `allocated_amount`
is zero.

**Returns**

`float` — Utilisation percentage (0.0 to 100.0), rounded to 1 decimal place.

---

### MeetingRecord

A record of a gram sabha or panchayat meeting.

```python
from aumai_smartgram.models import MeetingRecord

meeting = MeetingRecord(
    panchayat_id="GP-MH-PUN-001",
    date="2024-07-15",
    attendees_count=42,
    agenda_items=["Water supply review", "MGNREGA work allocation"],
    decisions=["Approve repair tender for handpump ward 3"],
    action_items=["Engineer to inspect by 2024-07-20", "Submit MGNREGA demand by 2024-07-31"],
)
```

#### Fields

| Field | Type | Required | Constraint | Default | Description |
|---|---|---|---|---|---|
| `panchayat_id` | `str` | Yes | — | — | ID of the panchayat this meeting belongs to. |
| `date` | `str` | Yes | — | — | Meeting date (ISO 8601 format recommended). |
| `attendees_count` | `int` | Yes | `>= 0` | — | Number of attendees present. |
| `agenda_items` | `list[str]` | No | — | `[]` | List of agenda items discussed. |
| `decisions` | `list[str]` | No | — | `[]` | Resolutions passed during the meeting. |
| `action_items` | `list[str]` | No | — | `[]` | Follow-up actions assigned, with responsible parties and deadlines. |

---

### SchemeInfo

Metadata about a government scheme available to gram panchayats.
Instances in the built-in dataset are created internally by `SchemeMapper`.

```python
from aumai_smartgram.models import SchemeInfo

scheme = SchemeInfo(
    name="MGNREGA",
    ministry="Ministry of Rural Development",
    description="100 days guaranteed wage employment per rural household per year.",
    allocation_type="demand-driven",
    eligible_panchayats="all_rural",
)
```

#### Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | `str` | Yes | — | Official scheme name. |
| `ministry` | `str` | Yes | — | Administering ministry. |
| `description` | `str` | Yes | — | Brief description of the scheme and its benefits. |
| `allocation_type` | `str` | No | `""` | How funds are allocated (e.g., `"demand-driven"`, `"unit-based"`, `"dbt"`). |
| `eligible_panchayats` | `str` | No | `"all"` | Eligibility tag used by `SchemeMapper.find_eligible`. |

---

## Core Classes

Import from `aumai_smartgram.core`.

---

### PanchayatRegistry

In-memory registry of `GramPanchayat` objects. Supports registration,
lookup by ID, and search by district or state.

```python
from aumai_smartgram.core import PanchayatRegistry

registry = PanchayatRegistry()
```

`PanchayatRegistry` has no constructor parameters.

#### `PanchayatRegistry.register`

```python
def register(self, panchayat: GramPanchayat) -> None
```

Register a panchayat. Overwrites any existing entry with the same
`panchayat_id`.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat` | `GramPanchayat` | The panchayat to register. |

**Returns**

`None`

#### `PanchayatRegistry.get`

```python
def get(self, panchayat_id: str) -> GramPanchayat | None
```

Retrieve a panchayat by ID.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat ID to look up. |

**Returns**

`GramPanchayat | None` — The registered panchayat, or `None` if not found.

#### `PanchayatRegistry.search_by_district`

```python
def search_by_district(self, district: str) -> list[GramPanchayat]
```

Return all panchayats whose `district` field contains `district` (case-insensitive substring match).

**Parameters**

| Name | Type | Description |
|---|---|---|
| `district` | `str` | District name or partial name to search for. |

**Returns**

`list[GramPanchayat]`

#### `PanchayatRegistry.search_by_state`

```python
def search_by_state(self, state: str) -> list[GramPanchayat]
```

Return all panchayats whose `state` field contains `state` (case-insensitive substring match).

**Parameters**

| Name | Type | Description |
|---|---|---|
| `state` | `str` | State name or partial name to search for. |

**Returns**

`list[GramPanchayat]`

#### `PanchayatRegistry.population_density`

```python
def population_density(self, panchayat_id: str) -> float
```

Calculate population density (persons per square kilometre) for a registered
panchayat.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat ID to query. |

**Returns**

`float` — Persons per sq km, rounded to 1 decimal place. Returns `0.0` if
the panchayat is not found or `area_sq_km` is zero.

#### `PanchayatRegistry.all_panchayats`

```python
def all_panchayats(self) -> list[GramPanchayat]
```

Return all registered panchayats as a list.

**Returns**

`list[GramPanchayat]`

**Example**

```python
registry.register(panchayat)
found = registry.get("GP-MH-PUN-001")
density = registry.population_density("GP-MH-PUN-001")
results = registry.search_by_district("Pune")
```

---

### ServiceTracker

In-memory tracker for `ServiceRequest` objects. Manages creation, status
updates, and statistical queries.

```python
from aumai_smartgram.core import ServiceTracker

tracker = ServiceTracker()
```

`ServiceTracker` has no constructor parameters.

#### `ServiceTracker.create`

```python
def create(self, request: ServiceRequest) -> None
```

Register a new service request. Overwrites any existing request with the same
`request_id`.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `request` | `ServiceRequest` | The service request to register. |

**Returns**

`None`

#### `ServiceTracker.update_status`

```python
def update_status(
    self,
    request_id: str,
    status: str,
    resolved_date: str | None = None,
) -> bool
```

Update the status of an existing request.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `request_id` | `str` | Required | ID of the request to update. |
| `status` | `str` | Required | New status value (e.g., `"resolved"`). |
| `resolved_date` | `str \| None` | `None` | If provided, sets `request.resolved_date`. |

**Returns**

`bool` — `True` if the request was found and updated, `False` if not found.

#### `ServiceTracker.get_pending`

```python
def get_pending(self, panchayat_id: str | None = None) -> list[ServiceRequest]
```

Return all requests with `status == "pending"`, sorted by priority ascending
(priority `1` = highest urgency returned first).

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `panchayat_id` | `str \| None` | `None` | If provided, filter results to this panchayat only. |

**Returns**

`list[ServiceRequest]` — Pending requests sorted by `priority` ascending.

#### `ServiceTracker.category_stats`

```python
def category_stats(self, panchayat_id: str) -> dict[str, int]
```

Count requests per category for a given panchayat (all statuses included).

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat to aggregate stats for. |

**Returns**

`dict[str, int]` — Maps `ServiceCategory.value` strings to request counts.

#### `ServiceTracker.resolution_rate`

```python
def resolution_rate(self, panchayat_id: str) -> float
```

Compute the percentage of requests that have been resolved for a panchayat.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat to compute the rate for. |

**Returns**

`float` — Resolution rate as a percentage (0.0 to 100.0), rounded to 1
decimal place. Returns `0.0` if no requests exist.

**Example**

```python
tracker.create(request)
tracker.update_status("SR-2024-0042", status="resolved", resolved_date="2024-07-01")
pending = tracker.get_pending(panchayat_id="GP-MH-PUN-001")
rate = tracker.resolution_rate("GP-MH-PUN-001")
stats = tracker.category_stats("GP-MH-PUN-001")
```

---

### BudgetAnalyzer

Analyses `BudgetAllocation` records for a panchayat and financial year.
Provides utilisation breakdowns and reallocation recommendations.

```python
from aumai_smartgram.core import BudgetAnalyzer

analyzer = BudgetAnalyzer()
```

`BudgetAnalyzer` has no constructor parameters.

#### `BudgetAnalyzer.add`

```python
def add(self, allocation: BudgetAllocation) -> None
```

Add a budget allocation record to the analyzer.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `allocation` | `BudgetAllocation` | The allocation to record. |

**Returns**

`None`

#### `BudgetAnalyzer.utilization_by_scheme`

```python
def utilization_by_scheme(self, panchayat_id: str, year: str) -> dict[str, float]
```

Return utilisation percentage per scheme for a specific panchayat and year.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | Panchayat to query. |
| `year` | `str` | Financial year identifier (e.g., `"2024-25"`). |

**Returns**

`dict[str, float]` — Maps scheme name to utilisation percentage.

#### `BudgetAnalyzer.under_utilized`

```python
def under_utilized(
    self,
    panchayat_id: str,
    year: str,
    threshold: float = 50.0,
) -> list[BudgetAllocation]
```

Return allocations with utilisation below `threshold` percent.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `panchayat_id` | `str` | Required | Panchayat to query. |
| `year` | `str` | Required | Financial year. |
| `threshold` | `float` | `50.0` | Utilisation percentage cutoff (exclusive). |

**Returns**

`list[BudgetAllocation]`

#### `BudgetAnalyzer.over_utilized`

```python
def over_utilized(
    self,
    panchayat_id: str,
    year: str,
    threshold: float = 90.0,
) -> list[BudgetAllocation]
```

Return allocations with utilisation above `threshold` percent.

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `panchayat_id` | `str` | Required | Panchayat to query. |
| `year` | `str` | Required | Financial year. |
| `threshold` | `float` | `90.0` | Utilisation percentage cutoff (exclusive). |

**Returns**

`list[BudgetAllocation]`

#### `BudgetAnalyzer.total_allocation`

```python
def total_allocation(self, panchayat_id: str, year: str) -> float
```

Sum all `allocated_amount` values for a panchayat and year.

**Returns**

`float` — Total allocation in rupees.

#### `BudgetAnalyzer.total_utilized`

```python
def total_utilized(self, panchayat_id: str, year: str) -> float
```

Sum all `utilized_amount` values for a panchayat and year.

**Returns**

`float` — Total utilised amount in rupees.

#### `BudgetAnalyzer.recommend_reallocation`

```python
def recommend_reallocation(self, panchayat_id: str, year: str) -> list[str]
```

Generate plain-text reallocation recommendations for all under-utilised
schemes (below 50% threshold). Each recommendation names the scheme, its
utilisation percentage, and the unused rupee amount.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | Panchayat to analyse. |
| `year` | `str` | Financial year. |

**Returns**

`list[str]` — One recommendation string per under-utilised scheme.

**Example**

```python
analyzer.add(BudgetAllocation(
    panchayat_id="GP-MH-PUN-001",
    financial_year="2024-25",
    scheme_name="MGNREGA",
    allocated_amount=500000.0,
    utilized_amount=320000.0,
))

total = analyzer.total_allocation("GP-MH-PUN-001", "2024-25")  # 500000.0
pct = analyzer.utilization_by_scheme("GP-MH-PUN-001", "2024-25")
recs = analyzer.recommend_reallocation("GP-MH-PUN-001", "2024-25")
```

---

### MeetingManager

Records and queries `MeetingRecord` objects for panchayat meetings.

```python
from aumai_smartgram.core import MeetingManager

manager = MeetingManager()
```

`MeetingManager` has no constructor parameters.

#### `MeetingManager.record`

```python
def record(self, meeting: MeetingRecord) -> None
```

Add a meeting record. Multiple records for the same panchayat accumulate.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `meeting` | `MeetingRecord` | The meeting record to store. |

**Returns**

`None`

#### `MeetingManager.get_meetings`

```python
def get_meetings(self, panchayat_id: str) -> list[MeetingRecord]
```

Return all meeting records for a panchayat.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat whose meetings to retrieve. |

**Returns**

`list[MeetingRecord]` — In insertion order.

#### `MeetingManager.all_action_items`

```python
def all_action_items(self, panchayat_id: str) -> list[str]
```

Aggregate all action items from all meetings for a panchayat into a single
flat list.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat to query. |

**Returns**

`list[str]` — All action items in meeting-insertion order.

#### `MeetingManager.meeting_count`

```python
def meeting_count(self, panchayat_id: str) -> int
```

Return the number of recorded meetings for a panchayat.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `panchayat_id` | `str` | The panchayat to query. |

**Returns**

`int`

**Example**

```python
manager.record(meeting)
all_items = manager.all_action_items("GP-MH-PUN-001")
count = manager.meeting_count("GP-MH-PUN-001")
```

---

### SchemeMapper

Provides access to the built-in catalogue of 15 central government schemes
and supports eligibility filtering and keyword search.

```python
from aumai_smartgram.core import SchemeMapper

mapper = SchemeMapper()
```

`SchemeMapper` has no constructor parameters. On construction, it loads the
built-in scheme catalogue (see [Built-in Schemes](#built-in-schemes)).

#### `SchemeMapper.find_eligible`

```python
def find_eligible(self, panchayat: GramPanchayat | None = None) -> list[SchemeInfo]
```

Return schemes eligible for the given panchayat based on its characteristics.
If `panchayat` is `None`, returns all 15 built-in schemes.

**Eligibility rules:**

| `eligible_panchayats` tag | Condition |
|---|---|
| `"all"` | Always included. |
| `"all_rural"` | Always included. |
| `"all_bpl"` | Always included. |
| `"farming_households"` | Always included. |
| `"census_towns"` | Included if `panchayat.population > 5000`. |
| `"unconnected_habitations"` | Included if `panchayat.population >= 250`. |
| `"houseless_kutcha"` | Always included. |

**Parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `panchayat` | `GramPanchayat \| None` | `None` | Panchayat to match. `None` returns all schemes. |

**Returns**

`list[SchemeInfo]`

#### `SchemeMapper.search`

```python
def search(self, query: str) -> list[SchemeInfo]
```

Search schemes by keyword. Matches against scheme `name` and `description`
(case-insensitive substring match).

**Parameters**

| Name | Type | Description |
|---|---|---|
| `query` | `str` | Keyword or phrase to search for. |

**Returns**

`list[SchemeInfo]` — All schemes whose name or description contains `query`.

#### `SchemeMapper.all_schemes`

```python
def all_schemes(self) -> list[SchemeInfo]
```

Return a copy of all 15 built-in schemes.

**Returns**

`list[SchemeInfo]`

**Example**

```python
mapper = SchemeMapper()
all_schemes = mapper.all_schemes()
water_schemes = mapper.search("water")
eligible = mapper.find_eligible(panchayat)
```

---

## CLI Commands

The `aumai-smartgram` (aliased as `main`) entry point groups four sub-commands.
All accept `--help`.

```
aumai-smartgram [--version] [--help] COMMAND [ARGS]...
```

All commands print a governance disclaimer at the end of their output.

---

### `register`

Register a gram panchayat from a JSON file. Prints a summary of the
registered panchayat including population density.

```
aumai-smartgram register --input panchayat.json
```

| Option | Type | Description |
|---|---|---|
| `--input PATH` | `Path` | Required. Path to a `GramPanchayat` JSON file. |

**Input JSON example**

```json
{
  "panchayat_id": "GP-MH-PUN-001",
  "name": "Shivajinagar Gram Panchayat",
  "block": "Haveli",
  "district": "Pune",
  "state": "Maharashtra",
  "population": 4500,
  "households": 890,
  "area_sq_km": 12.5
}
```

---

### `service`

Manage service requests. Supports creating from JSON, resolving by ID, and
listing pending requests.

```
aumai-smartgram service [--create PATH] [--resolve ID] [--panchayat ID] [--status]
```

| Option | Type | Description |
|---|---|---|
| `--create PATH` | `Path` | Create a new request from a `ServiceRequest` JSON file. |
| `--resolve STR` | `str` | Mark a request as resolved by its `request_id`. |
| `--panchayat STR` | `str` | Filter `--status` output to a specific panchayat ID. |
| `--status` | flag | List all pending requests, sorted by priority. |

---

### `budget`

Analyse budget utilisation for a panchayat and financial year.
Loads allocation records from a JSON array, prints a per-scheme table, and
outputs reallocation recommendations for under-utilised schemes.

```
aumai-smartgram budget --input budget.json --panchayat GP-MH-PUN-001 --year 2024-25
```

| Option | Type | Description |
|---|---|---|
| `--input PATH` | `Path` | Required. Path to a JSON array of `BudgetAllocation` objects. |
| `--panchayat STR` | `str` | Required. Panchayat ID to analyse. |
| `--year STR` | `str` | Required. Financial year (e.g., `"2024-25"`). |

---

### `schemes`

Find and display government schemes. Without `--search`, lists all 15
built-in schemes.

```
aumai-smartgram schemes [--panchayat ID] [--search QUERY]
```

| Option | Type | Description |
|---|---|---|
| `--panchayat STR` | `str` | (Reserved) Panchayat ID for eligibility context. |
| `--search STR` | `str` | Keyword to search scheme names and descriptions. |

---

## Built-in Schemes

`SchemeMapper` ships with 15 central government schemes pre-loaded:

| Scheme | Ministry | Allocation Type |
|---|---|---|
| MGNREGA | Rural Development | demand-driven |
| PMAY-Gramin | Rural Development | unit-based |
| Swachh Bharat Mission (Gramin) | Jal Shakti | unit-based |
| PMGSY | Rural Development | project-based |
| National Health Mission | Health | population-based |
| Samagra Shiksha | Education | population-based |
| National Rural Livelihood Mission | Rural Development | demand-driven |
| DDU-GKY | Rural Development | demand-driven |
| Jal Jeevan Mission | Jal Shakti | unit-based |
| PM-KISAN | Agriculture | dbt |
| RKVY-RAFTAAR | Agriculture | project-based |
| ICDS/Poshan Abhiyaan | Women & Child | anganwadi-based |
| Mid-Day Meal (PM-POSHAN) | Education | per-child |
| NSAP (National Social Assistance) | Rural Development | dbt |
| AMRUT 2.0 | Housing | project-based |

> **Disclaimer:** Scheme details are provided for reference only. Verify
> current eligibility criteria, allocation norms, and guidelines directly
> with the concerned ministry and local gram panchayat officials.
