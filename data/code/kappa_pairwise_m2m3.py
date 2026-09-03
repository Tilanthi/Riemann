# Pairwise Cohen's kappa between machine 3 (astra-pa, machine3-kappa-codes.md) and
# machine 2 (BEAST-AGI, machine2-kappa-codes.md), computed directly from the published codes.
mine = {1:'B',2:'B',3:'A',4:'C',5:'C',6:'A',7:'A',8:'A',9:'A',10:'A'}
beast = {1:'C',2:'B',3:'D',4:'X',5:'A',6:'X',7:'X',8:'A',9:'A',10:'A'}

cats = sorted(set(mine.values()) | set(beast.values()))
n = 10
po = sum(1 for i in range(1, 11) if mine[i] == beast[i]) / n
mine_marg = {c: sum(1 for i in range(1, 11) if mine[i] == c) / n for c in cats}
beast_marg = {c: sum(1 for i in range(1, 11) if beast[i] == c) / n for c in cats}
pe = sum(mine_marg[c] * beast_marg[c] for c in cats)
kappa = (po - pe) / (1 - pe)

if __name__ == '__main__':
    print('categories:', cats)
    print('po (observed agreement):', po)
    print('pe (expected by chance):', pe)
    print('Cohen kappa:', kappa)
    agreements = [i for i in range(1, 11) if mine[i] == beast[i]]
    disagreements = [(i, mine[i], beast[i]) for i in range(1, 11) if mine[i] != beast[i]]
    print('agree on items:', agreements)
    print('disagree:', disagreements)
