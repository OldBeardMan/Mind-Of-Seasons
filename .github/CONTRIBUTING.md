# Contributing to Mind of Seasons

## Conventional Commits

Używamy [Conventional Commits](https://www.conventionalcommits.org/) do formatowania commit messages.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Typy commitów

| Typ | Opis | Przykład |
|-----|------|----------|
| `feat` | Nowa funkcjonalność | `feat(player): add dash ability` |
| `fix` | Naprawa błędu | `fix(camera): correct offset calculation` |
| `docs` | Dokumentacja | `docs: update README` |
| `style` | Formatowanie (bez zmian logiki) | `style: fix indentation` |
| `refactor` | Refaktoryzacja | `refactor(npc): extract dialogue system` |
| `perf` | Optymalizacja wydajności | `perf(map): implement chunk loading` |
| `test` | Testy | `test(inventory): add unit tests` |
| `build` | Zmiany w buildzie | `build: update pygame version` |
| `ci` | CI/CD | `ci: add linting workflow` |
| `chore` | Inne zmiany | `chore: clean up unused imports` |

### Scope (opcjonalny)

Moduł którego dotyczy zmiana:
- `player` - gracz, ruch, animacje
- `npc` - NPC, dialogi
- `enemy` - wrogowie
- `map` - generowanie mapy, tło
- `inventory` - ekwipunek
- `camera` - kamera
- `ui` - interfejs użytkownika

### Breaking Changes

Jeśli zmiana łamie kompatybilność:
```
feat(player)!: change movement system

BREAKING CHANGE: Player now uses velocity-based movement
```

### Przykłady

```bash
# Nowa funkcjonalność
git commit -m "feat(player): add sprint mechanic"

# Bug fix
git commit -m "fix(enemy): prevent spawning on player position"

# Refaktoryzacja
git commit -m "refactor(map): split into smaller modules"

# Dokumentacja
git commit -m "docs: add installation guide"
```

---

## Nazewnictwo branchy

### Format

```
<type>/<issue-number>-<short-description>
```

### Typy branchy

| Prefix | Użycie | Przykład |
|--------|--------|----------|
| `feat/` | Nowe funkcjonalności | `feat/42-player-dash` |
| `fix/` | Naprawy błędów | `fix/15-camera-offset` |
| `docs/` | Dokumentacja | `docs/8-readme-update` |
| `refactor/` | Refaktoryzacja | `refactor/23-npc-system` |
| `test/` | Testy | `test/31-inventory-tests` |
| `chore/` | Maintenance | `chore/5-cleanup-imports` |
| `hotfix/` | Pilne poprawki | `hotfix/99-crash-on-start` |

### Zasady

1. **Zawsze dodawaj numer issue**: `feat/42-new-feature` (nie `feat/new-feature`)
2. Używaj lowercase i myślników: `feat/42-new-feature` (nie `feat/42-NewFeature`)
3. Krótko i na temat: `fix/15-player-collision` (nie `fix/15-fixing-the-player-collision-bug`)
4. Jeden branch = jedna funkcjonalność/fix = jedno issue

### Bez issue?

Jeśli nie ma issue (małe zmiany), możesz pominąć numer:
```
chore/cleanup-unused-imports
docs/typo-fix
```

---

## Workflow

1. Utwórz issue (lub znajdź istniejące)
2. Utwórz branch z numerem issue: `feat/42-player-dash`
3. Commituj z Conventional Commits
4. Otwórz PR z wypełnionym template (linkuj issue: `Closes #42`)
5. Code review
6. Merge do `main`

```bash
# Przykład workflow
git checkout -b feat/42-player-dash
# ... zmiany ...
git add .
git commit -m "feat(player): add dash ability with cooldown

Closes #42"
git push -u origin feat/42-player-dash
# Otwórz PR na GitHub
```
