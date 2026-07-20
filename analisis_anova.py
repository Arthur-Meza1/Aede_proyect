import re
import warnings
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from itertools import combinations

warnings.filterwarnings('ignore')

# ── 1. Cargar datos ──────────────────────────────────────────────────
df = pd.read_csv('resultados.csv', skiprows=11, skipinitialspace=True, dtype=str)

# Renombrar columnas con espacios
df.columns = [c.strip().replace('"', '') for c in df.columns]

# ── 2. Filtrar solo filas con datos de repeticiones (no _mean, _median, etc.) ──
def es_repeticion(name):
    return not name.endswith('_mean') and not name.endswith('_median') \
       and not name.endswith('_stddev') and not name.endswith('_cv')

df = df[df['name'].apply(es_repeticion)].copy()

# ── 3. Parsear columnas numéricas ────────────────────────────────────
for col in ['real_time', 'Comparaciones', 'Intercambios', 'RAM_Auxiliar_KB']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['real_time', 'Comparaciones', 'Intercambios'])

# ── 4. Extraer algoritmo, tamaño, tipo de dato ───────────────────────
def parse_name(name):
    # "BM_BubbleSort/1000/0/repeats:30"
    m = re.match(r'BM_(\w+)/(\d+)/(\d+)/', name)
    if m:
        algo = m.group(1)
        size = int(m.group(2))
        dtype = int(m.group(3))
        return algo, size, dtype
    return None, None, None

df[['algoritmo', 'tamaño', 'tipo_dato']] = df['name'].apply(
    lambda x: pd.Series(parse_name(x)))

# Mapa de tipos
tipo_map = {0: 'Aleatorio', 1: 'Ordenado', 2: 'Inverso', 3: 'Parcial'}
df['tipo_label'] = df['tipo_dato'].map(tipo_map)

df = df.dropna(subset=['algoritmo'])
print(f"Filas analizadas: {len(df)}")
print(f"Algoritmos: {df['algoritmo'].unique()}")
print(f"Tamaños: {sorted(df['tamaño'].unique())}")
print(f"Tipos de dato: {sorted(df['tipo_dato'].unique())}")
print()

# ── 5. Funciones de test ─────────────────────────────────────────────
NORMAL_THRESHOLD = 0.05  # p > 0.05 => no se rechaza normalidad

def elegir_test(grupos, variable):
    """
    Para cada grupo (lista de valores), test normalidad con Shapiro-Wilk.
    Si TODOS los grupos pasan normalidad -> ANOVA, sino -> Kruskal-Wallis.
    """
    pasa_normal = True
    for name_grp, vals in grupos:
        if len(vals) >= 3:
            _, p_shapiro = stats.shapiro(vals)
            if p_shapiro < NORMAL_THRESHOLD:
                pasa_normal = False
                break
    return 'ANOVA' if pasa_normal else 'Kruskal-Wallis'

def realizar_test(grupos, variable):
    """Ejecuta ANOVA o Kruskal-Wallis y devuelve resultados."""
    test_type = elegir_test(grupos, variable)
    nombres = [g[0] for g in grupos]
    valores = [g[1] for g in grupos]
    
    if test_type == 'ANOVA':
        # ANOVA de una vía
        f_val, p_val = stats.f_oneway(*valores)
        stat_name = 'F'
        stat_val = f_val
    else:
        h_val, p_val = stats.kruskal(*valores)
        stat_name = 'H'
        stat_val = h_val
    
    # Post-hoc si es significativo y hay >2 grupos
    posthoc = None
    if p_val < 0.05 and len(grupos) > 2:
        posthoc = []
        for (n1, v1), (n2, v2) in combinations(zip(nombres, valores), 2):
            if test_type == 'ANOVA':
                _, p_pair = stats.ttest_ind(v1, v2)
            else:
                _, p_pair = stats.mannwhitneyu(v1, v2, alternative='two-sided')
            posthoc.append((n1, n2, p_pair))
    
    return {
        'test': test_type,
        'stat_name': stat_name,
        'stat_val': stat_val,
        'p_val': p_val,
        'n_grupos': len(grupos),
        'posthoc': posthoc,
        'medias': {n: np.mean(v) for n, v in zip(nombres, valores)},
        'desvs': {n: np.std(v, ddof=1) for n, v in zip(nombres, valores)}
    }

