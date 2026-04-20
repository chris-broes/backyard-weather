def calculate_risk_score(temperature, humidity, wind_speed):
    score = 0
    
    # Temperature risk scoring
    if temperature < 0:
        score += 3
    elif 0 <= temperature < 10:
        score += 2
    elif 10 <= temperature < 20:
        score += 1
    
    # Humidity risk scoring
    if humidity > 80:
        score += 3
    elif 60 < humidity <= 80:
        score += 2
    elif 40 < humidity <= 60:
        score += 1
    
    # Wind speed risk scoring
    if wind_speed > 20:
        score += 3
    elif 10 < wind_speed <= 20:
        score += 2
    elif wind_speed <= 10:
        score += 1
    
    return score