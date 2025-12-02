from nicegui import ui

questions = [
    {"question": "Enter monthly travel spending:"},
    {"question": "Enter monthly dining spending:"},
    {"question": "Enter monthly entertainment spending:"},
    {"question": "Enter monthly groceries spending:"},
    {"question": "Enter monthly transit spending:"},
    {"question": "Enter monthly spending in any other categories:"}
]

user_inputs = []

def annual_spend(a, b, c):
    return (a + b + c) * 12

quiz_container = ui.column()

with quiz_container:
    ui.label("Tell us about your spending habits:")
    for q in questions:
        ui.label(q["question"])
        num_input = ui.number()
        user_inputs.append(num_input)
    submit_btn = ui.button("Submit")

def submit_quiz():
    try:
        values = [field.value for field in user_inputs]
    except Exception:
        ui.notify("Enter valid numbers.")
        return
    
    result = annual_spend(*values)
    
    quiz_container.clear()
    
    ui.label(f"Your annual spending: {result}")

submit_btn.on('click', submit_quiz)

ui.run()
