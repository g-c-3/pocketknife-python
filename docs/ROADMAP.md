# 🗺️ ROADMAP — pocketknife-python

> **For Claude:** Always read this file at the start of a new conversation using:
> ```
> curl https://raw.githubusercontent.com/GokulChandar/pocketknife-python/main/ROADMAP.md
> ```
> Check which boxes are ticked ✅ to know where we left off, then continue from the first unchecked item.

---

## Legend
- ✅ Complete — code written, tested, merged
- 🔨 In Progress — currently being built
- 📋 Planned — not started yet

---

## 🏗️ PHASE 1: THE FOUNDATION (Modules 1–10)

### 🎭 The "Just for Fun" Wing

- [ ] **1. `pocketknife.text_flair`**
  - `spongecase()` — alternating CaPs LiKe ThIs
  - `leetspeak()` — converts text to l33t 5p34k
  - `clapy()` — inserts 👏 clap 👏 emojis 👏 between 👏 words

- [ ] **2. `pocketknife.drama`**
  - `dramatic_progress()` — stressed loading bar with anxiety messages
  - `excuse_generator()` — generates fake but plausible crash log excuses

- [ ] **3. `pocketknife.absurd_units`**
  - `to_bananas(meters)` — converts meters to banana lengths
  - `to_coffees(joules)` — converts energy to cups of coffee
  - `to_jiffies(seconds)` — converts seconds to actual jiffies (1/100th of a second)

- [ ] **4. `pocketknife.dev_oracle`**
  - `should_i_deploy()` — warns if it's Friday afternoon; blesses deploys otherwise
  - `code_review_roulette()` — returns a random passive-aggressive PR review comment

### 🛠️ The "Pure Utility" Wing

- [ ] **5. `pocketknife.fuzzy_time`**
  - `around_noon(dt)` — humanizes datetimes ("about 3 hours ago", "just now")
  - `relative_age(dt)` — returns a human-readable age string for any datetime

- [ ] **6. `pocketknife.corporate_lorem`**
  - `buzzwords(n)` — generates n corporate buzzword sentences
  - `pirate(n)` — generates pirate-themed filler text

- [ ] **7. `pocketknife.flatpack`**
  - `flatten(d, sep=".")` — collapses nested dicts into dot-notation keys
  - `unflatten(d, sep=".")` — rebuilds a nested dict from dot-notation keys

- [ ] **8. `pocketknife.resilience`**
  - `@stubborn(retries=3, delay=1)` — decorator that retries a failing function
  - `fallback(fn, default)` — calls fn, returns default if it raises any exception

- [ ] **9. `pocketknife.sandbox`**
  - `temp_workspace()` — context manager creating a temp dir, cleaned up on exit

- [ ] **10. `pocketknife.inspector`**
  - `snoop(var)` — rich print of type, value, length, and memory size
  - `stopwatch()` — context manager that prints exact execution time on exit

---

## 🚀 PHASE 2: THE EXPANSION (Modules 11–30)

### 🎭 The "Just for Fun" Wing

- [ ] **11. `pocketknife.blame`**
  - `git_roulette()` — on crash, blames a random name from git log

- [ ] **12. `pocketknife.nostalgia`**
  - `dial_up_print(text)` — prints text character by character with modem sounds
  - `matrix_rain()` — renders a Matrix-style green character rain in the terminal

- [ ] **13. `pocketknife.overengineer`**
  - `@enterprise_edition` — wraps simple functions with verbose Java-style XML logs

- [ ] **14. `pocketknife.hype`**
  - `hype_man(iterable)` — wraps an iterable, shouting motivation every N iterations

- [ ] **15. `pocketknife.schrodinger`**
  - `quantum_bool()` — returns `True` exactly 50% of the time (the real 50/50)

- [ ] **16. `pocketknife.fortune`**
  - `zen_crash()` — exception hook that appends a peaceful proverb to any traceback

- [ ] **17. `pocketknife.soundtrack`**
  - `run_with_music(fn, url)` — prints a music link timed to the function's duration

- [ ] **18. `pocketknife.conspiracy`**
  - `generate_theory(vars)` — links your variable names to the Illuminati via GPT-style text

- [ ] **19. `pocketknife.pet`**
  - `feed_the_bird()` — terminal Tamagotchi; mood degrades if not run daily

- [ ] **20. `pocketknife.snark`**
  - `judge_type(x)` — passive-aggressive alternative to `type()` with commentary

### 🛠️ The "Pure Utility" Wing

- [ ] **21. `pocketknife.env_police`**
  - `require_env(*keys)` — raises clear error early if env vars are missing

- [ ] **22. `pocketknife.diet_pandas`**
  - `groupby_key(records, key)` — groups list of dicts by a field, no Pandas needed

