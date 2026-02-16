"""
Manually annotated ground truth for evaluation.
These 10 examples use real descriptions from the Netflix dataset.
"""
from src.schemas import ContentMetadata


annotations = [
    {
        "title": "3%",
        "description": "In a future where the elite inhabit an island paradise far from the crowded slums, you get one chance to join the 3% saved from squalor.",
        "expected": ContentMetadata(
            genres=["Sci-Fi", "Drama", "Thriller"],
            themes=["inequality", "survival", "ambition"],
            mood="dark",
            target_audience="adults",
            content_warnings=["violence"]
        )
    },
    {
        "title": "7:19",
        "description": "After a devastating earthquake hits Mexico City, trapped survivors from all walks of life wait to be rescued while trying desperately to stay alive.",
        "expected": ContentMetadata(
            genres=["Drama", "Thriller"],
            themes=["survival", "community", "disaster"],
            mood="tense",
            target_audience="adults",
            content_warnings=["death", "frightening scenes"]
        )
    },
    {
        "title": "23:59",
        "description": "When an army recruit is found dead, his fellow soldiers are forced to confront a terrifying secret that's haunting their jungle island training camp.",
        "expected": ContentMetadata(
            genres=["Horror", "Mystery", "Thriller"],
            themes=["death", "fear", "secrets"],
            mood="eerie",
            target_audience="adults",
            content_warnings=["violence", "death", "frightening scenes"]
        )
    },
    {
        "title": "9",
        "description": "In a postapocalyptic world, rag-doll robots hide in fear from dangerous machines out to exterminate them, until a brave newcomer joins the group.",
        "expected": ContentMetadata(
            genres=["Animation", "Sci-Fi", "Adventure"],
            themes=["survival", "courage", "friendship"],
            mood="dark",
            target_audience="teens",
            content_warnings=["violence", "frightening scenes"]
        )
    },
    {
        "title": "21",
        "description": "A brilliant group of students become card-counting experts with the intent of swindling millions out of Las Vegas casinos by playing blackjack.",
        "expected": ContentMetadata(
            genres=["Drama", "Thriller", "Crime"],
            themes=["ambition", "deception", "risk"],
            mood="thrilling",
            target_audience="adults",
            content_warnings=["gambling"]
        )
    },
    {
        "title": "Altered Minds",
        "description": "A genetics professor experiments with a treatment for his comatose sister that blends medical and shamanic cures, but unlocks a shocking side effect.",
        "expected": ContentMetadata(
            genres=["Sci-Fi", "Drama", "Thriller"],
            themes=["science", "family", "experimentation"],
            mood="suspenseful",
            target_audience="adults",
            content_warnings=["frightening scenes"]
        )
    },
    {
        "title": "Cadaver",
        "description": "After an awful accident, a couple admitted to a grisly hospital are separated and must find each other to escape — before death finds them.",
        "expected": ContentMetadata(
            genres=["Horror", "Thriller"],
            themes=["love", "survival", "death"],
            mood="eerie",
            target_audience="adults",
            content_warnings=["violence", "gore", "frightening scenes"]
        )
    },
    {
        "title": "187",
        "description": "After one of his high school students attacks him, dedicated teacher Trevor Garfield grows weary of the gang warfare in the New York City school system and moves to California to teach there, thinking it must be a less hostile environment.",
        "expected": ContentMetadata(
            genres=["Drama", "Crime"],
            themes=["education", "violence", "perseverance"],
            mood="dramatic",
            target_audience="adults",
            content_warnings=["violence"]
        )
    },
    {
        "title": "Clinical",
        "description": "When a doctor goes missing, his psychiatrist wife treats the bizarre medical condition of a psychic patient, who knows much more than he's leading on.",
        "expected": ContentMetadata(
            genres=["Mystery", "Thriller"],
            themes=["deception", "secrets", "psychology"],
            mood="suspenseful",
            target_audience="adults",
            content_warnings=[]
        )
    },
    {
        "title": "The Haunting",
        "description": "An architect and his wife move into a castle that is slated to become a luxury hotel. But something inside is determined to stop the renovation.",
        "expected": ContentMetadata(
            genres=["Horror", "Mystery"],
            themes=["fear", "supernatural", "isolation"],
            mood="eerie",
            target_audience="adults",
            content_warnings=["frightening scenes"]
        )
    },
]


if __name__ == "__main__":
    print(f"Total annotations: {len(annotations)}")
    for i, item in enumerate(annotations):
        print(f"\n[{i+1}] {item['title']}")
        print(f"    Genres: {item['expected'].genres}")
        print(f"    Themes: {item['expected'].themes}")
        print(f"    Mood: {item['expected'].mood}")
        print(f"    Audience: {item['expected'].target_audience}")
        print(f"    Warnings: {item['expected'].content_warnings}")