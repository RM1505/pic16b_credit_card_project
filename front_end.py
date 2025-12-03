from nicegui import ui
import json

def load_cards(path: str = "clean_cards.json"):
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)
	return data

cards = load_cards()

cards_dialog = ui.dialog()

with cards_dialog:
    with ui.card().classes("w-2/3 mx-auto p-6 mt-4"):
        ui.label("All Credit Cards").classes(
            "text-3xl font-bold text-blue-600 mb-4 text-center"
        )
        ui.label(f"Total cards found: {len(cards)}").classes(
            "text-lg font-medium mb-4"
        )

        with ui.column().classes("gap-2 max-h-[500px] overflow-y-auto"):
            for card in cards:
                ui.label(f"• {card.get('name', 'Unnamed Card')}").classes("text-md")

        ui.button("Close", on_click=cards_dialog.close).classes(
            "mt-4 bg-gray-300 px-4 py-2 rounded-lg"
        )

with ui.row().classes("w-full justify-center mt-8 mb-4"):
    ui.label("Welcome to your Credit Card Optimizer!") \
        .classes("text-5xl font-bold text-green-600")

with ui.row().classes("w-full justify-center mt-8 mb-4"):
    ui.label("We help you choose the best credit card for you.") \
        .classes("text-3xl font-bold text-green-500")

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

with ui.row().classes("w-full justify-center mt-6"):
    ui.button("View All Credit Cards", on_click=cards_dialog.open) \
        .classes("bg-blue-600 text-white px-6 py-3 rounded-lg text-lg hover:bg-blue-700")

ui.run()
