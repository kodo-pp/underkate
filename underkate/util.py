def clamp(x, minimum, maximum):
    if x < minimum:
        return minimum
    if x > maximum:
        return maximum
    return x
