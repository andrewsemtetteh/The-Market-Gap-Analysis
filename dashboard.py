import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#setting the page configuration
st.set_page_config(
    page_title="Sugar Trap Market Gap Analysis",
    page_icon="🍪",
    layout="wide",
    initial_sidebar_state="expanded"
)

#loading cleaned data downloaded from the project code file
@st.cache_data
def load_data():
    try:
        # Using the cleaned food_data.csv file
        food_data = pd.read_csv("food_data.csv")
        
        if food_data.empty or len(food_data) == 0:
            st.error("food_data.csv is empty. Please ensure the cleaned dataset is available.")
            return None
        
        return food_data
        
    except FileNotFoundError:
        st.error("food_data.csv not found. Please ensure the cleaned dataset is in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

#loading the data
food_data = load_data()

if food_data is None:
    st.stop()

st.markdown("""
<div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
    <h1 style="
        font-size: 3rem; 
        font-weight: 700; 
        color: #1f77b4;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    ">
        The <em>"Sugar Trap"</em> Market Gap Analysis
    </h1>
    <div style="
        font-size: 1.1rem; 
        color: #666; 
        font-weight: 400;
        margin-top: 1rem;
        line-height: 1.6;
    ">
        <strong>Client:</strong> Helix CPG Partners<br>
        <strong>Objective:</strong> Identify "Blue Ocean" opportunities in snack market by analyzing nutritional gaps in existing products.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Products", f"{len(food_data):,}")

with col2:
    avg_sugar = food_data['sugars_100g'].mean()
    st.metric("Avg Sugar (100g)", f"{avg_sugar:.1f}g")

with col3:
    avg_protein = food_data['proteins_100g'].mean()
    st.metric("Avg Protein (100g)", f"{avg_protein:.1f}g")

# Nutrient Matrix Visualization
st.markdown("## Nutrient Matrix: Sugar vs Protein")

# defining the thresholds
LOW_SUGAR = 10
HIGH_PROTEIN = 15

# Create scatter plot
fig = px.scatter(
    food_data,
    x='sugars_100g',
    y='proteins_100g',
    color='primary_category',
    title="Sugar vs Protein Content by Category",
    labels={
        'sugars_100g': 'Sugar (g per 100g)',
        'proteins_100g': 'Protein (g per 100g)',
        'primary_category': 'Primary Category'
    },
    template='plotly_white'  # Theme-aware template
)

# Add quadrant lines
fig.add_vline(x=LOW_SUGAR, line_dash="dash", line_color="red", 
              annotation_text=f"Low Sugar: {LOW_SUGAR}g")
fig.add_hline(y=HIGH_PROTEIN, line_dash="dash", line_color="green",
              annotation_text=f"High Protein: {HIGH_PROTEIN}g")

# Highlight Blue Ocean quadrant
fig.add_annotation(
    x=LOW_SUGAR/2, y=HIGH_PROTEIN*1.5,
    text="Blue Ocean<br>Low Sugar, High Protein",
    showarrow=True,
    arrowhead=2,
    bgcolor="rgba(76, 175, 80, 0.3)",
    bordercolor="green",
    borderwidth=2
)

# Update layout for consistent theming
fig.update_layout(
    font=dict(size=12),
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent background
)

st.plotly_chart(fig, use_container_width=True)

# the Blue Ocean Analysis
blue_ocean_products = food_data[
    (food_data['sugars_100g'] < LOW_SUGAR) & 
    (food_data['proteins_100g'] > HIGH_PROTEIN)
]

st.markdown(f"""
## Key Insight

Based on the data, the biggest market opportunity is in **{blue_ocean_products['primary_category'].mode().iloc[0] if len(blue_ocean_products) > 0 else 'Salty Snacks'}**, 
specifically targeting products with **>{HIGH_PROTEIN}g of protein** and **<{LOW_SUGAR}g of sugar**.

**Products in Blue Ocean Quadrant:** {len(blue_ocean_products):,}  
**Percentage of Total Market:** {(len(blue_ocean_products)/len(food_data)*100):.1f}%
""")

# Category filter for detailed analysis
selected_categories = st.multiselect(
    "Filter by Primary Categories:",
    options=food_data['primary_category'].unique().tolist(),
    default=food_data['primary_category'].unique().tolist()
)

if selected_categories:
    filtered_data = food_data[food_data['primary_category'].isin(selected_categories)]
    
    # updating thr scatter plot with filtered data
    fig_filtered = px.scatter(
        filtered_data,
        x='sugars_100g',
        y='proteins_100g',
        color='primary_category',
        title=f"Filtered Analysis: {', '.join(selected_categories)}",
        labels={
            'sugars_100g': 'Sugar (g per 100g)',
            'proteins_100g': 'Protein (g per 100g)',
            'primary_category': 'Primary Category'
        }
    )
    
    fig_filtered.add_vline(x=LOW_SUGAR, line_dash="dash", line_color="red")
    fig_filtered.add_hline(y=HIGH_PROTEIN, line_dash="dash", line_color="green")
    
    st.plotly_chart(fig_filtered, use_container_width=True)

# Ingredient Analysis for High Protein Products
st.markdown("## Hidden Gem: Protein Sources Analysis")

high_protein_products = food_data[food_data['proteins_100g'] > HIGH_PROTEIN]

if len(high_protein_products) > 0:
    # Extract protein sources from ingredients
    def extract_protein_sources(ingredients):
        if pd.isna(ingredients):
            return []
        ingredients_str = str(ingredients).lower()
        protein_keywords = ['whey', 'protein', 'peanut', 'almond', 'soy', 'casein', 'milk', 'egg', 'cheese']
        return [keyword for keyword in protein_keywords if keyword in ingredients_str]
    
    high_protein_products['protein_sources'] = high_protein_products['ingredients_text'].apply(extract_protein_sources)
    
    # Count protein sources
    all_sources = []
    for sources in high_protein_products['protein_sources']:
        all_sources.extend(sources)
    
    if all_sources:
        source_counts = pd.Series(all_sources).value_counts().head(3)
        
        st.markdown("### Top 3 Protein Sources in High-Protein Products:")
        for source, count in source_counts.items():
            st.write(f"**{source.title()}**: {count} products")

#candidate's Choice: Nutriscore Grade Analysis
st.markdown("## Candidate's Choice: Nutriscore Grade Distribution")

st.markdown("""
**Why I added this:**  
I chose this because Sugar vs. Protein shows one dimension of health but the Nutriscore grade captures the full nutritional picture i.e sugar, fat, salt, fiber, and protein etc combined into one A to E score. Therefore, category full of D and E grades represents a larger Blue Ocean opportunity for disruption.
""")

# Filter for valid nutriscore grades
nutriscore_data = food_data[food_data['nutriscore_grade'].isin(['a', 'b', 'c', 'd', 'e'])].copy()
nutriscore_data['nutriscore_grade'] = nutriscore_data['nutriscore_grade'].str.upper()

# Count products per category per grade
grade_counts = nutriscore_data.groupby(['primary_category', 'nutriscore_grade']).size().reset_index(name='product_count')

#filtering for categories with significant data (Total > 50 graded products)
category_totals = grade_counts.groupby('primary_category')['product_count'].sum()
significant_categories = category_totals[category_totals > 50].index
grade_counts = grade_counts[grade_counts['primary_category'].isin(significant_categories)]

# Create grouped bar chart
fig_nutriscore = px.bar(
    grade_counts,
    x='primary_category',
    y='product_count',
    color='nutriscore_grade',
    barmode='group',
    title='Nutriscore Grade Distribution by Category',
    labels={'primary_category': 'Category', 'product_count': 'Number of Products', 'nutriscore_grade': 'Grade'},
    color_discrete_map={'A': '#038141', 'B': '#85BB2F', 'C': '#FECB02', 'D': '#EE8100', 'E': '#E63E11'},
    height=600,
    template='plotly_white'  
)

#  grade key annotation
fig_nutriscore.add_annotation(
    xref="paper", yref="paper",
    x=1.15, y=0.5,
    text="<b>Grade Key:</b><br>A: Best Quality<br>B: Good Quality<br>C: Average<br>D: Lower Quality<br>E: Poorest Quality",
    showarrow=False,
    font=dict(size=12),
    align="left",
    bgcolor="rgba(0,0,0,0)",  # Transparent background
    bordercolor="black",
    borderwidth=1
)

fig_nutriscore.update_layout(
    xaxis_tickangle=-30,
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
    margin=dict(r=150),
    font=dict(size=12)  # Consistent font sizing
)

st.plotly_chart(fig_nutriscore, use_container_width=True)

# Calculate percentage of unhealthy (D/E) grades
total_per_category = nutriscore_data.groupby('primary_category').size().reset_index(name='total')
bad_per_category = nutriscore_data[nutriscore_data['nutriscore_grade'].isin(['D', 'E'])].groupby('primary_category').size().reset_index(name='bad_count')

full_health_summary = total_per_category.merge(bad_per_category, on='primary_category', how='left').fillna(0)
full_health_summary['pct_unhealthy'] = (full_health_summary['bad_count'] / full_health_summary['total'] * 100).round(1)
full_health_summary = full_health_summary.sort_values('pct_unhealthy', ascending=False)

st.markdown("### Percentage of Unhealthy Products by Category")
st.dataframe(full_health_summary[['primary_category', 'total', 'pct_unhealthy']], use_container_width=True)

st.markdown("---")
st.markdown("**Dashboard Created For:** Helix CPG Partners")
