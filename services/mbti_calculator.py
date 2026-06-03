def calculate_mbti(scores):
    """
    scores = {"EI": 3, "SN": -1, "TF": 5, "JP": -2}
    برمیگردونه: "ENTJ"
    """
    mbti = ""
    mbti += "E" if scores.get("EI", 0) > 0 else "I"
    mbti += "S" if scores.get("SN", 0) > 0 else "N"
    mbti += "T" if scores.get("TF", 0) > 0 else "F"
    mbti += "J" if scores.get("JP", 0) > 0 else "P"
    return mbti