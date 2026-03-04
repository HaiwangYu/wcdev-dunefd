#!/usr/bin/env python3
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List, Dict, Tuple


# -----------------------------
# HDF5 loading / preprocessing
# -----------------------------
def _load_2d(h5_path: str, dset_path: str) -> np.ndarray:
    with h5py.File(h5_path, "r") as f:
        if dset_path not in f:
            raise KeyError(f"Dataset not found: {dset_path}")
        data = f[dset_path][...]
    if data.ndim != 2:
        raise ValueError(f"Expected 2D dataset, got ndim={data.ndim}, shape={data.shape}")
    return data


def _prep(data: np.ndarray, transpose: bool = True, log_scale: bool = False) -> np.ndarray:
    img = data.T if transpose else data
    if log_scale:
        # NOTE: <=0 values become 1e-12 (sign info lost). Keep log_scale=False for signed charge plots.
        img = np.log10(np.maximum(img, 1e-12))
    return img


def _try_load_prepped(
    h5_path: str,
    group: str,
    name: str,
    transpose: bool,
    log_scale: bool,
) -> Optional[np.ndarray]:
    dset_path = f"/{group}/{name}"
    try:
        arr = _load_2d(h5_path, dset_path)
    except KeyError as e:
        print(f"[Warn] {e} -> skip")
        return None
    except Exception as e:
        print(f"[Warn] Failed to load {dset_path}: {e} -> skip")
        return None
    return _prep(arr, transpose=transpose, log_scale=log_scale)


def _load_optional_or_zeros(
    h5_path: str,
    group: str,
    name: str,
    transpose: bool,
    log_scale: bool,
    ref_shape: Tuple[int, int],
    warn_prefix: str = "",
) -> Tuple[np.ndarray, bool]:
    """
    Try load an optional dataset. If missing/fails/shape mismatch:
      - warn
      - return zeros(ref_shape)
      - available=False (so it won't be plotted)
    """
    img = _try_load_prepped(h5_path, group, name, transpose, log_scale)
    if img is None:
        tag = warn_prefix or name
        print(f"[Warn] {tag}: could not load /{group}/{name} -> use zeros & do NOT plot")
        return np.zeros(ref_shape, dtype=float), False

    if img.shape != ref_shape:
        tag = warn_prefix or name
        print(f"[Warn] {tag}: shape mismatch {img.shape} vs {ref_shape} -> use zeros & do NOT plot")
        return np.zeros(ref_shape, dtype=float), False

    return img, True


# -----------------------------
# APA suffix helpers
# -----------------------------
def apa_index_to_apa_number(apa_index: int) -> int:
    """0->1, 1->2, ..., 7->8"""
    if not (0 <= apa_index <= 7):
        raise ValueError(f"apa_index must be in [0..7], got {apa_index}")
    return apa_index + 1


def with_apa_suffix(base_name: str, apa_index: int, enabled: bool = True) -> Optional[str]:
    """
    Append APA index suffix to base_name (e.g. 'frame_gauss' + '3' -> 'frame_gauss3').
    If enabled=False, return None.
    """
    if not enabled:
        return None
    return f"{base_name}{apa_index}"


