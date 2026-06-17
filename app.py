import pandas as pd
import streamlit as st

from gps_imu_nav.pipeline import FusionPipeline
from gps_imu_nav.navigation import run_navigation
from gps_imu_nav.scenario2 import simulate_gps_outage
from gps_imu_nav.metrics import compute_position_errors, summarize_error_statistics


st.set_page_config(
    page_title="Projet GPS / IMU",
    page_icon="🛰️",
    layout="wide",
)


@st.cache_data
def load_pipeline_and_navigation(alpha: float = 0.7) -> pd.DataFrame:
    pipeline = FusionPipeline()
    pipeline.run()
    navigation_results = run_navigation(alpha=alpha, save_output=True)
    return navigation_results


def select_time_window(
    df: pd.DataFrame,
    mode: str,
    start_s: float = 0.0,
    duration_s: float | None = None,
) -> pd.DataFrame:
    if "time_s" not in df.columns:
        raise ValueError("La colonne 'time_s' est requise pour sélectionner une fenêtre.")

    out = df.sort_values("time_s").reset_index(drop=True).copy()

    if mode == "Trajet complet":
        return out

    if duration_s is None:
        raise ValueError("Une durée doit être fournie pour une fenêtre personnalisée.")

    end_s = start_s + duration_s
    out = out[(out["time_s"] >= start_s) & (out["time_s"] <= end_s)].copy()
    out = out.reset_index(drop=True)

    if out.empty:
        raise ValueError("La fenêtre choisie est vide. Ajustez le début ou la durée.")

    t0 = float(out["time_s"].iloc[0])
    out["time_s"] = out["time_s"] - t0
    return out


def build_scenario2(window_df: pd.DataFrame, outage_start_s: float) -> pd.DataFrame:
    scenario2_df = simulate_gps_outage(window_df, outage_start_s=outage_start_s)
    scenario2_df = compute_position_errors(
        scenario2_df,
        x_est_col="x_s2",
        y_est_col="y_s2",
        x_ref_col="x_gps",
        y_ref_col="y_gps",
        prefix="s2_err",
    )
    return scenario2_df


def build_xy_trajectory_df(
    df: pd.DataFrame,
    series: list[tuple[str, str, str]],
) -> pd.DataFrame:
    records = []
    for x_col, y_col, label in series:
        if x_col in df.columns and y_col in df.columns:
            tmp = df[[x_col, y_col]].copy()
            tmp.columns = ["x", "y"]
            tmp["Trajectoire"] = label
            records.append(tmp)

    if not records:
        return pd.DataFrame(columns=["x", "y", "Trajectoire"])

    return pd.concat(records, ignore_index=True)



def plot_trajectory_2d(df: pd.DataFrame, title: str, series: list[tuple[str, str, str]]):
    st.subheader(title)
    xy_df = build_xy_trajectory_df(df, series)

    if xy_df.empty:
        st.info("Aucune trajectoire 2D disponible pour cet affichage.")
        return

    st.scatter_chart(
        xy_df,
        x="x",
        y="y",
        color="Trajectoire",
        use_container_width=True,
    )



def render_summary_metrics(window_df: pd.DataFrame, alpha: float, outage_start_s: float):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Échantillons", len(window_df))
    c2.metric("Début fenêtre", f"{window_df['time_s'].min():.1f} s")
    c3.metric("Fin fenêtre", f"{window_df['time_s'].max():.1f} s")
    c4.metric("Panne GPS", f"{outage_start_s:.1f} s")
    st.caption(f"Coefficient alpha courant : {alpha:.2f}")


def plot_trajectory_chart(df: pd.DataFrame, title: str, cols: list[tuple[str, str]]):
    chart_df = pd.DataFrame({"time_s": df["time_s"]})
    labels = []
    for x_col, label in cols:
        if x_col in df.columns:
            chart_df[label] = df[x_col]
            labels.append(label)

    st.subheader(title)

    if not labels:
        st.info("Aucune donnée disponible pour ce graphique.")
        return

    st.line_chart(chart_df.set_index("time_s")[labels], use_container_width=True)


