import pytest

from midi_set_class.notation import (
    STR_TO_PITCHCLASS,
    midipitch_to_octave,
    midipitch_to_pitchclass,
    midipitch_to_scientific,
    parse_scientific,
    scientific_to_midipitch,
    scientific_to_pitchclass,
)

MAX_NR_ACCIDENTALS = 3
MIDI_TO_SCI_TESTS = {
    -1: ["A##-2", "B-2", "Cb-1", "Dbbb-1"],
    0: ["A###-2", "B#-2", "C-1", "Dbb-1"],
    1: ["B##-2", "C#-1", "Db-1", "Ebbb-1"],
    59: ["A##3", "B3", "Cb4", "Dbbb4"],
    60: ["A###3", "B#3", "C4", "Dbb4"],
    61: ["B##3", "C#4", "Db4", "Ebbb4"],
}
SCI_TO_MIDI_TESTS = {
    sci: midi for midi, sci_list in MIDI_TO_SCI_TESTS.items() for sci in sci_list
}


def test_midipitch_to_pitchclass():
    for octave in range(-3, 4):
        for ii in range(12):
            midipitch = (octave - 1) * 12 + ii
            assert midipitch_to_pitchclass(midipitch) == ii


def test_midipitch_to_octave():
    assert midipitch_to_octave(59) == 3
    assert midipitch_to_octave(60) == 4
    assert midipitch_to_octave(0) == -1
    assert midipitch_to_octave(-1) == -2
    assert midipitch_to_octave(59.4999) == 3
    assert midipitch_to_octave(59.5) == 4
    assert midipitch_to_octave(60.0001) == 4


def test_midipitch_to_scientific():
    for midipitch, sci_list in MIDI_TO_SCI_TESTS.items():
        assert midipitch_to_scientific(midipitch) in sci_list


def test_parse_scientific():
    invalid_scientific = [
        "c0",  # lowercase
        "C#",  # missing octave
        "C#b3",  # mix of sharps and flats
        "H3",  # invalid letter
        "C4#",  # wrong order
        1,  # wrong type: int
        1.1,  # wrong type: float
        f"G{(MAX_NR_ACCIDENTALS+1) * '#'}4",  # too many accidentals
    ]
    for invalid_sci in invalid_scientific:
        with pytest.raises(ValueError):
            parse_scientific(invalid_sci)
    for sci_str in STR_TO_PITCHCLASS.keys():
        parse_scientific(sci_str + "0")


def test_scientific_to_midipitch():
    for scientific, midipitch in SCI_TO_MIDI_TESTS.items():
        assert scientific_to_midipitch(scientific) == midipitch


def test_scientific_to_pitchclass():
    for sci_str, pitchclass in STR_TO_PITCHCLASS.items():
        for ii in range(-12, 13):
            assert scientific_to_pitchclass(sci_str + f"{ii}") == pitchclass
