import numpy as np
import pandas as pd


class GPSOutageSimulator:
    """
    Simule une perte temporaire du signal GPS.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def simulate_outage(self, start_time: float, duration: float) -> pd.DataFrame:
        end_time = start_time + duration

        if "time_s" not in self.data.columns:
            raise ValueError("La colonne 'time_s' est absente.")

        gps_columns = ["x_gps", "y_gps", "z_gps", "vx_gps", "vy_gps"]

        existing_gps_columns = [
            col for col in gps_columns
            if col in self.data.columns
        ]

        if not existing_gps_columns:
            raise ValueError("Aucune colonne GPS trouvée.")

        mask = (
            (self.data["time_s"] >= start_time)
            &
            (self.data["time_s"] <= end_time)
        )

        self.data.loc[mask, existing_gps_columns] = np.nan

        print(f"[OK] Panne GPS simulée entre {start_time} s et {end_time} s")

        return self.data