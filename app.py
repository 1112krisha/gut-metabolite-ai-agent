import streamlit as st
import pandas as pd
import openai
import json
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

MASTER_PROMPT = """
For the compound "{compound}", provide the following fields strictly in valid JSON format ONLY (no explanation, no extra text). Use these exact keys:

"Compound Name", "Metabolite", "Gut Metabolome Database", "Metabolite Database ID", "Chemical Formula", "Monoisotopic Mass", "Class of Metabolites", "Pathway Name", "Sample Type", "Metabolic Functions", "Origin", "Microbial Genus", "Microbial Species", "Microbial Strains", "Roles in Gut Health", "Immune Modulation", "Microbial Interactions", "Microbial Diversity Marker", "Digestive Efficiency Indicator", "Health Risk Biomarker", "Neuroendocrine Modulator", "Metabolic Syndrome Indicator", "Barrier Integrity Marker", "Inflammation Marker", "Anti-inflammatory", "Disease Association", "Influenced by Diet", "Gene Association", "RDA Value", "RDA Reference Unit", "RDA Category", "Reference", "MS Data Source".

If any data is not available, use "NA" as value.
"""

def generate_compound_data(compound):
    prompt = MASTER_PROMPT.format(compound=compound)
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert gut metabolite database assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=1200,
    )
    content = response['choices'][0]['message']['content']

    # Try parsing JSON
    try:
        data_json = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON substring if GPT added extra text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                data_json = json.loads(json_match.group(0))
            except:
                data_json = {"Compound Name": compound, "Error": "Failed to parse JSON after extraction"}
        else:
            data_json = {"Compound Name": compound, "Error": "No JSON found in GPT output"}

    return data_json

def main():
    st.title("Gut Metabolite AI Agent")

    uploaded_file = st.file_uploader("Upload CSV with 'Compound Name' column", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if 'Compound Name' not in df.columns:
            st.error("CSV must have 'Compound Name' column")
            return
        
        if st.button("Fill Data using AI Agent"):
            all_data = []
            progress = st.progress(0)
            total = len(df)
            for idx, row in df.iterrows():
                compound = row['Compound Name']
                st.write(f"Processing: {compound} ({idx+1}/{total})")
                data = generate_compound_data(compound)
                all_data.append(data)
                progress.progress((idx+1)/total)
            
            result_df = pd.DataFrame(all_data)
            st.success("Data filled successfully!")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download filled CSV",
                data=csv,
                file_name='gut_metabolites_filled.csv',
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
