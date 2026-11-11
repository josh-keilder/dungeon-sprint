def format_run_time(seconds):
    seconds = int(seconds * 100) / 100

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return f"{minutes:02d}:{remaining_seconds:05.2f}"
