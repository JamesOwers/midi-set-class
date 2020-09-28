"""Functions and classes pertaining to musical notation.

Notes have attributes:
* a pitch
* a duration
* a loudness (which we call velocity)

We use the following definitions for defining pitch:
* Scientific notation gives each pitch a letter (optionally an accidental), and a number
    * the pitch C4 is middle C
    * The sequence runs C through to B, i.e. the number increments when we get to the
        next C, so an example sequence of adjacent pitches:
        * ..., A4, A#4/Bb4, B4, C5, C#5/Db5, D5, ...
* Midipitch denotes pitch with a float
    * midipitch 69 is defined as A4 i.e. concert A
* The frequency of concert A, (A4, or midipitch 69) is 440Hz by default
* Pitch-class is an integer value from 0 to 11 with 0=C, 1=C#/Bb, ..., 10=A#/Bb, 11=B

We use the following conventions for duration/time in general:
* if a duration is represented with numbers of the order 1, it is assumed to be measured
    in quavers
    * a quaver is otherwise known as an eigth note - it spans 1/8 of a 4/4 bar
    * to convert these numbers to seconds, you must divide by the tempo of the piece
        in beats per T, where T is the time measure desired e.g. millisecond
* if a duration is represented with numbers of the order 1000 it is assumed to be
    measured in milliseconds

For reference:
* a standard Piano goes from midipitch 21 (A0, or 27.5 Hz) to midipitch 108 (C8, or 4186
    Hz).
* midipitch 0 is C-1 (i.e. octave -1)
* middle C is C4, which is midipitch 60
* an octave is the distance between a pitch and 12 above, e.g. C4 and C5
* there are 12 semitones in an octave
* a tone is 2 semitones
* increasing a pitch by an octave doubles its sinusoidal frequency
"""
import logging
import re
from typing import List, Optional, Union

import numpy as np

from midi_set_class.utils import log_and_raise

LOGGER = logging.getLogger(__name__)
A4_MIDIPITCH = 69
A4_FREQ = 440
MAX_NR_ACCIDENTALS = 3

PITCH_CHARACTERS = "CDEFGAB"
WHITE_KEYS_PITCHCLASS = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
BLACK_KEYS_PITCHCLASS = [1, 3, 6, 8, 10]  # C#/Db, D#/Eb, F#/Gb, G#/Ab, A#/Bb

STR_TO_PITCHCLASS = dict(zip(PITCH_CHARACTERS, WHITE_KEYS_PITCHCLASS))
NR_ACC_AND_PITCHCLASS_TO_STR = {
    nr_acc: {"sharp": {}, "flat": {}} for nr_acc in range(1, MAX_NR_ACCIDENTALS + 1)
}
for chr in PITCH_CHARACTERS:
    for nr_acc in range(1, MAX_NR_ACCIDENTALS + 1):
        # sharps
        pitch_str = f"{chr}{nr_acc*'#'}"
        pitchclass = (STR_TO_PITCHCLASS[chr] + nr_acc) % 12
        STR_TO_PITCHCLASS[pitch_str] = pitchclass
        NR_ACC_AND_PITCHCLASS_TO_STR[nr_acc]["sharp"][pitchclass] = chr
        # flats
        pitch_str = f"{chr}{nr_acc*'b'}"
        pitchclass = (STR_TO_PITCHCLASS[chr] - nr_acc) % 12
        STR_TO_PITCHCLASS[pitch_str] = pitchclass
        NR_ACC_AND_PITCHCLASS_TO_STR[nr_acc]["flat"][pitchclass] = chr

ACCIDENTAL_MATCH_STR = f"b{{0,{MAX_NR_ACCIDENTALS}}}|#{{0,{MAX_NR_ACCIDENTALS}}}"
SCIENTIFIC_PATTERN = re.compile(
    f"^([{PITCH_CHARACTERS}])({ACCIDENTAL_MATCH_STR})(-?[0-9]+)$"
)

