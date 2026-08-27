# CLAUDE.md

## Project Overview

Civic Survival is an infrastructure survival mod for Cities: Skylines II. It transforms the city builder into a crisis-management simulation where players must keep the power grid alive, defend against drone and missile attacks, and mobilize crews under pressure.

## Architecture

This repository contains the **client-side mod source code** published for transparency. It is **not a buildable distribution** — a full build requires the Cities: Skylines II Modding Toolkit and Unity environment. The server side is intentionally closed-source.

## Tech Stack

- **Language:** C# (Unity / Cities: Skylines II modding)
- **Framework:** Unity modding via CS2 Modding Toolkit
- **License:** PolyForm Strict 1.0.0 (client source); CC BY-NC-ND (game assets)

## Key Features

- Rolling blackouts, threat waves (Shahed drones, ballistic missiles), air defense
- Mobilization, spotters/intel, backup power, economy/finance
- Corruption/investigations, shadow economy, diplomacy/donor aid
- Information war, refugees, news/narrative, tutorial

## Development Notes

- This is the **public client source** for transparency — the server is the authority for balance and validation.
- The codebase is AI-generated under single-developer direction.
- Bug reports go to Discord, not GitHub Issues.
- Saves are not version-stable during Early Access beta.

## Repository Conventions

- User guide: `USER_GUIDE.md`
- Privacy policy: `PRIVACY.md`
- Build info: `BUILDING.md`
- Contributing: `CONTRIBUTING.md`
