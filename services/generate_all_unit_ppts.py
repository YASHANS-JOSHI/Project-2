from services.unit_ppt_generator import (
    generate_unit_presentation
)

ppt_files = {}

units_data = st.session_state.units_data

for unit_name, topics in units_data.items():

    ppt_path = generate_unit_presentation(
        unit_name,
        topics
    )

    ppt_files[unit_name] = ppt_path

st.session_state.ppt_files = ppt_files