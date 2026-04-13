import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

def plot_length_distribution(df: pd.DataFrame) -> go.Figure:
    """Vẽ Histogram phân phối độ dài trình tự."""
    fig = px.histogram(
        df, 
        x="Length", 
        nbins=20, 
        title="Phân phối độ dài trình tự",
        labels={"Length": "Độ dài (bp)"},
        color_discrete_sequence=["#2E8B57"]
    )
    fig.update_layout(bargap=0.1)
    return fig

def plot_organism_pie(df: pd.DataFrame) -> go.Figure:
    """Vẽ Pie chart top 10 loài xuất hiện nhiều nhất."""
    top_organisms = df['Organism'].value_counts().nlargest(10).reset_index()
    top_organisms.columns = ['Organism', 'Count']
    fig = px.pie(
        top_organisms, 
        values='Count', 
        names='Organism', 
        title="Top 10 Loài Phổ Biến",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Greens_r
    )
    return fig

def plot_submission_timeline(df: pd.DataFrame) -> go.Figure:
    """Vẽ Line chart số lượng submission theo năm."""
    # Xử lý parse cột ngày tháng cẩn thận
    df['Year'] = pd.to_datetime(df['Submission Date'], errors='coerce').dt.year
    timeline = df['Year'].dropna().value_counts().sort_index().reset_index()
    timeline.columns = ['Year', 'Count']
    
    fig = px.line(
        timeline, 
        x='Year', 
        y='Count', 
        markers=True, 
        title="Xu hướng Submission theo năm",
        labels={"Year": "Năm", "Count": "Số lượng sequences"}
    )
    fig.update_traces(line_color="#2E8B57", marker_color="green")
    return fig

def plot_nucleotide_composition(stats_dict: Dict[str, float]) -> go.Figure:
    """Vẽ Bar chart thành phần nucleotide A/T/G/C."""
    bases = ['A', 'T', 'G', 'C']
    percs = [stats_dict.get(f'%{b}', 0) for b in bases]
    
    fig = px.bar(
        x=bases, 
        y=percs, 
        color=bases,
        title="Thành phần Nucleotide",
        labels={"x": "Nucleotide", "y": "Tỷ lệ (%)"},
        color_discrete_map={'A': '#1f77b4', 'T': '#ff7f0e', 'G': '#2ca02c', 'C': '#d62728'}
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_gc_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Vẽ Heatmap minh họa (Do giới hạn metadata của efetch gb đôi khi không có GC sẵn, 
    ta sẽ đếm tần suất kết hợp giữa Organism x Gene Type).
    """
    heatmap_data = df.groupby(['Organism', 'Gene Type']).size().unstack(fill_value=0)
    fig = px.imshow(
        heatmap_data, 
        labels=dict(x="Loại Gen", y="Loài", color="Số lượng"),
        title="Tương quan Số lượng: Loài và Loại Gen",
        color_continuous_scale="Greens"
    )
    return fig