from nicegui import ui

with ui.row().classes("w-full justify-center mt-8 mb-4"):
    ui.label("Welcome to your Credit Card Optimizer!") \
        .classes("text-5xl font-bold text-green-600")

questions = [
    "Monthly travel spending",
    "Monthly dining spending",
    "Monthly entertainment spending",
    "Monthly groceries spending",
    "Monthly transit spending",
    "Monthly spending (other categories)",
]

def annual_spend(values):
    return sum(values) * 12


with ui.card().classes("w-1/2 mx-auto mt-10 p-6"):
    ui.label("Tell us about your spending habits:").classes("text-2xl font-bold mb-4")

    inputs = []
    with ui.column().classes("gap-3"):
        for q in questions:
            with ui.row().classes("items-center gap-4"):
                ui.label(q + ":").classes("w-56")
                num = ui.number(min=0, format='%.2f').classes("w-40")
                inputs.append(num)

    result_label = ui.label("").classes("text-xl font-medium mt-5 text-green-600")

    def submit():
        try:
            values = [float(i.value or 0) for i in inputs]
        except ValueError:
            ui.notify("Please enter valid numbers.", color="red")
            return
        
        total = annual_spend(values)
        result_label.set_text(f"Your estimated annual spending: ${total:,.2f}")

    ui.button("Calculate Annual Spending", on_click=submit).classes("mt-4")


ui.run()
