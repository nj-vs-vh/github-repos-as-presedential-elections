from typing import Dict

from math import sqrt


def sorted_dict(d: Dict) -> Dict:
    return {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}


def dict_to_dict_distance(d1: Dict, d2: Dict, method: str = 'L2') -> float:
    if len(d1) != len(d2):
        raise ValueError("Dicts must be the same size!")
    method = method.lower()
    if method == 'l2':
        sum_ = 0
        for v1, v2 in zip(d1.values(), d2.values()):
            sum_ += (v1 - v2) ** 2
        return sqrt(sum_)
    if method == 'linf' or method == 'cheb':
        return max(abs(v2 - v1) for v1, v2 in zip(d1.values(), d2.values()))
    else:
        raise ValueError(f"Unknown distance calculation method '{method}'")


def dict_pprint(d: Dict) -> None:
    """pprint from pprint module doesn't preserve dict order!"""
    for k, v in d.items():
        print(f'{k}: {v}')


def trim_distribution_dict(d: Dict, size: int, others_key: str = 'Other') -> Dict:
    if len(d) > size:
        trimmed_d = dict(list(d.items())[:size-1])
        trimmed_d[others_key] = 1 - sum(trimmed_d.values())
    else:
        trimmed_d = d
    return trimmed_d


if __name__ == "__main__":
    print(sorted_dict({'a': 5, 'b': 1}))
    print(dict_to_dict_distance({'x': 1, 'y': 0, 'z': 0}, {'x': 1, 'y': 2, 'z': 1}, method='L2'))
    print(dict_to_dict_distance({'x': 1, 'y': 0, 'z': 0}, {'x': 1, 'y': 2, 'z': 1}, method='Linf'))
