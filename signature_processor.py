import math

#Нормалізує підпис до стандартного розміру та центризації
def normalize_signature(signature):
    if not signature:
        return []

    min_x = min(point[0] for point in signature)
    max_x = max(point[0] for point in signature)
    min_y = min(point[1] for point in signature)
    max_y = max(point[1] for point in signature)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    max_range = max(max_x - min_x, max_y - min_y)

    normalized = []
    for x, y in signature:
        norm_x = (x - center_x) / max_range
        norm_y = (y - center_y) / max_range
        normalized.append((norm_x, norm_y))
    return normalized

#Інтерполює підпис до фіксованої кількості точок.
def interpolate_signature(signature, num_points=100):
    if len(signature) < 2:
        return signature

    interpolated = [signature[0]]
    for i in range(1, len(signature)):
        x1, y1 = signature[i - 1]
        x2, y2 = signature[i]
        num_inter_points = max(1, int(math.hypot(x2 - x1, y2 - y1) * num_points))
        for j in range(1, num_inter_points + 1):
            t = j / num_inter_points
            interpolated.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
    return interpolated[:num_points]
