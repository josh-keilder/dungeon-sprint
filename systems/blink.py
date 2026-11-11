from systems.timer import is_running, time_left


def is_blink_hidden(invulnerability, blink_interval):
    blink_phase = int(time_left(invulnerability) / blink_interval)
    return is_running(invulnerability) and blink_phase % 2 == 1
