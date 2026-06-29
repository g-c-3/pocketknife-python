# 🪛 pocketknife-python

> A collection of 50 weirdly specific, fun, and genuinely useful micro-utilities for everyday Python developers.

`pocketknife` bridges the gap between pure nonsense and hardcore utility — a **Standard Modular Package** where you import only the small pieces you need.

---

## ✨ Philosophy

- **Modular by design** — import only what you need, nothing more
- **Zero bloat** — each module is a focused, single-purpose tool
- **Fun + useful** — half of it will make you smile; the other half will save your day
- **No heavy dependencies** — standard library first, optional extras clearly marked

---

## 📦 Installation

```bash
pip install pocketknife-python
```

Or clone and install locally:

```bash
git clone https://github.com/GokulChandar/pocketknife-python.git
cd pocketknife-python
pip install -e .
```

---

## 🚀 Quick Examples

```python
# Fun stuff
from pocketknife.text_flair import spongecase
print(spongecase("why would you deploy on friday"))
# → "wHy WoUlD yOu DePlOy On FrIdAy"

# Useful stuff
from pocketknife.flatpack import flatten
flat = flatten({"a": {"b": {"c": 42}}})
# → {"a.b.c": 42}

# A bit of both
from pocketknife.dev_oracle import should_i_deploy
should_i_deploy()
# → "It is Friday at 4:47 PM. The answer is absolutely not."
```

---

## 🗂️ Module Index

The library is organized into **3 phases** of 50 modules total.

| Phase | Modules | Status |
|-------|---------|--------|
| Phase 1: The Foundation | 1–10 | 🔨 In Progress |
| Phase 2: The Expansion | 11–30 | 📋 Planned |
| Phase 3: The Micro-Architectures | 31–50 | 📋 Planned |

See [ROADMAP.md](ROADMAP.md) for the full detailed checklist.

---

## 📁 Project Structure

```
pocketknife/
├── text_flair.py
├── drama.py
├── absurd_units.py
├── dev_oracle.py
├── fuzzy_time.py
├── corporate_lorem.py
├── flatpack.py
├── resilience.py
├── sandbox.py
├── inspector.py
└── ... (50 modules total)
tests/
├── test_text_flair.py
└── ...
docs/
└── ...
README.md
ROADMAP.md
setup.py
```

---

## 👥 Contributors

| Role | Name |
|------|------|
| 🧠 Project Concept & Direction | **Gokul Chandar** |
| 💻 Code & Implementation | **Claude (Anthropic)** |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

This project is currently being built module by module. Once Phase 1 is complete, contribution guidelines will be added. Star the repo to follow the journey!

---

*Built with ☕ and a suspiciously large number of tabs open.*
