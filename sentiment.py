# sentiment.py – Meme Sentiment Scoring Module

def analyze_token_sentiment():
    # Placeholder scoring logic – replace with NLP or social signal data
    sentiments = [
        ("$OPTIDOG", "🔥 High Hype – Strong community buzz"),
        ("$FISH", "⚠️ Mixed – Buzz growing but with volatility"),
        ("$WENLAMBO", "🧊 Cooling – Hype dropping off"),
    ]

    message = "<b>📈 Meme Sentiment Scores</b>\n\n"
    for token, score in sentiments:
        message += f"{token}: {score}\n"

    return message.strip()
