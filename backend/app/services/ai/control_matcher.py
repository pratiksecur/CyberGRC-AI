from difflib import SequenceMatcher

from app.models.control import Control


def match_control(
    control_name: str,
    controls: list[Control],
):
    """
    Match an AI-recommended control to an
    existing control in the database.
    """

    best_match = None
    best_score = 0.0

    for control in controls:

        score = SequenceMatcher(
            None,
            control_name.lower(),
            control.title.lower(),
        ).ratio()

        if score > best_score:
            best_score = score
            best_match = control

    return best_match, best_score