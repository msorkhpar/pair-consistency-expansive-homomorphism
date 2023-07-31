import networkx as nx


# https://stackoverflow.com/a/27303476
def __select_k(spectrum, minimum_energy=0.9):
    running_total = 0.0
    total = sum(spectrum)
    if total == 0.0:
        return len(spectrum)
    for i in range(len(spectrum)):
        running_total += spectrum[i]
        if running_total / total >= minimum_energy:
            return i + 1
    return len(spectrum)


def similarity(g, h):
    laplacian1 = nx.spectrum.normalized_laplacian_spectrum(g)
    laplacian2 = nx.spectrum.normalized_laplacian_spectrum(h)
    k1 = __select_k(laplacian1)
    k2 = __select_k(laplacian2)
    k = min(k1, k2)
    return sum((laplacian1[:k] - laplacian2[:k]) ** 2)
