"""Chart generation module for various chart types."""

import plotly.express as px
import plotly.graph_objects as go


def create_chart(df, x_column, y_column, chart_type):
    """Create and return a Plotly chart based on the specified type."""
    if df[x_column].dtype == "object" and df[y_column].dtype in ["int64", "float64"]:
        if chart_type == "Bar":
            fig = px.bar(df, x=x_column, y=y_column, color=x_column, title=y_column)
        elif chart_type == "Line":
            fig = px.line(df, x=x_column, y=y_column, markers=True, title=y_column)
        elif chart_type == "Pie":
            fig = px.pie(df, names=x_column, values=y_column, title=y_column)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_column, y=y_column, size=y_column, color=x_column)
        elif chart_type == "Area":
            fig = px.area(df, x=x_column, y=y_column)
        elif chart_type == "Radar":
            fig = go.Figure(data=go.Scatterpolar(r=df[y_column], theta=df[x_column], fill='toself'))
        elif chart_type == "Doughnut":
            fig = go.Figure(data=[go.Pie(labels=df[x_column], values=df[y_column], hole=0.4)])
            fig.update_layout(title=y_column)
        else:
            fig = px.bar(df, x=x_column, y=y_column)

        fig.update_layout(height=600, template="simple_white")
        return fig
    else:
        return None