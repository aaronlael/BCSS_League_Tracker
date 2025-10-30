from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def fuzzy_sort_names(data: dict) -> dict:
    participants = data["participants"]
    scraped_data = data["scraped_data"]

    participant_names = [p["name"] for p in participants]

    sorted_participants = []
    processed_participant_ids = set()

    for scraped_item in scraped_data:
        scraped_name = scraped_item["name"]
        best_match_name, score = process.extractOne(scraped_name, participant_names, scorer=fuzz.token_sort_ratio)

        if score >= 70:
            for participant in participants:
                if participant["name"] == best_match_name and participant["id"] not in processed_participant_ids:
                    sorted_participants.append(participant)
                    processed_participant_ids.add(participant["id"])
                    break

    for participant in participants:
        if participant["id"] not in processed_participant_ids:
            sorted_participants.append(participant)

    data["participants"] = sorted_participants
    return data