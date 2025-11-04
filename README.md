# KPI_UI2

**LTE - 5G Drive Test KPI Visualization Tool**

This project is a Streamlit-based web application for visualizing and comparing Key Performance Indicators (KPIs) from drive test data of different vendors.

## Features

- Upload and compare KPI Excel files from two vendors
- Interactive charts and tables for KPI analysis
- Customizable sheet and vendor names
- Supports .xlsx files up to 200MB

## Getting Started

### Prerequisites

- Python 3.8+
- The required Python packages (see `requirements.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akolukisa/KPI_UI2.git
   cd KPI_UI2
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

### Usage

1. Open the app in your browser (usually at `http://localhost:8501`).
2. Enter the names for Vendor 1 and Vendor 2.
3. Upload the Excel files for each vendor.
4. Specify the sheet name containing the formatted data (default: `Series Formatted Data`).
5. View and analyze the KPI charts and tables.

## Data Format

The application expects Excel files (.xlsx) with the following structure:

- **Sheet Name:** Should match the name entered in the app (default: `Series Formatted Data`)
- **Required Columns:**

You can download the sample Excel template here:
[Download KPI_UI2_template.xlsx](KPI_UI2_template.xlsx)

The template contains the following columns:

```
Message, Time, Distance, Longitude, Latitude, UE_Capabilities, UE_Bands_GSM, UE_Bands_UMTS, UE_Bands_LTE, Source_Node_Type, Target_Node_Type, Source_Node_Id, Target_Node_Id, ServingCellRadioID, Technology_Mode, Radio_Access_Mode, FileName, LTE_UE_EARFCN_DL, LTE_UE_EARFCN_UL, LTE_UE_Bandwidth_DL, LTE_UE_Bandwidth_UL, LTE_UE_RB_Num_Max_DL, LTE_UE_Carrier_Num_DL, LTE_UE_Ant_Num, LTE_UE_Ant_Num_eNB, LTE_UE_BAND_DL, LTE_UE_Transmission_Scheme_DL, LTE_UE_PCI, LTE_UE_RSSI, LTE_UE_RSRP, LTE_UE_RSRQ, LTE_UE_Srxlev, LTE_UE_Starting_DL_Timing, LTE_UE_PathLoss_DL, LTE_UE_CA_Configured, LTE_UE_CA_Active, LTE_UE_SINR, LTE_UE_PMI, LTE_UE_TM_DL, LTE_UE_RI, LTE_UE_CFI, LTE_UE_SpatialRank, LTE_UE_WideBand_CQI_Average, LTE_UE_RB_Num_DL, LTE_UE_TB_Size_Average_DL, LTE_UE_TB_Size_Max_DL, LTE_UE_FrameUsage_DL, LTE_UE_MCS_Average_DL, LTE_UE_ACK_Rate_DL, LTE_UE_NACK_Rate_DL, LTE_UE_BLER_DL, LTE_UE_DiscardRate_DL, LTE_UE_Throughput_L1_DL, LTE_UE_Throughput_RLC_DL, LTE_UE_Throughput_PDCP_DL, LTE_UE_PayloadRate_L1_DL, LTE_UE_PDCP_NumBytes_DL, LTE_UE_NumBytes_DL, LTE_UE_RACH_PreamblePwrOffset, LTE_UE_RACH_Backoff, LTE_UE_Modulation_Avg_DL, LTE_UE_BLER_DL_1st_transmission, LTE_UE_BLER_DL_last_transmission, LTE_UE_SumInstances_DL, LTE_UE_SIB1_Decode_Fail_Rate, LTE_UE_SIB1_Decode_FailedAttemptCount, LTE_UE_RLC_AM_BLER_DL, LTE_UE_ModulationUsage_QPSK_DL, LTE_UE_ModulationUsage_16QAM_DL, LTE_UE_ModulationUsage_64QAM_DL, LTE_UE_ModulationUsage_256QAM_DL, LTE_UE_Timing_Advance, LTE_UE_Starting_UL_Timing, LTE_UE_UL_Timing_Adjusted, LTE_UE_TM_UL, LTE_UE_Carrier_Num_UL, LTE_UE_CA_Configured_UL, LTE_UE_NumBytes_UL, LTE_UE_FrameUsage_UL, LTE_UE_Power_Tx_PUCCH, LTE_UE_Power_Tx_PUSCH, LTE_UE_Total_Power_Tx_PUSCH, LTE_UE_Power_Tx_PRACH, LTE_UE_RB_Num_UL, LTE_UE_TB_Size_Average_UL, LTE_UE_TB_Size_Max_UL, LTE_UE_MCS_Average_UL, LTE_UE_Modulation_Avg_UL, LTE_UE_Throughput_L1_UL, LTE_UE_MAC_Throughput_UL, LTE_UE_Throughput_RLC_UL, LTE_UE_Throughput_PDCP_UL, LTE_UE_PayloadRate_L1_UL, LTE_UE_PDCP_NumBytes_UL, LTE_UE_PDCP_PDU_Discarded_UL, LTE_UE_RLC_AM_BLER_UL, LTE_UE_PDCP_AM_BLER_UL, LTE_UE_RLCPacket_Count_AM_UL, LTE_UE_PDCPPacket_Count_AM_UL, LTE_UE_ModulationUsage_BPSK_UL, LTE_UE_ModulationUsage_QPSK_UL, LTE_UE_ModulationUsage_16QAM_UL, LTE_UE_ModulationUsage_64QAM_UL, LTE_UE_SFN, LTE_RRCConnection_ID, LTE_Event_TTIbundling_active_start, LTE_Event_TTIbundling_active_stop, LTE_UE_TTIbundling_active_stop_cause, LTE_UE_TTIbundling_active, LTE_UE_CA_Active_Duration, LTE_UE_CA_Configured_Duration, App_Throughput_DL, Physical_Throughput_DL, App_Throughput_UL, Physical_Throughput_UL, Physical_DataVolume_MeasureInterval, Physical_Throughput_DL_LTE_NonCA, Physical_Throughput_DL_LTE_CA, Physical_Throughput_DL_LTE, Physical_DataVolume_DL_LTE_LAA, Physical_DataVolume_DL_LTE_NonCA, Physical_DataVolume_DL_LTE_CA, Physical_DataVolume_DL_LTE, Physical_DataVolume_DL
```

- Each row represents a measurement for a specific event or time.
- KPI columns should contain numeric values where applicable.

## License

This project is licensed under the [LICENSE](LICENSE) file.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
