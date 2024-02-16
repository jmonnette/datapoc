def calculate_score(age):
    if age < 22:
        return 500
    elif age >= 22 and age <= 30:
        return 650
    elif age > 30 and age <= 40:
        return 750
    else:
        return 820
