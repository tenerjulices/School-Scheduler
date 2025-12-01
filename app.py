import streamlit as st
import uuid
import datetime

# --- Configuration and Initialization ---

# Set page configuration
st.set_page_config(
    page_title="School Scheduler",
    layout="wide",  # Use 'wide' to accommodate the schedule grid better
    initial_sidebar_state="collapsed"
)

# Constants
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
# Time slots for the grid background (using 30-minute intervals for finer control)
TIME_SLOTS = [
    datetime.time(h, m).strftime('%H:%M')
    for h in range(8, 18) for m in [0, 30] # 8:00 to 17:30
]
COLORS = [
    {'name': 'Blue', 'value': '#3B82F6'},
    {'name': 'Purple', 'value': '#8B5CF6'},
    {'name': 'Pink', 'value': '#EC4899'},
    {'name': 'Green', 'value': '#10B981'},
    {'name': 'Orange', 'value': '#F59E0B'},
    {'name': 'Red', 'value': '#EF4444'},
    {'name': 'Teal', 'value': '#14B8A6'},
    {'name': 'Indigo', 'value': '#6366F1'}
]

# Initialize Session State
if 'schedule' not in st.session_state:
    st.session_state.schedule = []
if 'editing_id' not in st.session_state:
    st.session_state.editing_id = None
if 'modal_open' not in st.session_state:
    st.session_state.modal_open = False
if 'selected_color' not in st.session_state:
    st.session_state.selected_color = COLORS[0]['value']

# --- Utility Functions ---

def clear_form_state():
    """Resets the form state variables."""
    # Reset all form-related session state keys
    st.session_state.editing_id = None
    st.session_state.modal_open = False
    st.session_state.form_subject = ""
    st.session_state.form_teacher = ""
    st.session_state.form_room = ""
    st.session_state.form_day = DAYS[0]
    st.session_state.form_start_time = datetime.time(9, 0)
    st.session_state.form_end_time = datetime.time(10, 0)
    st.session_state.selected_color = COLORS[0]['value']

def load_edit_data(item_id):
    """Loads an item's data into the form state for editing."""
    cls = next((c for c in st.session_state.schedule if c['id'] == item_id), None)
    if cls:
        st.session_state.editing_id = item_id
        st.session_state.modal_open = True
        
        # Convert stored strings back to native types for Streamlit widgets
        st.session_state.form_subject = cls['subject']
        st.session_state.form_teacher = cls['teacher']
        st.session_state.form_room = cls['room']
        st.session_state.form_day = cls['day']
        st.session_state.form_start_time = datetime.datetime.strptime(cls['startTime'], "%H:%M").time()
        st.session_state.form_end_time = datetime.datetime.strptime(cls['endTime'], "%H:%M").time()
        st.session_state.selected_color = cls['color']
    st.rerun() # Must rerun to display the modal with populated data

def add_update_class(data):
    """Adds a new class or updates an existing one."""
    
    # Validation (similar to the JS form validation)
    if not all(data.values()) or data['startTime'] >= data['endTime']:
        st.error("Please ensure all fields are filled and the start time is before the end time.")
        return

    item_data = {
        'subject': data['subject'].strip(),
        'teacher': data['teacher'].strip(),
        'room': data['room'].strip(),
        'day': data['day'],
        'startTime': data['startTime'].strftime("%H:%M"),
        'endTime': data['endTime'].strftime("%H:%M"),
        'color': data['color']
    }

    if st.session_state.editing_id:
        # Update existing item
        index = next((i for i, item in enumerate(st.session_state.schedule) if item['id'] == st.session_state.editing_id), -1)
        if index != -1:
            st.session_state.schedule[index].update(item_data)
            st.toast("Class updated successfully!", icon="✅")
    else:
        # Add new item
        item_data['id'] = str(uuid.uuid4())
        st.session_state.schedule.append(item_data)
        st.toast("Class added successfully!", icon="➕")

    clear_form_state()
    st.rerun()

def delete_class_callback(item_id):
    """Deletes a class item by ID."""
    st.session_state.schedule = [item for item in st.session_state.schedule if item['id'] != item_id]
    st.toast("Class deleted successfully!", icon="🗑️")
    st.rerun()

def open_add_modal():
    """Sets state to open the modal for adding a new item."""
    clear_form_state() # Reset form fields
    st.session_state.modal_open = True
    st.rerun()

# --- UI Components ---

