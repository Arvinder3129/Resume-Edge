import streamlit as st
import pandas as pd
import altair as alt
from resume_parser import extract_text_from_pdf
from embeddings import encode_texts
from ranking import rank_resumes

st.set_page_config(page_title="AI Resume Ranking System", layout="wide")
st.title("AI Resume Ranking System")

# 🌈 Custom CSS for curved graph boxes
st.markdown("""
    <style>
    /* Outer card adapts to theme background */
    .outer-card {
        background-color: var(--background-color);
        padding: 25px;
        border-radius: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin-bottom: 30px;
        transition: all 0.3s ease;
    }

    /* Inner card adapts to secondary background */
    .inner-card {
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        padding: 20px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
    }

    /* Text color adapts to theme */
    .inner-card h3 {
        color: var(--text-color);
        font-weight: 600;
        margin-bottom: 15px;
    }

    /* Optional: subtle border glow for dark mode */
    @media (prefers-color-scheme: dark) {
        .outer-card {
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 6px 25px rgba(255,255,255,0.05);
        }
        .inner-card {
            box-shadow: inset 0 0 10px rgba(255,255,255,0.05);
        }
    }
    </style>
""", unsafe_allow_html=True)



# Input job description
job_description = st.text_area("Enter Job Description")

# Upload multiple resumes
uploaded_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files and job_description:
    resumes = []
    for file in uploaded_files:
        text = extract_text_from_pdf(file)
        resumes.append({"Name": file.name, "Summary": text})

    # Generate embeddings
    resume_embeddings = encode_texts([r["Summary"] for r in resumes])
    job_embedding = encode_texts([job_description])

    # Rank resumes
    ranked = rank_resumes(resume_embeddings, job_embedding, resumes)

    # Convert to DataFrame
    df = pd.DataFrame(ranked)[["Name", "MatchScore"]]
    df["MatchScore"] = df["MatchScore"].astype(float)

    # Categorize
    def categorize(score):
        if score > 70:
            return "Strong"
        elif score > 40:
            return "Moderate"
        else:
            return "Weak"
    df["Category"] = df["MatchScore"].apply(categorize)

    # 🧭 Two curved graph boxes side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="outer-card"><div class="inner-card"><h3>📈 Resume Match Timeline</h3>', unsafe_allow_html=True)
        line_chart = (
            alt.Chart(df)
            .mark_line(point=True, strokeWidth=3)
            .encode(
                x=alt.X("Name:N", title="Candidate"),
                y=alt.Y("MatchScore:Q", title="Match Score"),
                color=alt.value("#4F46E5"),
                tooltip=["Name", "MatchScore"]
            )
            .properties(width=500, height=300)
        )
        st.altair_chart(line_chart, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="outer-card"><div class="inner-card"><h3>📊 Resume Strength & Gaps</h3>', unsafe_allow_html=True)
        bar_chart = (
            alt.Chart(df)
            .mark_bar(size=40, cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
            .encode(
                x=alt.X("Category:N", title="Category"),
                y=alt.Y("count()", title="Number of Resumes"),
                color=alt.Color(
                    "Category:N",
                    scale=alt.Scale(domain=["Strong", "Moderate", "Weak"],
                                   range=["#22C55E", "#FACC15", "#EF4444"])
                ),
                tooltip=["Category", "count()"]
            )
            .properties(width=500, height=300)
        )
        st.altair_chart(bar_chart, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    # 📋 Table in a curved card
    st.markdown('<div class="outer-card"><div class="inner-card"><h3>📋 Ranked Resume Table</h3>', unsafe_allow_html=True)
    st.dataframe(df.sort_values(by="MatchScore", ascending=False), use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # 🥇 Highlight best candidate
    best_candidate = df.loc[df["MatchScore"].idxmax()]
    st.success(f"🏆 Best Match: **{best_candidate['Name']}** with score {best_candidate['MatchScore']:.2f}")

    # 📥 Download results
    st.download_button(
        label="Download Results as CSV",
        data=df.to_csv(index=False),
        file_name="ranked_resumes.csv",
        mime="text/csv"
    )
