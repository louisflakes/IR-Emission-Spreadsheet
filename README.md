# IR Emission Spreadsheet & Calculator

Radiometric infrared emission calculator based on the **Planck function** and **Stefan-Boltzmann law**.  
Computes total and band-integrated radiated power for any grey-body object given its temperature, surface area, emissivity, and a wavelength band of interest.

---

## Files

| File | Description |
|------|-------------|
| `ir_emission_calculator.xlsx` | Interactive Excel workbook with three sheets (Calculator, Integration, Comparison) |
| `ir_emission.py` | Python module + CLI script — same physics, no dependencies beyond stdlib |

---

## Physics

**Total radiated power** (Stefan-Boltzmann):

$$P_{total} = \varepsilon \cdot \sigma \cdot T^4 \cdot A$$

**Band-integrated power** (Planck midpoint rule):

$$P_{band} = \varepsilon \cdot A \cdot \pi \int_{\lambda_1}^{\lambda_2} B(\lambda, T) \, d\lambda$$

where the Planck spectral radiance is:

$$B(\lambda, T) = \frac{2hc^2}{\lambda^5} \cdot \frac{1}{e^{hc / \lambda k_B T} - 1}$$

---

## Excel Workbook

Three sheets:

- **IR Calculator** — enter temperature, surface area, emissivity, and wavelength band; results update automatically
- **Integration** — 500-row Planck midpoint table (visible for inspection)
- **Comparison** — side-by-side comparison of up to 4 objects with independent inputs and a quick emissivity reference table

---

## Python Usage

### Interactive CLI

```bash
python ir_emission.py
```

```
═══════════════════════════════════════════════════════
  Radiometric IR Emission Calculator
═══════════════════════════════════════════════════════
Temperature (°C) [150]:
Surface area (m²) [0.05]:
Emissivity ε  (0–1) [0.96]:
Band start λ₁ (µm) [8.0]:
Band end   λ₂ (µm) [10.0]:
Integration steps [500]:
```

### As a module

```python
from ir_emission import calc_emission, compare

# Single object
result = calc_emission(
    temp_c=150,
    area_m2=0.117,   # ~1-gallon sphere
    emissivity=0.96,
    lambda1_um=8.0,
    lambda2_um=10.0
)
print(result)
# {'temp_k': 423.15, 'peak_lambda_um': 6.849, 'p_total_w': ..., 'p_band_w': ..., ...}

# Side-by-side comparison
objects = [
    {"label": "1 gal @ 150°C", "temp_c": 150, "area_m2": 0.117, "emissivity": 0.96, "lambda1_um": 8, "lambda2_um": 10},
    {"label": "1 qt @ 200°C",  "temp_c": 200, "area_m2": 0.047, "emissivity": 0.96, "lambda1_um": 8, "lambda2_um": 10},
]
for r in compare(objects):
    print(f"{r['label']}: {r['p_band_w']:.2f} W in band")
```

---

## Emissivity Reference

| Material | ε |
|----------|---|
| Water / ice | 0.95–0.97 |
| Human skin | 0.97–0.99 |
| Painted surfaces | 0.90–0.95 |
| Concrete / asphalt | 0.90–0.97 |
| Oxidised steel | 0.70–0.80 |
| Polished copper | 0.03–0.05 |
| Polished aluminium | 0.04–0.06 |

---

## Notes

- All calculations assume thermal equilibrium and uniform grey-body emissivity.
- Surface area — not mass or volume — is the key size parameter for radiation.
- The 8–10 µm band sits within the atmospheric transmission window used by thermal cameras.
- The π factor in the band integral correctly converts sr-based Planck radiance to hemispherical irradiance, consistent with σT⁴.