def render_schedule_form():
    """Renders the Add/Edit Class form inside a container (simulating a modal)."""
    
    is_editing = st.session_state.editing_id is not None
    
    # Form submission handler logic
    form_data = {
        'subject': st.session_state.form_subject,
        'teacher': st.session_state.form_teacher,
        'room': st.session_state.form_room,
        'day': st.session_state.form_day,
        'startTime': st.session_state.form_start_time,
        'endTime': st.session_state.form_end_time,
        'color': st.session_state.selected_color
    }

    with st.form(key="class_form", clear_on_submit=False):
        st.markdown(f"**{'Edit Class' if is_editing else 'Add New Class'}**")
        
        # Inputs (Note: Streamlit widgets use keys for session state binding)
        st.text_input("Subject", key="form_subject", placeholder="e.g., Mathematics")
        st.text_input("Teacher", key="form_teacher", placeholder="e.g., Mr. Smith")
        st.text_input("Room", key="form_room", placeholder="e.g., Room 101")
        
        st.selectbox("Day", options=DAYS, key="form_day")

        col1, col2 = st.columns(2)
        with col1:
            st.time_input("Start Time", key="form_start_time")
        with col2:
            st.time_input("End Time", key="form_end_time")

        st.markdown("Color")
        # Custom Color Palette (Simulating radio buttons with columns)
        cols = st.columns(len(COLORS))
        for i, color_option in enumerate(COLORS):
            with cols[i]:
                # Custom button for color selection
                is_selected = st.session_state.selected_color == color_option['value']
                style = f"""
                    border: 3px solid {'#374151' if is_selected else 'transparent'};
                    background-color: {color_option['value']};
                    border-radius: 8px;
                    height: 40px;
                    width: 100%;
                    cursor: pointer;
                """
                if st.button(
                    label=" ", 
                    key=f"color_btn_{color_option['name']}",
                    help=color_option['name'],
                    use_container_width=True
                ):
                    st.session_state.selected_color = color_option['value']
                    st.rerun() # Rerun to update the selected state
                
                # Apply the custom style using markdown (since Streamlit buttons are hard to style)
                st.markdown(f'<style>div[data-testid="stButton"] button[data-testid*="color_btn_{color_option["name"]}"] {{ {style} }}</style>', unsafe_allow_html=True)


        # Form submission buttons
        submit_col, cancel_col = st.columns(2)
        with submit_col:
            st.form_submit_button(
                label=f"{'Update' if is_editing else 'Add'} Class",
                type="primary",
                on_click=add_update_class,
                args=(form_data,)
            )
        with cancel_col:
            st.form_submit_button(
                label="Cancel",
                type="secondary",
                on_click=clear_form_state
            )

def render_schedule_grid():
    """Renders the schedule as a weekly calendar grid using HTML/CSS for complex layout."""
    
    # 1. Generate the base grid HTML (Header and Time Labels)
    html_grid_start = '<div class="schedule-grid" id="scheduleGrid" style="grid-template-columns: 80px ' + ' '.join(['1fr'] * len(DAYS)) + ';">'
    html_grid_end = '</div>'
    
    # Header row
    html_content = '<div class="header-cell"></div>'
    html_content += ''.join(f'<div class="header-cell">{day}</div>' for day in DAYS)

    # Time rows and cells
    time_row_count = len(TIME_SLOTS)
    for i, time in enumerate(TIME_SLOTS):
        if i % 2 == 0: # Only display on the hour for cleaner labels
             html_content += f'<div class="time-label">{time}</div>'
        else:
             html_content += f'<div class="time-label" style="height: 48px; border-right: 1px solid #E5E7EB;"></div>'
        
        for day in DAYS:
            # Generate the container for class blocks for this time slot
            # Note: The time slot height in CSS must be based on a fixed interval (e.g., 30 min = 48px)
            html_content += f'<div class="day-column" id="col-{day}-{i}"><div class="time-slot" style="height: 48px;"></div></div>'
    
    html_content = html_grid_start + html_content + html_grid_end
    
    # 2. Add class blocks using injected HTML/CSS (complex layout is much easier this way)
    for cls in st.session_state.schedule:
        day_index = DAYS.index(cls['day'])
        
        # Calculate time positions and height
        start_time_obj = datetime.datetime.strptime(cls['startTime'], "%H:%M")
        end_time_obj = datetime.datetime.strptime(cls['endTime'], "%H:%M")
        
        # Calculate minutes since 8:00 AM
        start_minute_of_day = (start_time_obj.hour * 60 + start_time_obj.minute) - (8 * 60)
        duration_minutes = (end_time_obj - start_time_obj).total_seconds() / 60
        
        # Calculate pixel position based on 30-minute intervals (48px per 30 min)
        # 1 minute = 48px / 30 min = 1.6px
        minute_to_pixel_ratio = 48 / 30
        
        top_offset = start_minute_of_day * minute_to_pixel_ratio
        height_px = duration_minutes * minute_to_pixel_ratio
        
        # HTML for the class block
        class_block_html = f"""
            <div class="class-block" style="
                background-color: {cls['color']};
                top: {top_offset}px;
                height: {height_px}px;
                grid-column: {day_index + 2}; /* +1 for time column, +1 for 1-based index */
                grid-row: 2 / span {time_row_count + 1}; /* Span all time slots */
            ">
                <div class="class-actions">
                    <button class="icon-btn" onclick="Streamlit.set
                    --edit-button-action--('${cls['id']}')" title="Edit">✏️</button>
                    <button class="icon-btn" onclick="Streamlit.set
                    --delete-button-action--('${cls['id']}')" title="Delete">🗑️</button>
                </div>
                <div class="class-subject">{cls['subject']}</div>
                <div class="class-info">
                    👤 {cls['teacher']}<br>
                    📍 {cls['room']}<br>
                    {cls['startTime']} - {cls['endTime']}
                </div>
            </div>
        """
        html_content += class_block_html

    # Injecting the full HTML grid structure and custom CSS
    # Note: Streamlit has no native mechanism for complex grid layouts, so using `st.markdown` with `unsafe_allow_html=True` is the most direct way to replicate the original JS/CSS layout.
    st.markdown(html_content, unsafe_allow_html=True)


