import openai
import pandas as pd
import streamlit as st
import time

# Set your OpenAI API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Streamlit GUI ---
st.title("🧠 Gut Metabolite AI Agent")
st.write("Upload a CSV file with a column named **'Compound Name'** to fetch gut metabolite data.")

uploaded_file = st.file_uploader("📁 Upload CSV", type=["csv"])
if uploaded_file:
    input_df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded!")

    if st.button("🚀 Fill Data"):
        with st.spinner("Fetching data using AI..."):

            # Define master fields for output
            output_columns = [
                "Compound Name", "Metabolite (Y/N)", "Gut Metabolome Database", "Metabolite Database ID",
                "Chemical Formula", "Monoisotopic Mass", "Class of Metabolites", "Pathway Name", "Sample Type",
                "Metabolic Functions", "Origin", "Microbial Genus", "Microbial Species", "Microbial Strains",
                "Roles in Gut Health", "Immune Pathway Summary", "Key Microbial Interaction",
                "Microbiome Diversity Insight", "Digestive/Absorption Insight", "Primary Disease Risk",
                "Gut-Brain Axis Role", "Role in Metabolic Dysfunction", "Effect on Gut Barrier",
                "Inflammation Role", "Anti-inflammatory Mechanism", "Disease Association",
                "Influenced by Diet", "Gene Association", "RDA Value", "RDA Reference Unit",
                "RDA Category", "Reference", "MS Data Source"
            ]

            result_data = []

            for index, row in input_df.iterrows():
                compound = row["Compound Name"]

                # Compose smart prompt
                prompt = f"""
Search any of these databases: MiMeDB, GMMAD, HMDB, VMH, EnteroPathway, GutMGene, MAGMD, Metabolomics Workbench, KEGG, MetaCyc, METLIN, FooDB, ECMDB, FMDB, BioCyc.

Extract data for: **{compound}** (gut metabolite). Only use what is available in any database — NA if not found.

Return in CSV row format (no explanation), with the following columns:
{', '.join(output_columns)}

Each field must be based on available info from one or more sources — you are not required to use all databases.
                """

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                    )
                    content = response["choices"][0]["message"]["content"]

                    # Try splitting into CSV row
                    values = content.strip().split(",")
                    if len(values) == len(output_columns):
                        result_data.append(values)
                    else:
                        st.warning(f"⚠️ Skipped {compound} — response did not match expected columns.")
                        result_data.append([compound] + ["NA"] * (len(output_columns) - 1))
                    time.sleep(2)  # avoid rate limits

                except Exception as e:
                    st.error(f"❌ Error processing {compound}: {str(e)}")
                    result_data.append([compound] + ["NA"] * (len(output_columns) - 1))

            # Create output DataFrame and show
            output_df = pd.DataFrame(result_data, columns=output_columns)
            st.success("✅ All compounds processed!")

            # Display and download
            st.dataframe(output_df)
            st.download_button("📥 Download Filled CSV", output_df.to_csv(index=False), "filled_data.csv", "text/csv")

else:
    st.info("⬆️ Please upload a CSV file first.")
