import streamlit as st
import pandas as pd

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="GPA & CGPA Calculator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Prevent scrolling issues */
    .stDataEditor {
        position: relative !important;
    }
    
    /* Smooth transitions */
    * {
        transition: none !important;
    }
    
    /* Remove unwanted animations */
    [data-testid="stMetricContainer"] {
        animation: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION - CRITICAL
# ============================================================================
if "semesters_data" not in st.session_state:
    st.session_state.semesters_data = {}

# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_gpa(courses_list):
    """Calculate GPA: Σ(Credit Hours × Grade Points) / Σ(Credit Hours)"""
    if not courses_list or not isinstance(courses_list, list):
        return 0.0
    
    total_credits = 0.0
    total_points = 0.0
    
    for course in courses_list:
        if not isinstance(course, dict):
            continue
        
        course_name = str(course.get("Course Name", "")).strip()
        if not course_name:
            continue
        
        try:
            credit_hours = float(course.get("Credit Hours") or 0)
            grade_points = float(course.get("Grade Points") or 0)
            
            if credit_hours > 0:
                total_credits += credit_hours
                total_points += credit_hours * grade_points
        except (ValueError, TypeError):
            continue
    
    if total_credits == 0:
        return 0.0
    
    gpa = total_points / total_credits
    return round(max(0.0, min(gpa, 4.0)), 2)

def calculate_cgpa(semesters_data):
    """Calculate CGPA: weighted average of all courses"""
    if not isinstance(semesters_data, dict) or not semesters_data:
        return 0.0
    
    total_credits = 0.0
    total_points = 0.0
    
    for sem_name, courses_list in semesters_data.items():
        if not isinstance(courses_list, list):
            continue
        
        for course in courses_list:
            if not isinstance(course, dict):
                continue
            
            course_name = str(course.get("Course Name", "")).strip()
            if not course_name:
                continue
            
            try:
                credit_hours = float(course.get("Credit Hours") or 0)
                grade_points = float(course.get("Grade Points") or 0)
                
                if credit_hours > 0:
                    total_credits += credit_hours
                    total_points += credit_hours * grade_points
            except (ValueError, TypeError):
                continue
    
    if total_credits == 0:
        return 0.0
    
    cgpa = total_points / total_credits
    return round(max(0.0, min(cgpa, 4.0)), 2)

def get_total_courses():
    """Get total number of valid courses"""
    count = 0
    for sem_name, courses_list in st.session_state.semesters_data.items():
        if not isinstance(courses_list, list):
            continue
        for course in courses_list:
            if isinstance(course, dict) and str(course.get("Course Name", "")).strip():
                count += 1
    return count

def get_total_credits():
    """Get total credits across all semesters"""
    total = 0.0
    for sem_name, courses_list in st.session_state.semesters_data.items():
        if not isinstance(courses_list, list):
            continue
        for course in courses_list:
            try:
                if str(course.get("Course Name", "")).strip():
                    credit_val = course.get("Credit Hours", 0)
                    if credit_val is None:
                        credit_val = 0
                    total += float(credit_val)
            except (ValueError, TypeError):
                pass
    return round(total, 1)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("⚙️ Controls")
    
    if st.button("➕ Add Semester", use_container_width=True):
        semester_num = len(st.session_state.semesters_data) + 1
        st.session_state.semesters_data[f"Semester {semester_num}"] = [
            {"Course Name": "", "Credit Hours": 0.0, "Grade Points": 0.0}
        ]
        st.rerun()
    
    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state.semesters_data = {}
        st.rerun()
    
    st.divider()
    
    if st.session_state.semesters_data:
        st.subheader("Quick Stats")
        cgpa = calculate_cgpa(st.session_state.semesters_data)
        st.metric("📊 CGPA", f"{cgpa:.2f}")
        st.metric("📅 Semesters", len(st.session_state.semesters_data))
        st.metric("📖 Courses", get_total_courses())
        st.metric("🎓 Credits", get_total_credits())

# ============================================================================
# MAIN HEADER
# ============================================================================

st.title("📚 GPA & CGPA Calculator")
st.markdown("Manage your academic performance with precision")
st.divider()

# ============================================================================
# MAIN CONTENT
# ============================================================================

if not st.session_state.semesters_data:
    st.info("👈 Click 'Add Semester' to start tracking your GPA")
else:
    # Top metrics
    cgpa = calculate_cgpa(st.session_state.semesters_data)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CGPA", f"{cgpa:.2f}")
    with col2:
        st.metric("Semesters", len(st.session_state.semesters_data))
    with col3:
        st.metric("Courses", get_total_courses())
    with col4:
        st.metric("Credits", get_total_credits())
    
    st.divider()
    
    # Progress bar
    st.subheader("Progress")
    progress_pct = min(cgpa / 4.0, 1.0)
    st.progress(progress_pct, text=f"{cgpa:.2f} / 4.0")
    
    st.divider()
    
    # Semesters section - NO TABS TO AVOID SCROLL ISSUES
    st.subheader("Semester Details")
    
    sem_names = list(st.session_state.semesters_data.keys())
    
    for sem_idx, sem_name in enumerate(sem_names):
        with st.container(border=True):
            col_title, col_delete = st.columns([4, 1])
            
            with col_title:
                st.subheader(f"{sem_name}")
            
            with col_delete:
                if st.button("🗑️ Delete", key=f"del_{sem_idx}"):
                    del st.session_state.semesters_data[sem_name]
                    st.rerun()
            
            # Get current courses for this semester
            courses_list = st.session_state.semesters_data[sem_name]
            
            # Create columns for manual input instead of data_editor
            courses_input = []
            
            # Header row
            header_col1, header_col2, header_col3 = st.columns([3, 1.5, 1.5])
            with header_col1:
                st.write("**Course Name**")
            with header_col2:
                st.write("**Credit Hours**")
            with header_col3:
                st.write("**Grade Points**")
            
            # Input rows
            for course_idx, course in enumerate(courses_list):
                input_col1, input_col2, input_col3, del_col = st.columns([3, 1.5, 1.5, 0.5])
                
                with input_col1:
                    course_name = st.text_input(
                        "Course",
                        value=course.get("Course Name", ""),
                        label_visibility="collapsed",
                        key=f"course_name_{sem_idx}_{course_idx}"
                    )
                
                with input_col2:
                    credit_hours = st.number_input(
                        "Credit",
                        value=float(course.get("Credit Hours", 0.0)),
                        min_value=0.0,
                        max_value=10.0,
                        step=0.5,
                        label_visibility="collapsed",
                        key=f"credit_hours_{sem_idx}_{course_idx}"
                    )
                
                with input_col3:
                    grade_points = st.number_input(
                        "Grade",
                        value=float(course.get("Grade Points", 0.0)),
                        min_value=0.0,
                        max_value=4.0,
                        step=0.1,
                        label_visibility="collapsed",
                        key=f"grade_points_{sem_idx}_{course_idx}"
                    )
                
                with del_col:
                    if st.button("❌", key=f"del_course_{sem_idx}_{course_idx}", help="Delete course"):
                        courses_list.pop(course_idx)
                        st.rerun()
                
                courses_input.append({
                    "Course Name": course_name,
                    "Credit Hours": credit_hours,
                    "Grade Points": grade_points
                })
            
            # Update semester data
            st.session_state.semesters_data[sem_name] = courses_input
            
            # Add row button
            col_add, col_empty = st.columns([1, 4])
            with col_add:
                if st.button("➕ Add Course", key=f"add_course_{sem_idx}"):
                    st.session_state.semesters_data[sem_name].append({
                        "Course Name": "",
                        "Credit Hours": 0.0,
                        "Grade Points": 0.0
                    })
                    st.rerun()
            
            # Semester stats
            sem_gpa = calculate_gpa(courses_list)
            sem_courses = sum(1 for c in courses_list if str(c.get("Course Name", "")).strip())
            sem_credits = sum(float(c.get("Credit Hours", 0) or 0) for c in courses_list if str(c.get("Course Name", "")).strip())
            
            st.divider()
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("GPA", f"{sem_gpa:.2f}")
            with stat_col2:
                st.metric("Courses", sem_courses)
            with stat_col3:
                st.metric("Credits", f"{sem_credits:.1f}")
    
    st.divider()
    
    # Summary table
    st.subheader("Summary")
    summary_data = []
    
    for sem_name, courses_list in st.session_state.semesters_data.items():
        gpa = calculate_gpa(courses_list)
        courses_count = sum(1 for c in courses_list if str(c.get("Course Name", "")).strip())
        credits = sum(float(c.get("Credit Hours", 0) or 0) for c in courses_list if str(c.get("Course Name", "")).strip())
        
        summary_data.append({
            "Semester": sem_name,
            "Courses": courses_count,
            "Credits": f"{credits:.1f}",
            "GPA": f"{gpa:.2f}"
        })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p><strong>GPA:</strong> Σ(Credit Hours × Grade Points) / Σ(Credit Hours)</p>
    <p><strong>CGPA:</strong> Σ(All Credits × Grades) / Σ(All Credits)</p>
    </div>
""", unsafe_allow_html=True)