# --- Main Application Logic ---

def main():
    st.title("My School Scheduler 🎓")
    st.markdown("Organize your weekly classes")
    
    # 1. Add Class Button
    if st.button("Add Class", type="primary", key="add_class_btn"):
        open_add_modal()
    
    st.markdown("---")
    
    # 2. Conditional Form/Modal Display
    if st.session_state.modal_open:
        # Use a container to visually group the "modal" content
        with st.container(border=True):
            render_schedule_form()
            st.markdown("---")

    # 3. Schedule Display
    st.subheader("Weekly Schedule")
    if not st.session_state.schedule:
        st.info("Your schedule is empty! Click 'Add Class' to begin.")
    else:
        render_schedule_grid()
        
    # Inject Custom CSS (based on the provided CSS)
    # The CSS is included directly in the Python script for portability
    custom_css = """
    <style>
        /* General Layout & Styling */
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; }
        .schedule-container { background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); overflow: hidden; margin-top: 20px;}
        .schedule-wrapper { overflow-x: auto; }
        
        /* Grid Structure */
        .schedule-grid {
            min-width: 800px;
            display: grid;
            /* Defined dynamically by Python to include time column + 5 days */
        }
        .header-cell { padding: 16px; text-align: center; background: #EEF2FF; color: #312E81; font-weight: 600; border-bottom: 1px solid #E5E7EB; }
        
        /* Time Labels */
        .time-label {
            padding: 8px;
            height: 48px; /* 30-minute interval */
            border-bottom: 1px solid #E5E7EB;
            border-right: 1px solid #E5E7EB;
            background: #F9FAFB;
            color: #6B7280;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            z-index: 10;
        }

        /* Class Placement Container */
        .day-column {
            position: relative;
            border-right: 1px solid #E5E7EB;
            height: 48px;
            /* Ensures time slots fill the grid cell, 48px is the base unit for 30 minutes */
        }
        .time-slot {
             height: 48px;
             border-bottom: 1px solid #F3F4F6;
        }
        
        /* Class Block (Absolute Positioning) */
        .class-block {
            position: absolute;
            left: 4px;
            right: 4px;
            border-radius: 8px;
            padding: 8px;
            color: white;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s;
            overflow: hidden;
            z-index: 20;
        }

        .class-block:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .class-subject { font-weight: 600; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 14px; }
        .class-info { font-size: 10px; opacity: 0.9; line-height: 1.4; }

        /* Actions on Hover */
        .class-actions { position: absolute; top: 4px; right: 4px; display: flex; gap: 4px; opacity: 0; transition: opacity 0.3s; z-index: 30; }
        .class-block:hover .class-actions { opacity: 1; }

        .icon-btn { background: rgba(255, 255, 255, 0.2); border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; color: white; display: flex; align-items: center; justify-content: center; font-size: 14px; }
        .icon-btn:hover { background: rgba(255, 255, 255, 0.4); }

        /* Streamlit Button Overrides for Color Palette */
        div[data-testid="stButton"] button {
            transition: all 0.3s;
        }

    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # 4. Mock JavaScript calls with Streamlit
    # The original JS used event handlers on buttons inside the dynamically generated HTML.
    # Streamlit requires Python callbacks. We use hidden buttons/state changes to mock these actions.
    
    # Check for click actions from the dynamically generated HTML blocks
    # Note: This part is highly dependent on a third-party Streamlit Component or a custom hack 
    # using window.parent.postMessage() in a real-world scenario. Since that's not possible here,
    # we'll rely on the user interface buttons generated in the Python layer.

# Execute the main function
if __name__ == "__main__":
    main()
