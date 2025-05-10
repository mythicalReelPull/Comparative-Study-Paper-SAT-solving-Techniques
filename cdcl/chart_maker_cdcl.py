import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

import matplotlib
matplotlib.use('Agg')

def plot_solving_performance(csv_file, output_folder):
        """
    Load data from the specified CSV file and plot solving performance.

    Args:
        csv_file (str): Path to the CSV file containing solving performance data.
        output_folder (str): Path to the folder where the output chart will be saved.

    Returns:
        None
    """
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: The file {csv_file} is empty.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file {csv_file}: {e}")
        return

    # Filter out rows that are not per-instance data
    df = df[df['Filename'].notna()]

    # Extract clause counts and solving times
    clause_counts = df['Clauses'].unique()
    mean_times = []
    max_times = []
    min_times = []

    for count in clause_counts:
        group = df[df['Clauses'] == count]
        mean_times.append(group['Solving Time (s)'].mean())
        max_times.append(group['Solving Time (s)'].max())
        min_times.append(group['Solving Time (s)'].min())

    # Prepare bar positions
    x = range(len(clause_counts))
    width = 0.25

    # Plotting as a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar([i - width for i in x], mean_times, width=width, label='Mean Time', color='blue', alpha=0.6)
    plt.bar(x, min_times, width=width, label='Min Time', color='yellow', alpha=0.6)
    plt.bar([i + width for i in x], max_times, width=width, label='Max Time', color='green', alpha=0.6)

    # Adding data labels on top of the bars with higher precision
    for i, bar in enumerate(plt.bar([i - width for i in x], mean_times, width=width)):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.6f}', ha='center', va='bottom')

    for i, bar in enumerate(plt.bar(x, min_times, width=width)):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.6f}', ha='center', va='bottom')

    for i, bar in enumerate(plt.bar([i + width for i in x], max_times, width=width)):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.6f}', ha='center', va='bottom')

    plt.xlabel('Number of Clauses')
    plt.ylabel('Time (seconds)')  # Update ylabel to reflect only time
    plt.title('SAT Solver Performance: Mean, Min, and Max Solving Times')
    plt.xticks(x, clause_counts)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the figure to the output folder
    output_file = os.path.join(output_folder, 'performance_chart.png')
    plt.savefig(output_file)
    print(f"Chart saved to: {output_file}")

def plot_memory_usage(csv_file, output_folder):
        """
    Load data from the specified CSV file and plot memory usage.

    Args:
        csv_file (str): Path to the CSV file containing memory usage data.
        output_folder (str): Path to the folder where the output chart will be saved.

    Returns:
        None
    """
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: The file {csv_file} is empty.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file {csv_file}: {e}")
        return

    # Filter out rows that are not per-instance data
    df = df[df['Filename'].notna()]

    # Extract clause counts and median memory usage
    clause_counts = df['Clauses'].unique()
    median_memory = []

    for count in clause_counts:
        group = df[df['Clauses'] == count]
        median_memory.append(group['Memory Used (MB)'].median())  # Calculate median memory

    # Remove NaN values from clause_counts and median_memory
    valid_indices = ~np.isnan(median_memory)  # Get indices where median_memory is not NaN
    clause_counts = clause_counts[valid_indices]  # Filter clause_counts
    median_memory = np.array(median_memory)[valid_indices]  # Filter median_memory

    # Prepare line plot
    plt.figure(figsize=(10, 6))
    plt.plot(clause_counts, median_memory, marker='o', color='orange', label='Median Memory (MB)')
    
    # Adding data labels on top of the line
    for i, value in enumerate(median_memory):
        plt.text(clause_counts[i], value, f'{value:.6f}', ha='center', va='bottom')

    plt.xlabel('Number of Clauses')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Median Memory Usage by Number of Clauses')
    plt.xticks(clause_counts)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the figure to the output folder
    output_file = os.path.join(output_folder, 'median_memory_usage_chart.png')
    plt.savefig(output_file)
    print(f"Memory usage chart saved to: {output_file}")

if __name__ == '__main__':
    """
    Main entry point for the script. Generates performance and memory usage charts
    from a specified CSV file and saves them to the output folder.
    """
    # Path to the CSV file
    csv_file = r'C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\cdcl\results\solving_results.csv'
    # Specify the output folder for the chart images
    output_folder = r'C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\cdcl\charts'
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    plot_solving_performance(csv_file, output_folder)
    plot_memory_usage(csv_file, output_folder)  # Call the new function
