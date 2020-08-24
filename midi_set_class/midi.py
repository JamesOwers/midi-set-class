"""Functions for handling midi files."""
import logging
from pathlib import Path
from typing import Union

import pandas as pd
import pretty_midi

LOGGER = logging.getLogger(__name__)
PATHLIKE = Union[Path, str]
COLNAMES = ["onset", "track", "pitch", "duration", "velocity"]


def midi_to_df(midi_path: PATHLIKE) -> pd.DataFrame:
    """Get the data from a MIDI file and load it into a pandas DataFrame.

    Parses information from a midi file. The output is a DataFrame with 5 columns:
    * onset: Onset time of the note.
    * track: The track number of the instrument the note is from.
    * pitch: The MIDI pitch number for the note.
    * duration: The duration of the note (offset - onset).
    * velocity: The strength/volume of the note.

    The data is sorted in that order.

    Args:
        midi_path: the path pointing to the midi file to read.

    Returns:
        df : A pandas DataFrame containing the notes parsed from the given MIDI

    """
    midi_path = str(midi_path)
    try:
        midi = pretty_midi.PrettyMIDI(midi_path)
    except Exception as e:
        LOGGER.error(f"Couldn't read MIDI. Got error {e}. Returning None.")
        return None

    notes = []
    for index, instrument in enumerate(midi.instruments):
        for note in instrument.notes:
            notes.append(
                {
                    "onset": note.start,
                    "track": index,
                    "pitch": note.pitch,
                    "duration": note.end - note.start,
                    "velocity": note.velocity,
                }
            )
    if len(notes) == 0:
        LOGGER.warn(f"The MIDI file located at {midi_path} is empty. Returning None.")
        return None
    df = pd.DataFrame(notes)[COLNAMES]
    df = df.sort_values(COLNAMES)
    df = df.reset_index(drop=True)
    return df
