"""
=============================================================================
Mamaearth Returns & Growth Intelligence Pipeline
Part 2 - Task 11: Data Visualizations
File: analysis/visualize.py

Generates two publication-grade visual charts saved to visualizations/:
1. visualizations/return_rate_by_payment.png
   - Bar chart showing return rates across payment methods.
   - Highlights COD as the primary driver of return volume.
2. visualizations/monthly_revenue_trend.png
   - Line chart comparing apparent vs. outlier-corrected monthly revenue.
   - Illustrates the January distortion and highlights March 2026 as true peak.
=============================================================================
"""

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter
import pandas as pd

# Directories
ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_GEN_DIR = ROOT / "analysis" / "generated"
OUTPUT_DIR = ROOT / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

def plot_return_rate_by_payment():
    """Generates a clean bar chart comparing return rates by payment method."""
    csv_path = ANALYSIS_GEN_DIR / "payment_summary.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}. Run clean_and_eda.py first.")

    df = pd.read_csv(csv_path)
    df = df.sort_values(by="return_rate_pct", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

    # Highlight COD with a prominent alert tone, and digital prepaid with neutral teal
    colors = ["#d9534f" if m == "COD" else "#2e8b57" for m in df["payment_method"]]
    bars = ax.bar(df["payment_method"], df["return_rate_pct"], color=colors, width=0.52, edgecolor="none", zorder=3)

    # Annotate bar labels
    for bar, (_, row) in zip(bars, df.iterrows()):
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 1.2,
            f"{yval:.1f}%\n(n={int(row['count'])})",
            ha="center",
            va="bottom",
            fontsize=10.5,
            fontweight="bold",
            color="#222222"
        )

    # Typography and styling
    ax.set_title("Return Rate by Payment Method (COD Risk Concentration)", fontsize=14, fontweight="bold", pad=20, color="#1a202c")
    ax.set_xlabel("Payment Method", fontsize=11, fontweight="bold", labelpad=10, color="#2d3748")
    ax.set_ylabel("Return Rate (%)", fontsize=11, fontweight="bold", labelpad=10, color="#2d3748")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
    ax.set_ylim(0, 58)

    # Grid and aesthetic spines
    ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e0")
    ax.spines["bottom"].set_color("#cbd5e0")

    # Callout annotation
    ax.annotate(
        "COD return rate is >3x higher\nthan Cards & >2.3x higher than UPI",
        xy=(0, 44.4),
        xytext=(0.65, 42.0),
        arrowprops=dict(facecolor="#d9534f", arrowstyle="->", lw=1.5),
        fontsize=9.5,
        fontweight="semibold",
        color="#c53030",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#fff5f5", edgecolor="#feb2b2", lw=1)
    )

    plt.tight_layout()
    output_file = OUTPUT_DIR / "return_rate_by_payment.png"
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")

def plot_monthly_revenue_trend():
    """Generates a dual-line chart comparing apparent vs outlier-corrected monthly revenue."""
    csv_path = ANALYSIS_GEN_DIR / "monthly_revenue.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing {csv_path}. Run clean_and_eda.py first.")

    df = pd.read_csv(csv_path)

    # Format month labels to readable format: 'Jan 2026', 'Feb 2026', etc.
    month_labels = [pd.to_datetime(m).strftime("%b %Y") for m in df["month"]]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Plot both series
    ax.plot(
        month_labels,
        df["apparent_revenue_inr"],
        marker="o",
        linewidth=2.2,
        color="#a0aec0",
        linestyle="--",
        label="Apparent Revenue (with bulk outliers)",
        zorder=3
    )
    ax.plot(
        month_labels,
        df["corrected_revenue_inr"],
        marker="s",
        linewidth=2.6,
        color="#2b6cb0",
        label="Corrected Revenue (organic baseline)",
        zorder=4
    )

    # Highlight March 2026 True Peak
    march_idx = 2
    march_rev = df.loc[march_idx, "corrected_revenue_inr"]
    ax.scatter(month_labels[march_idx], march_rev, color="#3182ce", s=130, zorder=5)
    ax.annotate(
        f"True Organic Peak\nINR {march_rev:,.0f}",
        xy=(march_idx, march_rev),
        xytext=(march_idx - 0.2, march_rev + 3000),
        arrowprops=dict(facecolor="#2b6cb0", arrowstyle="->", lw=1.5),
        fontsize=9.5,
        fontweight="bold",
        color="#2b6cb0",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#ebf8ff", edgecolor="#bee3f8", lw=1)
    )

    # Highlight January Outlier Distortion
    jan_idx = 0
    jan_apparent = df.loc[jan_idx, "apparent_revenue_inr"]
    jan_corrected = df.loc[jan_idx, "corrected_revenue_inr"]
    ax.scatter(month_labels[jan_idx], jan_apparent, color="#e53e3e", s=100, zorder=5)
    ax.annotate(
        f"Distorted by 2 bulk orders\n(+INR {jan_apparent - jan_corrected:,.0f})",
        xy=(jan_idx, jan_apparent),
        xytext=(jan_idx + 0.15, jan_apparent - 2500),
        arrowprops=dict(facecolor="#e53e3e", arrowstyle="->", lw=1.2),
        fontsize=9,
        color="#c53030",
        fontweight="semibold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff5f5", edgecolor="#feb2b2", lw=1)
    )

    # Formatting
    ax.set_title("Monthly Revenue Trend: Apparent vs. Outlier-Corrected Baseline", fontsize=14, fontweight="bold", pad=20, color="#1a202c")
    ax.set_xlabel("Order Month", fontsize=11, fontweight="bold", labelpad=10, color="#2d3748")
    ax.set_ylabel("Booked Revenue (INR)", fontsize=11, fontweight="bold", labelpad=10, color="#2d3748")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"INR {x:,.0f}"))
    ax.set_ylim(5000, 33000)

    # Grid & aesthetics
    ax.grid(axis="both", linestyle="--", alpha=0.35, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e0")
    ax.spines["bottom"].set_color("#cbd5e0")

    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#e2e8f0", loc="upper right", fontsize=9.5)

    plt.tight_layout()
    output_file = OUTPUT_DIR / "monthly_revenue_trend.png"
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Saved: {output_file}")

def main():
    print("=" * 60)
    print("GENERATING VISUALIZATIONS (visualizations/)")
    print("=" * 60)
    plot_return_rate_by_payment()
    plot_monthly_revenue_trend()
    print("Both visual charts successfully generated!\n")

if __name__ == "__main__":
    main()
