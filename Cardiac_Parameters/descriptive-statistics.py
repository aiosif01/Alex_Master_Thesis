import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('raw_data.csv')

# Rename columns to remove special characters and match the metrics
df.columns = [col.replace('[', '').replace(']', '').replace('/', '').replace(' ', '_') for col in df.columns]

# Rename specific columns to match the expected format
column_mapping = {
    'EDV_pre_ml': 'EDV_pre',
    'EDV_post_ml': 'EDV_post',
    'ESV_pre_ml': 'ESV_pre',
    'ESV_post_ml': 'ESV_post',
    'SV_pre_ml': 'SV_pre',
    'SV_post_ml': 'SV_post',
    'EF_pre_%': 'EF_pre',
    'EF_post_%': 'EF_post',
    'HR_pre_bpm': 'HR_pre',
    'HR_post_bpm': 'HR_post',
    'CO_pre_Lmin': 'CO_pre',
    'CO_post_Lmin': 'CO_post',
    'SI_pre': 'SI_pre',
    'SI_post': 'SI_post',
    'CI_pre': 'CI_pre',
    'CI_post': 'CI_post',
    'E/A_ratio_pre': 'EA_ratio_pre',
    'E/A_ratio_post': 'EA_ratio_post'
}

df = df.rename(columns=column_mapping)

# List of metrics to analyze
metrics = ['EDV', 'ESV', 'SV', 'EF', 'HR', 'CO', 'SI', 'CI', 'EA_ratio']

# Function to visualize the results
def visualize_results(df, metrics):
    num_metrics = len(metrics)
    num_cols = 3
    num_rows = (num_metrics + num_cols - 1) // num_cols
    
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 3.5 * num_rows))
    axes = axes.flatten()
    
    unit_measures = {
        'EDV': 'ml', 'ESV': 'ml', 'SV': 'ml',
        'EF': '%', 'HR': 'bpm', 'CO': 'L/min',
        'SI': 'ml/m²', 'CI': 'L/min/m²', 'EA_ratio': ''
    }
    
    palette = {
    'healthy': ['#ff7f0e', '#ffbb78'],  # Orange tones for Healthy
    'univentricle': ['#f0e68c', '#fffacd']  # Light golden yellow tones for Univentricle
    }

    
    for i, metric in enumerate(metrics):
        pre_col = f'{metric}_pre'
        post_col = f'{metric}_post'
        
        # Melt the dataframe to long format
        df_melted = pd.melt(df, id_vars=['Patient', 'Condition'], 
                            value_vars=[pre_col, post_col],
                            var_name='Exercise', value_name=metric)
        df_melted['Exercise'] = df_melted['Exercise'].map(lambda x: 'Pre-exercise' if 'pre' in x else 'Post-exercise')

        sns.boxplot(ax=axes[i], x='Condition', y=metric, hue='Exercise', data=df_melted, 
                    palette=[palette['healthy'][0], palette['healthy'][1]])
        
        sns.stripplot(ax=axes[i], x='Condition', y=metric, hue='Exercise', data=df_melted, 
                      dodge=True, linewidth=1, palette=[palette['healthy'][0], palette['healthy'][1]], alpha=0.7, jitter=False)
        
        # Connect min, max, and median values between pre and post exercise
        for condition in df['Condition'].unique():
            condition_data = df[df['Condition'] == condition]
            x_pos = 0 if condition.lower() == 'healthy' else 1
            
            # Calculate min, max, and median for pre and post exercise
            min_pre = condition_data[pre_col].min()
            max_pre = condition_data[pre_col].max()
            median_pre = condition_data[pre_col].median()
            
            min_post = condition_data[post_col].min()
            max_post = condition_data[post_col].max()
            median_post = condition_data[post_col].median()
            
            # Plot lines connecting min, max, and median values
            axes[i].plot([x_pos - 0.2, x_pos + 0.2], [min_pre, min_post], color='black', linestyle='--', linewidth=1)
            axes[i].plot([x_pos - 0.2, x_pos + 0.2], [max_pre, max_post], color='black', linestyle='--', linewidth=1)
            axes[i].plot([x_pos - 0.2, x_pos + 0.2], [median_pre, median_post], color='black', linestyle='-', linewidth=1.5)
        
        axes[i].set_title(metric, fontsize=14, fontweight='semibold')
        axes[i].set_ylabel(unit_measures[metric], fontsize=12, fontweight='semibold')
        axes[i].set_xlabel('')  # Remove x-axis label
        axes[i].tick_params(axis='both', which='major', labelsize=10)
        
        # Update x-axis ticks and labels
        x_labels = ['Healthy', 'Univentricle']
        axes[i].set_xticks([0, 1])  # Set tick locations
        axes[i].set_xticklabels(x_labels, fontsize=12, fontweight='semibold')
        
        axes[i].legend([],[], frameon=False)  # Remove individual legends
        
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])  # Remove empty subplots

    # Create a custom legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=palette['healthy'][0], markersize=10, label='Pre-exercise'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=palette['healthy'][1], markersize=10, label='Post-exercise')
    ]

    # Create the legend with custom layout
    legend = fig.legend(handles=legend_elements, 
                        loc='upper right', 
                        bbox_to_anchor=(1, 1), 
                        title='', 
                        ncol=1, 
                        columnspacing=1, 
                        handletextpad=0.5,
                        labelspacing=0.5,
                        fontsize=14,  # Increased legend font size to 14
                        frameon=True)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95], h_pad=2, w_pad=2.5)  # Fine-tune the padding for better spacing
    plt.subplots_adjust(right=0.95)  # Make room for the legend
    plt.show()

# Visualize results for each metric
visualize_results(df, metrics)