"""Admission différée avec préférences strictes, incomplètes et capacités."""

from collections import deque


class Matcher:
    def __init__(self, candidates, schools, capacities):
        self.candidates = candidates
        self.schools = schools
        self.capacities = capacities
        if set(schools) != set(capacities):
            raise ValueError("Capacités incomplètes")
        if any(type(v) is not int or v < 0 for v in capacities.values()):
            raise ValueError("Capacité entière non négative requise")
        for name, prefs in candidates.items():
            if len(prefs) != len(set(prefs)) or set(prefs) - set(schools):
                raise ValueError("Préférences candidat invalides")
        for name, prefs in schools.items():
            if len(prefs) != len(set(prefs)) or set(prefs) - set(candidates):
                raise ValueError("Préférences établissement invalides")
        self.ranks = {s: {c: i for i, c in enumerate(prefs)} for s, prefs in schools.items()}

    def solve(self):
        accepted = {s: [] for s in self.schools}
        position = {c: 0 for c in self.candidates}
        free = deque(sorted(self.candidates))
        proposals = 0
        while free:
            candidate = free.popleft()
            preferences = self.candidates[candidate]
            if position[candidate] >= len(preferences):
                continue
            school = preferences[position[candidate]]
            position[candidate] += 1
            proposals += 1
            if candidate not in self.ranks[school] or self.capacities[school] == 0:
                free.append(candidate)
                continue
            accepted[school].append(candidate)
            accepted[school].sort(key=self.ranks[school].get)
            if len(accepted[school]) > self.capacities[school]:
                free.append(accepted[school].pop())
        assignments = {c: None for c in self.candidates}
        for school, group in accepted.items():
            for c in group:
                assignments[c] = school
        return {
            "assignments": assignments,
            "accepted": accepted,
            "proposals": proposals,
            "blocking_pairs": self.blocking(assignments),
        }

    def blocking(self, assignments):
        if set(assignments) != set(self.candidates):
            raise ValueError("Affectations incomplètes")
        groups = {s: [] for s in self.schools}
        for c, s in assignments.items():
            if s is not None:
                if s not in groups or s not in self.candidates[c] or c not in self.ranks[s]:
                    raise ValueError("Affectation inacceptable")
                groups[s].append(c)
        if any(len(groups[s]) > self.capacities[s] for s in groups):
            raise ValueError("Capacité dépassée")
        pairs = []
        for c, prefs in self.candidates.items():
            current = assignments[c]
            better = prefs if current is None else prefs[: prefs.index(current)]
            for s in better:
                rank = self.ranks[s]
                if c not in rank or self.capacities[s] == 0:
                    continue
                if len(groups[s]) < self.capacities[s] or any(
                    rank[c] < rank[other] for other in groups[s]
                ):
                    pairs.append([c, s])
        return pairs


def run(request, db=":memory:"):
    return Matcher(request["candidates"], request["schools"], request["capacities"]).solve()
