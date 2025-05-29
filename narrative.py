# narrative.py – Narrative Classification Engine

def classify_narrative(symbol: str, name: str) -> str:
    """
    Classify the meme narrative of a token based on its symbol or name.
    """
    tag = symbol.lower() + " " + name.lower()

    if any(x in tag for x in ["elon", "musk", "tesla"]):
        return "🚀 Elon-themed"
    elif any(x in tag for x in ["dog", "shib", "inu", "puppy", "woof"]):
        return "🐶 Dog-themed"
    elif any(x in tag for x in ["cat", "meow", "kitty"]):
        return "🐱 Cat-themed"
    elif any(x in tag for x in ["pepe", "frog"]):
        return "🐸 Pepe/Frog"
    elif any(x in tag for x in ["wizard", "magic", "spell"]):
        return "🧙 Wizard/Fantasy"
    elif any(x in tag for x in ["baby", "kid", "child"]):
        return "🍼 Baby-themed"
    elif any(x in tag for x in ["milady", "waifu", "anime"]):
        return "🌸 Anime/Milady"
    elif any(x in tag for x in ["trump", "maga", "biden"]):
        return "🇺🇸 Political"
    elif any(x in tag for x in ["ghost", "spirit", "phantom"]):
        return "👻 Ghost/Spooky"
    elif any(x in tag for x in ["cow", "bull", "moo"]):
        return "🐄 Animal Farm"
    elif any(x in tag for x in ["moon", "astro", "space"]):
        return "🌕 Space/Moon"
    elif any(x in tag for x in ["max", "mad", "rage"]):
        return "🔥 Angry Meme"
    else:
        return "🧩 Misc/Unknown"
