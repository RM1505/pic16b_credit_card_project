from nicegui import ui
import json
import import_ipynb
from solver import get_dicts, optimize_cardspace
import pandas as pd

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

category_keys = [
    "Travel",
    "Groceries & Dining",
    "Gas & Utilities",
    "Retail & Entertainment",
    "All Purchases"
]

questions = [f"Monthly spend on {cat}" for cat in category_keys]

df= pd.read_json("cards_w_score.json")


with ui.card().classes("w-1/2 mx-auto mt-10 p-6"):
    ui.label("Tell us about your spending habits:").classes("text-2xl font-bold mb-4")

    inputs = {
        "Travel": 0,
        "Groceries & Dining": 0,
        "Gas & Utilities": 0,
        "Retail & Entertainment": 0,
        "All Purchases": 0
    }

    with ui.column().classes("gap-3"):
        for i in range(len(questions)):
            with ui.row().classes("items-center gap-4"):
                ui.label(questions[i] + ":").classes("w-56")
                num = ui.number(min=0, format='%.2f').classes("w-40")
                inputs[category_keys[i]] = num
        ui.label("Which best describes your credit score?")
        dropdown = ui.select(
            options=["Excellent", "Very Good", "Good", "Fair", "Poor"],
            value=None,                
            with_input=False           
        )

    result_html = ui.html("", sanitize=None).classes("text-xl font-medium mt-5 text-green-600")

    def submit():
        try:
            solver_inputs = {}
            for key, element in inputs.items():
                solver_inputs[key] = float(element.value or 0.0)
        except ValueError:
            ui.notify("Please enter valid numbers.", color="red")
            return
        
        realistic_cards = df[df["score"] == dropdown.value]
        dict_cards, fees= get_dicts(realistic_cards)

        chosen, total, held, breakdown = optimize_cardspace(dict_cards, fees, solver_inputs, 800)
        #result_label.set_text(f"Your estimated annual spending: ${chosen:,.2f}")
        output_lines = [f"Your optimal wallet is:"]
        elements_used = []
        for key, element in chosen.items():
            if element not in elements_used:
                elements_used.append(element)
                output_lines.append(f"• {element} ")
        output_lines.append(f"Estimated annual rewards: ${total:,.2f}")
        html_content = "<br>".join(output_lines)
        result_html.set_content(html_content)

    ui.button("Calculate Annual Spending", on_click=submit).classes("mt-4")

with ui.row().classes("w-full justify-center mt-6"):
    ui.button("View All Credit Cards", on_click=cards_dialog.open) \
        .classes("bg-blue-600 text-white px-6 py-3 rounded-lg text-lg hover:bg-blue-700")

ui.run()