# -----------------------------
# Main plotting function
# -----------------------------
def save_waveforms_truth_vs_multi(
    reco_h5: str,
    truth_h5: str,
    outdir: str = "wf_out",
    reco_group: str = "100",
    truth_group: str = "0",
    # APA selection
    apa_index: int = 0,  # 0..7 (0=>APA1, 3=>APA4)
    # Base dataset names (suffix will be added automatically for these)
    truth_base: str = "frame_deposplat",
    gauss_base: str = "frame_gauss",
    loose_lf_base: str = "frame_loose_lf",
    mp2_roi_base: str = "frame_mp2_roi",
    mp3_roi_base: str = "frame_mp3_roi",
    # Decon has no APA suffix (per your request)
    decon_name: str = "frame_decon_charge0",
    # Plot toggles
    plot_gauss: bool = True,
    plot_decon: bool = True,
    plot_loose_lf: bool = True,
    plot_mp2_roi: bool = True,
    plot_mp3_roi: bool = True,
    # Ranges / style
    wire_start: int = 330,
    wire_end: int = 380,   # inclusive
    tmin: int = 3000,
    tmax: int = 4000,
    transpose: bool = True,
    log_scale: bool = False,
    dpi: int = 200,
    show: bool = False,
):
    os.makedirs(outdir, exist_ok=True)

    apa_no = apa_index_to_apa_number(apa_index)

    # Build dataset names with APA suffix (no need to manually edit trailing digits)
    truth_name = with_apa_suffix(truth_base, apa_index, enabled=True)
    gauss_name = with_apa_suffix(gauss_base, apa_index, enabled=True)
    loose_name = with_apa_suffix(loose_lf_base, apa_index, enabled=True)
    mp2_name = with_apa_suffix(mp2_roi_base, apa_index, enabled=True)
    mp3_name = with_apa_suffix(mp3_roi_base, apa_index, enabled=True)

    # --- Load truth (required) ---
    truth_img = _try_load_prepped(truth_h5, truth_group, truth_name, transpose, log_scale)
    if truth_img is None:
        raise RuntimeError(
            f"Truth dataset could not be loaded: /{truth_group}/{truth_name} "
            f"(apa_index={apa_index}, APA{apa_no})."
        )

    ref_shape = truth_img.shape  # (time, wire) after prep
    n_time, n_wire = ref_shape

    # --- Load optional overlays (missing -> warn + zeros + not plotted) ---
    gauss_img, gauss_ok = _load_optional_or_zeros(
        reco_h5, reco_group, gauss_name, transpose, log_scale, ref_shape, warn_prefix="gauss"
    )
    decon_img, decon_ok = _load_optional_or_zeros(
        reco_h5, reco_group, decon_name, transpose, log_scale, ref_shape, warn_prefix="decon"
    )
    loose_img, loose_ok = _load_optional_or_zeros(
        reco_h5, reco_group, loose_name, transpose, log_scale, ref_shape, warn_prefix="loose_lf"
    )
    mp2_img, mp2_ok = _load_optional_or_zeros(
        reco_h5, reco_group, mp2_name, transpose, log_scale, ref_shape, warn_prefix="mp2_roi"
    )
    mp3_img, mp3_ok = _load_optional_or_zeros(
        reco_h5, reco_group, mp3_name, transpose, log_scale, ref_shape, warn_prefix="mp3_roi"
    )

    # --- clamp ranges ---
    tmin2 = max(0, tmin)
    tmax2 = min(n_time - 1, tmax)
    if tmin2 > tmax2:
        raise ValueError(f"Invalid time range after clamp: tmin={tmin2}, tmax={tmax2}, n_time={n_time}")

    w0 = max(0, wire_start)
    w1 = min(n_wire - 1, wire_end)
    if w0 > w1:
        raise ValueError(f"Invalid wire range after clamp: wire_start={w0}, wire_end={w1}, n_wire={n_wire}")

    tt = np.arange(tmin2, tmax2 + 1)

    overlays = ["truth"]
    if plot_gauss and gauss_ok:
        overlays.append("gauss")
    if plot_decon and decon_ok:
        overlays.append("decon")
    if plot_loose_lf and loose_ok:
        overlays.append("loose_lf")
    if plot_mp2_roi and mp2_ok:
        overlays.append("mp2_roi")
    if plot_mp3_roi and mp3_ok:
        overlays.append("mp3_roi")

    print(f"[Info] APA index={apa_index} -> APA{apa_no}")
    print(f"[Info] truth dataset = /{truth_group}/{truth_name}")
    print(f"[Info] truth_img shape (time, wire) = {ref_shape}")
    print(f"[Info] overlays (actually plotted) = {overlays}")
    print(f"[Info] Saving waveforms: wire {w0}..{w1}, time {tmin2}..{tmax2} -> {outdir}")

    for wire_ch in range(w0, w1 + 1):
        wf_truth = truth_img[tmin2:tmax2 + 1, wire_ch]

        plt.figure(figsize=(10, 4))
        plt.plot(tt, wf_truth, label="truth")

        if plot_gauss and gauss_ok:
            plt.plot(tt, gauss_img[tmin2:tmax2 + 1, wire_ch], label="gauss")

        if plot_decon and decon_ok:
            plt.plot(tt, decon_img[tmin2:tmax2 + 1, wire_ch], label="decon")

        if plot_loose_lf and loose_ok:
            plt.plot(tt, loose_img[tmin2:tmax2 + 1, wire_ch], label="loose_lf")

        if plot_mp2_roi and mp2_ok:
            plt.plot(tt, mp2_img[tmin2:tmax2 + 1, wire_ch], label="mp2_roi")

        if plot_mp3_roi and mp3_ok:
            plt.plot(tt, mp3_img[tmin2:tmax2 + 1, wire_ch], label="mp3_roi")

        plt.xlabel("time tick")
        plt.ylabel("charge" + (" (log10)" if log_scale else ""))
        plt.title(f"APA{apa_no} | wire={wire_ch}, time=[{tmin2},{tmax2}]")

        # y-limits
        if log_scale:
            # Choose limits from plotted data to avoid invalid/NaN ranges.
            ys = [wf_truth]
            if plot_gauss and gauss_ok:
                ys.append(gauss_img[tmin2:tmax2 + 1, wire_ch])
            if plot_decon and decon_ok:
                ys.append(decon_img[tmin2:tmax2 + 1, wire_ch])
            if plot_loose_lf and loose_ok:
                ys.append(loose_img[tmin2:tmax2 + 1, wire_ch])
            if plot_mp2_roi and mp2_ok:
                ys.append(mp2_img[tmin2:tmax2 + 1, wire_ch])
            if plot_mp3_roi and mp3_ok:
                ys.append(mp3_img[tmin2:tmax2 + 1, wire_ch])
            yall = np.concatenate([np.asarray(y, dtype=float) for y in ys])
            ylo = np.nanmin(yall)
            yhi = np.nanmax(yall)
            if np.isfinite(ylo) and np.isfinite(yhi) and ylo != yhi:
                pad = 0.05 * (yhi - ylo)
                plt.ylim(ylo - pad, yhi + pad)
        else:
            plt.ylim(-2000, 12000)

        plt.legend()
        plt.tight_layout()

        fname = f"wf_APA{apa_no}_wire{wire_ch}_t{tmin2}-{tmax2}.png"
        fpath = os.path.join(outdir, fname)
        plt.savefig(fpath, dpi=dpi, bbox_inches="tight")

        if show:
            plt.show()

        plt.close()
        print(f"[Saved] {fpath}")


if __name__ == "__main__":
    workdir = "Wiener_tight_U-pdhd/"
    reco_h5  = workdir + "g4-rec-0.h5"
    truth_h5 = workdir + "g4-tru-0.h5"

    save_waveforms_truth_vs_multi(
        reco_h5=reco_h5,
        truth_h5=truth_h5,
        outdir=workdir,
        reco_group="100",
        truth_group="0",
        apa_index=0,  # 0..7 (0=>APA1, 3=>APA4)
        # base names (suffix auto-added)
        truth_base="frame_deposplat",
        gauss_base="frame_gauss",
        loose_lf_base="frame_loose_lf",
        mp2_roi_base="frame_mp2_roi",
        mp3_roi_base="frame_mp3_roi",
        # decon (no APA suffix)
        decon_name="frame_decon_charge0",
        # toggles
        plot_gauss=False,
        plot_decon=True,
        plot_loose_lf=False,
        plot_mp2_roi=False,
        plot_mp3_roi=False,
        # ranges
        wire_start=200,
        wire_end=201,
        tmin=3200,
        tmax=3400,
        transpose=True,
        log_scale=False,
        dpi=300,
        show=False,
    )

