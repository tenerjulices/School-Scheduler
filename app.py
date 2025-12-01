import streamlit as st
import uuid
import datetime

# --- Configuration and Initialization ---
# Set page configuration for a clean layout
st.set_page_config(
    page_title="School Day Scheduler",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize Session State for the schedule data
# Data Structure: list of dictionaries, e.g.,
# [{'id': 'abc-123', 'name': 'Calculus III', 'time': '10:00', 'days': ['Mon', 'Wed', 'Fri']}]
if 'schedule_items' not in st.session_state:
    st.session_state.schedule_items = []
if 'edit_item_id' not in st.session_state:
    st.session_state.edit_item_id = None

DAYS_OF_WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# --- Utility Functions ---

def clear_form():
    """Resets the form state and clears the edit ID."""
    st.session_state.class_name = ""
    st.session_state.class_time = datetime.time(9, 0) # Default to 9:00 AM
    st.session_state.selected_days = []
    st.session_state.edit_item_id = None
    st.session_state.modal_open = False # Close the modal (form)

def add_edit_class(name, time, days):
    """Adds a new class or updates an existing one."""
    if not name or not time or not days:
        st.error("Please fill in the class name, time, and select at least one day.")
        return

    item_data = {
        'name': name.strip(),
        'time': time.strftime("%H:%M"), # Store time as HH:MM string
        'days': days
    }

    if st.session_state.edit_item_id:
        # Update existing item
        index = next((i for i, item in enumerate(st.session_state.schedule_items) if item['id'] == st.session_state.edit_item_id), -1)
        if index != -1:
            st.session_state.schedule_items[index].update(item_data)
            st.toast("Class updated successfully!", icon="✅")
        else:
            st.error("Error: Item to edit not found.")
    else:
        # Add new item
        item_data['id'] = str(uuid.uuid4())
        st.session_state.schedule_items.append(item_data)
        st.toast("Class added successfully!", icon="➕")

    # Clear state and trigger re-run to refresh view
    clear_form()
    st.rerun()

def delete_class(item_id):
    """Deletes a class item by ID."""
    st.session_state.schedule_items = [item for item in st.session_state.schedule_items if item['id'] != item_id]
    st.toast("Class deleted successfully!", icon="🗑️")
    st.rerun()

def load_edit_form(item_id):
    """Loads an existing item's data into the form for editing."""
    item = next((item for item in st.session_state.schedule_items if item['id'] == item_id), None)
    if item:
        # Convert stored time string back to datetime.time object for Streamlit's time_input
        time_obj = datetime.datetime.strptime(item['time'], "%H:%M").time()

        # Set session state variables used by the form widgets
        st.session_state.class_name = item['name']
        st.session_state.class_time = time_obj
        st.session_state.selected_days = item['days']
        st.session_state.edit_item_id = item_id
        st.session_state.modal_open = True
        st.rerun() # Rerun to display the form with populated data

# --- UI Components ---

def render_schedule_form():
    """Renders the Add/Edit Class form."""
    is_editing = st.session_state.edit_item_id is not None
    
    # Use st.form to group inputs and buttons for atomic submission
    with st.form(key="class_form", clear_on_submit=False):
        st.markdown(f"**{'Edit Class' if is_editing else 'Add New Class'}**", unsafe_allow_html=True)
        
        # 1. Class Name
        st.text_input(
            "Class Name / Subject",
            key="class_name",
            placeholder="e.g., Calculus III",
            label_visibility="visible",
            value=st.session_state.get('class_name', '')
        )

        # 2. Start Time
        st.time_input(
            "Start Time",
            key="class_time",
            label_visibility="visible",
            value=st.session_state.get('class_time', datetime.time(9, 0))
        )

        # 3. Days of the Week (Multiselect for simplicity)
        st.markdown("Days of the Week:")
        selected_days = st.multiselect(
            "Select days",
            options=DAYS_OF_WEEK,
            default=st.session_state.get('selected_days', []),
            label_visibility="collapsed",
            key="selected_days"
        )

        # Form submission buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            st.form_submit_button(
                label=f"{'Update' if is_editing else 'Save'} Class",
                type="primary",
                on_click=add_edit_class,
                args=(st.session_state.class_name, st.session_state.class_time, st.session_state.selected_days)
            )
        with col2:
            # Use st.button outside of the submit_button for actions that shouldn't require validation
            st.form_submit_button(
                label="Cancel",
                type="secondary",
                on_click=clear_form
            )

