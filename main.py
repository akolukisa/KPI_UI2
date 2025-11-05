import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import numpy as np  # Added for binning

# --- FILE PATHS AND SHEET NAME ---
# Reading from your specified file paths
path_pw = '/Users/akolukisa/Downloads/PW_Turkcell_DL.xlsx'
path_hw = '/Users/akolukisa/Downloads/HW_Turkcell_DL.xlsx'
sheet_name = 'Series Formatted Data'

# Define the custom limits for RSRP/Pathloss
RSRP_COL = 'LTE_UE_RSRP'
PATHLOSS_COL = 'LTE_UE_PathLoss_DL'
BLER_COL = 'LTE_UE_BLER_DL'  # BLER column name

CUSTOM_LIMITS = {
    RSRP_COL: (-110, -60),
    PATHLOSS_COL: (80, 130),
    BLER_COL: (0, 20)  # Custom limit for BLER (0-20)
}

# --- PLOTTING AND ANALYSIS COLUMNS (14 Options) ---
PLOTTING_COLUMNS = {
    '1': 'LTE_UE_RSRP',
    '2': 'LTE_UE_PathLoss_DL',
    '3': 'Physical_Throughput_DL',
    '4': 'Longitude',
    '5': 'Latitude',
    '6': 'LTE_UE_RI',
    '7': 'LTE_UE_Power_Tx_PUCCH',
    '8': 'LTE_UE_Power_Tx_PUSCH',
    '9': 'LTE_UE_Total_Power_Tx_PUSCH',
    '10': 'LTE_UE_MCS_Average_DL',
    '11': 'LTE_UE_Throughput_PDCP_DL',
    '12': 'LTE_UE_BLER_DL',
    '13': 'LTE_UE_Throughput_L1_DL',
    '14': 'LTE_UE_SINR'  # UPDATED: SINR Added
}


def guess_band_column(df):
    """Guess a column that represents 'band' information from the dataframe."""
    candidates = [c for c in df.columns if 'band' in c.lower()]
    if 'LTE_UE_EARFCN_DL' in df.columns:
        return 'LTE_UE_EARFCN_DL'
    return candidates[0] if candidates else None


def _mean_safe(series):
    try:
        s = pd.to_numeric(series, errors='coerce')
        s = s.dropna()
        return float(s.mean()) if len(s) else None
    except Exception:
        return None


