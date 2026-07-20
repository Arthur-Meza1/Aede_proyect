import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import argparse
import warnings
import os

warnings.filterwarnings("ignore")
sns.set_theme(style="white", font="DejaVu Sans", font_scale=1.1)
plt.rcParams.update({
    "axes.facecolor": "#f8f9fa",
    "axes.edgecolor": "#dee2e6",
    "axes.grid": True,
    "grid.color": "#dee2e6",
    "grid.alpha": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
})

DIST_MAP = {"0": "Aleatorio", "1": "Ordenado", "2": "Inverso", "3": "Parcial"}
ALGO_ORDER = ["BubbleSort", "InsertionSort", "MergeSort", "QuickSort", "HeapSort"]

ALGO_PALETTE = {
    "BubbleSort":    "#d62728",
    "InsertionSort": "#ff7f0e",
    "MergeSort":     "#2ca02c",
    "QuickSort":     "#1f77b4",
    "HeapSort":      "#9467bd",
}

DIST_PALETTE = {
    "Aleatorio":  "#1f77b4",
    "Ordenado":   "#2ca02c",
    "Inverso":    "#d62728",
    "Parcial":    "#ff7f0e",
}

DIST_COLORS_ORDERED = ["#1f77b4", "#2ca02c", "#d62728", "#ff7f0e"]


def parse_benchmark_name(name):
    m = re.match(r"BM_(\w+)/(\d+)/(\d+)", name)
    if not m:
        return None
    algo = m.group(1)
    n = int(m.group(2))
    dist = DIST_MAP.get(m.group(3), m.group(3))
    suffix = name.split("repeats:30")[-1]
    return {"algorithm": algo, "n": n, "distribution": dist, "aggregate": bool(suffix)}


def load_results(path):
    with open(path) as f:
        lines = f.readlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith("name,"))
    df = pd.read_csv(path, skiprows=header_idx, quotechar='"',
                     dtype={"Comparaciones": float, "Intercambios": float,
                            "RAM_Auxiliar_KB": float, "real_time": float,
                            "cpu_time": float})
    parsed = df["name"].apply(parse_benchmark_name)
    valid = parsed.notna()
    meta = pd.DataFrame(parsed[valid].tolist(), index=df[valid].index)
    df = df[valid].copy()
    for col in meta.columns:
        df[col] = meta[col]
    df = df[~df["aggregate"]].copy()
    df["cpu_time_ms"] = df["cpu_time"] / 1e6
    df["real_time_ms"] = df["real_time"] / 1e6
    return df


def _config_axes(ax, xlabel, ylabel, title=None, legend_title=None):
    ax.set_xlabel(xlabel, fontsize=12, fontweight="semibold")
    ax.set_ylabel(ylabel, fontsize=12, fontweight="semibold")
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    if legend_title and ax.get_legend():
        ax.get_legend().set_title(legend_title)
        ax.get_legend().get_frame().set_facecolor("white")
        ax.get_legend().get_frame().set_edgecolor("#dee2e6")


def plot_tiempo_por_algoritmo_y_distribucion(df, output_dir):
    for algo in ALGO_ORDER:
        sub = df[df["algorithm"] == algo]
        if sub.empty:
            continue
        g = sns.catplot(
            data=sub, x="n", y="cpu_time_ms", hue="distribution",
            kind="box", height=5, aspect=1.4, log_scale=(True, True),
            palette=DIST_COLORS_ORDERED, linewidth=1.2, width=0.6,
            boxprops=dict(alpha=0.85), whiskerprops=dict(linewidth=1.2),
            capprops=dict(linewidth=1.2), medianprops=dict(linewidth=1.8, color="black"),
            flierprops=dict(marker="o", markersize=4, markerfacecolor="#adb5bd",
                            markeredgecolor="none", alpha=0.5),
        )
        algo_label = algo.replace("Sort", " Sort")
        g.fig.suptitle(f"{algo_label} — Tiempo de CPU por Tamaño y Distribución",
                       y=1.03, fontsize=14, fontweight="bold")
        g.set_axis_labels("Tamaño (n)", "Tiempo de CPU (ms)")
        g._legend.set_title("Distribución")
        for text in g._legend.get_texts():
            text.set_fontsize(10)
        g.tight_layout()
        g.savefig(f"{output_dir}/tiempo_{algo}.png")
        plt.close(g.fig)


