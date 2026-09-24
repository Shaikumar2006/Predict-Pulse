# Predictive Maintenance & Energy-Cost Advisory System

> Turning early-stage bearing vibration into a **rupee-per-week energy-cost signal**, built for Indian SME manufacturers who can't afford enterprise condition monitoring.

**Yuva Yodha 2026 · Smart Manufacturing Track — Industrial Energy & Process Efficiency**

<!-- Optional: add badges, e.g. Python version, license, build status -->
<!-- ![Python](https://img.shields.io/badge/python-3.x-blue) ![License](https://img.shields.io/badge/license-MIT-green) -->

---

## Table of Contents

- [Why this exists](#why-this-exists)
- [What it does](#what-it-does)
- [How it works](#how-it-works)
- [Results](#results)
- [Getting started](#getting-started)
- [Project structure](#project-structure)
- [Assumptions and baseline](#assumptions-and-baseline)
- [Affordability and deployment](#affordability-and-deployment)
- [Roadmap](#roadmap)
- [Limitations](#limitations)
- [Team](#team)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Why this exists

Industry accounts for roughly **35–40% of India's total energy consumption**, and energy can be **15–30% of production cost** for SME manufacturers. Much of that energy goes to motors, pumps, compressors and fans, and almost none of it is monitored for mechanical degradation.

Faults develop for weeks before a breakdown, and during that time the degrading machine quietly draws more electricity for the same output. SMEs are usually stuck with two options:

- **Reactive maintenance:** fix it when it breaks. Emergency repairs cost roughly 3–5× more than planned ones.
- **Time-based maintenance:** replace parts on a fixed schedule, regardless of condition.

Commercial condition-monitoring systems exist, but they are priced and packaged for large plants.

## What it does

The system detects **early-stage bearing degradation** from vibration signals. Unlike most fault-detection tools, which stop at "a fault was detected", it turns that degradation into two numbers an operator can act on:

| Output | Meaning |
|---|---|
| **Estimated ₹ / week energy cost** | Severity is converted into an efficiency loss and a weekly excess energy cost, using the motor's rated power and local tariff. |
| **Avoidable emergency-repair premium** | The extra repair cost avoided by acting early, based on the documented 3–5× reactive-vs-planned repair gap. |

## How it works

```mermaid
flowchart LR
    A[Vibration signal<br/>raw time-series per machine] --> B[Feature extraction<br/>six features]
    B --> C[Baseline model<br/>unsupervised, healthy period only]
    C --> D[Severity score<br/>per-machine threshold]
    D --> E[Dashboard<br/>health score, alert, ₹/week]
```

1. **Vibration signal:** a raw time-series per machine.
2. **Feature extraction:** six features, including defect-frequency energy derived from bearing geometry.
3. **Baseline model:** unsupervised, trained only on that machine's *healthy* operating period, so **no labelled failure history is needed**.
4. **Severity score:** the alert threshold is calibrated to that bearing's own noise floor.
5. **Dashboard output:** a running health score, an alert, and the ₹/week cost of inaction.

**Design finding:** outer-race, inner-race and roller-element faults produce genuinely different baseline vibration noise, so a single fixed alert threshold does not transfer across fault types. Calibrating each bearing's threshold from its own healthy noise level is what makes the approach hold up across them.

## Results

Validated on **real bearings run to physical failure**, using the NASA / IMS Prognostics Data Repository (Rexnord ZA-2115 bearings). This is not a simulated dataset.

| Bearing | Fault type | Early-warning lead time |
|---|---|---|
| Bearing 1 | Outer race | **3.08 days** |
| Bearing 3 | Inner race | **2.35 days** |
| Bearing 4 | Roller element | **4.98 days** |

<!-- Optional: add a plot, e.g. ![Health score vs time](docs/images/health_score.png) -->
<!-- Optional: add a dashboard screenshot, e.g. ![Dashboard](docs/images/dashboard.png) -->

## Getting started

<!-- TODO: replace with your actual setup. The commands below are placeholders. -->

**Prerequisites**

- Python 3.x <!-- TODO: confirm version -->
- The NASA / IMS bearing dataset (see [Acknowledgements](#acknowledgements))

**Install**

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

**Run the pipeline**

```bash
# TODO: replace with your real entry point(s)
python run_pipeline.py --data path/to/ims_data
```

**Launch the dashboard**

```bash
# TODO: replace with your real dashboard command
```

## Project structure

<!-- TODO: replace with your actual layout. -->

```
.
├── data/            # NASA / IMS data (not committed; see Acknowledgements)
├── src/             # feature extraction, baseline model, severity scoring, cost translation
├── dashboard/       # dashboard prototype
├── notebooks/       # analysis and validation
├── docs/            # pitch deck, architecture diagram, images
├── requirements.txt
└── README.md
```

## Assumptions and baseline

| Item | Value | Basis |
|---|---|---|
| **Baseline** | SME machine on reactive or fixed-schedule maintenance, with no visibility into actual condition | Typical SME practice |
| **Efficiency loss from degradation** | 1.5–4% | Published motor-fault literature |
| **Repair premium avoided** | 3–5× | Documented reactive-vs-planned repair cost gap |
| **Rated-power basis** | IE3 efficiency class combined with local tariff | India's BEE-mandated IE3 standard |

The ₹/week figure is an **estimate** built on these assumptions. It is a decision aid, not a metered measurement.

## Affordability and deployment

| | This system | Commercial wireless sensors |
|---|---|---|
| **Cost per monitoring point** | ~₹1,500–2,000 (ESP32-class hardware) | ₹15,000–50,000 |

The detection and cost-translation pipeline is already validated on real historical sensor data. Hardware is the next deployment step, using commodity, locally available ESP32-class components rather than proprietary wireless nodes.

## Roadmap

- [x] Detection and cost-translation pipeline validated on real historical data (NASA / IMS)
- [x] Working dashboard prototype
- [ ] Build the ESP32-class sensor node (~₹1,500–2,000 per point) and connect its live stream to the pipeline
- [ ] Pilot with an SME partner: validate lead time and cost estimates in live, in-plant conditions
- [ ] Extend feature extraction to more pump, motor and compressor types and additional SME sites

## Limitations

- Validated on **three bearings** from one public dataset. Results on other machines and operating conditions are not yet established.
- No physical sensor install has been done yet; live in-plant performance is a pilot goal.
- Cost figures depend on literature-derived assumptions (efficiency loss, repair premium) and should be tuned with a plant's real data.

## Team

**Gear Sense**: electronics and signal-processing and machine-learning strength, combined with a materials / failure-characterization research background.

| Member | About |
|---|---|
| Shaik Muhammad Umar | Metallurgy and Material Sciences Undergrad at NIT Durgapur |
| Md. Inzemam Khan | Electronics and Communications Undergrad at NIT Durgapur |
| Shaik Mohammed Zabeehullah | Electronics and Communications Undergrad at NIT Durgapur |

## Acknowledgements

- **Data:** NASA / IMS Prognostics Data Repository, Rexnord ZA-2115 bearing run-to-failure datasets. Please cite and download from the original source: <!-- TODO: add the official dataset link -->
- Built for the **Yuva Yodha 2026** Smart Manufacturing track.

## License 
This project is licensed under the [MIT License].
