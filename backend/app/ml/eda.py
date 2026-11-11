"""Generate reproducible EDA plots from the validated real dataset."""
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from .data_loader import TARGET, FEATURES


def generate_eda(frame, output_dir: str | Path) -> list[str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    sns.set_theme(style="whitegrid")
    def save(name):
        path = output / name
        plt.tight_layout(); plt.savefig(path, dpi=150); plt.close(); paths.append(str(path))
    ax = frame[TARGET].value_counts().sort_index().plot(kind="bar", color=["#3b82f6", "#ef4444"])
    ax.set(title="Class distribution", xlabel="Class (0 legitimate, 1 fraud)", ylabel="Transactions"); save("class_distribution.png")
    sns.histplot(data=frame, x="Amount", hue=TARGET, bins=60, element="step", stat="density", common_norm=False)
    plt.title("Transaction amount distribution (full range)"); save("amount_distribution.png")
    sns.histplot(data=frame, x="Time", hue=TARGET, bins=60, element="step", stat="density", common_norm=False)
    plt.title("Transaction time distribution"); save("time_distribution.png")
    sns.histplot(data=frame[frame[TARGET] == 1], x="Amount", bins=50, color="#ef4444")
    plt.title("Fraud transaction amounts"); save("fraud_amount_distribution.png")
    plt.figure(figsize=(16, 12)); sns.heatmap(frame.corr(numeric_only=True), cmap="coolwarm", center=0)
    plt.title("Feature correlation"); save("correlation_heatmap.png")
    frame[TARGET].value_counts(normalize=True).sort_index().mul(100).plot(kind="bar", color=["#3b82f6", "#ef4444"])
    plt.ylabel("Percent"); plt.title("Fraud percentage by class"); save("class_percentage.png")
    sample_features = ["V1", "V2", "V3", "V4", "V14", "V17"]
    melted = frame[sample_features + [TARGET]].melt(id_vars=TARGET, var_name="feature", value_name="value")
    grid = sns.displot(data=melted, x="value", col="feature", hue=TARGET, col_wrap=3, kind="hist", bins=35, height=3)
    grid.savefig(output / "feature_distributions.png", dpi=150); plt.close(grid.figure); paths.append(str(output / "feature_distributions.png"))
    return paths