ABC_SHARP_CHR = "^"
ABC_FLAT_CHR = "_"
ABC_NAT_CHR = "="
ABC_ACCIDENTAL_STR = (
    fr"\{ABC_SHARP_CHR}{{0,{MAX_NR_ACCIDENTALS}}}|"
    fr"{ABC_FLAT_CHR}{{0,{MAX_NR_ACCIDENTALS}}}|"
    fr"{ABC_NAT_CHR}{{0,{MAX_NR_ACCIDENTALS}}}"
)
ABC_LETTER_CHR = r"[A-Ga-g]"
ABC_OCT_UP = "'"
ABC_OCT_DOWN = ","
ABC_MAX_OCTAVES = 8
ABC_OCTAVE_STR = (
    fr"{ABC_OCT_UP}{{0,{ABC_MAX_OCTAVES}}}|\{ABC_OCT_DOWN}{{0,{ABC_MAX_OCTAVES}}}"
)
ABC_PITCH_MATCH_STR = f"^({ABC_ACCIDENTAL_STR})({ABC_LETTER_CHR})({ABC_OCTAVE_STR})$"
ABC_PATTERN = re.compile(ABC_PITCH_MATCH_STR)
ABC_PITCH_CHR_TO_SCIENTIFIC = {
    "C": "C4",
    "D": "D4",
    "E": "E4",
    "F": "F4",
    "G": "G4",
    "A": "A4",
    "B": "B4",
    "c": "C5",
    "d": "D5",
    "e": "E5",
    "f": "F5",
    "g": "G5",
    "a": "A5",
    "b": "B5",
}


def midipitch_to_freq(midipitch: float) -> float:
    """Converts midipitches to frequencies (in Hertz).

    Args:
        midipitch: the midipitch value to convert to frequency.

    Returns:
        freq: the frequency value of the supplied midipitch.
    """
    freq = 2 ** ((midipitch - A4_MIDIPITCH) / 12) * A4_FREQ
    return freq


def freq_to_midipitch(freq: float) -> float:
    """Converts frequencies (in Hertz) to midipitches.

    Args:
        freq: the frequency value in Hertz to convert to midipitch.

    Returns:
        midipitch: the midipitch value of the supplied frequency.
    """
    midipitch = 12 * np.log2(freq / A4_FREQ) + A4_MIDIPITCH
    return midipitch


def midipitch_to_pitchclass(midipitch: float) -> int:
    """Converts midipitch to numeric pitch-class.

    Will first round the midipitch to the nearest integer.

    Pitch-class is an integer value from 0 to 11 with 0=C, 1=C#/Bb, ..., 10=A#/Bb, 11=B.
    The midipitch supplied must be an integer.

    Args:
        midipitch: the midipitch value to convert.

    Returns:
        pitchclass: the pitch-class value of the midipitch.
    """
    midipitch = int(round(midipitch))
    pitchclass = midipitch % 12
    return pitchclass


def midipitch_to_octave(midipitch: float) -> int:
    """Converts midipitch to numeric octave number.

    Will first round the midipitch to the nearest integer.

    Octave 0 begins with C0 which is midipitch 12. Midipitch 0 is C-1, octave -1. For
    reference, a standard 88 key piano, the first key is A0 (=> the first C is C1).

    Args:
        midipitch: the midipitch value to convert.

    Returns:
        octave: the octave value of the midipitch.
    """
    midipitch = int(round(midipitch))
    octave = (midipitch - 12) // 12
    return octave


