# Contributing to Weigh to Go! 🎉

Contributions to **Weigh to Go!** help the app better serve people tracking
their health goals.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Contribution Types](#contribution-types)
- [Development Setup](#development-setup)
- [Testing Strategy](#testing-strategy)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Recognition](#recognition)
- [Resources](#resources)

---

## 📜 Code of Conduct

### Pledge

This project is committed to providing a friendly, safe, and welcoming
environment for all contributors regardless of experience level, gender
identity, sexual orientation, disability, personal appearance, body size,
race, ethnicity, age, religion, or nationality.

### Standards

**Behavior that contributes to a positive environment:**

- ✅ Welcoming and inclusive language
- ✅ Respectful disagreement on differing viewpoints and experiences
- ✅ Graceful acceptance of constructive criticism
- ✅ Focus on what is best for the community
- ✅ Empathy toward other community members

**Unacceptable behavior:**

- ❌ Trolling, insulting or derogatory comments, and personal attacks
- ❌ Public or private harassment
- ❌ Publishing others' private information without permission
- ❌ Other conduct that could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project maintainer. All complaints will be reviewed
and investigated promptly and fairly.

---

## 🚀 Getting Started

### Prerequisites

WeighToGo is a polyglot monorepo — the Android codebase lives under `android/`
and the web rebuild lives under `web/`. Install only the prerequisites for the
stack relevant to the intended contribution.

**Shared (any contribution):**

- Git installed and configured
- A GitHub account
- [pre-commit](https://pre-commit.com/) (`pip install pre-commit` or `brew install pre-commit`) — runs lint, format, type-check, and tests on staged files

**Android (`android/`):**

- [Android Studio](https://developer.android.com/studio) Ladybug (2024.2.1+)
- [JDK 21](https://adoptium.net/) or higher
- Android SDK 34 (Android 14)

**Web (`web/`):**

- [Python 3.12+](https://www.python.org/) and [uv](https://docs.astral.sh/uv/) — backend
- [Node.js 20.19+ or 22+](https://nodejs.org/) — frontend
- [Docker](https://www.docker.com/) and Docker Compose — local PostgreSQL

The full quality-gate matrix (linters, type-checkers, test runners, coverage
thresholds) is specified in the SRS §11 (Quality Engineering).

### Setting up a local copy

External contributors fork and clone:

```bash
# 1. Fork the repository on GitHub
# 2. Clone the fork
git clone https://github.com/<github-username>/WeighToGo.git
cd WeighToGo

# 3. Add upstream remote
git remote add upstream https://github.com/rgoshen-snhu/WeighToGo.git

# 4. Keep the fork in sync
git fetch upstream
git checkout main
git merge upstream/main
```

The project maintainer works directly off `git@github.com:rgoshen-snhu/WeighToGo.git`
and pushes branches to the `snhu` remote per the repository's internal
conventions.

---

## 🤝 Contribution Types

### 🐛 Bug Reports

**Before submitting a bug report:**

1. Check the [existing issues](https://github.com/rgoshen-snhu/WeighToGo/issues) to avoid duplicates
2. Confirm the bug reproduces on the latest commit on `main`
3. Collect stack-appropriate information:
   - **Android bugs:** device model, Android version, app version, logcat output
   - **Web frontend bugs:** browser and version, OS, console errors
   - **Web backend bugs:** backend commit or tag, request/response excerpt with PII redacted

Submit via the Bug Report issue template.

### 💡 Feature Suggestions

**Before submitting a feature request:**

1. Check the [roadmap in README.md](README.md#roadmap) to see whether the feature is already planned
2. Search existing issues for similar suggestions
3. Confirm the feature aligns with the app's simplicity-focused design

Submit via the Feature Request issue template.

### 📝 Documentation Improvements

Documentation improvements are always welcome:

- Typo or clarity fixes to existing documentation
- New examples or tutorials
- Better code comments
- Translation

### 💻 Code Contributions

Open areas for code contribution:

- **Bug fixes** — check issues labeled `bug`
- **New features** — check issues labeled `enhancement`
- **Tests** — improve test coverage
- **Refactoring** — improve code quality
- **Performance** — optimize application performance

---

## 🛠️ Development Setup

### Activate pre-commit hooks (any stack)

After cloning, install the hooks once:

```bash
pre-commit install
```

The hooks are scoped per stack — backend hooks fire only on `web/backend/*.py`,
frontend hooks fire only on `web/frontend/**` — so contributions that don't
touch a stack don't pay its cost.

### Android (`android/`)

**1. Import project**

1. Open Android Studio
2. Select **File → Open**
3. Navigate to the `android/` directory inside the clone (the Gradle project root)
4. Wait for Gradle sync to complete

**2. Configure code style**

Import the project code style settings:

1. **File → Settings → Editor → Code Style**
2. Click the gear icon → **Import Scheme**
3. Select `config/codestyle.xml` (if available)

Manual configuration:

- **Indentation:** 4 spaces (no tabs)
- **Line length:** 120 characters max
- **Braces:** Same line (K&R style)

**3. Run tests**

```bash
cd android

# Unit tests
./gradlew test

# Instrumented tests
./gradlew connectedAndroidTest

# Lint
./gradlew lint
```

### Web Backend (`web/backend/`)

```bash
cd web/backend
cp .env.example .env             # adjust values as needed
docker compose up -d             # start local PostgreSQL
uv sync                          # install dependencies
uv run alembic upgrade head      # apply database migrations

# Run the dev server
uv run uvicorn weighttogo.main:app --reload

# Quality gates (also run by pre-commit and CI)
uv run ruff check .              # lint
uv run ruff format .             # format
uv run mypy                      # type-check
uv run pytest                    # tests (coverage thresholds enforced)
uv run pytest --cov              # explicit coverage report
```

The API serves at `http://localhost:8000`; `GET /health` reports service status.
The OpenAPI snapshot at `docs/api/openapi.json` is regenerated as part of
release closeout — do not edit it by hand.

### Web Frontend (`web/frontend/`)

```bash
cd web/frontend
cp .env.example .env             # adjust values as needed
npm install

# Run the dev server
npm run dev

# Quality gates (also run by pre-commit and CI)
npm run lint                     # eslint
npm run format:check             # prettier (write with `npm run format`)
npm run typecheck                # tsc
npm test                         # vitest (coverage thresholds enforced)
npm run test:e2e                 # playwright (requires backend running)
```

The frontend serves at `http://localhost:5173` and proxies API calls to the
backend dev server.

### Create a branch

Branch names use the `feature/`, `fix/`, `docs/`, or `chore/` prefix:

```bash
git checkout -b feature/<feature-name>
git checkout -b fix/<bug-description>
```

---

## 🧪 Testing Strategy

### Web Testing

**Backend (pytest):** test-driven development is the default. Tests live under
`web/backend/tests/` mirroring the source tree. Unit tests target domain and
application layers (no framework imports allowed); integration tests target
infrastructure adapters with a real PostgreSQL via the `conftest.py` fixtures.
Coverage threshold is enforced in CI per SRS §11.

```python
# Example unit test for a use case
def test_create_weight_entry_persists_when_valid(
    weight_repo: FakeWeightRepository,
) -> None:
    use_case = CreateWeightEntryUseCase(weight_repo)
    request = CreateWeightEntryRequest(
        user_id=UserId("user-1"),
        value=Decimal("180.5"),
        unit=WeightUnit.LBS,
        observation_date=date(2026, 5, 23),
    )

    result = use_case.execute(request)

    assert result.entry.id is not None
    assert weight_repo.find_by_id(result.entry.id) == result.entry
```

**Frontend (vitest):** component tests use Testing Library; HTTP calls are
mocked with MSW (Mock Service Worker) at the network boundary rather than
mocking individual `fetch` calls. Coverage threshold is enforced in CI.

```typescript
// Example component test
test('renders a not-found state when the entry fetch returns 404', async () => {
  server.use(
    http.get('/api/v1/weight-entries/:id', () =>
      HttpResponse.json({ detail: 'Not found' }, { status: 404 })
    )
  );

  render(<WeightEntryFormPage />, { wrapper: AllProviders });

  expect(await screen.findByText(/entry not found/i)).toBeInTheDocument();
  expect(screen.queryByRole('form')).not.toBeInTheDocument();
});
```

**End-to-end (Playwright):** specs live under `web/frontend/tests/e2e/` and run
the full stack (frontend + backend + database). They are deliberately scoped to
critical user flows: registration, login, weight entry create/edit/delete,
dashboard summary.

**ADR-0014** (TanStack Query for server state) means frontend tests should not
mock `useQuery`/`useMutation` directly — mock the HTTP layer via MSW so the
query lifecycle still exercises real cache behavior.

### Android Testing

**Use Mocks** (Mockito) for:

- **Unit tests** — testing business logic in isolation
- **Activity tests** — testing UI behavior and interactions
- **Fast feedback** — tests that need to run quickly
- **Edge cases** — simulating error conditions, null returns

**Example**: `MainActivityTest` uses Mockito mocks to test authentication
redirect without a real database.

**Use Real Database** (Integration tests) for:

- **DAO tests** — verifying SQL queries and database constraints
- **Data integrity** — testing transactions, foreign keys, unique constraints
- **Multi-step workflows** — testing end-to-end data flows
- **Migration verification** — ensuring database schema changes work correctly

**Example**: `LoginActivityIntegrationTest` uses a real database to verify
DAO/SessionManager integration.

**Dependency Injection for Testing.** Activities use **package-private setter
injection** to allow test code to inject mocks:

```java
// Production code (Activity)
private UserDAO userDAO;

void setUserDAO(UserDAO userDAO) {
    if (userDAO == null) {
        throw new IllegalArgumentException("UserDAO cannot be null");
    }
    this.userDAO = userDAO;
}

private void initDataLayer() {
    if (userDAO == null) {
        userDAO = new UserDAO(WeighToGoDBHelper.getInstance(this));
    }
}
```

```java
// Test code
@Mock private UserDAO mockUserDAO;

@Before
public void setUp() {
    MockitoAnnotations.openMocks(this);

    ActivityController<MainActivity> controller = Robolectric.buildActivity(MainActivity.class);
    activity = controller.get();

    // Inject mocks BEFORE onCreate()
    activity.setUserDAO(mockUserDAO);

    // Set default behaviors
    when(mockUserDAO.getUserById(1L)).thenReturn(testUser);

    // NOW call lifecycle methods
    controller.create().start().resume();
}
```

**Mock stubbing.** Always stub mock method calls that return values:

```java
@Before
public void setUp() {
    // Stub DAO insert methods to return realistic IDs
    when(mockWeightEntryDAO.insertWeightEntry(any(WeightEntry.class)))
            .thenAnswer(invocation -> System.currentTimeMillis() % 1000000);

    when(mockGoalWeightDAO.insertGoal(any(GoalWeight.class)))
            .thenReturn(1L);

    // Stub getter methods
    when(mockUserDAO.getUserById(testUserId)).thenReturn(testUser);
}
```

**Verification.** Use `verify()` to ensure mocked methods are called:

```java
@Test
public void test_login_callsSessionManager() {
    // ACT
    loginButton.performClick();

    // ASSERT
    verify(mockSessionManager).createSession(any(User.class));
}
```

**See also**:

- ADR-0005: Dependency Injection for Testing
- `docs/architecture/WeighToGo_Database_Architecture.md` for DAO testing guidelines

---

## 📏 Code Style Guidelines

Code style is enforced by tooling on every commit — `pre-commit` runs the
appropriate linter and formatter per stack. The sections below describe
conventions beyond what the tools auto-fix.

### Python Style (Web Backend)

- **Formatter and linter:** `ruff` (configured in `web/backend/pyproject.toml`) — formats and lints; do not bypass.
- **Type-checker:** `mypy` strict mode — every public function annotated.
- **Imports:** `ruff` auto-sorts; never edit import order manually.
- **Domain code under `web/backend/src/weighttogo/domain/`** must not import FastAPI, SQLAlchemy, or any infrastructure framework — this is the dependency rule from ADR-0012 (Three-Pattern Backend Architecture) and is enforced by `import-linter` in CI.

### TypeScript Style (Web Frontend)

- **Formatter:** `prettier` (configured in `web/frontend/.prettierrc`).
- **Linter:** `eslint` with `@typescript-eslint`; strict rules — no `any`, no unused exports.
- **Type-checker:** `tsc --noEmit` runs in CI; `strict: true` in `tsconfig.json`.
- **Component naming:** PascalCase; one component per file when feasible.
- **Server state:** managed via TanStack Query (per ADR-0014) — no ad-hoc `useEffect` fetches.

### Java Style Guide

The Android codebase follows the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) with these specifics:

#### Naming Conventions

```java
// Classes: PascalCase
public class WeightEntryActivity { }

// Methods: camelCase (verb phrases)
public void saveWeightEntry() { }

// Variables: camelCase
private float currentWeight;

// Constants: SCREAMING_SNAKE_CASE
public static final int MAX_WEIGHT = 1000;

// Layout IDs: snake_case with type prefix
// button_save, text_weight_display, edit_password

// Resource files: snake_case
// activity_main.xml, item_weight_history.xml
```

#### Code Organization

```java
public class ExampleActivity extends AppCompatActivity {

    // 1. Constants
    private static final String TAG = "ExampleActivity";

    // 2. Static fields
    private static int instanceCount = 0;

    // 3. Instance fields (UI elements first, then data)
    private Button btnSave;
    private EditText etWeight;
    private WeightDAO weightDAO;

    // 4. Lifecycle methods (in order)
    @Override
    protected void onCreate(Bundle savedInstanceState) { }

    @Override
    protected void onResume() { }

    @Override
    protected void onPause() { }

    // 5. UI initialization
    private void initViews() { }

    private void setupListeners() { }

    // 6. Business logic methods
    private void saveWeight() { }

    private void validateInput() { }

    // 7. Helper/utility methods
    private String formatWeight(float weight) { }
}
```

#### Comments

```java
// Javadoc for public methods
/**
 * Saves the weight entry to the database.
 *
 * @param weight The weight value in the user's preferred unit
 * @param date   The date of the weight entry
 * @return true if save was successful, false otherwise
 */
public boolean saveWeightEntry(float weight, String date) { }

// Inline comments are sparing, reserved for complex logic
// Calculate progress percentage (avoid division by zero)
float progress = (startWeight - currentWeight) / Math.max(startWeight - goalWeight, 0.1f);
```

### XML Layout Guidelines

```xml
<!-- Consistent attribute ordering -->
<Button
    android:id="@+id/btn_save"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginStart="16dp"
    android:layout_marginEnd="16dp"
    android:text="@string/save"
    android:textColor="@color/white"
    android:background="@drawable/btn_primary" />

<!-- Attribute order:
     1. android:id
     2. android:layout_width, layout_height
     3. android:layout_* (margins, constraints)
     4. android:* (other android attrs)
     5. app:* (custom/library attrs)
     6. tools:* (design-time attrs)
-->
```

### Resource Naming

| Type | Convention | Example |
|------|------------|---------|
| Layout | `<type>_<description>` | `activity_login.xml` |
| Drawable | `<type>_<description>` | `ic_weight.xml`, `bg_card.xml` |
| String | `<screen>_<description>` | `login_title`, `dashboard_greeting` |
| Color | `<description>` | `primary_teal`, `text_secondary` |
| Dimen | `<type>_<description>` | `margin_standard`, `text_headline` |

---

## 💬 Commit Message Guidelines

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Build, config, or tooling changes |
| `perf` | Performance improvement |
| `ci` | CI configuration |
| `build` | Build system or external dependencies |

### Examples

```bash
# Feature
feat(weight-entry): add unit toggle for lbs/kg conversion

# Bug fix
fix(database): resolve crash when saving null date

# Documentation
docs(readme): update installation instructions

# Refactoring
refactor(login): extract validation logic to utility class

# With body and footer
feat(notifications): add goal achievement celebration

Implement push notification when user reaches goal weight.
Includes custom celebration animation and sound.

Closes #42
```

### Rules

- Use **imperative mood** ("add" not "added" or "adds")
- **Do not capitalize** the subject line
- **No period** at the end of subject
- Keep subject line **under 50 characters**
- Wrap body at **72 characters**
- Reference issues in footer with `Closes #XX` or `Fixes #XX`

---

## 🔄 Pull Request Process

### Before submitting

- [ ] Code follows style guidelines
- [ ] Self-review against `docs/standards/cs499_code_review_checklist.md` is complete
- [ ] Comments added for complex logic
- [ ] Documentation updated if needed
- [ ] All tests pass locally
- [ ] No new warnings introduced
- [ ] Branch is up-to-date with `main`

### Submitting a PR

1. **Push the branch:**

```bash
git push origin feature/<feature-name>
```

2. **Open a Pull Request** on GitHub.

3. **Fill out the PR template** in `.github/PR_TEMPLATE.md` completely:
   - Clear title following commit conventions
   - Description of changes
   - Link to related issue(s)
   - Screenshots for UI changes
   - Testing instructions

### PR Title Format

```
feat(scope): brief description
fix(scope): brief description
docs(scope): brief description
```

### Review Process

1. **Automated checks** must pass (build, tests, lint, security audit)
2. **Self-review** against `docs/standards/cs499_code_review_checklist.md`
3. **Address feedback** via additional commits
4. **Squash and merge** when approved

### After merge

- Delete the feature branch
- Update local `main`:

```bash
git checkout main
git pull upstream main      # external contributors
git pull snhu main          # project maintainer
```

---

## 📝 Issue Guidelines

### Bug Report Template

The canonical templates live in `.github/ISSUE_TEMPLATE/`. The skeleton below
covers the common fields; add stack-specific information based on where the bug
occurred.

```markdown
**Stack:** Android / Web (frontend / backend) / Cross-stack

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
The behavior that was expected.

**Screenshots**
If applicable, add screenshots.

**Environment (Android):**
 - Device: [e.g., Pixel 7]
 - Android Version: [e.g., 14]
 - App Version: [e.g., 1.0.0]

**Environment (Web):**
 - Browser and version: [e.g., Chrome 130, Firefox 132]
 - OS: [e.g., macOS 14, Windows 11]
 - Backend commit / tag (if reproducible against a specific build)
 - Console errors or backend log excerpt (redact PII)

**Additional context**
Any other context about the problem.
```

### Feature Request Template

```markdown
**Is the feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution**
The desired outcome.

**Describe alternatives considered**
Any alternative solutions considered.

**Additional context**
Any other context or screenshots.
```

---

## 🏆 Recognition

Contributors are recognized in:

- **README.md** — listed in the Author / Contributors section
- **Release notes** — mentioned for significant contributions
- **GitHub** — all contributors visible in the repository

---

## ❓ Questions?

- **General questions:** open a [Discussion](https://github.com/rgoshen-snhu/WeighToGo/discussions)
- **Bug or feature:** open an [Issue](https://github.com/rgoshen-snhu/WeighToGo/issues)
- **Security issues:** email the maintainer directly (do not open a public issue)

---

## 📚 Resources

**Project-specific**

- [Architecture](ARCHITECTURE.md) — 30-second orientation; SRS §4 is authoritative
- [Software Requirements Specification](docs/specs/WeighToGo_Web_SRS_v2.md) — authoritative for the web rebuild
- [Architecture Decision Records](docs/adr/README.md) — numbered engineering decisions
- [Design Decision Records](docs/ddr/README.md) — numbered design decisions

**Web stack**

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [React 19](https://react.dev/)
- [TanStack Query v5](https://tanstack.com/query/latest)
- [Material UI v9](https://mui.com/)
- [Playwright](https://playwright.dev/)

**Android stack**

- [Android Developer Guides](https://developer.android.com/guide)
- [Material Design Guidelines](https://material.io/design)
- [Java Style Guide](https://google.github.io/styleguide/javaguide.html)

**Workflow**

- [Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

<p align="center">
  <strong>Contributions to Weigh to Go! are appreciated.</strong>
</p>