def plot_tiempo_todos_algoritmos(df, output_dir):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(
        data=df, x="algorithm", y="cpu_time_ms", hue="distribution",
        order=ALGO_ORDER, palette=DIST_COLORS_ORDERED, linewidth=1.0, width=0.7,
        boxprops=dict(alpha=0.85), medianprops=dict(linewidth=1.8, color="black"),
        flierprops=dict(marker="o", markersize=3, markerfacecolor="#adb5bd",
                        markeredgecolor="none", alpha=0.4),
        ax=ax,
    )
    ax.set_yscale("log")
    labels = [a.replace("Sort", " Sort") for a in ALGO_ORDER]
    ax.set_xticklabels(labels, fontsize=11)
    _config_axes(ax, "Algoritmo", "Tiempo de CPU (ms) — escala log",
                 title="Tiempo de CPU por Algoritmo y Distribución",
                 legend_title="Distribución")
    plt.setp(ax.get_legend().get_texts(), fontsize=10)
    ax.get_legend().set_frame_on(True)
    fig.savefig(f"{output_dir}/tiempo_todos.png")
    plt.close(fig)


def plot_comparaciones_swaps_por_algoritmo(df, output_dir):
    for metrica, label, unit in [("Comparaciones", "Comparaciones", ""),
                                 ("Intercambios", "Intercambios", "")]:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.scatterplot(
            data=df, x="n", y=metrica, hue="algorithm", style="distribution",
            palette=ALGO_PALETTE, alpha=0.35, s=18, linewidth=0,
            ax=ax,
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        _config_axes(ax, "Tamaño (n)", f"{label}{unit}",
                     title=f"{label} vs Tamaño por Algoritmo",
                     legend_title="Algoritmo / Distrib.")
        leg = ax.get_legend()
        if leg:
            leg.set_frame_on(True)
            leg.get_frame().set_facecolor("white")
            leg.get_frame().set_edgecolor("#dee2e6")
            for text in leg.get_texts():
                text.set_fontsize(9)
        fig.savefig(f"{output_dir}/{metrica.lower()}_vs_n.png")
        plt.close(fig)


def plot_comparaciones_swaps_por_distribucion(df, output_dir):
    dist_order = ["Aleatorio", "Ordenado", "Inverso", "Parcial"]
    for metrica, label in [("Comparaciones", "Comparaciones"),
                           ("Intercambios", "Intercambios")]:
        g = sns.relplot(
            data=df, x="n", y=metrica, hue="algorithm",
            col="distribution", col_wrap=2, col_order=dist_order,
            kind="scatter", height=4, aspect=1.3,
            palette=ALGO_PALETTE, alpha=0.4, s=15, linewidth=0,
        )
        for ax, dist_name in zip(g.axes.flatten(), dist_order):
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_title(dist_name, fontsize=12, fontweight="bold", pad=10)
            ax.grid(True, alpha=0.4)
        g.set_axis_labels("Tamaño (n)", label)
        g.fig.suptitle(f"{label} por Distribución", y=1.03, fontsize=14, fontweight="bold")
        g._legend.set_title("Algoritmo")
        g._legend.set_frame_on(True)
        g._legend.get_frame().set_facecolor("white")
        g.tight_layout()
        g.savefig(f"{output_dir}/{metrica.lower()}_por_distribucion.png")
        plt.close(g.fig)


def plot_ram_auxiliar(df, output_dir):
    ram = df[["algorithm", "n", "RAM_Auxiliar_KB"]].drop_duplicates()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = sns.barplot(
        data=ram, x="n", y="RAM_Auxiliar_KB", hue="algorithm",
        palette=ALGO_PALETTE, alpha=0.85, edgecolor="white", linewidth=0.5,
        ax=ax,
    )
    _config_axes(ax, "Tamaño (n)", "RAM Auxiliar (KB)",
                 title="RAM Auxiliar por Algoritmo y Tamaño",
                 legend_title="Algoritmo")
    ax.get_legend().set_frame_on(True)
    ax.get_legend().get_frame().set_facecolor("white")
    for container in bars.containers:
        for bar in container:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                        f"{h:.0f}", ha="center", va="bottom", fontsize=8,
                        fontweight="bold", color="#495057")
    fig.savefig(f"{output_dir}/ram_auxiliar.png")
    plt.close(fig)