def aggregate_metrics(df_slice):
    """Aggregate key KPI metrics on a dataframe slice. Returns a dict of values."""
    metrics = {}

    metric_info = {
        'CountOfSamples': {'unit': 'samples', 'description': 'Number of samples'},
        'RSRP': {'unit': 'dBm', 'description': 'Reference Signal Received Power'},
        'RSRQ': {'unit': 'dB', 'description': 'Reference Signal Received Quality'},
        'SINR': {'unit': 'dB', 'description': 'Signal to Interference Noise Ratio'},
        'PathLoss_DL': {'unit': 'dB', 'description': 'Downlink Path Loss'},
        'RI': {'unit': 'index', 'description': 'Rank Indicator'},
        'PDCP_DL': {'unit': 'Mbps', 'description': 'PDCP Downlink Throughput'},
        'L1_DL': {'unit': 'Mbps', 'description': 'L1 Downlink Throughput'},
        'BLER_DL': {'unit': '%', 'description': 'Block Error Rate Downlink'},
        'PUSCH_PWR': {'unit': 'dBm', 'description': 'PUSCH Transmit Power'},
        'PUCCH_PWR': {'unit': 'dBm', 'description': 'PUCCH Transmit Power'},
        'TOTAL_PWR': {'unit': 'dBm', 'description': 'Total Transmit Power'},
        'MCS_AVG_DL': {'unit': 'index', 'description': 'MCS Average Downlink'},
        'UE_Power_Tx': {'unit': 'dBm', 'description': 'UE Transmit Power'},
        'L1toPDCPTp_ratio': {'unit': '', 'description': 'L1 to PDCP Throughput Ratio'},
        'QPSK_pct': {'unit': '%', 'description': 'QPSK Modulation Percentage'},
        'QAM16_pct': {'unit': '%', 'description': '16QAM Modulation Percentage'},
        'QAM64_pct': {'unit': '%', 'description': '64QAM Modulation Percentage'},
        'QAM256_pct': {'unit': '%', 'description': '256QAM Modulation Percentage'},
    }

    metrics['CountOfSamples'] = {'value': int(len(df_slice)), 'unit': metric_info['CountOfSamples']['unit'], 'description': metric_info['CountOfSamples']['description']}

    # Known columns
    colmap = {
        'RSRP': 'LTE_UE_RSRP',
        'RSRQ': 'LTE_UE_RSRQ',
        'SINR': 'LTE_UE_SINR',
        'PathLoss_DL': 'LTE_UE_PathLoss_DL',
        'RI': 'LTE_UE_RI',
        'PDCP_DL': 'LTE_UE_Throughput_PDCP_DL',
        'L1_DL': 'LTE_UE_Throughput_L1_DL',
        'BLER_DL': 'LTE_UE_BLER_DL',
        'PUSCH_PWR': 'LTE_UE_Power_Tx_PUSCH',
        'PUCCH_PWR': 'LTE_UE_Power_Tx_PUCCH',
        'TOTAL_PWR': 'LTE_UE_Total_Power_Tx_PUSCH',
        'MCS_AVG_DL': 'LTE_UE_MCS_Average_DL',
    }

    for key, col in colmap.items():
        val = _mean_safe(df_slice[col]) if col in df_slice.columns else None
        metrics[key] = {'value': val, 'unit': metric_info.get(key, {}).get('unit', ''), 'description': metric_info.get(key, {}).get('description', '')}

    # Prefer TOTAL power if available
    ue_power_tx_val = metrics['TOTAL_PWR']['value'] or metrics['PUSCH_PWR']['value'] or metrics['PUCCH_PWR']['value']
    metrics['UE_Power_Tx'] = {'value': ue_power_tx_val, 'unit': metric_info['UE_Power_Tx']['unit'], 'description': metric_info['UE_Power_Tx']['description']}

    # Ratio L1/PDCP throughput
    l1_dl_val = metrics['L1_DL']['value']
    pdcp_dl_val = metrics['PDCP_DL']['value']
    if l1_dl_val and pdcp_dl_val and pdcp_dl_val != 0:
        ratio_val = l1_dl_val / pdcp_dl_val
    else:
        ratio_val = None
    metrics['L1toPDCPTp_ratio'] = {'value': ratio_val, 'unit': metric_info['L1toPDCPTp_ratio']['unit'], 'description': metric_info['L1toPDCPTp_ratio']['description']}

    # Modulation percentages if a categorical column exists
    mod_cols = [c for c in df_slice.columns if 'modulation' in c.lower() or 'qam' in c.lower()]
    mod_col = mod_cols[0] if mod_cols else None
    if mod_col is not None:
        mods = df_slice[mod_col].astype(str).str.upper()
        total = len(mods)
        def pct(label):
            cnt = (mods == label).sum()
            return round(cnt * 100.0 / total, 2) if total else None
        metrics['QPSK_pct'] = {'value': pct('QPSK'), 'unit': metric_info['QPSK_pct']['unit'], 'description': metric_info['QPSK_pct']['description']}
        metrics['QAM16_pct'] = {'value': pct('16QAM'), 'unit': metric_info['QAM16_pct']['unit'], 'description': metric_info['QAM16_pct']['description']}
        metrics['QAM64_pct'] = {'value': pct('64QAM'), 'unit': metric_info['QAM64_pct']['unit'], 'description': metric_info['QAM64_pct']['description']}
        metrics['QAM256_pct'] = {'value': pct('256QAM'), 'unit': metric_info['QAM256_pct']['unit'], 'description': metric_info['QAM256_pct']['description']}
    else:
        metrics['QPSK_pct'] = {'value': None, 'unit': metric_info['QPSK_pct']['unit'], 'description': metric_info['QPSK_pct']['description']}
        metrics['QAM16_pct'] = {'value': None, 'unit': metric_info['QAM16_pct']['unit'], 'description': metric_info['QAM16_pct']['description']}
        metrics['QAM64_pct'] = {'value': None, 'unit': metric_info['QAM64_pct']['unit'], 'description': metric_info['QAM64_pct']['description']}
        metrics['QAM256_pct'] = {'value': None, 'unit': metric_info['QAM256_pct']['unit'], 'description': metric_info['QAM256_pct']['description']}

    return metrics


