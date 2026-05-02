# DS Translator — Alfred Workflow

[简体中文](README.md)

Lightweight Alfred workflow for **Chinese ↔ English** lookup via DeepSeek; supports `context // word` for disambiguation.

## Install

1. Open **[Releases (latest)](https://github.com/BitSparse/alfred_llm_translator/releases/latest)**, download **DS-Translator.alfredworkflow** from Assets, double-click to import. (Or clone and run `bash build.sh` locally.)
2. Open **DS Translator** in Alfred, click **[x]**, and set your [DeepSeek](https://platform.deepseek.com) **API Key**.

## Usage

In Alfred, type:

```
tr hello
tr 法律 // brief
tr 编程 // variable
```


| Pattern              | Meaning                            |
| -------------------- | ---------------------------------- |
| `tr word`            | Translate; direction auto-detected |
| `tr context // word` | Use context for clearer sense      |


**Enter** copies the selected line to the clipboard.

## Notes

- Needs **Alfred 5** + Powerpack, **Python 3**, and a DeepSeek API key.  
- Model, temperature, etc. are in **Configure Workflow** with sensible defaults.

