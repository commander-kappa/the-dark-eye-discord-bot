# The Dark Eye — Discord Bot
Access your character sheet data (exported from an Optolith.json) and roll on your stats directly from Discord.

[![Python](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Repo](https://img.shields.io/badge/repo-commander--kappa/the--dark--eye--discord--bot-blue)](https://codeberg.org/kappa-dev/the-dark-eye-discord-bot)

Table of Contents
- [About](#about)
- [Features](#features)
- [Demo & Examples](#demo--examples)
- [Installation](#installation)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

## About
This Discord bot is a utility for the 5th Edition of the fantasy themed [The Dark Eye](https://en.wikipedia.org/wiki/The_Dark_Eye_(role-playing_game)) (TDE) / 'Das Schwarze Auge (DSA)' german tabletop role-playing game. The code is directly based on my [CLI version of this project](https://codeberg.org/kappa-dev/the-dark-eye-cli-tool). With this tool players can either import their **JSON** character sheets created in [Optolith](https://optolith.app/en/download), a free graphical TDE5 character generation tool, or convert and import their completed **official deluxe character sheet PDF** (INFO: Because I have only ever got my hands on the german deluxe PDF, I could not implement a converter for the english version yet).

## Features
- Assign privileged **Gamemaster** roles, which can add or remove players.
- Import character data from Optolith JSON exports or completed PDF sheets.
- List and select imported characters per Discord user.
- Roll dices and attributes or skills from character data.
- Friendly, readable result messages for players and Gamemasters.
- Persistent character storage in a directory format.
- Extensible command architecture to add new systems or roll types.

## Demo & Examples
- Import:
```text
/upload_character sheet.json [discord_user default:self]
```

- Select a character:
```text
/select_character file_name

```

- Show a selected character summary:
```text
/show_info [discord_user default:self]

Name.......... Herbert Albert Jodelbert (LZ)
Geschlecht.... m
Alter......... 21
Gewicht....... 80
Größe......... 180
Familie....... Irmgart & Hans, Bertina, Berthold
Geburtsort.... Degendorf
Geburtsdatum.. 1019 / 7. Praios
Persönlichkeit Hitzköpfig, Streng, Pflichtbewusst
```
- Show a selected characters talents:
```text
/show_talents [id_min default:0] [id_max default:58] [discord_user default:self]

===== [Körper] ================================================

[00] Fliegen................ [MU/IN/GE] BE:JA   R:0    FW:0  ""
[01] Gaukeleien............. [MU/CH/FF] BE:JA   R:0    FW:0  ""
[02] Klettern............... [MU/GE/KK] BE:JA   R:0    FW:6  ""
[03] Körperbeherrschung..... [GE/GE/KO] BE:JA   R:0    FW:5  ""
[04] Kraftakt............... [KO/KK/KK] BE:JA   R:0    FW:6  ""
[05] Reiten................. [CH/GE/KK] BE:JA   R:0    FW:0  ""
[06] Schwimmen.............. [GE/KO/KK] BE:JA   R:0    FW:4  ""
[07] Selbstbeherrschung..... [MU/MU/KO] BE:NEIN R:0    FW:6  ""
[08] Singen................. [KL/CH/KO] BE:EVTL R:0    FW:0  ""
[09] Sinnesschärfe.......... [KL/IN/IN] BE:EVTL R:0    FW:9  ""

[...]

===== [Handwerk] ==============================================

[42] Alchimie............... [MU/KL/FF] BE:JA   R:0    FW:0  ""
[43] Boote & Schiffe........ [FF/GE/KK] BE:JA   R:0    FW:0  ""
[44] Fahrzeuge.............. [CH/FF/KO] BE:JA   R:0    FW:0  ""
[45] Handel................. [KL/IN/CH] BE:NEIN R:0    FW:5  ""
[46] Heilkunde Gift......... [MU/KL/IN] BE:JA   R:0    FW:3  ""
[47] Heilkunde Krankheiten.. [MU/IN/KO] BE:JA   R:0    FW:3  ""
[48] Heilkunde Seele........ [IN/CH/KO] BE:NEIN R:0    FW:0  ""
[49] Heilkunde Wunden....... [KL/FF/FF] BE:JA   R:0    FW:6  ""
[50] Holzbearbeitung........ [FF/GE/KK] BE:JA   R:0    FW:7  ""
[51] Lebensmittelbearbeitung [IN/FF/FF] BE:JA   R:0    FW:7  ""
[52] Lederbearbeitung....... [FF/GE/KO] BE:JA   R:0    FW:3  ""
[53] Malen & Zeichnen....... [IN/FF/FF] BE:JA   R:0    FW:0  ""
[54] Metallbearbeitung...... [FF/KO/KK] BE:JA   R:0    FW:0  ""
[55] Musizieren............. [CH/FF/KO] BE:JA   R:0    FW:0  ""
[56] Schlösserknacken....... [IN/FF/FF] BE:JA   R:0    FW:0  ""
[57] Steinbearbeitung....... [FF/FF/KK] BE:JA   R:0    FW:0  ""
[58] Stoffbearbeitung....... [KL/FF/FF] BE:JA   R:0    FW:4  ""

```

- Roll an Attribute:
```text
/roll_attribute ID [roll_modificator default:0] [discord_user default:self]
/roll_attribute IN [2]

Roll on Attribute [IN] for Herbert Albert Jodelbert:

[IN] Intuition 13
(FAILURE) [12]+2
```
- Roll an Talent:
```text
/roll_talent ID [roll_modificator default:0] [discord_user default:self]
/roll_talent 9 [-1]

Roll on Talent [9] for Herbert Albert Jodelbert:

Sinnesschärfe (Körper) [KL/IN/IN] BE:EVTL R:0    FW:9  ""
10/13/13 x [15, 17, 17]-1 = FW:9 - 10 = -1
(FAILURE) QS: 0
```

## Installation
1. Clone the repo:
```bash
git clone https://codeberg.org/kappa-dev/the-dark-eye-discord-bot
```

2. Activate the virtual environment and install dependencies with [UV Python project manager](https://docs.astral.sh/uv/):
```bash
uv sync
```

3. Create a discord bot for your account on https://discord.com/developers/applications

4. Run the bot and enter the token for your created discord bot:
```bash
uv run src/main.py
```
```text
Creating /home/user/Development/the-dark-eye-discord-bot/src/../res/ACTIVE_PLAYER
TOKEN file does not exist!
Creating /home/user/Development/the-dark-eye-discord-bot/src/../res/TOKEN
TOKEN file empty!
Enter your discord bot TOKEN: 
```
5. Add Gamemasters to the MASTER file (either by answering the text prompt or by editing the file manually)
```text
Creating /home/user/Development/the-dark-eye-discord-bot/src/../res/MASTER
You have not entered any Gamemasters in the MASTER file. Please Enter the discord ID for all users that are suppossed to have Master permissions
You will now be prompted to enter all Gamemasters discord IDs. You may exit by typing 'exit'.
Enter a discord user ID: 
```

## Tech Stack
- Language: Python (async)
- Discord integration: discord.py 
- Data: JSON parsing following the Optolith schema

## Contributing
Contributions are welcome:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/<short-description>`
3. Add tests for new behavior.
4. Open a pull request with a clear description of changes and why they matter.

## Roadmap
Planned or desirable enhancements:
- Access to combat stats
- improved Exception handling
- command interface for pdf extraction

## License
This repository is provided under the GPL3.0 License. See the `LICENSE` file for details.

## Contact
Maintained by kappa-dev — codeberg@kappa-dev.de
