# 馃椇锔� ROADMAP 鈥� pocketknife-python 

> **For Claude:** Always read this file at the start of a new conversation using:
> ```
> curl https://raw.githubusercontent.com/GokulChandar/pocketknife-python/main/ROADMAP.md
> ```
> Check which boxes are ticked 鉁� to know where we left off, then continue from the first unchecked item.

---

## Legend
- 鉁� Complete 鈥� code written, tested, merged
- 馃敤 In Progress 鈥� currently being built
- 馃搵 Planned 鈥� not started yet

---

## 馃彈锔� PHASE 1: THE FOUNDATION (Modules 1鈥�10)

### 馃幁 The "Just for Fun" Wing

- [x] **1. `pocketknife.text_flair`**
  - `spongecase()` 鈥� alternating CaPs LiKe ThIs
  - `leetspeak()` 鈥� converts text to l33t 5p34k
  - `clapy()` 鈥� inserts 馃憦 clap 馃憦 emojis 馃憦 between 馃憦 words

- [x] **2. `pocketknife.drama`**
  - `dramatic_progress()` 鈥� stressed loading bar with anxiety messages
  - `excuse_generator()` 鈥� generates fake but plausible crash log excuses

- [x] **3. `pocketknife.absurd_units`**
  - `to_bananas(meters)` 鈥� converts meters to banana lengths
  - `to_coffees(joules)` 鈥� converts energy to cups of coffee
  - `to_jiffies(seconds)` 鈥� converts seconds to actual jiffies (1/100th of a second)

- [x] **4. `pocketknife.dev_oracle`**
  - `should_i_deploy()` 鈥� warns if it's Friday afternoon; blesses deploys otherwise
  - `code_review_roulette()` 鈥� returns a random passive-aggressive PR review comment

### 馃洜锔� The "Pure Utility" Wing

- [x] **5. `pocketknife.fuzzy_time`**
  - `around_noon(dt)` 鈥� humanizes datetimes ("about 3 hours ago", "just now")
  - `relative_age(dt)` 鈥� returns a human-readable age string for any datetime

- [x] **6. `pocketknife.corporate_lorem`**
  - `buzzwords(n)` 鈥� generates n corporate buzzword sentences
  - `pirate(n)` 鈥� generates pirate-themed filler text

- [x] **7. `pocketknife.flatpack`**
  - `flatten(d, sep=".")` 鈥� collapses nested dicts into dot-notation keys
  - `unflatten(d, sep=".")` 鈥� rebuilds a nested dict from dot-notation keys

- [x] **8. `pocketknife.resilience`**
  - `@stubborn(retries=3, delay=1)` 鈥� decorator that retries a failing function
  - `fallback(fn, default)` 鈥� calls fn, returns default if it raises any exception

- [x] **9. `pocketknife.sandbox`**
  - `temp_workspace()` 鈥� context manager creating a temp dir, cleaned up on exit

- [x] **10. `pocketknife.inspector`**
  - `snoop(var)` 鈥� rich print of type, value, length, and memory size
  - `stopwatch()` 鈥� context manager that prints exact execution time on exit

---

## 馃殌 PHASE 2: THE EXPANSION (Modules 11鈥�30)

### 馃幁 The "Just for Fun" Wing

- [x] **11. `pocketknife.blame`**
  - `git_roulette()` 鈥� on crash, blames a random name from git log

- [x] **12. `pocketknife.nostalgia`**
  - `dial_up_print(text)` 鈥� prints text character by character with modem sounds
  - `matrix_rain()` 鈥� renders a Matrix-style green character rain in the terminal

- [ ] **13. `pocketknife.overengineer`**
  - `@enterprise_edition` 鈥� wraps simple functions with verbose Java-style XML logs

- [ ] **14. `pocketknife.hype`**
  - `hype_man(iterable)` 鈥� wraps an iterable, shouting motivation every N iterations

- [ ] **15. `pocketknife.schrodinger`**
  - `quantum_bool()` 鈥� returns `True` exactly 50% of the time (the real 50/50)

- [ ] **16. `pocketknife.fortune`**
  - `zen_crash()` 鈥� exception hook that appends a peaceful proverb to any traceback

- [ ] **17. `pocketknife.soundtrack`**
  - `run_with_music(fn, url)` 鈥� prints a music link timed to the function's duration

- [ ] **18. `pocketknife.conspiracy`**
  - `generate_theory(vars)` 鈥� links your variable names to the Illuminati via GPT-style text

- [ ] **19. `pocketknife.pet`**
  - `feed_the_bird()` 鈥� terminal Tamagotchi; mood degrades if not run daily

- [ ] **20. `pocketknife.snark`**
  - `judge_type(x)` 鈥� passive-aggressive alternative to `type()` with commentary

### 馃洜锔� The "Pure Utility" Wing

- [ ] **21. `pocketknife.env_police`**
  - `require_env(*keys)` 鈥� raises clear error early if env vars are missing

- [ ] **22. `pocketknife.diet_pandas`**
  - `groupby_key(records, key)` 鈥� groups list of dicts by a field, no Pandas needed

