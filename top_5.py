import pandas as pd

# =====================================================
# LOAD FILE
# =====================================================

df = pd.read_csv("Week3_Final_Exclusive_Results.csv")

# =====================================================
# FILTER VERY_NEGATIVE TICKETS
# =====================================================

very_negative_df = df[df["sentiment"] == "VERY_NEGATIVE"].copy()

# =====================================================
# KEYWORD DICTIONARIES
# =====================================================

severity_keywords = {
    "data loss": 10,
    "security breach": 10,
    "system outage": 9,
    "crashed": 8,
    "corrupted": 8,
    "cannot access": 8,
    "account locked": 8,
    "payment failed": 7,
    "unusable": 7,
    "critical issue": 7,
}

business_keywords = {
    "team cannot work": 10,
    "business interrupted": 10,
    "production stopped": 10,
    "unable to work": 9,
    "work blocked": 9,
    "customer impact": 8,
}

emotion_keywords = {
    "unacceptable": 5,
    "worst": 5,
    "extremely disappointed": 5,
    "frustrated": 4,
    "angry": 4,
    "urgent": 4,
}

# =====================================================
# SCORING FUNCTION
# =====================================================


def calculate_score(row):

    text = str(row["Cleaned_Description"]).lower()

    explanation = str(row["explanation_of_sentiment"]).lower()

    score = 0

    # =================================================
    # DATA LOSS / RECOVERY
    # =================================================

    if "data loss" in explanation:
        score += 10

    # =================================================
    # LOGIN / ACCESS / ACCOUNT ISSUES
    # =================================================

    if "cannot access" in text or "invalid credentials" in text or "account" in text:
        score += 8

    # =================================================
    # HARDWARE / DEVICE FAILURE
    # =================================================

    if "not turning on" in text or "hardware" in text or "battery" in text:
        score += 7

    # =================================================
    # ESCALATION / FRUSTRATION
    # =================================================

    if "multiple times" in text or "still" in text or "urgent" in text:
        score += 5

    return score


# =====================================================
# APPLY SCORE
# =====================================================

very_negative_df["priority_score"] = very_negative_df.apply(calculate_score, axis=1)

# =====================================================
# SORT AND PICK TOP 5
# =====================================================

top5 = very_negative_df.sort_values(by="priority_score", ascending=False).head(5)

# =====================================================
# DISPLAY RESULTS
# =====================================================

print("\nTOP 5 VERY_NEGATIVE TICKETS\n")

print(top5[["Cleaned_Description", "sentiment", "priority_score"]])

# =====================================================
# SAVE FILE
# =====================================================

top5.to_csv("Top5_Very_Negative_Tickets.csv", index=False)

print("\nTop 5 tickets saved successfully.")