- [ ] **23. `pocketknife.chunker`**
  - `paginate(iterable, size)` — safely splits any iterable into chunks of `size`

- [ ] **24. `pocketknife.lazy_logger`**
  - `@log_to_file(path)` — decorator logging function inputs/outputs to a file

- [ ] **25. `pocketknife.dict_diff`**
  - `compare(a, b)` — returns added, removed, and modified keys between two dicts

- [ ] **26. `pocketknife.file_scout`**
  - `find_first(pattern, root=".")` — finds first file matching a regex in a dir tree

- [ ] **27. `pocketknife.safe_math`**
  - `divide(a, b, default=None)` — safe division with a fallback on zero/type errors

- [ ] **28. `pocketknife.clean_strings`**
  - `normalize_text(s)` — strips weird Unicode, normalizes whitespace for DB input

- [ ] **29. `pocketknife.secret_keeper`**
  - `mask_secrets(d, keys)` — recursively hides sensitive values in nested dicts/logs

- [ ] **30. `pocketknife.gossip`**
  - `tell_me_about(obj)` — upgraded `dir()` printing markdown tables of methods + docs

---

## 🏛️ PHASE 3: THE MICRO-ARCHITECTURES (Modules 31–50)

### 🎭 The "Just for Fun" Wing

- [ ] **31. `pocketknife.rubber_duck`**
  - `summon_duck()` — ELIZA-style debug chatbot that asks Socratic questions

- [ ] **32. `pocketknife.xp_tracker`**
  - `@award_xp(points)` — saves XP to hidden file on test pass; prints level-ups

- [ ] **33. `pocketknife.chaos_monkey`**
  - `unleash_monkey(rate=0.05)` — randomly fails 5% of local HTTP requests

- [ ] **34. `pocketknife.bouncing_dvd`**
  - `standby_screen(text)` — bounces text around the terminal on script completion

- [ ] **35. `pocketknife.narrator`**
  - `@narrate` — uses OS TTS to read function start/finish/crash states aloud

### 🛠️ The "Pure Utility" Wing

- [ ] **36. `pocketknife.memoize_disk`**
  - `@cache_to(path)` — caches slow function results to a JSON file on disk

- [ ] **37. `pocketknife.fast_map`**
  - `multithread(fn, items)` — one-line concurrent.futures wrapper for I/O tasks

- [ ] **38. `pocketknife.easy_env`**
  - `generate_env_template(filepath)` — reads Python file, extracts all `os.environ` keys to `.env.template`

- [ ] **39. `pocketknife.fake_server`**
  - `WebhookReceiver()` — context manager spinning up a local HTTP server to catch POSTs

- [ ] **40. `pocketknife.auto_cli`**
  - `turn_into_cli(fn)` — parses type hints to auto-generate an `argparse` CLI

- [ ] **41. `pocketknife.shape_check`**
  - `validate(data, schema)` — pure-Python dict validator (lightweight Pydantic alternative)

- [ ] **42. `pocketknife.watchdog`**
  - `on_file_change(path, callback)` — background loop triggering callback on file save

- [ ] **43. `pocketknife.tiny_orm`**
  - `dict_to_sqlite(d, db_path)` — auto-creates SQLite DB and schema from a dict

- [ ] **44. `pocketknife.stealth_get`**
  - `fetch_page(url)` — scraping wrapper with User-Agent rotation and human-like delays

- [ ] **45. `pocketknife.stream_csv`**
  - `read_huge_csv(path)` — generator yielding rows from multi-GB CSVs without RAM bloat

- [ ] **46. `pocketknife.git_snapshot`**
  - `zip_working_state(output)` — respects `.gitignore` to create a clean ZIP backup

- [ ] **47. `pocketknife.regex_presets`**
  - `extract.emails(text)` — extracts all emails from a string
  - `extract.urls(text)` — extracts all URLs from a string

- [ ] **48. `pocketknife.file_hash`**
  - `hash_directory(path)` — recursive SHA-256 master hash of an entire directory

- [ ] **49. `pocketknife.token_bucket`**
  - `@rate_limit(calls, period)` — pure-Python rate limiter decorator

- [ ] **50. `pocketknife.memory_leak`**
  - `memory_watch()` — context manager warning of RAM growth inside a block

---

## 📦 Project Infrastructure

- [ ] `setup.py` / `pyproject.toml` — pip-installable package config
- [ ] `pocketknife/__init__.py` — package init with version
- [ ] `tests/` directory with base test structure
- [ ] `LICENSE` (MIT)
- [ ] `README.md` — complete with examples and contributor credits
- [ ] PyPI publish (after Phase 1 complete)

---

*Last updated: Phase 1 not yet started. Begin with Module 1: `pocketknife.text_flair`.*
