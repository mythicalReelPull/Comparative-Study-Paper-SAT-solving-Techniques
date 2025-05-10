import pandas as pd
import matplotlib.pyplot as plt
import os

import matplotlib
matplotlib.use('Agg')

def plot_performance(csv_file):
        """
    Read the CSV file and plot the performance of heuristics.

    Args:
        csv_file (str): Path to the CSV file containing performance data.

    Returns:
        None
    """
    try:
        # Load the CSV file, skipping bad lines
        df = pd.read_csv(csv_file, on_bad_lines='skip')

        # Debug: Print the DataFrame to check its contents
        print(f"DataFrame loaded from {csv_file}:")
        print(df)

        # Check if the DataFrame is empty
        if df.empty:
            print("The DataFrame is empty. No data to process.")
            return

        # Filter out rows that contain statistics
        stats_df = df[df['heuristic'].notna() & df['result'].notna()]

        # Debug: Print the filtered DataFrame
        print("Filtered DataFrame for statistics:")
        print(stats_df)

        # Check if the filtered DataFrame is empty
        if stats_df.empty:
            print("No statistics found after filtering.")
            return

        # Prepare data for plotting
        heuristics = stats_df['heuristic'].unique()
        min_times = []
        avg_times = []
        max_times = []

        for heuristic in heuristics:
            heuristic_stats = stats_df[stats_df['heuristic'] == heuristic]
            if heuristic_stats.empty:
                print(f"No statistics found for heuristic: {heuristic}")
                continue  # Skip if no statistics found

            # Collect times for the heuristic and convert to milliseconds
            times = heuristic_stats['time_seconds'].astype(float) * 1000  # Convert to milliseconds

            # Calculate min, avg, and max times
            min_times.append(times.min())
            avg_times.append(times.mean())
            max_times.append(times.max())

        # Create a bar chart
        bar_width = 0.25
        x = range(len(heuristics))

        plt.bar(x, min_times, width=bar_width, label='Min Time (ms)', color='blue', align='center')
        plt.bar([p + bar_width for p in x], avg_times, width=bar_width, label='Average Time (ms)', color='yellow', align='center')
        plt.bar([p + bar_width * 2 for p in x], max_times, width=bar_width, label='Max Time (ms)', color='green', align='center')

        # Adding labels and title
        plt.xlabel('Heuristics')
        plt.ylabel('Time (milliseconds)')
        plt.title('Performance Comparison of Heuristics')
        plt.xticks([p + bar_width for p in x], heuristics)
        plt.legend()

        # Save the plot as an image file
        output_file = os.path.join(os.path.dirname(csv_file), 'performance_plot.png')
        plt.tight_layout()
        plt.savefig(output_file)  # Save the figure
        print(f"Plot saved as {output_file}")

        plt.close()  # Close the plot to free up memory

    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")

def plot_average_memory_usage(csv_file):
        """
    Main entry point for the script. Prompts the user to select a heuristic, tests the Davis-Putnam algorithm
    on all DIMACS CNF files in a specified folder, and saves the results to a CSV file.
    """
    try:
        # Load the CSV file, skipping bad lines
        df = pd.read_csv(csv_file, on_bad_lines='skip')

        # Check if the DataFrame is empty
        if df.empty:
            print("The DataFrame is empty. No data to process.")
            return

        # Filter out rows that contain statistics
        stats_df = df[df['heuristic'].notna() & df['memory_used_mb'].notna()]

        # Prepare data for plotting
        heuristics = stats_df['heuristic'].unique()
        avg_memory = []

        for heuristic in heuristics:
            heuristic_stats = stats_df[stats_df['heuristic'] == heuristic]
            if heuristic_stats.empty:
                print(f"No statistics found for heuristic: {heuristic}")
                continue  # Skip if no statistics found

            # Calculate average memory usage
            avg_memory.append(heuristic_stats['memory_used_mb'].mean())

        # Create a bar chart
        bar_width = 0.4
        x = range(len(heuristics))

        plt.figure(figsize=(10, 6))
        plt.bar(x, avg_memory, width=bar_width, label='Average Memory Usage (MB)', color='orange', align='center')

        # Adding labels and title
        plt.xlabel('Heuristics')
        plt.ylabel('Memory Usage (MB)')
        plt.title('Average Memory Usage by Heuristic')
        plt.xticks(x, heuristics)
        plt.legend()

        # Save the plot as an image file
        output_file = os.path.join(os.path.dirname(csv_file), 'average_memory_usage_plot.png')
        plt.tight_layout()
        plt.savefig(output_file)  # Save the figure
        print(f"Average memory usage plot saved as {output_file}")

        plt.close()  # Close the plot to free up memory

    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")

if __name__ == "__main__":
    # Path to the results directory
    results_dir = r'C:\Users\MrWoo\OneDrive\Faculty\SAT_SOLVING\TEST_DPLL\results'
    
    # Search for all CSV files in the results directory
    csv_files = [f for f in os.listdir(results_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the results directory.")
    else:
        for csv_file in csv_files:
            csv_file_path = os.path.join(results_dir, csv_file)
            print(f"Processing file: {csv_file_path}")
            plot_performance(csv_file_path)
            plot_average_memory_usage(csv_file_path)