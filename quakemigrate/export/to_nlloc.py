# -*- coding: utf-8 -*-
"""
This module provides parsers to export an ObsPy Catalog to the NonLinLoc input
file format. We prefer this to the one offered by ObsPy as it includes the
additional weighting term.

"""

import warnings

from obspy.core.event import Event


ONSETS = {"i": "impulsive", "e": "emergent"}
ONSETS_REVERSE = {"impulsive": "i", "emergent": "e"}
POLARITIES = {"c": "positive", "u": "positive", "d": "negative"}
POLARITIES_REVERSE = {"positive": "u", "negative": "d"}


def nlloc_obs(event, filename):
    """
    Write a NonLinLoc Phase file from an obspy Catalog object.

    Parameters
    ----------
    event : obspy Catalog object
        Contains information on a single event.

    filename : str
        Name of NonLinLoc phase file.

    """
    info = []

    if not isinstance(event, Event):
        msg = ("Writing NonLinLoc Phase file is only supported for Catalogs "
               "with a single Event in it (use a for loop over the catalog "
               "and provide an output file name for each event).")
        raise ValueError(msg)

    fmt = ("{:s} {:s} {:s} {:s} {:s} {:s} {:s} {:s} " +
           "{:7.4f} GAU {:9.2e} {:9.2e} {:9.2e} {:9.2e} {:9.2e}")

    for pick in event.picks:
        wid = pick.waveform_id
        station = wid.station_code or "?"
        component = wid.channel_code and wid.channel_code[-1].upper() or "?"
        if component not in "ZNEH":
            component = "?"
        onset = ONSETS_REVERSE.get(pick.onset, "?")
        phase_type = pick.phase_hint or "?"
        polarity = POLARITIES_REVERSE.get(pick.polarity, "?")
        date = pick.time.strftime("%Y%m%d")
        hourminute = pick.time.strftime("%H%M")
        seconds = pick.time.second + pick.time.microsecond * 1e-6
        time_error = pick.time_errors.uncertainty or -1
        if time_error == -1:
            try:
                time_error = (pick.time_errors.upper_uncertainty +
                              pick.time_errors.lower_uncertainty) / 2.0
            except Exception:
                pass
        info_ = fmt.format(station.ljust(6), "?".ljust(4), component.ljust(4),
                           onset.ljust(1), phase_type.ljust(6), polarity.ljust(1),
                           date, hourminute, seconds, time_error, -1, -1, -1, 1)
        info.append(info_)

    if info:
        info = "\n".join(sorted(info) + [""])
    else:
        msg = "No pick information, writing empty NLLOC OBS file."
        warnings.warn(msg)
    with open(filename, "w") as fh:
        for line in info:
            fh.write(line)