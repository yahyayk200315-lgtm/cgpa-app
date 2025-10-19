import streamlit as st
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="GPA & CGPA Calculator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "semesters" not in st.session_state:
    st.session_state.semesters = {}

def calculate_gpa(courses_df):
    """Calculate GPA for a semester."""
    if len(courses_df) == 0 or courses_df["Credit Hours"].sum() == 0:
        return 0.0
    
    total_points = (courses_df["Credit Hours"] * courses_df["Grade Points"]).sum()
    total_credits = courses_df["Credit Hours"].sum()
    return round(total_points / total_credits, 2)

def calculate_cgpa(semesters):
    """Calculate CGPA across all semesters."""
    if not semesters:
        return 0.0
    
    all_courses = []
    for sem_data in semesters.values():
        if isinstance(sem_data, dict) and "courses" in sem_data:
            all_courses.extend(sem_data["courses"])
    
    if not all_courses:
        return 0.0
    
    courses_df = pd.DataFrame(all_courses)
    if len(courses_df) == 0 or courses_df["Credit Hours"].sum() == 0:
        return 0.0
    
    total_points = (courses_df["Credit Hours"] * courses_df["Grade Points"]).sum()
    total_credits = courses_df["Credit Hours"].sum()
    return round(total_points / total_credits, 2)

def add_semester():
    """Add a new semester."""
    semester_num = len(st.session_state.semesters) + 1
    st.session_state.semesters[f"Semester {semester_num}"] = {
        "courses": [{"Course Name": "", "Credit Hours": 0.0, "Grade Points": 0.0}]
    }

def delete_semester(semester_name):
    """Delete a semester."""
    if semester_name in st.session_state.semesters:
        del st.session_state.semesters[semester_name]
        st.rerun()

def reset_all():
    """Reset all data."""
    st.session_state.semesters = {}
    st.rerun()

# Header
st.title("📚 GPA & CGPA Calculator")
st.markdown("---")

# Sidebar Controls
with st.sidebar:
    st.header("Controls")
    if st.button("➕ Add Semester", use_container_width=True, key="add_sem"):
        add_semester()
        st.rerun()
    
    st.divider()
    
    if st.button("🔄 Reset All Data", use_container_width=True, key="reset"):
        reset_all()

# Main Content
if not st.session_state.semesters:
    st.info("👈 Click 'Add Semester' in the sidebar to get started!")
else:
    # Overall CGPA Display
    cgpa = calculate_cgpa(st.session_state.semesters)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 Cumulative CGPA", value=f"{cgpa:.2f}", delta=None)
    
    with col2:
        total_semesters = len(st.session_state.semesters)
        st.metric(label="📅 Semesters", value=total_semesters)
    
    with col3:
        all_courses = []
        for sem_data in st.session_state.semesters.values():
            if isinstance(sem_data, dict) and "courses" in sem_data:
                all_courses.extend(sem_data["courses"])
        st.metric(label="📖 Total Courses", value=len(all_courses))
    
    # CGPA Progress Bar
    st.divider()
    st.subheader("CGPA Progress")
    st.progress(min(cgpa / 4.0, 1.0), text=f"{cgpa:.2f} / 4.0")
    
    st.divider()
    
    # Semester Tabs
    if len(st.session_state.semesters) > 0:
        tab_names = list(st.session_state.semesters.keys())
        tabs = st.tabs([f"📖 {name}" for name in tab_names])
        
        for tab, sem_name in zip(tabs, tab_names):
            with tab:
                sem_data = st.session_state.semesters[sem_name]
                
                # Create DataFrame for editing
                courses_df = pd.DataFrame(sem_data["courses"])
                
                # Data Editor with proper state management
                edited_df = st.data_editor(
                    courses_df,
                    key=f"editor_{sem_name}",
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "Course Name": st.column_config.TextColumn(
                            "Course Name",
                            width="medium"
                        ),
                        "Credit Hours": st.column_config.NumberColumn(
                            "Credit Hours",
                            width="small",
                            min_value=0,
                            max_value=10,
                            step=0.5
                        ),
                        "Grade Points": st.column_config.NumberColumn(
                            "Grade Points",
                            width="small",
                            min_value=0,
                            max_value=4.0,
                            step=0.1
                        ),
                    },
                    hide_index=False,
                    on_change=lambda: None
                )
                
                # Update session state with edited data
                if not edited_df.empty:
                    st.session_state.semesters[sem_name]["courses"] = edited_df.to_dict(orient="records")
                
                # Calculate GPA for this semester
                gpa = calculate_gpa(edited_df)
                
                # Display GPA and actions
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.metric(
                        label=f"{sem_name} GPA",
                        value=f"{gpa:.2f}",
                        delta=None
                    )
                
                with col2:
                    semester_progress = min(gpa / 4.0, 1.0)
                    st.progress(semester_progress, text=f"{gpa:.2f} / 4.0")
                
                with col3:
                    if st.button(f"🗑️ Delete {sem_name}", key=f"del_{sem_name}", use_container_width=True):
                        delete_semester(sem_name)
        
        st.divider()
        
        # Summary Table
        st.subheader("📋 Semester Summary")
        summary_data = []
        for sem_name, sem_data in st.session_state.semesters.items():
            courses_df = pd.DataFrame(sem_data["courses"])
            gpa = calculate_gpa(courses_df)
            total_credits = courses_df["Credit Hours"].sum()
            total_courses = len(courses_df)
            
            summary_data.append({
                "Semester": sem_name,
                "Total Courses": total_courses,
                "Total Credits": total_credits,
                "GPA": f"{gpa:.2f}"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
    <p>GPA Formula: Σ(Credit Hours × Grade Points) / Σ(Credit Hours)</p>
    <p>CGPA Formula: Weighted average of all semester GPAs</p>
    </div>
    """,
    unsafe_allow_html=True
)
