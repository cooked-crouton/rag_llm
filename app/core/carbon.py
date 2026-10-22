from codecarbon import EmissionsTracker
import logging

logger = logging.getLogger(__name__)

def track_emissions(project_name: str = "recipe_generation"):
    """
    Décorateur ou context manager pour mesurer les émissions carbone.
    """
    tracker = EmissionsTracker(
        project_name=project_name,
        measure_power_secs=15,
        save_to_file=True,
        output_file="emissions.csv"
    )
    return tracker