def plot_comparativa_n(df, output_dir, n):
    sub = df[df["n"] == n]
    if sub.empty:
        return
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5))
    labels = [a.replace("Sort", " Sort") for a in ALGO_ORDER]

    sns.boxplot(
        data=sub, x="algorithm", y="cpu_time_ms", hue="distribution",
        order=ALGO_ORDER, palette=DIST_COLORS_ORDERED, linewidth=1.0, width=0.7,
        boxprops=dict(alpha=0.85), medianprops=dict(linewidth=1.8, color="black"),
        flierprops=dict(marker="o", markersize=3, markerfacecolor="#adb5bd",
                        markeredgecolor="none", alpha=0.4),
        ax=ax1,
    )
    ax1.set_xticklabels(labels, fontsize=10)
    _config_axes(ax1, None, "Tiempo de CPU (ms)",
                 title=f"Tiempo CPU — n = {n:,}", legend_title="Distribución")

    sns.boxplot(
        data=sub, x="algorithm", y="Comparaciones", hue="distribution",
        order=ALGO_ORDER, palette=DIST_COLORS_ORDERED, linewidth=1.0, width=0.7,
        boxprops=dict(alpha=0.85), medianprops=dict(linewidth=1.8, color="black"),
        flierprops=dict(marker="o", markersize=3, markerfacecolor="#adb5bd",
                        markeredgecolor="none", alpha=0.4),
        ax=ax2,
    )
    ax2.set_xticklabels(labels, fontsize=10)
    _config_axes(ax2, None, "Comparaciones",
                 title=f"Comparaciones — n = {n:,}", legend_title="Distribución")

    for ax in (ax1, ax2):
        ax.set_xlabel("Algoritmo", fontsize=12, fontweight="semibold")
        leg = ax.get_legend()
        if leg:
            leg.set_frame_on(True)
            leg.get_frame().set_facecolor("white")
            leg.get_frame().set_edgecolor("#dee2e6")
            for t in leg.get_texts():
                t.set_fontsize(9)

    plt.tight_layout()
    fig.savefig(f"{output_dir}/comparativa_n{n}.png")
    plt.close(fig)


def generar_informe_html(df, output_dir):
    pivot = df.groupby(["algorithm", "n"])["cpu_time_ms"].agg(["mean", "std"]).round(2)
    pivot.columns = ["Media (ms)", "Desv. Estándar (ms)"]

    n_total = len(df)
    n_algos = len(df["algorithm"].unique())
    n_sizes = len(df["n"].unique())
    n_dists = len(df["distribution"].unique())
    pivot_html = pivot.to_html()
    sizes = sorted(df["n"].unique())

    html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Resultados - Sorting Benchmark</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #1a1a2e; line-height: 1.6; }}
.header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
          color: white; padding: 30px 0; text-align: center; margin-bottom: 30px; }}
