# European LBO Screening & Simulation Pipeline

This project is an end-to-end pipeline designed to **identify and evaluate potential Leveraged Buyout (LBO) opportunities among European companies**.

At the core of the system is the **SAI Note (Score of Attractivity of Investment)** — a scoring framework designed to rapidly estimate whether a company could represent a viable LBO target.

The system combines:

- **Python-based financial data collection**
- **SQL structured storage**
- **quantitative scoring of LBO attractiveness**
- **Excel LBO modelling connected via Power Query**

The objective is to **reduce the time required to identify promising investment targets** while still allowing analysts to run a simplified deal simulation.

The workflow reflects a simplified version of the analytical pipeline used in **private equity deal sourcing and screening**.

---

# The SAI Note – Score of Attractivity of Investment

Private equity firms review **thousands of potential companies** but only pursue a very small number of transactions.  

The most scarce resource in deal sourcing is **analyst time**.

The **SAI Note** was designed as a simple screening metric that helps answer a first question:

> *Is this company worth spending time modelling in detail?*

Rather than building a full LBO model for every company, the SAI score provides a **quick first-pass attractiveness indicator**.

It combines several dimensions that are typically important in LBO transactions:

- stability of cash flows
- debt capacity
- margin improvement potential
- balance sheet strength
- sector benchmarks

The score **does not replace detailed financial analysis**.  
Instead it acts as a **filter**, allowing analysts to focus attention on companies that already show favourable structural characteristics.

In practice this type of scoring system helps to:

- **prioritize targets faster**
- **reduce time spent on weak candidates**
- **standardize the initial screening logic**
- **improve comparability across companies**

Once companies are ranked using the SAI score, analysts can move to the next step: **simulating the economics of a potential acquisition.**

---

# Pipeline Overview

The project is structured as a pipeline moving from raw financial data to a user-driven LBO simulation.

1. **Python scraping & data collection**
2. **Data storage in SQL database**
3. **Company scoring (SAI Note)**
4. **Excel import through Power Query**
5. **User-driven LBO simulation**

Below is the high-level architecture of the pipeline.

![Pipeline](pipeline_visualisation.png)

*(replace the file name with your pipeline PNG once uploaded to the repo)*

---

# Project Goal

The project evaluates **European listed companies** and estimates their **potential attractiveness for a leveraged buyout**.

The process occurs in two stages.

### Stage 1 — Screening

Companies are ranked using the **SAI Note**, which evaluates structural LBO suitability.

### Stage 2 — Simulation

Once a company is selected, the user can run a simplified **LBO simulation** using adjustable assumptions such as:

- leverage
- revenue growth
- EBITDA improvement
- holding period
- entry and exit multiples

The model then estimates the **investment performance for the sponsor**.

---

# Key LBO Metrics Produced

The simulation generates common private-equity deal metrics:

- **IRR / TRI**
- **MOIC**
- **EBITDA at Exit**
- **Exit Multiple**
- **Enterprise Value**
- **Net Debt**
- **Sponsor Equity Value**
- **Sponsor Equity at Entry**

These outputs allow a quick view of whether the investment could meet typical **private equity return targets**.

---

# System Architecture

## 1. Python Data Layer

Python scripts collect and prepare financial information.

Main responsibilities:

- fetch company financial statements
- collect market data
- compute derived financial metrics
- enrich datasets with indicators relevant to LBO screening

Libraries used:
