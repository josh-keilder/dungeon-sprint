# Floats can't store most decimals exactly: 0.29 is really 0.28999...,
# so 0.29 * 100 is 28.999... and int() would give 28. The tiny nudge fixes that.
FLOAT_NUDGE = 1e-6


def to_centiseconds(seconds):
    return int(seconds * 100 + FLOAT_NUDGE)


def format_run_time(seconds):
    centiseconds = to_centiseconds(seconds)

    minutes = centiseconds // 6000
    whole_seconds = centiseconds // 100 % 60
    hundredths = centiseconds % 100

    return f"{minutes:02d}:{whole_seconds:02d}.{hundredths:02d}"
