"""Module: predictor.py."""
# ml/predictor.py
import numpy as np

import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

def sudden_spike(view_history, threshold=1.5):
    if len(view_history) < 3:
        return False

    moving_avg = np.mean(view_history[:-1])
    latest = view_history[-1]

    if latest > threshold * moving_avg:
        return True
    return False


def generate_plot(x_values, y_values, title='Channel Growth', xlabel='Days', ylabel='Views'):
    plt.figure(figsize=(8, 4))
    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close()

    return f"data:image/png;base64,{plot_data}"