def band_vendor_stats(df, band_col, vendor1_label='PW', vendor2_label='HW'):
    """Compute bandwise metrics for each vendor. Returns {vendor: {band: metrics}}."""
    if band_col is None or band_col not in df.columns:
        raise ValueError("Band column not found in dataframe.")

    result = {vendor1_label: {}, vendor2_label: {}}
    for vendor in [vendor1_label, vendor2_label]:
        dfx = df[df['Source'] == vendor]
        # Ensure band values are clean
        bands = dfx[band_col].dropna().astype(str).unique()
        for band in sorted(bands):
            slice_df = dfx[dfx[band_col].astype(str) == band]
            result[vendor][band] = aggregate_metrics(slice_df)
    return result


def load_data(hw_source=None, pw_source=None, sheet_name_override=None, vendor1_name=None, vendor2_name=None):
    """Loads and concatenates the Excel data.
    hw_source/pw_source can be file paths (str) or file-like objects (e.g., Streamlit UploadedFile).
    If not provided, falls back to default paths.
    """
    sname = sheet_name_override or sheet_name
    try:
        # Resolve sources
        hw_input = hw_source if hw_source is not None else path_hw
        pw_input = pw_source if pw_source is not None else path_pw

        df_hw = pd.read_excel(hw_input, sheet_name=sname)
        df_pw = pd.read_excel(pw_input, sheet_name=sname)

        # Assign vendor labels to source
        src_hw = vendor2_name.strip() if isinstance(vendor2_name, str) and vendor2_name.strip() != '' else 'HW'
        src_pw = vendor1_name.strip() if isinstance(vendor1_name, str) and vendor1_name.strip() != '' else 'PW'

        df_hw['Source'] = src_hw
        df_pw['Source'] = src_pw
        df = pd.concat([df_hw, df_pw], ignore_index=True)
        return df

    except FileNotFoundError:
        print("\nError: Files not found in the specified path.")
        print(f"Please check the following paths or upload files:\n{path_hw}\n{path_pw}")
        sys.exit(1)
    except ValueError:
        print(f"\nError: Sheet named '{sname}' not found in your Excel file. Please check the correct sheet name.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


def get_user_selection(axis_name, choices):
    """Gets axis selection from the user."""
    print(f"\n--- {axis_name} Metric Selection ---")

    for key, value in choices.items():
        print(f"{key}: {value}")

    while True:
        # UPDATED: Range is now (1-14)
        choice = input(
            f"Please enter a number for the {axis_name} metric ({list(choices.keys())[0]}-{list(choices.keys())[-1]}): ")
        if choice in choices:
            return choices[choice]
        else:
            print("Invalid selection. Please try again.")


def create_interactive_plot(df, x_col, y1_col, y2_col):
    """Creates two separate dual-axis plots and saves PNG to Desktop.
    Default styles: Y1=scatter, Y2=bar.
    """

    fig = build_dual_axis_fig(df, x_col, y1_col, y2_col, left_style='scatter', right_style='bar')

    # !!! SAVING THE PLOT TO DESKTOP !!!
    desktop_path = os.path.expanduser('~/Desktop')
    file_name = f'seperated_plot_PW_vs_HW_{x_col}_vs_{y1_col}_and_{y2_col}_barchart_0.5bin.png'.replace(' ',
                                                                                                        '_').replace(
        '/', '_')
    full_path = os.path.join(desktop_path, file_name)

    fig.savefig(full_path)
    print(f"\n✅ Dual-Axis (Scatter/Bar) Plot successfully saved to your Desktop as '{file_name}'.")


def build_dual_axis_fig(df, x_col, y1_col, y2_col, left_style='scatter', right_style='bar', vendor1_label='PW', vendor2_label='HW'):
    """Builds and returns a Matplotlib Figure with two subplots (PW and HW).
    Styles can be 'scatter' or 'bar' independently for Y1 (left axis) and Y2 (right axis).
    """

    # 1. Data Cleaning and Conversion to Numeric
    columns_to_keep = ['Source', x_col, y1_col, y2_col]
    df_plot = df.dropna(subset=columns_to_keep).copy()

    for col in [x_col, y1_col, y2_col]:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
    df_plot.dropna(subset=[x_col, y1_col, y2_col], inplace=True)

    if df_plot.empty:
        print(f"\nError: Not enough data found for the selected columns ({x_col}, {y1_col}, and {y2_col}).")
        return

    # .copy() added to fix SettingWithCopyWarning
    df_hw_plot = df_plot[df_plot['Source'] == vendor2_label].copy()
    df_pw_plot = df_plot[df_plot['Source'] == vendor1_label].copy()

    # --- BINNING FOR BARCHART (0.5 increments), computed as needed ---
    df_hw_plot['x_bin'] = np.floor(df_hw_plot[x_col] * 2) / 2
    df_pw_plot['x_bin'] = np.floor(df_pw_plot[x_col] * 2) / 2

    # Precompute binned means for Y1/Y2 only if needed
    hw_binned_y1 = df_hw_plot.groupby('x_bin')[y1_col].mean() if left_style == 'bar' else None
    pw_binned_y1 = df_pw_plot.groupby('x_bin')[y1_col].mean() if left_style == 'bar' else None

    hw_binned_y2 = df_hw_plot.groupby('x_bin')[y2_col].mean() if right_style == 'bar' else None
    pw_binned_y2 = df_pw_plot.groupby('x_bin')[y2_col].mean() if right_style == 'bar' else None

    # Calculate global min/max for y1 and y2 across both vendors
    global_y1_min = min(df_pw_plot[y1_col].min(), df_hw_plot[y1_col].min())
    global_y1_max = max(df_pw_plot[y1_col].max(), df_hw_plot[y1_col].max())

    if right_style == 'bar':
        global_y2_min = min(pw_binned_y2.min(), hw_binned_y2.min())
        global_y2_max = max(pw_binned_y2.max(), hw_binned_y2.max())
    else:
        global_y2_min = min(df_pw_plot[y2_col].min(), df_hw_plot[y2_col].min())
        global_y2_max = max(df_pw_plot[y2_col].max(), df_hw_plot[y2_col].max())

    # Apply custom limits if they exist for y1_col or y2_col
    if y1_col == PATHLOSS_COL and y1_lim:
        global_y1_min, global_y1_max = y1_lim
    elif y1_col != PATHLOSS_COL and global_y1_min >= 0:
        global_y1_min = 0 # Ensure y-axis starts from 0 for non-pathloss positive values

    if y2_col == PATHLOSS_COL and y2_lim:
        global_y2_min, global_y2_max = y2_lim
    elif y2_col != PATHLOSS_COL and global_y2_min >= 0:
        global_y2_min = 0 # Ensure y-axis starts from 0 for non-pathloss positive values

    # Set default max to 1 if data is empty or 0
    if pd.isna(global_y1_max) or global_y1_max == 0: global_y1_max = 1
    if pd.isna(global_y2_max) or global_y2_max == 0: global_y2_max = 1

    # --- LOGIC FOR APPLYING CUSTOM AXIS LIMITS ---
    x_lim = CUSTOM_LIMITS.get(x_col)
    y1_lim = CUSTOM_LIMITS.get(y1_col)  # For left axis
    y2_lim = CUSTOM_LIMITS.get(y2_col)  # For right axis

    if x_lim or y1_lim or y2_lim:
        print(f"\nApplying Custom Limits: ", end="")
        if x_lim:
            print(f"X-Axis ({x_lim[0]} to {x_lim[1]}) ", end="")
        if y1_lim:
            print(f"Y1-Axis ({y1_lim[0]} to {y1_lim[1]}) ", end="")
        if y2_lim:
            print(f"Y2-Axis ({y2_lim[0]} to {y2_lim[1]}) ", end="")
        print(".")

    # 2. Creating the Plot: Two Separate Subplots
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))  # Flatter aspect ratio

    # --- Subplot 1: PW (LEFT Side - axes[0]) ---
    ax_pw_left = axes[0]
    ax_pw_right = ax_pw_left.twinx()

    # Left Axis (Y1)
    if left_style == 'bar':
        ax_pw_left.bar(pw_binned_y1.index, pw_binned_y1.values,
                       label=f'{y1_col} (Bar Mean)', color='tab:orange', alpha=0.6, width=0.4)
    else:
        ax_pw_left.scatter(df_pw_plot[x_col], df_pw_plot[y1_col],
                           label=f'{y1_col} (Scatter)', color='tab:orange', alpha=0.7, s=10)

    # Right Axis (Y2)
    if right_style == 'bar':
        ax_pw_right.bar(pw_binned_y2.index, pw_binned_y2.values,
                        label=f'{y2_col} (Bar Mean)', color='tab:green', alpha=0.4, width=0.4)
    else:
        ax_pw_right.scatter(df_pw_plot[x_col], df_pw_plot[y2_col],
                            label=f'{y2_col} (Scatter)', color='tab:green', alpha=0.6, s=10)

    if x_lim:
        ax_pw_left.set_xlim(x_lim)

    # Apply global y-limits
    ax_pw_left.set_ylim(global_y1_min, global_y1_max)
    ax_pw_right.set_ylim(global_y2_min, global_y2_max)

    # Titles and Labels (with wrap text)
    ax_pw_left.set_title(f'{vendor1_label} Data: {y1_col} ({"Bar" if left_style=="bar" else "Scatter"}) & {y2_col} ({"Bar" if right_style=="bar" else "Scatter"})\nvs. {x_col}')
    ax_pw_left.set_xlabel(x_col)
    ax_pw_left.set_ylabel(y1_col, color='tab:orange')
    ax_pw_right.set_ylabel(f'{y2_col} ({"Mean" if right_style=="bar" else "Scatter"})', color='tab:green')
    ax_pw_left.grid(True, linestyle='--', alpha=0.7)

    # Add combined legend for PW (zorder fix)
    h1, l1 = ax_pw_left.get_legend_handles_labels()
    h2, l2 = ax_pw_right.get_legend_handles_labels()
    leg_pw = ax_pw_left.legend(handles=h1 + h2, labels=l1 + l2, loc='upper left')
    leg_pw.set_zorder(10)  # Set zorder on the legend object

    # --- Subplot 2: HW (RIGHT Side - axes[1]) ---
    ax_hw_left = axes[1]
    ax_hw_right = ax_hw_left.twinx()

    # Left Axis (Y1)
    if left_style == 'bar':
        ax_hw_left.bar(hw_binned_y1.index, hw_binned_y1.values,
                       label=f'{y1_col} (Bar Mean)', color='tab:blue', alpha=0.6, width=0.4)
    else:
        ax_hw_left.scatter(df_hw_plot[x_col], df_hw_plot[y1_col],
                           label=f'{y1_col} (Scatter)', color='tab:blue', alpha=0.7, s=10)

    # Right Axis (Y2)
    if right_style == 'bar':
        ax_hw_right.bar(hw_binned_y2.index, hw_binned_y2.values,
                        label=f'{y2_col} (Bar Mean)', color='tab:red', alpha=0.4, width=0.4)
    else:
        ax_hw_right.scatter(df_hw_plot[x_col], df_hw_plot[y2_col],
                            label=f'{y2_col} (Scatter)', color='tab:red', alpha=0.6, s=10)

    if x_lim:
        ax_hw_left.set_xlim(x_lim)

    # Apply global y-limits
    ax_hw_left.set_ylim(global_y1_min, global_y1_max)
    ax_hw_right.set_ylim(global_y2_min, global_y2_max)

    # Titles and Labels (with wrap text)
    ax_hw_left.set_title(f'{vendor2_label} Data: {y1_col} ({"Bar" if left_style=="bar" else "Scatter"}) & {y2_col} ({"Bar" if right_style=="bar" else "Scatter"})\nvs. {x_col}')
    ax_hw_left.set_xlabel(x_col)
    ax_hw_left.set_ylabel(y1_col, color='tab:blue')
    ax_hw_right.set_ylabel(f'{y2_col} (Mean)', color='tab:red')
    ax_hw_left.grid(True, linestyle='--', alpha=0.7)

    # Add combined legend for HW (zorder fix)
    h1_hw, l1_hw = ax_hw_left.get_legend_handles_labels()
    h2_hw, l2_hw = ax_hw_right.get_legend_handles_labels()
    leg_hw = ax_hw_left.legend(handles=h1_hw + h2_hw, labels=l1_hw + l2_hw, loc='upper left')
    leg_hw.set_zorder(10)  # Set zorder on the legend object

    # Main Title
    plt.suptitle(f'{y1_col} & {y2_col} vs. {x_col} — {vendor1_label} / {vendor2_label} ({"Bar" if left_style=="bar" else "Scatter"} / {"Bar" if right_style=="bar" else "Scatter"})', fontsize=16)

    # Use tight_layout to account for wrap text
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    return fig


