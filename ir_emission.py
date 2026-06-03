"""
ir_emission.py
==============
Radiometric IR emission calculator — Planck / Stefan-Boltzmann

Computes:
  - Total radiated power (Stefan-Boltzmann)
  - Band-integrated power in a specified wavelength range (Planck midpoint rule)
  - Band fraction, band irradiance, Wien peak wavelength

Usage (interactive):
    python ir_emission.py

Usage (as module):
    from ir_emission import calc_emission
    result = calc_emission(temp_c=150, area_m2=0.117, emissivity=0.96,
                           lambda1_um=8.0, lambda2_um=10.0)
    print(result)
"""

import math

# ── Physical constants ────────────────────────────────────────────────────────
H   = 6.62607015e-34   # Planck constant       J·s
C   = 2.99792458e8     # Speed of light        m/s
K_B = 1.380649e-23     # Boltzmann constant    J/K
SIG = 5.670374419e-8   # Stefan-Boltzmann      W/m²K⁴


def planck_spectral_radiance(wavelength_um: float, temp_k: float) -> float:
    """
    Spectral radiance B(λ, T) in W / m² / sr / µm.

    Parameters
    ----------
    wavelength_um : float  Wavelength in micrometres
    temp_k        : float  Temperature in Kelvin

    Returns
    -------
    float  Spectral radiance [W/m²/sr/µm]
    """
    lam_m = wavelength_um * 1e-6
    exponent = min(H * C / (lam_m * K_B * temp_k), 700)  # clamp to avoid overflow
    return (2 * H * C**2 / lam_m**5) / (math.exp(exponent) - 1) * 1e-6


def integrate_planck_band(temp_k: float, lambda1_um: float, lambda2_um: float,
                           n_steps: int = 500) -> float:
    """
    Integrate Planck spectral radiance over [lambda1, lambda2] using the
    midpoint rule.  Returns hemispherical spectral irradiance in W / m².

    The factor π converts sr-based radiance to hemispherical irradiance,
    consistent with σT⁴ from Stefan-Boltzmann.
    """
    dl = (lambda2_um - lambda1_um) / n_steps
    total = sum(
        planck_spectral_radiance(lambda1_um + (i + 0.5) * dl, temp_k)
        for i in range(n_steps)
    )
    return math.pi * total * dl * 1e-6   # dl µm → m handled inside planck; *1e-6 for µm→m of dl


def calc_emission(temp_c: float, area_m2: float, emissivity: float,
                  lambda1_um: float, lambda2_um: float,
                  n_steps: int = 500) -> dict:
    """
    Calculate radiometric emission for a grey-body object.

    Parameters
    ----------
    temp_c      : float  Surface temperature in °C
    area_m2     : float  Radiating surface area in m²
    emissivity  : float  Grey-body emissivity (0–1)
    lambda1_um  : float  Band start wavelength in µm
    lambda2_um  : float  Band end wavelength in µm
    n_steps     : int    Integration steps (default 500)

    Returns
    -------
    dict with keys:
        temp_k          Temperature in Kelvin
        peak_lambda_um  Wien peak wavelength (µm)
        p_total_w       Total radiated power (W)  — Stefan-Boltzmann
        p_band_w        Power in [λ₁, λ₂] band (W)
        band_fraction   p_band / p_total
        band_irradiance Band power per unit area (W/m²)
    """
    temp_k = temp_c + 273.15
    peak_lambda = 2897.8 / temp_k
    p_total = emissivity * SIG * temp_k**4 * area_m2
    band_irradiance_per_m2 = emissivity * integrate_planck_band(temp_k, lambda1_um, lambda2_um, n_steps)
    p_band = band_irradiance_per_m2 * area_m2

    return {
        "temp_k":           round(temp_k, 3),
        "peak_lambda_um":   round(peak_lambda, 3),
        "p_total_w":        round(p_total, 4),
        "p_band_w":         round(p_band, 4),
        "band_fraction":    round(p_band / p_total, 6) if p_total else 0.0,
        "band_irradiance":  round(band_irradiance_per_m2, 4),
    }


def compare(objects: list[dict]) -> list[dict]:
    """
    Run calc_emission on a list of object dicts.
    Each dict must have keys: temp_c, area_m2, emissivity, lambda1_um, lambda2_um.
    Returns list of result dicts with the input label preserved.
    """
    results = []
    for obj in objects:
        r = calc_emission(**{k: v for k, v in obj.items() if k != "label"})
        r["label"] = obj.get("label", "Object")
        results.append(r)
    return results


def _prompt_float(prompt: str, default: float) -> float:
    raw = input(f"{prompt} [{default}]: ").strip()
    return float(raw) if raw else default


def _prompt_int(prompt: str, default: int) -> int:
    raw = input(f"{prompt} [{default}]: ").strip()
    return int(raw) if raw else default


def interactive():
    print("\n" + "═" * 54)
    print("  Radiometric IR Emission Calculator")
    print("═" * 54)
    temp_c     = _prompt_float("Temperature (°C)",         150.0)
    area_m2    = _prompt_float("Surface area (m²)",         0.05)
    emissivity = _prompt_float("Emissivity ε  (0–1)",       0.96)
    lambda1    = _prompt_float("Band start λ₁ (µm)",         8.0)
    lambda2    = _prompt_float("Band end   λ₂ (µm)",        10.0)
    n_steps    = _prompt_int  ("Integration steps",          500)

    r = calc_emission(temp_c, area_m2, emissivity, lambda1, lambda2, n_steps)

    print("\n" + "─" * 54)
    print(f"  Temperature             {r['temp_k']:.2f} K")
    print(f"  Wien peak wavelength    {r['peak_lambda_um']:.2f} µm")
    print(f"  Total radiated power    {r['p_total_w']:.3f} W")
    print(f"  Band power [{lambda1}–{lambda2} µm]  {r['p_band_w']:.3f} W")
    print(f"  Band fraction           {r['band_fraction']*100:.3f} %")
    print(f"  Band irradiance         {r['band_irradiance']:.3f} W/m²")
    print("─" * 54 + "\n")


if __name__ == "__main__":
    interactive()