.header h1 {{ font-size: 28px; margin-bottom: 6px; letter-spacing: 0.5px; }}
.header p {{ font-size: 14px; opacity: 0.8; }}
.container {{ max-width: 1300px; margin: auto; padding: 0 20px; }}
.card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #e8eaed; }}
.card h2 {{ font-size: 20px; color: #1a1a2e; margin-bottom: 16px; padding-bottom: 8px;
           border-bottom: 3px solid #0f3460; }}
.stats {{ display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 20px; }}
.stat {{ flex: 1; min-width: 140px; background: #f8f9fa; border-radius: 8px; padding: 14px 18px; text-align: center; }}
.stat .num {{ font-size: 24px; font-weight: bold; color: #0f3460; }}
.stat .lbl {{ font-size: 12px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e8eaed; }}
th {{ background: #0f3460; color: white; font-weight: 600; font-size: 12px;
     text-transform: uppercase; letter-spacing: 0.5px; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
tr:hover {{ background: #e8f0fe; }}
.gallery {{ display: flex; flex-wrap: wrap; gap: 24px; justify-content: center; }}
.gallery-item {{ flex: 1 1 45%; min-width: 420px; background: #f8f9fa; border-radius: 8px;
                padding: 12px; border: 1px solid #e8eaed; }}
.gallery-item h3 {{ font-size: 14px; color: #1a1a2e; margin-bottom: 8px;
                   padding-left: 4px; }}
.gallery-item img {{ width: 100%; height: auto; border-radius: 4px;
                    background: white; display: block; }}
.legend {{ font-size: 11px; color: #6c757d; text-align: right; margin-top: 4px; }}
</style></head>
<body>
<div class="header">
  <h1>Benchmark de Algoritmos de Ordenamiento</h1>
  <p>Resultados generados a partir de Google Benchmark &bull; 30 repeticiones por configuraci&oacute;n</p>
</div>
<div class="container">
<div class="card">
  <h2>Resumen</h2>
  <div class="stats">
    <div class="stat"><div class="num">{n_total}</div><div class="lbl">Ejecuciones</div></div>
    <div class="stat"><div class="num">{n_algos}</div><div class="lbl">Algoritmos</div></div>
    <div class="stat"><div class="num">{n_sizes}</div><div class="lbl">Tama&ntilde;os (n)</div></div>
    <div class="stat"><div class="num">{n_dists}</div><div class="lbl">Distribuciones</div></div>
  </div>
  <h3>Tiempo de CPU promedio (ms) por Algoritmo y Tama&ntilde;o</h3>
  {pivot_html}
</div>
<div class="card">
  <h2>Visualizaciones</h2>
  <div class="gallery">
"""

    plots = [
        ("tiempo_todos.png", "Tiempo de CPU — Todos los algoritmos"),
        ("tiempo_BubbleSort.png", "Bubble Sort — Tiempo CPU"),
        ("tiempo_InsertionSort.png", "Insertion Sort — Tiempo CPU"),
        ("tiempo_MergeSort.png", "Merge Sort — Tiempo CPU"),
        ("tiempo_QuickSort.png", "Quick Sort — Tiempo CPU"),
        ("tiempo_HeapSort.png", "Heap Sort — Tiempo CPU"),
        ("comparaciones_vs_n.png", "Comparaciones vs Tamaño"),
        ("intercambios_vs_n.png", "Intercambios vs Tamaño"),
        ("comparaciones_por_distribucion.png", "Comparaciones por Distribución"),
        ("intercambios_por_distribucion.png", "Intercambios por Distribución"),
        ("ram_auxiliar.png", "RAM Auxiliar por Algoritmo"),
    ]

    sizes = sorted(df["n"].unique())
    for s in sizes:
        plots.append((f"comparativa_n{s}.png", f"Comparativa n = {s:,}"))

    for fname, caption in plots:
        html += f'<div class="gallery-item"><h3>{caption}</h3><img src="{fname}" alt="{caption}"></div>\n'

    html += """</div></div>
<div class="card">
  <h2>Notas</h2>
  <ul style="padding-left: 20px; font-size: 13px; color: #495057;">
    <li>Las mediciones se realizaron con Google Benchmark compilado en modo <strong>DEBUG</strong> — los tiempos absolutos son más altos que en una build optimizada.</li>
    <li>Merge Sort es el único algoritmo con RAM auxiliar no nula: <em>(n × sizeof(int)) / 1024</em> KB.</li>
    <li>Quick Sort usa mediana-de-3 para la selección del pivote.</li>
    <li>Distribuciones: <strong>Aleatorio</strong> (shuffle), <strong>Ordenado</strong> (ascendente),
       <strong>Inverso</strong> (descendente), <strong>Parcial</strong> (~90% ordenado).</li>
  </ul>
</div>
</div>
</body>
</html>"""

    with open(f"{output_dir}/index.html", "w") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="Visualizar resultados de sorting benchmark")
    parser.add_argument("csv", nargs="?", default="resultados.csv",
                        help="Ruta al archivo CSV de resultados")
    parser.add_argument("--output", "-o", default="graficas",
                        help="Directorio de salida para las gráficas")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print(f"Cargando {args.csv} ...")
    df = load_results(args.csv)
    print(f"Datos cargados: {len(df)} ejecuciones válidas")

    print("Generando gráficas de tiempo por algoritmo...")
    plot_tiempo_por_algoritmo_y_distribucion(df, args.output)
    plot_tiempo_todos_algoritmos(df, args.output)

    print("Generando gráficas de comparaciones e intercambios...")
    plot_comparaciones_swaps_por_algoritmo(df, args.output)
    plot_comparaciones_swaps_por_distribucion(df, args.output)

    print("Generando gráfica de RAM auxiliar...")
    plot_ram_auxiliar(df, args.output)

    print("Generando comparativas detalladas...")
    for n in sorted(df["n"].unique()):
        plot_comparativa_n(df, args.output, n)

    print("Generando informe HTML...")
    generar_informe_html(df, args.output)

    print(f"¡Listo! Las gráficas se guardaron en '{args.output}/'")
    print(f"Abre '{args.output}/index.html' en tu navegador para ver el informe completo.")


if __name__ == "__main__":
    main()
