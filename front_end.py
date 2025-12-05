from nicegui import ui
import json
from solver import get_dicts, optimize_cardspace
import pandas as pd

def load_cards(path: str = "cards_w_score.json"):
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)
	return data

cards = load_cards()

# Group cards by issuer for sleeeker display
cards_by_issuer = {}
for card in cards:
    issuer = card.get("issuer")
    cards_by_issuer.setdefault(issuer, []).append(card)

cards_dialog = ui.dialog()

with cards_dialog:
    with ui.card().classes("w-2/3 mx-auto p-6 mt-4"):
        ui.label("All Credit Cards").classes(
            "text-3xl font-bold text-emerald-400 mb-4 text-center"
        )
        ui.label(f"Total cards found: {len(cards)}").classes(
            "text-lg font-medium mb-4"
        )

        with ui.column().classes("gap-3 max-h-[500px] overflow-y-auto w-full"):
            # Sort issuers alphabetically
            for issuer in sorted(cards_by_issuer.keys()):
                ui.label(issuer).classes("text-xl font-semibold mt-2 mb-1 text-left")

                for card in cards_by_issuer[issuer]:
                    card_name = card.get("name")

                    # Expansion shows issuer and rewards bullets when clicked
                    with ui.expansion(card_name).classes("w-full"):
                        ui.label(f"Issuer: {issuer}").classes("font-medium mb-2")

                        annual_fee = card.get("annual_fee")
                        score = card.get("score")

                        ui.label(f"Annual fee: {annual_fee}").classes("text-sm")
                        ui.label(f"Typical credit score: {score}").classes("text-sm mb-2")

                        rewards = card.get("rewards") or card.get("clean_rewards")

                        # Rewards as bullet points
                        ui.label("Rewards:").classes("font-medium mb-1")

                        with ui.column().classes("pl-4 gap-1"):
                            if isinstance(rewards, list):
                                if rewards and isinstance(rewards[0], str):
                                    for r in rewards:
                                        ui.label(f"• {r}").classes("text-sm")
                                else:
                                    ui.label("• No rewards information available.").classes("text-sm italic")
									
        ui.button("Close", on_click=cards_dialog.close).classes(
            "mt-4 bg-gray-300 px-4 py-2 rounded-lg"
        )

with ui.column().classes(
    "min-h-screen w-full items-center bg-black text-black"
):

    ui.space()

    with ui.column().classes("items-center text-center px-4"):
        ui.label("Welcome to your Credit Card Optimizer!").classes(
            "text-6xl font-extrabold tracking-tight text-emerald-400 drop-shadow-lg mb-3"
        )
        ui.label(
            "We help choose the best credit card for you. Turn your spending into maximum rewards.").classes(
            "text-3xl md:text-3xl font-semibold text-green-500 max-w-2xl leading-snug"
        )
		        ui.label("How it works:").classes(
                    "mt-6 mb-2 text-3xl font-bold text-emerald-400 underline underline-offset-4"
        )
        ui.markdown("""
            1. We take your monthly spending and estimate yearly totals.<br>
            2. We filter cards by your credit score range.<br>
            3. Our solver picks the combination of cards that maximizes your estimated rewards, subject to constraints.<br>
            """
        ).classes("text-2xl font-semibold text-green-300 font-medium max-w-2xl leading-relaxed text-left")

        with ui.row().classes("mt-4 gap-3"):
            ui.button("Browse Credit Cards", on_click=cards_dialog.open).classes(
                "bg-emerald-500 hover:bg-emerald-600 text-white font-semibold "
                "px-4 py-2 rounded-full text-sm md:text-base shadow-lg shadow-emerald-900/50"
            )
            ui.label("💳").classes("text-3xl md:text-4xl")

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
            output_lines.append(f"Estimated Annual Rewards: ${total:,.2f}")
            html_content = "<br>".join(output_lines)
            result_html.set_content(html_content)

        ui.button("Calculate Annual Rewards", on_click=submit).classes("mt-4")

ui.run()