def midipitch_to_scientific(
    midipitch: float, acc_type: str = "sharp", nr_acc: Optional[int] = None,
) -> Union[str, ValueError]:
    """Converts an integer midipitch into scientific notation.

    Scientific notation can only represent integer midipitches, so will error if the
    supplied midipitch is not an integer value.

    Args:
        midipitch: the midipitch value to convert to scientific.
        acc_type: whether to use sharps (#) or flats (b) in the output.
        nr_acc: if specified, insists on a specific number of accidentals to
            use in the output.

    Returns:
        pitch_str: the scientific pitch value.

    Exceptions:
        ValueError: if the supplied midipitch is not an integer.
    """
    if acc_type == "sharp":
        accidental_chr = "#"
    elif acc_type == "flat":
        accidental_chr = "b"
    else:
        msg = f"acc_type must be in ('sharp', 'flat'), you supplied {repr(acc_type)}"
        log_and_raise(LOGGER, msg)

    if midipitch != int(midipitch):
        msg = f"midipitch must be whole number, you supplied {repr(midipitch)}"
        log_and_raise(LOGGER, msg)
    midipitch = int(midipitch)

    octave = midipitch_to_octave(midipitch)
    pitchclass = midipitch_to_pitchclass(midipitch)

    if nr_acc is not None:
        pitch_chr = NR_ACC_AND_PITCHCLASS_TO_STR[nr_acc][acc_type][pitchclass]
        accidental_str = nr_acc * accidental_chr
    else:
        if pitchclass in WHITE_KEYS_PITCHCLASS:
            idx = WHITE_KEYS_PITCHCLASS.index(pitchclass)
            accidental_str = ""
            pitch_chr = PITCH_CHARACTERS[idx]
        if pitchclass in BLACK_KEYS_PITCHCLASS:
            # black keys: C#/Db, D#/Eb, F#/Gb, G#/Ab, A#/Bb
            sharp_pitch_characters = ["C", "D", "F", "G", "A"]
            flat_pitch_characters = ["D", "E", "G", "A", "B"]
            idx = BLACK_KEYS_PITCHCLASS.index(pitchclass)
            if acc_type == "flat":
                accidental_str = "b"
                pitch_chr = flat_pitch_characters[idx]
            else:
                accidental_str = "#"
                pitch_chr = sharp_pitch_characters[idx]

    pitch_str = "{}{}{}".format(pitch_chr, accidental_str, octave)
    return pitch_str


def parse_scientific(pitch_str: str) -> Union[List[str], ValueError]:
    """Parses scientific pitch string.

    Args:
        pitch_str: the string to check.

    Returns:
        matched_groups: a list of all the groups matched.
    Raises:
        ValueError: if the string is not a valid scientific pitch string
    """
    if not isinstance(pitch_str, str):
        msg = f"Scientific pitch must be a string, got {repr(pitch_str)}."
        log_and_raise(LOGGER, msg)
    if not SCIENTIFIC_PATTERN.match(pitch_str):
        msg = f"Not a valid scientific note, got {repr(pitch_str)}."
        log_and_raise(LOGGER, msg)
    matched_groups = SCIENTIFIC_PATTERN.match(pitch_str).groups()
    return matched_groups


def scientific_to_midipitch(pitch_str: str) -> int:
    """Converts a scientific pitch to a midipitch.

    Args:
        pitch_str: the string to convert.

    Returns:
        midipitch: the resulting midipitch integer.
    """
    pitch_chr, accidental_str, octave = parse_scientific(pitch_str)
    idx = PITCH_CHARACTERS.index(pitch_chr)
    midipitch = 12 * (int(octave) + 1) + WHITE_KEYS_PITCHCLASS[idx]
    nr_accidentals = len(accidental_str)
    if nr_accidentals != 0:
        if "#" in accidental_str:
            midipitch += nr_accidentals
        else:
            midipitch -= nr_accidentals
    return midipitch


def scientific_to_pitchclass(pitch_str: str) -> int:
    """Gets the pitch-class of a scientific pitch.

    Args:
        pitch_str: the string to convert.

    Returns:
        pitchclass: the pitch-class value of the scientific pitch string.
    """
    return midipitch_to_pitchclass(scientific_to_midipitch(pitch_str))


def parse_abc(pitch_str: str) -> Union[List[str], ValueError]:
    """Parses abc pitch string.

    Args:
        pitch_str: the string to check.

    Returns:
        matched_groups: a list of all the groups matched.
    Raises:
        ValueError: if the string is not a valid scientific pitch string
    """
    if not isinstance(pitch_str, str):
        msg = f"ABC pitch must be a string, got {repr(pitch_str)}."
        log_and_raise(LOGGER, msg)
    if not ABC_PATTERN.match(pitch_str):
        msg = f"Not a valid abc note, got {repr(pitch_str)}."
        log_and_raise(LOGGER, msg)
    matched_groups = ABC_PATTERN.match(pitch_str).groups()
    return matched_groups


