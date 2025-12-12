import pytest
import pandas as pd
from final_parser import Parsing

# clean_text tests

def test_clean_text_removes_explanations():
    parser = Parsing(pd.DataFrame())
    text = "Earn 5% back. For example, you'll get rewards fast. APR is 20%."
    cleaned = parser.clean_text(text)
    assert "For example" not in cleaned
    assert "you'll get" not in cleaned
    assert "APR" not in cleaned
    assert "Earn 5% back." in cleaned

def test_clean_text_handles_list():
    parser = Parsing(pd.DataFrame())
    text = ["Earn 3% back.", "This means you save money."]
    cleaned = parser.clean_text(text)
    assert "This means" not in cleaned
    assert "Earn 3% back." in cleaned


# reward_type tests

def test_reward_type_detects_time_triggers():
    parser = Parsing(pd.DataFrame())
    text = "Earn extra rewards after 12 months."
    triggers, timing = parser.reward_type(text)
    assert "after" in triggers
    assert timing["after"][0]["number"] == 12
    assert timing["after"][0]["unit"] == "months"

def test_reward_type_ignores_year_values():
    parser = Parsing(pd.DataFrame())
    text = "Bonus starts after 2024 year."
    triggers, timing = parser.reward_type(text)
    assert timing == {}  # year ignored for being unrealistic


# annual_fee_parse tests

def test_annual_fee_single_value():
    parser = Parsing(pd.DataFrame())
    assert parser.annual_fee_parse("$95") == 95.0

def test_annual_fee_range():
    parser = Parsing(pd.DataFrame())
    fee = parser.annual_fee_parse("$0 - $95")
    assert fee == 47.5

def test_annual_fee_with_zero_prefix():
    parser = Parsing(pd.DataFrame())
    fee = parser.annual_fee_parse("0-95")
    assert fee == 47.5


# extract_rate_data tests

def test_extract_rate_percent():
    parser = Parsing(pd.DataFrame())
    import re
    match = re.search(r"(\$)?(\d+)(\$)?(\d+)?(%)", "Earn 5% back")
    data = parser.extract_rate_data(match)
    assert data["rate"] == 5
    assert data["unit"] == "percent"


# reward_specification tests

def test_reward_specification_basic():
    parser = Parsing(pd.DataFrame())
    rewards = parser.reward_specification("Earn 3% on dining purchases.")
    assert len(rewards) == 1
    assert rewards[0]["category"] == "dining"
    assert rewards[0]["rate"] == 3
    assert rewards[0]["unit"] == "percent"

def test_reward_specification_excludes_time_numbers():
    parser = Parsing(pd.DataFrame())
    rewards = parser.reward_specification("Earn 5 points after 12 months.")
    assert rewards == []  # 5 points belongs to time trigger context and gets excluded


# CleanParsedData tests

def test_clean_parsed_data_filters_unrealistic():
    df = pd.DataFrame({
        "structured_rewards": [[
            {"rate": 50000, "unit": "percent"},   # unrealistic
            {"rate": 5, "unit": "percent"}        # valid
        ]]
    })

    parser = Parsing(df)
    cleaned = parser.CleanParsedData(df)

    assert len(cleaned.loc[0, "structured_rewards"]) == 1
    assert cleaned.loc[0, "structured_rewards"][0]["rate"] == 5

# NewDataFrame tests

def test_new_dataframe_creates_columns():
    df = pd.DataFrame({
        "rewards": ["Earn 3% on dining."],
        "annual_fee": ["$95"]
    })

    parser = Parsing(df)
    new_df = parser.NewDataFrame()

    assert "structured_rewards" in new_df.columns
    assert "timing_triggers" in new_df.columns
    assert new_df.loc[0, "annual_fee"] == 95.0
    assert len(new_df.loc[0, "structured_rewards"]) == 1

