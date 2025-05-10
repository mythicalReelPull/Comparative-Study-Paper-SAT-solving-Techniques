import pandas as pd
import matplotlib.pyplot as plt
import os

import matplotlib
matplotlib.use('Agg')

def plot_heuristic_performance(csv_folder, output_folder):
        """
    Load data from all CSV files in the specified folder and plot heuristic performance.

    Args:
        csv_folder (str): Path to the folder containing CSV files with heuristic performance data.
        output_folder (str): Path to the folder where the output chart will be saved.

    Returns:
        None
    """
    # Load and filter the data
    all_data = []
    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_folder, filename)
            try:
                df = pd.read_csv(file_path)
                all_data.append(df)
            except FileNotFoundError:
                print(f"Error: The file {file_path} was not found.")
                continue
            except pd.errors.EmptyDataError:
                print(f"Error: The file {file_path} is empty.")
                continue
            except Exception as e:
                print(f"An error occurred while reading the CSV file {file_path}: {e}")
                continue

    if not all_data:
        print("No valid CSV files found in the specified folder.")
        return

    # Combine all data into a single DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)

    # Filter out rows that are not per-instance data
    combined_df = combined_df[combined_df['filename'].notna()]

    # Group by heuristic and compute stats in milliseconds
    stats = (
        combined_df
        .groupby('heuristic')['time_seconds']
        .agg(mean='mean', min='min', max='max')
        .reset_index()
    )

    # Convert times from seconds to milliseconds
    stats['mean'] *= 1000
    stats['min'] *= 1000
    stats['max'] *= 1000

    # Prepare bar positions
    x = range(len(stats))
    width = 0.25

    # Plotting as a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar([i - width for i in x], stats['mean'], width=width, label='Mean Time', color='blue')
    plt.bar(x, stats['min'], width=width, label='Min Time', color='yellow')
    plt.bar([i + width for i in x], stats['max'], width=width, label='Max Time', color='green')

    plt.xlabel('Heuristic')
    plt.ylabel('Time (milliseconds)')
    plt.title('Heuristic Performance: Mean, Min, and Max Times')
    plt.xticks(x, stats['heuristic'])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the figure to the output folder
    output_file = os.path.join(output_folder, 'heuristic_performance.png')
    plt.savefig(output_file)
    print(f"Chart saved to: {output_file}")

def plot_average_memory_usage(csv_folder, output_folder):
        """
    Load data from all CSV files and plot average memory usage for each heuristic.

    Args:
        csv_folder (str): Path to the folder containing CSV files with memory usage data.
        output_folder (str): Path to the folder where the output chart will be saved.

    Returns:
        None
    """
    all_data = []
    for filename in os.listdir(csv_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_folder, filename)
            try:
                df = pd.read_csv(file_path)
                all_data.append(df)
            except Exception as e:
                print(f"An error occurred while reading the CSV file {file_path}: {e}")
                continue

    if not all_data:
        print("No valid CSV files found in the specified folder.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df[combined_df['filename'].notna()]

    # Group by heuristic and compute average memory usage
    memory_stats = (
        combined_df
        .groupby('heuristic')['memory_used_mb']
        .agg(average_memory='mean')
        .reset_index()
    )

    # Prepare bar positions
    x = range(len(memory_stats))

    # Plotting as a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(x, memory_stats['average_memory'], width=0.4, label='Average Memory Usage', color='orange')

    plt.xlabel('Heuristic')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Average Memory Usage by Heuristic')
    plt.xticks(x, memory_stats['heuristic'])
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Save the figure to the output folder
    output_file = os.path.join(output_folder, 'average_memory_usage.png')
    plt.savefig(output_file)
    print(f"Average memory usage chart saved to: {output_file}")

if __name__ == '__main__':
    """
    Main entry point for the script. Generates performance and memory usage charts
    from CSV files in the specified folder and saves them to the output folder.
    """
    # Path to the folder containing CSV files
    csv_folder = r'C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\TEST_DP\results'
    # Specify the output folder for the chart images
    output_folder = r'C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\TEST_DP\charts'
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    plot_heuristic_performance(csv_folder, output_folder)
    plot_average_memory_usage(csv_folder, output_folder)
