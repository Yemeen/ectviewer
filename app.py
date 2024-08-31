"""
ECT Visualizer
--------------
This Streamlit app visualizes the Euler Characteristic Transform (ECT) for various 2D shapes.

Author: Your Name
License: MIT
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from ect import ECT, EmbeddedGraph
import io
from sklearn.datasets import make_moons

@st.cache_data
def generate_sample_data(shape, n_points=100):
    if shape == "Circle":
        t = np.linspace(0, 2*np.pi, n_points)
        x = np.cos(t)
        y = np.sin(t)
    elif shape == "Square":
        t = np.linspace(0, 4, n_points)
        x = np.where(t < 1, t, np.where(t < 2, 1, np.where(t < 3, 3-t, 0)))
        y = np.where(t < 1, 0, np.where(t < 2, t-1, np.where(t < 3, 1, 4-t)))
    elif shape == "Triangle":
        t = np.linspace(0, 3, n_points)
        x = np.where(t < 1, t, np.where(t < 2, 2-t, 0))
        y = np.where(t < 1, 0, np.where(t < 2, t-1, 3-t))
    elif shape == "Two Moons":
        x, _ = make_moons(n_samples=n_points, noise=0.1)
        return x
    elif shape == "Random":
        x = np.random.rand(n_points)
        y = np.random.rand(n_points)
    else:
        raise ValueError(f"Unknown shape: {shape}")
    return np.column_stack((x, y))

@st.cache_data
def process_ect(data, num_dirs, num_thresh):
    G = EmbeddedGraph()
    G.add_cycle(data)
    G.set_PCA_coordinates(center_type='min_max', scale_radius=1)
    
    myect = ECT(num_dirs=num_dirs, num_thresh=num_thresh)
    myect.set_bounding_radius(1)
    M = myect.calculateECT(G)
    
    return myect, M

st.title("ECT Visualizer")

if 'data' not in st.session_state:
    st.session_state.data = None

left_column, right_column = st.columns([1, 2])


with left_column:
    
    data_option = st.radio("Choose data source:", ["Example dataset", "Upload your own"])

    if data_option == "Example dataset":
        example_shapes = [ "Square","Circle", "Triangle", "Two Moons", "Random"]
        selected_shape = st.selectbox("Select an example shape:", example_shapes)
        n_points = st.slider("Number of points", min_value=50, max_value=500, value=100, step=50)
        st.session_state.data = generate_sample_data(selected_shape, n_points)
    else:
        uploaded_file = st.file_uploader("Upload your dataset (txt file with coordinates)", type="txt")
        if uploaded_file is not None:
            st.session_state.data = np.loadtxt(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        else:
            st.warning("Please upload a file.")

    
    num_dirs = st.slider("Number of directions", min_value=10, max_value=100, value=50)
    num_thresh = st.slider("Number of thresholds", min_value=10, max_value=100, value=50)

    
    if st.session_state.data is not None:
        if st.button("Apply ECT"):
            st.session_state.apply_ect = True


with right_column:
    if st.session_state.data is not None and 'apply_ect' in st.session_state and st.session_state.apply_ect:
        myect, M = process_ect(st.session_state.data, num_dirs, num_thresh)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        G = EmbeddedGraph()
        G.add_cycle(st.session_state.data)
        G.set_PCA_coordinates(center_type='min_max', scale_radius=1)
        G.plot(ax=ax1, with_labels=False, node_size=10)
        ax1.set_title("Original Shape")
        
        myect.plotECT()
        ax2.set_title("Euler Characteristic Transform")
        
        st.pyplot(fig)

        fig, ax = plt.subplots(figsize=(8, 6))
        myect.plotSECT()
        ax.set_title("Smooth Euler Characteristic Transform")
        st.pyplot(fig)
