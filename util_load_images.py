import re
from collections import namedtuple
from itertools import count, repeat

from bpy_extras.image_utils import load_image

# -----------------------------------------------------------------------------
# Image loading

ImageSpec = namedtuple(
    'ImageSpec',
    ['image', 'size', 'frame_start', 'frame_offset', 'frame_duration', 'use_alpha'])

num_regex = re.compile('[0-9]')  # Find a single number
nums_regex = re.compile('[0-9]+')  # Find a set of numbers


def find_image_sequences(files):
    """From a group of files, detect image sequences.

    This returns a generator of tuples, which contain the filename,
    start frame, and length of the detected sequence

    >>> list(find_image_sequences([
    ...     "test2-001.jp2", "test2-002.jp2",
    ...     "test3-003.jp2", "test3-004.jp2", "test3-005.jp2", "test3-006.jp2",
    ...     "blaah"]))
    [('blaah', 1, 1), ('test2-001.jp2', 1, 2), ('test3-003.jp2', 3, 4)]

    """
    files = iter(sorted(files))
    prev_file = None
    pattern = ""
    matches = []
    segment = None
    length = 1
    for filename in files:
        new_pattern = num_regex.sub('#', filename)
        new_matches = list(map(int, nums_regex.findall(filename)))
        if new_pattern == pattern:
            # this file looks like it may be in sequence from the previous

            # if there are multiple sets of numbers, figure out what changed
            if segment is None:
                for i, prev, cur in zip(count(), matches, new_matches):
                    if prev != cur:
                        segment = i
                        break

            # did it only change by one?
            for i, prev, cur in zip(count(), matches, new_matches):
                if i == segment:
                    # We expect this to increment
                    prev = prev + length
                if prev != cur:
                    break

            # All good!
            else:
                length += 1
                continue

        # No continuation -> spit out what we found and reset counters
        if prev_file:
            if length > 1:
                yield prev_file, matches[segment], length
            else:
                yield prev_file, 1, 1

        prev_file = filename
        matches = new_matches
        pattern = new_pattern
        segment = None
        length = 1

    if prev_file:
        if length > 1:
            yield prev_file, matches[segment], length
        else:
            yield prev_file, 1, 1


def load_images(filenames, directory, force_reload=True, frame_start=1, find_sequences=True):
    """Wrapper for bpy's load_image

    Loads a set of images, movies, or even image sequences
    Returns a generator of ImageSpec wrapper objects later used for texture setup
    """
    if find_sequences:  # if finding sequences, we need some pre-processing first
        file_iter = find_image_sequences(filenames)
    else:
        file_iter = zip(filenames, repeat(1), repeat(1))

    for filename, offset, frames in file_iter:
        image = load_image(filename, directory,
                           check_existing=True, force_reload=force_reload)
        image.use_alpha = True if image.depth == 32 else False

        # Size is unavailable for sequences, so we grab it early
        size = tuple(image.size)
        if size == (0, 0):
            continue

        if image.source == 'MOVIE':
            # Blender BPY BUG!
            # This number is only valid when read a second time in 2.77
            # This repeated line is not a mistake
            frames = image.frame_duration
            frames = image.frame_duration

        elif frames > 1:  # Not movie, but multiple frames -> image sequence
            image.source = 'SEQUENCE'

        yield ImageSpec(image, size, frame_start, offset - 1, frames, image.use_alpha)