def abc_to_midipitch(abc_str: str) -> int:
    """Converts a string representing a note in abc midipitches.

    Args:
        abc: the abc string convert to midipitch.

    Returns:
        midipitch: the midipitch value of the supplied string.
    """
    accidental_str, pitch_chr, octave_str = parse_abc(abc_str)
    sci_pitch_chr = ABC_PITCH_CHR_TO_SCIENTIFIC[pitch_chr]
    midipitch = scientific_to_midipitch(sci_pitch_chr)
    nr_acc = len(accidental_str)
    if nr_acc > 0:
        if ABC_SHARP_CHR in accidental_str:
            midipitch += nr_acc
        elif ABC_FLAT_CHR in accidental_str:
            midipitch -= nr_acc
    nr_oct = len(octave_str)
    if nr_oct > 0:
        if ABC_OCT_UP in octave_str:
            midipitch += 12 * nr_oct
        elif ABC_OCT_DOWN in octave_str:
            midipitch -= 12 * nr_oct
    return midipitch


def abc_to_scientific(abc_str: str) -> str:
    """Converts a string representing a note in abc to scientific.

    Args:
        abc_str: the abc string convert to midipitch.

    Returns:
        sci_str: the scientific pitch value of the supplied string.
    """
    accidental_str, _, _ = parse_abc(abc_str)
    nr_acc = len(accidental_str)
    if nr_acc > 0:
        if ABC_SHARP_CHR in accidental_str:
            acc_type = "sharp"
        elif ABC_FLAT_CHR in accidental_str:
            acc_type = "flat"
    midipitch = abc_to_midipitch(abc_str)
    return midipitch_to_scientific(midipitch, acc_type=acc_type, nr_acc=nr_acc)


def scientific_to_abc(pitch_str: str) -> str:
    """Converts a string representing a pitch in scientific to abc.

    Args:
        pitch_str: the scientific string convert to abc.

    Returns:
        abc_str: the abc pitch value of the supplied string.
    """
    pitch_chr, accidental_str, octave = parse_scientific(pitch_str)
    oct_int = int(octave)
    if oct_int <= 3:
        nr_oct = -(oct_int - 4)
        oct_str = ABC_OCT_DOWN * nr_oct
        pitch_chr = pitch_chr.upper()
    elif oct_int == 4:
        oct_str = ""
        pitch_chr = pitch_chr.upper()
    elif oct_int == 5:
        oct_str = ""
        pitch_chr = pitch_chr.lower()
    elif oct_int >= 6:
        nr_oct = oct_int - 5
        oct_str = ABC_OCT_UP * nr_oct
        pitch_chr = pitch_chr.lower()

    nr_acc = len(accidental_str)
    if nr_acc > 0:
        if "#" in accidental_str:
            acc_str = ABC_SHARP_CHR * nr_acc
        elif "b" in accidental_str:
            acc_str = ABC_FLAT_CHR * nr_acc
    else:
        acc_str = ""
    return f"{acc_str}{pitch_chr}{oct_str}"


def midipitch_to_abc(
    midipitch: float, acc_type: str = "sharp", nr_acc: Optional[int] = None,
) -> Union[str, ValueError]:
    """Converts an integer midipitch into abc notation.

    ABC notation can only represent integer midipitches, so will error if the
    supplied midipitch is not an integer value.

    Args:
        midipitch: the midipitch value to convert to scientific.
        acc_type: whether to use sharps (#) or flats (b) in the output.
        nr_acc: if specified, insists on a specific number of accidentals to
            use in the output.

    Returns:
        pitch_str: the abc pitch value.

    Exceptions:
        ValueError: if the supplied midipitch is not an integer.
    """
    sci_pitch_str = midipitch_to_scientific(midipitch, acc_type=acc_type, nr_acc=nr_acc)
    return scientific_to_abc(sci_pitch_str)
