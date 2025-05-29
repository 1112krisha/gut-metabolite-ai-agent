import streamlit as st
import pandas as pd
import openai
import os
import time

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Gut Metabolite AI Agent Data Filler")

uploaded_file = st.file_uploader("Upload your CSV file with 'Compound Name' column", type=["csv"])

MASTER_PROMPT_TEMPLATE = """
Search across the following gut-related databases: MiMeDB, GMMAD, HMDB, VMH, EnteroPathway, GutMGene, MAGMD, Metabolomics Workbench, KEGG, MetaCyc, METLIN, FooDB, ECMDB, FMDB, and BioCyc. Extract comprehensive data for the compound: "{compound_name}" and structure the output with the following columns:
• Compound Name
• Metabolite (Y/N — is it a known gut metabolite?)
• Gut Metabolome Database (name of database source)
• Metabolite Database ID (unique database ID)
• Chemical Formula
• Monoisotopic Mass
• Class of Metabolites (e.g., SCFA, bile acid, polyphenol)
• Pathway Name (biochemical or metabolic pathway)
• Sample Type (stool, blood, urine, both, or other)
• Metabolic Functions (brief summary of roles)
• Origin (Human, Microbial, Dietary)
• Microbial Genus
• Microbial Species
• Microbial Strains
• Roles in Gut Health (e.g., supports mucosa, combats dysbiosis)
• Summarize the key immune pathway affected and the resulting immune response.
• Provide the most significant microbial interaction and its functional consequence in the gut ecosystem.
• Explain what this marker reveals about gut microbiome diversity in one sentence.
• Describe how this metabolite reflects digestive or absorption capacity and its clinical significance.
• Identify the primary disease risk this metabolite indicates and its predictive value.
• Explain this metabolite's gut-brain axis mechanism and its neurological/hormonal effect.
• Describe this metabolite's role in metabolic dysfunction and its association with obesity/diabetes.
• Explain how this metabolite affects intestinal barrier function and gut permeability.
• Identify whether this metabolite promotes or reduces inflammation and its primary pathway.
• Describe the specific anti-inflammatory mechanism and its protective health benefit.
• Disease Association (e.g., IBD, NAFLD, CRC)
• Influenced by Diet (Y/N with dietary sources or inhibitors)
• Gene Association (relevant host/microbial genes)
• RDA Value (e.g., 500 mg/day)
• RDA Reference Unit (mg/day, μmol/L, etc.)
• RDA Category (Adult, Infant, Pregnant, Elderly, etc.)
• Reference (PubMed ID, DOI, or database source link)
• MS Data Source (Mass spectrometry platform/data ID)
For all descriptive fields, provide concise scientific answers (1–3 sentences each). Use "NA" if data is not available. Output should be in CSV or JSON format for easy import into a database.
"""

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if "Compound Name" not in df.columns:
        st.error("Your CSV file must contain a column named 'Compound Name'.")
    else:
        st.write("Input Data Preview:")
        st.dataframe(df.head())

        if st.button("Fill Data using AI Agent"):
            all_responses = []
            for idx, row in df.iterrows():
                compound = row['Compound Name']
                prompt = MASTER_PROMPT_TEMPLATE.format(compound_name=compound)

                with st.spinner(f"Processing {compound} ({idx+1}/{len(df)})..."):
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.2,
                            max_tokens=800,
                        )
                        content = response['choices'][0]['message']['content']
                    except Exception as e:
                        content = f"Error fetching data for {compound}: {str(e)}"

                all_responses.append({
                    "Compound Name": compound,
                    "AI Response": content
                })

                # Optional: avoid rate limits
                time.sleep(1.5)

            # Show all results in a dataframe
            result_df = pd.DataFrame(all_responses)
            st.write("AI Filled Data Preview:")
            st.dataframe(result_df)

            # Allow download of results as CSV
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download filled data as CSV",
                data=csv,
                file_name='filled_gut_metabolite_data.csv',
                mime='text/csv',
            )
else:
    st.info("Upload a CSV file containing a 'Compound Name' column to start.")