def format_resultado(r, variable):
    """Formatea el resultado del test."""
    sig = '***' if r['p_val'] < 0.001 else '**' if r['p_val'] < 0.01 else '*' if r['p_val'] < 0.05 else 'ns'
    p_str = f"{r['p_val']:.6f}" if r['p_val'] >= 1e-4 else f"{r['p_val']:.2e}"
    line = f"  Test: {r['test']:15s} | {r['stat_name']} = {r['stat_val']:10.4f} | p = {p_str} {sig}"
    return line

def tabla_posthoc(posthoc):
    if not posthoc:
        return "  (No aplica)"
    lines = ["  Post-hoc (comparaciones por pares):"]
    for n1, n2, p in posthoc:
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        p_str = f"{p:.6f}" if p >= 1e-4 else f"{p:.2e}"
        lines.append(f"    {n1:12s} vs {n2:12s} | p = {p_str} {sig}")
    return "\n".join(lines)

# ── 6. ANÁLISIS 1: Comparar tipos de dato por algoritmo+tamaño ───────
print("═" * 80)
print("ANÁLISIS 1: COMPARAR TIPOS DE DATO (0,1,2,3) POR ALGORITMO Y TAMAÑO")
print("═" * 80)

variables = ['real_time', 'Comparaciones', 'Intercambios']
var_labels = {'real_time': 'Tiempo (ns)', 'Comparaciones': 'Comparaciones', 'Intercambios': 'Intercambios'}

for algo in sorted(df['algoritmo'].unique()):
    for size in sorted(df['tamaño'].unique()):
        sub = df[(df['algoritmo'] == algo) & (df['tamaño'] == size)]
        if sub.empty:
            continue
        
        print(f"\n{'-' * 70}")
        print(f"Algoritmo: {algo:15s} | Tamaño: {size}")
        print(f"{'-' * 70}")
        
        for var in variables:
            grupos = []
            for dt in sorted(sub['tipo_dato'].unique()):
                vals = sub[sub['tipo_dato'] == dt][var].dropna().values
                if len(vals) > 0:
                    grupos.append((tipo_map[dt], vals))
            
            if len(grupos) < 2:
                continue
            
            r = realizar_test(grupos, var)
            
            print(f"\n  Variable: {var_labels[var]}")
            print(f"  {'-' * 40}")
            for name, vals in grupos:
                print(f"    {name:12s} | n={len(vals):2d} | media={np.mean(vals):>12.2f} | std={np.std(vals,ddof=1):>12.2f}")
            print(f"  {'-' * 40}")
            print(f"  {format_resultado(r, var)}")
            if r['posthoc']:
                print(tabla_posthoc(r['posthoc']))

# ── 7. ANÁLISIS 2: Comparar algoritmos por tipo de dato y tamaño ─────
print("\n\n" + "═" * 80)
print("ANÁLISIS 2: COMPARAR ALGORITMOS POR TIPO DE DATO Y TAMAÑO")
print("═" * 80)

for size in sorted(df['tamaño'].unique()):
    for dt in sorted(df['tipo_dato'].unique()):
        sub = df[(df['tamaño'] == size) & (df['tipo_dato'] == dt)]
        if sub.empty:
            continue
        
        print(f"\n{'-' * 70}")
        print(f"Tamaño: {size:7d} | Tipo de dato: {tipo_map[dt]:12s}")
        print(f"{'-' * 70}")
        
        for var in variables:
            grupos = []
            for algo in sorted(sub['algoritmo'].unique()):
                vals = sub[sub['algoritmo'] == algo][var].dropna().values
                if len(vals) > 0:
                    grupos.append((algo, vals))
            
            if len(grupos) < 2:
                continue
            
            r = realizar_test(grupos, var)
            
            print(f"\n  Variable: {var_labels[var]}")
            print(f"  {'-' * 40}")
            for name, vals in grupos:
                print(f"    {name:15s} | n={len(vals):2d} | media={np.mean(vals):>14.2f} | std={np.std(vals,ddof=1):>14.2f}")
            print(f"  {'-' * 40}")
            print(f"  {format_resultado(r, var)}")
            if r['posthoc']:
                print(tabla_posthoc(r['posthoc']))

print("\n\nListo. Significancia: * p<0.05  ** p<0.01  *** p<0.001  ns = no significativo")