- [ ] **23. `pocketknife.chunker`**
  - `paginate(iterable, size)` 鈥� safely splits any iterable into chunks of `size`

- [ ] **24. `pocketknife.lazy_logger`**
  - `@log_to_file(path)` 鈥� decorator logging function inputs/outputs to a file

- [ ] **25. `pocketknife.dict_diff`**
  - `compare(a, b)` 鈥� returns added, removed, and modified keys between two dicts

- [ ] **26. `pocketknife.file_scout`**
  - `find_first(pattern, root=".")` 鈥� finds first file matching a regex in a dir tree

- [ ] **27. `pocketknife.safe_math`**
  - `divide(a, b, default=None)` 鈥� safe division with a fallback on zero/type errors

- [ ] **28. `pocketknife.clean_strings`**
  - `normalize_text(s)` 鈥� strips weird Unicode, normalizes whitespace for DB input

- [ ] **29. `pocketknife.secret_keeper`**
  - `mask_secrets(d, keys)` 鈥� recursively hides sensitive values in nested dicts/logs

- [ ] **30. `pocketknife.gossip`**
  - `tell_me_about(obj)` 鈥� upgraded `dir()` printing markdown tables of methods + docs

---

## 馃彌锔� PHASE 3: THE MICRO-ARCHITECTURES (Modules 31鈥�50)

### 馃幁 The "Just for Fun" Wing

- [ ] **31. `pocketknife.rubber_duck`**
  - `summon_duck()` 鈥� ELIZA-style debug chatbot that asks Socratic questions

- [ ] **32. `pocketknife.xp_tracker`**
  - `@award_xp(points)` 鈥� saves XP to hidden file on test pass; prints level-ups

- [ ] **33. `pocketknife.chaos_monkey`**
  - `unleash_monkey(rate=0.05)` 鈥� randomly fails 5% of local HTTP requests

- [ ] **34. `pocketknife.bouncing_dvd`**
  - `standby_screen(text)` 鈥� bounces text around the terminal on script completion

- [ ] **35. `pocketknife.narrator`**
  - `@narrate` 鈥� uses OS TTS to read function start/finish/crash states aloud

### 馃洜锔� The "Pure Utility" Wing

- [ ] **36. `pocketknife.memoize_disk`**
  - `@cache_to(path)` 鈥� caches slow function results to a JSON file on disk

- [ ] **37. `pocketknife.fast_map`**
  - `multithread(fn, items)` 鈥� one-line concurrent.futures wrapper for I/O tasks

- [ ] **38. `pocketknife.easy_env`**
  - `generate_env_template(filepath)` 鈥� reads Python file, extracts all `os.environ` keys to `.env.template`

- [ ] **39. `pocketknife.fake_server`**
  - `WebhookReceiver()` 鈥� context manager spinning up a local HTTP server to catch POSTs

- [ ] **40. `pocketknife.auto_cli`**
  - `turn_into_cli(fn)` 鈥� parses type hints to auto-generate an `argparse` CLI

- [ ] **41. `pocketknife.shape_check`**
  - `validate(data, schema)` 鈥� pure-Python dict validator (lightweight Pydantic alternative)

- [ ] **42. `pocketknife.watchdog`**
  - `on_file_change(path, callback)` 鈥� background loop triggering callback on file save

- [ ] **43. `pocketknife.tiny_orm`**
  - `dict_to_sqlite(d, db_path)` 鈥� auto-creates SQLite DB and schema from a dict

- [ ] **44. `pocketknife.stealth_get`**
  - `fetch_page(url)` 鈥� scraping wrapper with User-Agent rotation and human-like delays

- [ ] **45. `pocketknife.stream_csv`**
  - `read_huge_csv(path)` 鈥� generator yielding rows from multi-GB CSVs without RAM bloat

- [ ] **46. `pocketknife.git_snapshot`**
  - `zip_working_state(output)` 鈥� respects `.gitignore` to create a clean ZIP backup

- [ ] **47. `pocketknife.regex_presets`**
  - `extract.emails(text)` 鈥� extracts all emails from a string
  - `extract.urls(text)` 鈥� extracts all URLs from a string

- [ ] **48. `pocketknife.file_hash`**
  - `hash_directory(path)` 鈥� recursive SHA-256 master hash of an entire directory

- [ ] **49. `pocketknife.token_bucket`**
  - `@rate_limit(calls, period)` 鈥� pure-Python rate limiter decorator

- [ ] **50. `pocketknife.memory_leak`**
  - `memory_watch()` 鈥� context manager warning of RAM growth inside a block

---

## 馃摝 Project Infrastructure

- [ ] `setup.py` / `pyproject.toml` 鈥� pip-installable package config
- [ ] `pocketknife/__init__.py` 鈥� package init with version
- [ ] `tests/` directory with base test structure
- [ ] `LICENSE` (MIT)
- [ ] `README.md` 鈥� complete with examples and contributor credits
- [ ] PyPI publish (after Phase 1 complete)

---

*Last updated: Phase 1 not yet started. Begin with Module 1: `pocketknife.text_flair`.*
