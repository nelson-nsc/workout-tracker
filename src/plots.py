import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


class Plot:
    def __init__(self, df: pd.DataFrame):
        """
        This class contains a range of performance metrics visualised using plotly.
        """
        self.df = df
        self.exercise = self.df["Exercise"].values[0]
        self.variation = self.df["Variation"].values[0]

    def personal_record(self) -> None:
        """
        Plot the Personal Record (PR) of a given exercise and variation across time.
        """
        pr = -np.inf
        date_arr = []
        weight_arr = []
        counts_arr = []

        for date in self.df["Date"]:
            temp = self.df.loc[self.df["Date"] == date]
            max_weight = temp["Weight"].max()

            max_weight_str = temp["Weight"].max()
            counts = temp.loc[temp["Weight"] == max_weight_str]["Count"].max()
            if max_weight > pr:
                pr = max_weight
                date_arr.append(date)
                weight_arr.append(max_weight)
                counts_arr.append(counts)

        variation = "" if self.variation == "/" else self.variation

        fig = go.Figure(
            [
                go.Scatter(
                    x=date_arr,
                    y=weight_arr,
                    marker=dict(
                        size=counts_arr,
                        sizemode="area",
                        sizeref=2.0 * max(counts_arr) / (40.0**2),
                        sizemin=4,
                    ),
                )
            ]
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="kg",
            title=f"{self.exercise} {variation} PR",
        )
        # <extra></extra> removes the "trace 0" text
        hovertemplate = (
            "Date: %{x}<br>"
            + "Weight: %{y} kg<br>"
            + "Count: %{customdata[0]}"
            + "<extra></extra>"
        )
        fig.update_traces(
            customdata=pd.DataFrame(counts_arr), hovertemplate=hovertemplate
        )
        fig.update_layout(hovermode="x unified")

        return fig

    def volume_breakdown(self, period: str) -> None:
        self.df["Volume"] = self.df["Weight"] * self.df["Count"]

        self.df["Weight_hover"] = self.df["Weight"].apply(str) + " kg"
        bands_values = ["1.0 kg", "0.1 kg", "0.2 kg", "0.6 kg", "0.8 kg"]
        bands_str = ["Body Weight", "Purple", "Black", "Green", "Orange"]
        for i, j in zip(bands_values, bands_str):
            self.df["Weight_hover"] = np.where(
                self.df["Weight_hover"] == i, j, self.df["Weight_hover"]
            )

        fig = px.bar(
            self.df,
            x="Date",
            y="Volume",
            custom_data=["Weight_hover", "Count"],
            color="Set",
        )

        hovertemplate = (
            "Date: %{x}<br>"
            + "Volume: %{y} <br>"
            + "Weight: %{customdata[0]}<br>"
            + "Count: %{customdata[1]}"
            + "<extra></extra>"
        )

        fig.update_traces(hovertemplate=hovertemplate)
        start_date, end_date = self._get_period(period)
        fig.update_layout(xaxis_range=[start_date, end_date], dragmode='pan')
        return fig

    def _get_period(self, period: str) -> [str, str]:
        dic_date_range = {
            "Last 1 month": 30,
            "Last 3 months": 90,
            "Last 6 months": 180,
            "Last 12 months": 365,
        }

        end_date = self.df["Date"].max()
        start_date = end_date - pd.to_timedelta(dic_date_range[period], unit="d")
        print(dic_date_range[period])
        print(start_date)
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
