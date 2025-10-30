def analyze_tag_data(raw_data):
    """Processes raw data into dashboard statistics."""

    # 1. Check if data is valid and extract the records list
    if not raw_data or not raw_data[0]:
       return None

    records = raw_data[0]

    # 2. Calculate Current Owner Stats (Most recent record)
    current_owner_data = {}
    if records:
        most_recent = records[0] # Data is already sorted DESC
        current_owner_data = {
            'name': most_recent['name'],
            'date_taken': most_recent['date'],
            'place_earned': most_recent['place']
        }

    # 3. Calculate Summary Stats
    rounds_active = len(records)
    total_strokes = sum(record['score'] for record in records if isinstance(record.get('score'), int))

    summary_data = {
        'rounds_active': rounds_active,
        'total_strokes': total_strokes
    }

    # 4. History (All records are the history)
    # To summarize previous owners, we identify unique holders and their stats.
    history_data = []
    unique_owners = {}

    for i, record in enumerate(records):
        history_data.append({
            'date': record['date'],
            'name': record['name'],
            'place': record['place'],
            'score': record['score'],
            'is_current': i == 0,
            # Simple way to track unique owners for the "History" section
            'is_new_holder': record['name'] not in unique_owners,
        })
        unique_owners[record['name']] = True # Mark as seen

    return {
        'current_owner': current_owner_data,
        'summary': summary_data,
        'history': history_data
    }