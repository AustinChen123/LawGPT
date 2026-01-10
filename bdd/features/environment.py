import time

def after_scenario(context, scenario):
    """
    Hooks that run after each scenario.
    We add a delay to prevent hitting Gemini API rate limits (429) during testing.
    """
    print(f"\n[INFO] Scenario '{scenario.name}' finished. Sleeping for 60s to reset API quota...")
    time.sleep(60)