def build_scatter_fig(df, x_col, y1_col, vendor1_label='PW', vendor2_label='HW'):
    """Builds and returns a Matplotlib Figure with two scatter subplots (PW and HW) when y2 is None."""

    # 1. Data Cleaning and Conversion to Numeric
    columns_to_keep = ['Source', x_col, y1_col]
    df_plot = df.dropna(subset=columns_to_keep).copy()

    for col in [x_col, y1_col]:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
    df_plot.dropna(subset=[x_col, y1_col], inplace=True)

    if df_plot.empty:
        print(f"\nError: Not enough data found for the selected columns ({x_col} and {y1_col}).")
        return None

    # .copy() added to fix SettingWithCopyWarning
    df_hw_plot = df_plot[df_plot['Source'] == vendor2_label].copy()
    df_pw_plot = df_plot[df_plot['Source'] == vendor1_label].copy()

    # --- LOGIC FOR APPLYING CUSTOM AXIS LIMITS ---
    x_lim = CUSTOM_LIMITS.get(x_col)
    y1_lim = CUSTOM_LIMITS.get(y1_col)  # For left axis

    if x_lim or y1_lim:
        print(f"\nApplying Custom Limits: ", end="")
        if x_lim:
            print(f"X-Axis ({x_lim[0]} to {x_lim[1]}) ", end="")
        if y1_lim:
            print(f"Y1-Axis ({y1_lim[0]} to {y1_lim[1]}) ", end="")
        print(".")

    # 2. Creating the Plot: Two Separate Subplots (Scatter only)
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))

    # --- Subplot 1: PW (LEFT Side - axes[0]) ---
    ax_pw = axes[0]
    ax_pw.scatter(df_pw_plot[x_col], df_pw_plot[y1_col], label=f'{y1_col} (Scatter)', color='tab:orange', alpha=0.7, s=10)
    if x_lim:
        ax_pw.set_xlim(x_lim)
    # Calculate global min/max for y1 across both vendors
    global_y1_min = min(df_pw_plot[y1_col].min(), df_hw_plot[y1_col].min())
    global_y1_max = max(df_pw_plot[y1_col].max(), df_hw_plot[y1_col].max())

    # Apply custom limits if they exist for y1_col
    if y1_col == PATHLOSS_COL and y1_lim:
        global_y1_min, global_y1_max = y1_lim
    elif y1_col != PATHLOSS_COL and global_y1_min >= 0:
        global_y1_min = 0 # Ensure y-axis starts from 0 for non-pathloss positive values

    # Set default max to 1 if data is empty or 0
    if pd.isna(global_y1_max) or global_y1_max == 0: global_y1_max = 1

    # --- LOGIC FOR APPLYING CUSTOM AXIS LIMITS ---
    x_lim = CUSTOM_LIMITS.get(x_col)
    y1_lim = CUSTOM_LIMITS.get(y1_col)  # For left axis

    if x_lim or y1_lim:
        print(f"\nApplying Custom Limits: ", end="")
        if x_lim:
            print(f"X-Axis ({x_lim[0]} to {x_lim[1]}) ", end="")
        if y1_lim:
            print(f"Y1-Axis ({y1_lim[0]} to {y1_lim[1]}) ", end="")
        print(".")

    # 2. Creating the Plot: Two Separate Subplots (Scatter only)
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))

    # --- Subplot 1: PW (LEFT Side - axes[0]) ---
    ax_pw = axes[0]
    ax_pw.scatter(df_pw_plot[x_col], df_pw_plot[y1_col], label=f'{y1_col} (Scatter)', color='tab:orange', alpha=0.7, s=10)
    if x_lim:
        ax_pw.set_xlim(x_lim)
    ax_pw.set_ylim(global_y1_min, global_y1_max)
    ax_pw.set_title(f'{vendor1_label} Data: {y1_col} (Scatter) vs. {x_col}')
    ax_pw.set_xlabel(x_col)
    ax_pw.set_ylabel(y1_col, color='tab:orange')
    ax_pw.grid(True, linestyle='--', alpha=0.7)
    ax_pw.legend(loc='upper left')

    # --- Subplot 2: HW (RIGHT Side - axes[1]) ---
    ax_hw = axes[1]
    ax_hw.scatter(df_hw_plot[x_col], df_hw_plot[y1_col], label=f'{y1_col} (Scatter)', color='tab:blue', alpha=0.7, s=10)
    if x_lim:
        ax_hw.set_xlim(x_lim)
    ax_hw.set_ylim(global_y1_min, global_y1_max)
    ax_hw.set_title(f'{vendor2_label} Data: {y1_col} (Scatter) vs. {x_col}')
    ax_hw.set_xlabel(x_col)
    ax_hw.set_ylabel(y1_col, color='tab:blue')
    ax_hw.grid(True, linestyle='--', alpha=0.7)
    ax_hw.legend(loc='upper left')

    # Main Title
    plt.suptitle(f'{y1_col} vs. {x_col} (Scatter Only) — {vendor1_label} / {vendor2_label}', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    return fig


def build_single_fig(df, x_col, y1_col, y1_style='scatter', vendor1_label='PW', vendor2_label='HW'):
    """Builds and returns a Matplotlib Figure with two subplots (PW and HW) for a single Y metric.
    y1_style can be 'scatter' or 'bar'. When 'bar', values are binned on X in 0.5 increments and the mean is plotted.
    """

    # 1. Data Cleaning and Conversion to Numeric
    columns_to_keep = ['Source', x_col, y1_col]
    df_plot = df.dropna(subset=columns_to_keep).copy()

    for col in [x_col, y1_col]:
        df_plot[col] = pd.to_numeric(df_plot[col], errors='coerce')
    df_plot.dropna(subset=[x_col, y1_col], inplace=True)

    if df_plot.empty:
        print(f"\nError: Not enough data found for the selected columns ({x_col} and {y1_col}).")
        return None

    # Separate vendors
    df_hw_plot = df_plot[df_plot['Source'] == vendor2_label].copy()
    df_pw_plot = df_plot[df_plot['Source'] == vendor1_label].copy()

    # Optional binning for bar style
    pw_binned_y1 = None
    hw_binned_y1 = None
    if y1_style == 'bar':
        df_hw_plot['x_bin'] = np.floor(df_hw_plot[x_col] * 2) / 2
        df_pw_plot['x_bin'] = np.floor(df_pw_plot[x_col] * 2) / 2
        hw_binned_y1 = df_hw_plot.groupby('x_bin')[y1_col].mean()
        pw_binned_y1 = df_pw_plot.groupby('x_bin')[y1_col].mean()

    # Axis limits
    x_lim = CUSTOM_LIMITS.get(x_col)
    y1_lim = CUSTOM_LIMITS.get(y1_col)

    # Calculate global min/max for y1 across both vendors
    global_y1_min = min(df_pw_plot[y1_col].min(), df_hw_plot[y1_col].min())
    global_y1_max = max(df_pw_plot[y1_col].max(), df_hw_plot[y1_col].max())

    # Apply custom limits if they exist for y1_col
    if y1_col == PATHLOSS_COL and y1_lim:
        global_y1_min, global_y1_max = y1_lim
    elif y1_col != PATHLOSS_COL and global_y1_min >= 0:
        global_y1_min = 0

    # Default max to 1 if empty or 0
    if pd.isna(global_y1_max) or global_y1_max == 0:
        global_y1_max = 1

    # 2. Create plot with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))

    # --- PW subplot ---
    ax_pw = axes[0]
    if y1_style == 'bar':
        ax_pw.bar(pw_binned_y1.index, pw_binned_y1.values,
                  label=f'{y1_col} (Bar Mean)', color='tab:orange', alpha=0.6, width=0.4)
    else:
        ax_pw.scatter(df_pw_plot[x_col], df_pw_plot[y1_col],
                      label=f'{y1_col} (Scatter)', color='tab:orange', alpha=0.7, s=10)
    if x_lim:
        ax_pw.set_xlim(x_lim)
    ax_pw.set_ylim(global_y1_min, global_y1_max)
    ax_pw.set_title(f'{vendor1_label} Data: {y1_col} ({"Bar" if y1_style=="bar" else "Scatter"}) vs. {x_col}')
    ax_pw.set_xlabel(x_col)
    ax_pw.set_ylabel(y1_col, color='tab:orange')
    ax_pw.grid(True, linestyle='--', alpha=0.7)
    ax_pw.legend(loc='upper left')

    # --- HW subplot ---
    ax_hw = axes[1]
    if y1_style == 'bar':
        ax_hw.bar(hw_binned_y1.index, hw_binned_y1.values,
                  label=f'{y1_col} (Bar Mean)', color='tab:blue', alpha=0.6, width=0.4)
    else:
        ax_hw.scatter(df_hw_plot[x_col], df_hw_plot[y1_col],
                      label=f'{y1_col} (Scatter)', color='tab:blue', alpha=0.7, s=10)
    if x_lim:
        ax_hw.set_xlim(x_lim)
    ax_hw.set_ylim(global_y1_min, global_y1_max)
    ax_hw.set_title(f'{vendor2_label} Data: {y1_col} ({"Bar" if y1_style=="bar" else "Scatter"}) vs. {x_col}')
    ax_hw.set_xlabel(x_col)
    ax_hw.set_ylabel(y1_col, color='tab:blue')
    ax_hw.grid(True, linestyle='--', alpha=0.7)
    ax_hw.legend(loc='upper left')

    # Main title
    plt.suptitle(f'{y1_col} vs. {x_col} — {vendor1_label} / {vendor2_label} ({"Bar" if y1_style=="bar" else "Scatter"})', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    return fig


if __name__ == "__main__":
    print("--- Interactive Dual-Axis Plot Generator Started ---")

    df = load_data()

    # No menu, straight to the graphics selection
    print("\n--- Dual-Axis Plot Metric Selection ---")
    x_axis_name = get_user_selection('X-Axis (Common)', PLOTTING_COLUMNS)
    y1_axis_name = get_user_selection('Y1-Axis (Left, Scatter)', PLOTTING_COLUMNS)
    y2_axis_name = get_user_selection('Y2-Axis (Right, Bar-Mean)', PLOTTING_COLUMNS)

    create_interactive_plot(df, x_axis_name, y1_axis_name, y2_axis_name)