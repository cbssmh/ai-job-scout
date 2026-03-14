import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Job Scout Dashboard",
    page_icon="💼",
    layout="wide",
)

st.title("💼 AI Job Scout Dashboard")
st.caption("Real-world job analysis and personalized recommendation dashboard")


def parse_csv_text(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def fetch_jobs():
    response = requests.get(f"{API_BASE_URL}/jobs/", timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_analysis():
    response = requests.get(f"{API_BASE_URL}/analysis/", timeout=30)
    response.raise_for_status()
    return response.json()


def run_analysis(limit: int):
    response = requests.post(
        f"{API_BASE_URL}/analysis/run",
        params={"limit": limit},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def run_recommendations(skills: list[str], preferred_countries: list[str], visa_needed: bool):
    payload = {
        "skills": skills,
        "preferred_countries": preferred_countries,
        "visa_needed": visa_needed,
    }

    response = requests.post(
        f"{API_BASE_URL}/recommendations/run",
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def apply_job_filters(items, search_text: str, min_score: int):
    filtered = []

    search_text_lower = search_text.lower().strip()

    for item in items:
        title = str(item.get("title", "")).lower()
        company = str(item.get("company", "")).lower()
        role = str(item.get("role", "")).lower()
        tech_stack = str(item.get("tech_stack", "")).lower()
        score = int(item.get("match_score", 0))

        if score < min_score:
            continue

        if search_text_lower:
            target_text = f"{title} {company} {role} {tech_stack}"
            if search_text_lower not in target_text:
                continue

        filtered.append(item)

    return filtered


def build_job_lookup(jobs):
    return {job["id"]: job for job in jobs if "id" in job}


with st.sidebar:
    st.header("Settings")

    api_url_input = st.text_input("API Base URL", value=API_BASE_URL)
    if api_url_input.strip():
        API_BASE_URL = api_url_input.strip()

    st.divider()

    st.subheader("Analysis")
    analysis_limit = st.slider("Batch analysis limit", min_value=1, max_value=50, value=10, step=1)

    if st.button("Run Analysis Batch", use_container_width=True):
        try:
            with st.spinner("Running analysis batch..."):
                result = run_analysis(analysis_limit)
            st.success(f"Analyzed {len(result)} jobs")
        except Exception as e:
            st.error(f"Analysis failed: {e}")

    st.divider()

    st.subheader("Recommendation Profile")

    skills_input = st.text_area(
        "Skills (comma-separated)",
        value="Python, FastAPI, Docker, AWS",
        height=110,
    )

    countries_input = st.text_input(
        "Preferred Countries (comma-separated)",
        value="Germany",
    )

    visa_needed = st.checkbox("Need visa sponsorship", value=True)

    st.divider()

    st.subheader("Recommendation Filters")
    search_text = st.text_input("Search title/company/role/tech", value="")
    min_score = st.slider("Minimum match score", min_value=0, max_value=100, value=0, step=5)
    top_n = st.selectbox("Show top N recommendations", [5, 10, 20, 50, 100], index=1)

    run_reco = st.button("Get Recommendations", type="primary", use_container_width=True)


jobs = []
analysis_rows = []
job_lookup = {}

try:
    jobs = fetch_jobs()
    job_lookup = build_job_lookup(jobs)
except Exception:
    pass

try:
    analysis_rows = fetch_analysis()
except Exception:
    pass


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Stored Jobs", len(jobs))

with col2:
    st.metric("Analyzed Jobs", len(analysis_rows))

with col3:
    coverage = round((len(analysis_rows) / len(jobs)) * 100, 1) if jobs else 0
    st.metric("Analysis Coverage", f"{coverage}%")

with col4:
    remaining = max(len(jobs) - len(analysis_rows), 0)
    st.metric("Pending Analysis", remaining)


tab1, tab2, tab3 = st.tabs(["Recommendations", "Stored Jobs", "Analysis Results"])


with tab1:
    st.subheader("Top Job Matches")

    if run_reco:
        skills = parse_csv_text(skills_input)
        preferred_countries = parse_csv_text(countries_input)

        try:
            with st.spinner("Fetching recommendations..."):
                recommendations = run_recommendations(
                    skills=skills,
                    preferred_countries=preferred_countries,
                    visa_needed=visa_needed,
                )

            recommendations = apply_job_filters(
                recommendations,
                search_text=search_text,
                min_score=min_score,
            )

            if not recommendations:
                st.info("No recommendations matched your current filters.")
            else:
                visible = recommendations[:top_n]

                score_values = [item.get("match_score", 0) for item in visible]
                avg_score = round(sum(score_values) / len(score_values), 1) if score_values else 0

                top_stats_1, top_stats_2, top_stats_3 = st.columns(3)
                top_stats_1.metric("Filtered Results", len(recommendations))
                top_stats_2.metric("Visible Results", len(visible))
                top_stats_3.metric("Average Score", avg_score)

                for idx, item in enumerate(visible, start=1):
                    source_job = job_lookup.get(item["job_id"], {})
                    job_url = source_job.get("url", "")
                    location = source_job.get("location", "Unknown")

                    with st.container(border=True):
                        title_cols = st.columns([5, 1])

                        with title_cols[0]:
                            st.markdown(f"### {idx}. {item['title']}")

                        with title_cols[1]:
                            if job_url:
                                st.link_button("Open Job", job_url, use_container_width=True)

                        st.write(f"**Company:** {item['company']}")
                        st.write(f"**Location:** {location}")
                        st.write(f"**Role:** {item.get('role') or 'Unknown'}")
                        st.write(f"**Tech Stack:** {item.get('tech_stack') or 'N/A'}")
                        st.write(f"**Visa Sponsorship:** {item.get('visa_sponsorship') or 'unknown'}")

                        metric_cols = st.columns(5)
                        metric_cols[0].metric("Match Score", item.get("match_score", 0))
                        metric_cols[1].metric("Skill Score", item.get("skill_score", 0))
                        metric_cols[2].metric("Language Bonus", item.get("language_bonus", 0))
                        metric_cols[3].metric("Visa Bonus", item.get("visa_bonus", 0))
                        metric_cols[4].metric("Location Bonus", item.get("location_bonus", 0))

                        st.write(f"**Reason:** {item.get('reason', '')}")

                st.divider()
                st.subheader("Recommendation Table")
                st.dataframe(visible, use_container_width=True)

        except Exception as e:
            st.error(f"Recommendation request failed: {e}")
    else:
        st.info("Set your profile in the sidebar and click **Get Recommendations**.")


with tab2:
    st.subheader("Stored Jobs")

    if not jobs:
        st.info("No jobs stored yet.")
    else:
        job_search = st.text_input("Search stored jobs", value="", key="job_search")
        preview_n = st.selectbox("Jobs preview count", [10, 20, 50, 100], index=1)

        filtered_jobs = []
        job_search_lower = job_search.lower().strip()

        for job in jobs:
            title = str(job.get("title", "")).lower()
            company = str(job.get("company", "")).lower()
            location = str(job.get("location", "")).lower()

            if job_search_lower and job_search_lower not in f"{title} {company} {location}":
                continue

            filtered_jobs.append(job)

        st.write(f"Filtered stored jobs: {len(filtered_jobs)}")
        st.dataframe(filtered_jobs[:preview_n], use_container_width=True)

        with st.expander("Show stored job cards"):
            for job in filtered_jobs[:10]:
                with st.container(border=True):
                    st.write(f"**Title:** {job.get('title')}")
                    st.write(f"**Company:** {job.get('company')}")
                    st.write(f"**Location:** {job.get('location')}")
                    if job.get("url"):
                        st.link_button("Open Original Posting", job["url"])
                    description = job.get("description_raw", "") or ""
                    st.write(description[:500] + ("..." if len(description) > 500 else ""))


with tab3:
    st.subheader("Analysis Results")

    if not analysis_rows:
        st.info("No analysis results found.")
    else:
        analysis_search = st.text_input("Search analysis results", value="", key="analysis_search")
        preview_n = st.selectbox("Analysis preview count", [10, 20, 50, 100], index=1, key="analysis_preview")

        filtered_analysis = []
        analysis_search_lower = analysis_search.lower().strip()

        for row in analysis_rows:
            role = str(row.get("role", "")).lower()
            tech_stack = str(row.get("tech_stack", "")).lower()
            summary = str(row.get("summary", "")).lower()

            if analysis_search_lower and analysis_search_lower not in f"{role} {tech_stack} {summary}":
                continue

            filtered_analysis.append(row)

        st.write(f"Filtered analysis rows: {len(filtered_analysis)}")
        st.dataframe(filtered_analysis[:preview_n], use_container_width=True)

        with st.expander("Show detailed analysis cards"):
            for row in filtered_analysis[:10]:
                source_job = job_lookup.get(row.get("job_id"), {})
                with st.container(border=True):
                    st.write(f"**Job ID:** {row.get('job_id')}")
                    st.write(f"**Title:** {source_job.get('title', 'Unknown')}")
                    st.write(f"**Company:** {source_job.get('company', 'Unknown')}")
                    st.write(f"**Role:** {row.get('role')}")
                    st.write(f"**Tech Stack:** {row.get('tech_stack')}")
                    st.write(f"**Experience:** {row.get('experience_level')}")
                    st.write(f"**Language:** {row.get('language_requirement')}")
                    st.write(f"**Visa:** {row.get('visa_sponsorship')}")
                    st.write(f"**Summary:** {row.get('summary')}")
                    if source_job.get("url"):
                        st.link_button("Open Original Posting", source_job["url"])