def render_schedule_display():
    """Renders the list of schedule items."""
    sorted_items = st.session_state.schedule_items
    
    st.subheader("Classes Overview")

    if not sorted_items:
        st.info("Your schedule is empty! Click 'Add New Class' to begin.")
        return

    # Create a grid layout for the schedule items (3 columns on wide screens, 1 on mobile)
    cols = st.columns(min(len(sorted_items), 3)) 
    
    for i, item in enumerate(sorted_items):
        col = cols[i % len(cols)] # Assign to column in a round-robin fashion
        
        with col:
            # Styled card for each class
            card_html = f"""
            <div style="
                background-color: white; 
                padding: 16px; 
                border-radius: 12px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
                border-left: 5px solid #4f46e5;
                margin-bottom: 15px;
            ">
                <h3 style="font-weight: 700; color: #4f46e5; font-size: 1.25rem; margin-bottom: 4px;">{item['name']}</h3>
                <p style="font-weight: 800; color: #1f2937; font-size: 2rem; margin-bottom: 12px;">
                    {item['time']}
                </p>
                <p style="font-size: 0.875rem; color: #4b5563; font-weight: 500; margin-bottom: 8px;">Repeats on:</p>
                <div style="display: flex; flex-wrap: wrap; gap: 4px;">
            """
            
            for day in DAYS_OF_WEEK:
                is_active = day in item['days']
                bg_color = '#eef2ff' if is_active else '#f3f4f6'
                text_color = '#4f46e5' if is_active else '#9ca3af'
                card_html += f"""
                    <span style="
                        padding: 2px 8px; 
                        font-size: 0.75rem; 
                        font-weight: 600; 
                        border-radius: 9999px; 
                        background-color: {bg_color}; 
                        color: {text_color};
                    ">
                        {day}
                    </span>
                """
            
            card_html += "</div></div>"
            st.markdown(card_html, unsafe_allow_html=True)

            # Edit and Delete buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.button("Edit", key=f"edit_{item['id']}", on_click=load_edit_form, args=(item['id'],), use_container_width=True)
            with btn_col2:
                st.button("Delete", key=f"delete_{item['id']}", on_click=delete_class, args=(item['id'],), use_container_width=True)

# --- Main App Logic ---

def main():
    st.title("My Semester Schedule")
    st.markdown("Manage your classes and lecture times in one place.")

    # 1. Action Button to open the form
    if st.button("+ Add New Class", key="add_new_btn", type="primary"):
        # Set state to open the modal/form area
        st.session_state.edit_item_id = None
        st.session_state.modal_open = True
        clear_form() # Reset the form values for a fresh add
        st.rerun()

    st.markdown("---")
    
    # 2. Conditional Form/Modal Display
    if st.session_state.get('modal_open', False):
        st.sidebar.markdown('<style>#sidebar-content {padding-top: 2rem;}</style>', unsafe_allow_html=True)
        # Use a temporary placeholder in the main body to indicate the form is active
        st.empty() 
        with st.container():
            st.header(f"{'Edit' if st.session_state.edit_item_id else 'Add'} Class")
            render_schedule_form()
            st.markdown("---")

    # 3. Schedule Display
    render_schedule_display()
    
    # 4. Footer (User/App ID Mock)
    st.markdown("---")
    st.markdown(
        f"""
        <footer style='text-align: center; font-size: 0.75rem; color: #9ca3af;'>
            <p>Application ID: streamlit-scheduler-app</p>
            <p>User ID: {st.session_state.get('user_session_id', 'N/A')}</p>
        </footer>
        """,
        unsafe_allow_html=True
    )

    # Initialize a static session ID for the user footer
    if 'user_session_id' not in st.session_state:
        st.session_state.user_session_id = str(uuid.uuid4())
        
# Execute the main function
if __name__ == "__main__":
    main()