def main():
    st.title("Fusion GPS / IMU en Python")
    st.markdown(
        """
        Cette application permet de :
        - charger et prétraiter les données GPS / IMU,
        - analyser la navigation sur tout le trajet ou sur une fenêtre temporelle,
        - comparer GPS, IMU et fusion,
        - simuler une panne GPS.
        """
    )

    st.sidebar.header("Paramètres")

    alpha = st.sidebar.slider(
        "Coefficient de fusion alpha",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
    )

    analysis_mode = st.sidebar.radio(
        "Durée d'analyse",
        ["Trajet complet", "Fenêtre personnalisée"],
    )

    start_s = 0.0
    duration_s = None

    if analysis_mode == "Fenêtre personnalisée":
        start_s = st.sidebar.number_input(
            "Début de la fenêtre (s)",
            min_value=0.0,
            value=0.0,
            step=10.0,
        )
        duration_s = st.sidebar.number_input(
            "Durée de la fenêtre (s)",
            min_value=1.0,
            value=300.0,
            step=10.0,
        )

    outage_start_s = st.sidebar.number_input(
        "Instant de panne GPS (s)",
        min_value=0.0,
        value=30.0,
        step=5.0,
    )

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Accueil",
            "Chargement et prétraitement",
            "Scénario 1 — Fusion GPS/IMU",
            "Scénario 2 — Panne GPS",
            "Comparaison des résultats",
            "Export",
        ],
    )

    try:
        navigation_results = load_pipeline_and_navigation(alpha=alpha)
        window_df = select_time_window(
            navigation_results,
            mode=analysis_mode,
            start_s=start_s,
            duration_s=duration_s,
        )
    except Exception as exc:
        st.error(f"Erreur lors du chargement des données : {exc}")
        return

    if menu == "Accueil":
        st.subheader("Présentation")
        st.write("Le projet compare trois modes de navigation :")
        st.write("- GPS seul")
        st.write("- IMU seule")
        st.write("- Fusion GPS / IMU")
        st.write("Il inclut aussi une simulation de panne GPS.")
        st.success("Astuce : une fenêtre de 300 s donne souvent une démonstration plus lisible.")

        st.subheader("Résumé de la fenêtre courante")
        render_summary_metrics(window_df, alpha=alpha, outage_start_s=outage_start_s)

    elif menu == "Chargement et prétraitement":
        st.subheader("Aperçu des données")
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.dataframe(window_df.head(20), use_container_width=True)
        with col2:
            st.write(f"Shape : {window_df.shape}")
            st.write("Colonnes disponibles :")
            st.write(list(window_df.columns))

    elif menu == "Scénario 1 — Fusion GPS/IMU":
        tab1, tab2, tab3 = st.tabs([
            "Trajectoire 2D",
            "Séries temporelles",
            "Tableau",
        ])

        with tab1:
            plot_trajectory_2d(
                window_df,
                "Trajectoire 2D — GPS / IMU / Fusion",
                [
                    ("x_gps", "y_gps", "GPS"),
                    ("x_imu", "y_imu", "IMU"),
                    ("x_fused", "y_fused", "Fusion"),
                ],
            )

        with tab2:
            plot_trajectory_chart(
                window_df,
                "Évolution de x en fonction du temps",
                [("x_gps", "x_gps"), ("x_imu", "x_imu"), ("x_fused", "x_fused")],
            )

            plot_trajectory_chart(
                window_df,
                "Évolution de y en fonction du temps",
                [("y_gps", "y_gps"), ("y_imu", "y_imu"), ("y_fused", "y_fused")],
            )

            if {"vx_imu", "vy_imu"}.issubset(window_df.columns):
                plot_trajectory_chart(
                    window_df,
                    "Vitesses estimées",
                    [("vx_imu", "vx_imu"), ("vy_imu", "vy_imu"), ("vx_fused", "vx_fused"), ("vy_fused", "vy_fused")],
                )

        with tab3:
            st.dataframe(
                window_df[
                    [c for c in ["time_s", "x_gps", "y_gps", "x_imu", "y_imu", "x_fused", "y_fused"] if c in window_df.columns]
                ].head(30),
                use_container_width=True,
            )

    elif menu == "Scénario 2 — Panne GPS":
        try:
            scenario2_df = build_scenario2(window_df, outage_start_s=outage_start_s)
        except Exception as exc:
            st.error(f"Erreur scénario 2 : {exc}")
            return

        tab1, tab2, tab3, tab4 = st.tabs([
            "Trajectoire 2D",
            "Trajectoires x/y",
            "Erreur 2D",
            "Tableau",
        ])

        with tab1:
            plot_trajectory_2d(
                scenario2_df,
                "Trajectoire 2D — GPS de référence vs scénario 2",
                [
                    ("x_gps", "y_gps", "GPS"),
                    ("x_s2", "y_s2", "Scénario 2"),
                ],
            )

        with tab2:
            plot_trajectory_chart(
                scenario2_df,
                "Trajectoire scénario 2 — axe x",
                [("x_gps", "x_gps"), ("x_s2", "x_s2")],
            )

            plot_trajectory_chart(
                scenario2_df,
                "Trajectoire scénario 2 — axe y",
                [("y_gps", "y_gps"), ("y_s2", "y_s2")],
            )

        with tab3:
            if "s2_err_2d" in scenario2_df.columns:
                plot_trajectory_chart(
                    scenario2_df,
                    "Erreur 2D scénario 2",
                    [("s2_err_2d", "s2_err_2d")],
                )
            else:
                st.info("La colonne s2_err_2d n'est pas disponible pour cette configuration.")

        with tab4:
            st.dataframe(
                scenario2_df[
                    [c for c in ["time_s", "gps_available", "x_gps", "y_gps", "x_s2", "y_s2", "s2_err_2d"] if c in scenario2_df.columns]
                ].head(30),
                use_container_width=True,
            )

    elif menu == "Comparaison des résultats":
        try:
            scenario2_df = build_scenario2(window_df, outage_start_s=outage_start_s)
        except Exception as exc:
            st.error(f"Erreur calcul scénario 2 : {exc}")
            return

        col1, col2 = st.columns(2)

        with col1:
            summary = pd.DataFrame({
                "Mode": ["GPS", "IMU", "Fusion"],
                "x_final": [
                    window_df["x_gps"].iloc[-1] if "x_gps" in window_df.columns else None,
                    window_df["x_imu"].iloc[-1] if "x_imu" in window_df.columns else None,
                    window_df["x_fused"].iloc[-1] if "x_fused" in window_df.columns else None,
                ],
                "y_final": [
                    window_df["y_gps"].iloc[-1] if "y_gps" in window_df.columns else None,
                    window_df["y_imu"].iloc[-1] if "y_imu" in window_df.columns else None,
                    window_df["y_fused"].iloc[-1] if "y_fused" in window_df.columns else None,
                ],
            })
            st.subheader("Résumé final")
            st.dataframe(summary, use_container_width=True)

        with col2:
            s2_phase_gps = scenario2_df[scenario2_df["gps_available"]]
            if not s2_phase_gps.empty and "s2_err_2d" in s2_phase_gps.columns:
                stats_s2 = summarize_error_statistics(
                    s2_phase_gps,
                    err_2d_col="s2_err_2d",
                )
                st.subheader("Statistiques scénario 2")
                st.dataframe(stats_s2, use_container_width=True)
            else:
                st.info("Aucune statistique scénario 2 disponible pour cette configuration.")

    elif menu == "Export":
        st.subheader("Export des données")

        csv_data = window_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger la fenêtre courante en CSV",
            data=csv_data,
            file_name="window_navigation_results.csv",
            mime="text/csv",
        )

        full_csv = navigation_results.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger le trajet complet en CSV",
            data=full_csv,
            file_name="full_navigation_results.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()