# Mermaid diagram types: syntax and examples

Each example is complete and valid. Copy the shape, then change the labels. Do not add a `theme` line for chat output.

## flowchart

`LR` left to right, `TD` top down. Shapes: `[box]`, `(rounded)`, `{decision}`, `[(database)]`, `((circle))`. Edge labels: `-->|text|`.

```mermaid
flowchart LR
    A[Request] --> B{Valid?}
    B -->|yes| C[Process]
    B -->|no| D[Reject]
    subgraph Backend
        C --> E[(Database)]
    end
    C & D --> F[Reply]
```

## sequenceDiagram

`->>` request, `-->>` reply, `+`/`-` activate and deactivate, `alt`/`else` for branches, `Note` for remarks.

```mermaid
sequenceDiagram
    actor User
    participant API
    participant Auth
    User->>+API: POST /login
    API->>+Auth: validate(credentials)
    Auth-->>-API: token
    alt valid
        API-->>User: 200 OK
    else invalid
        API-->>-User: 401
    end
    Note over API,Auth: Tokens expire after 1 hour
```

## classDiagram

Visibility `+` public, `-` private. Relations: `<|--` inheritance, `-->` association, `*--` composition, `o--` aggregation.

```mermaid
classDiagram
    class Vehicle {
        +String vin
        +start() void
    }
    class Car
    class Wheel
    Vehicle <|-- Car
    Car "1" --> "4" Wheel : has
```

## erDiagram

Cardinality: `||` exactly one, `o|` zero or one, `|{` one or more, `o{` zero or more. Mark keys with `PK` and `FK`.

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    CUSTOMER {
        int id PK
        string name
    }
    ORDER {
        int id PK
        int customer_id FK
    }
```

## stateDiagram-v2

`[*]` is the start and end state.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review : submit
    Review --> Approved : approve
    Review --> Draft : reject
    Approved --> [*]
```

## gantt

Set `dateFormat`. Task syntax: `name :status, id, start, duration`. Statuses: `done`, `active`, `crit`. A start can be `after <id>`.

```mermaid
gantt
    title Release plan
    dateFormat YYYY-MM-DD
    section Build
    Design  :done, d1, 2026-10-01, 5d
    Develop :active, d2, after d1, 10d
    section Launch
    Test    :d3, after d2, 4d
    Release :milestone, after d3, 0d
```

## timeline

```mermaid
timeline
    title Product history
    2024 : Prototype
    2025 : First customers
         : Desktop app
    2026 : Reports and scheduling
```

## mindmap

Hierarchy is set by indentation. The root can use `(( ))` for a circle.

```mermaid
mindmap
  root((Dealer reports))
    Service
      Labor rate
      Efficiency
    Sales
      Leads
      Gross
    Master report
```

## pie

```mermaid
pie showData
    title Work mix
    "Labor" : 55
    "Parts" : 35
    "Other" : 10
```

## gitGraph

```mermaid
gitGraph
    commit id: "init"
    branch feature
    checkout feature
    commit id: "add report"
    checkout main
    merge feature
    commit id: "release"
```

## C4Context (experimental)

Prefer a `flowchart` with subgraphs when exact look matters.

```mermaid
C4Context
    title System context
    Person(manager, "Manager", "Reads daily reports")
    System(app, "Ask Dealer", "Builds and sends reports")
    System_Ext(dms, "DMS", "Dealer data")
    Rel(manager, app, "Uses")
    Rel(app, dms, "Reads data")
```
