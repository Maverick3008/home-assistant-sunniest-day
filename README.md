# Sunniest Day for Home Assistant

# Sonnigster Tag für Home Assistant

A custom Home Assistant integration that analyzes your weather forecast and shows the sunniest upcoming day.

Eine Custom Integration für Home Assistant, die deine Wettervorhersage auswertet und den sonnigsten kommenden Tag anzeigt.

---


## 🇩🇪 Deutsch

## Funktionen

* Wetter-Entität direkt in der Home-Assistant-Oberfläche auswählen
* Ruft automatisch die tägliche Wettervorhersage ab
* Berechnet den sonnigsten kommenden Tag
* Kann den heutigen Tag nach einer einstellbaren Uhrzeit ignorieren
* Erstellt fertige Sensoren für Dashboards und Automationen
* Gewichtung für Regen und UV-Index einstellbar
* Keine eigenen YAML-Template-Sensoren notwendig

---

## Erstellte Sensoren

Nach der Einrichtung erstellt die Integration zum Beispiel folgende Sensoren:

```text
sensor.sonnigster_tag
sensor.sonnigster_tag_mit_datum
sensor.sonnigster_tag_wettervorhersage
```

Beispielwerte:

```text
Montag
Montag 29.06
```

Der Wettervorhersage-Sensor speichert zusätzlich die Rohdaten der Vorhersage als Attribut.

---

## Funktionsweise

Die Integration ruft die tägliche Wettervorhersage der ausgewählten Wetter-Entität ab und berechnet für jeden kommenden Tag einen Score.

Grundbewertung:

```text
sonnig          = 100 Punkte
teilweise wolkig = 70 Punkte
wolkig          = 40 Punkte
regnerisch      = 10 Punkte
andere           = 0 Punkte
```

Zusätzliche Anpassungen:

```text
Regen senkt den Score
UV-Index erhöht den Score
```

Der Tag mit dem höchsten Score wird als sonnigster Tag ausgegeben.

---

## Konfiguration

Die Integration kann vollständig über die Home-Assistant-Oberfläche eingerichtet werden.

Einstellbare Optionen:

* Wetter-Entität
* Anzahl der zu prüfenden Vorhersage-Tage
* Heutigen Tag ab bestimmter Uhrzeit ignorieren
* Regen-Abwertung
* UV-Index-Aufwertung
* Aktualisierungsintervall

---

## Installation

### Manuelle Installation

1. Dieses Repository herunterladen oder klonen.
2. Den Integrationsordner nach Home Assistant kopieren:

```text
custom_components/sonnigster_tag
```

Die Struktur sollte danach so aussehen:

```text
config/
└── custom_components/
    └── sonnigster_tag/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── manifest.json
        ├── sensor.py
        ├── strings.json
        └── translations/
            ├── de.json
            └── en.json
```

3. Home Assistant neu starten.
4. Öffnen:

```text
Einstellungen → Geräte & Dienste → Integration hinzufügen
```

5. Nach folgender Integration suchen:

```text
Sonnigster Tag
```

6. Wetter-Entität auswählen und speichern.

---

## HACS

Die Integration kann auch als benutzerdefiniertes Repository in HACS hinzugefügt werden.

1. HACS öffnen.
2. Oben rechts das Drei-Punkte-Menü öffnen.
3. `Benutzerdefinierte Repositories` auswählen.
4. Die URL dieses GitHub-Repositories einfügen.
5. Kategorie `Integration` auswählen.
6. Integration installieren.
7. Home Assistant neu starten.

---

## Beispielhafte Nutzung

Die erstellten Sensoren können verwendet werden für:

* Dashboard-Karten
* Wetterübersichten
* Benachrichtigungen
* Gartenplanung
* Planung von Outdoor-Aktivitäten
* Automationen abhängig vom besten Wettertag

Beispielidee:

```text
Benachrichtigung senden, wenn sich der sonnigste Tag der Woche ändert.
```

---

## Voraussetzungen

* Home Assistant mit Unterstützung für Wettervorhersagen
* Mindestens eine eingerichtete Wetter-Entität
* Eine Wetter-Integration, die tägliche Vorhersagen bereitstellt

---

## Hinweise

Die Qualität des Ergebnisses hängt vom ausgewählten Wetteranbieter ab.
Einige Wetteranbieter liefern möglicherweise nicht alle Werte, zum Beispiel UV-Index oder Niederschlag.

---

## 🇬🇧 English

## Features

* Select your Home Assistant weather entity directly in the UI
* Automatically fetches the daily weather forecast
* Calculates the sunniest upcoming day
* Optionally ignores today after a configurable time
* Creates easy-to-use sensors for dashboards and automations
* Supports configurable scoring for precipitation and UV index
* No YAML template sensors required

---

## Created sensors

After setup, the integration creates sensors like:

```text
sensor.sonnigster_tag
sensor.sonnigster_tag_mit_datum
sensor.sonnigster_tag_wettervorhersage
```

Example values:

```text
Monday
Monday 29.06
```

The forecast sensor also stores the raw forecast data as an attribute.

---

## How it works

The integration fetches the daily forecast from the selected weather entity and calculates a score for each upcoming day.

Basic scoring:

```text
sunny          = 100 points
partly cloudy = 70 points
cloudy         = 40 points
rainy          = 10 points
other          = 0 points
```

Additional adjustments:

```text
precipitation reduces the score
UV index increases the score
```

The day with the highest score is shown as the sunniest day.

---

## Configuration

The integration can be configured completely through the Home Assistant UI.

Available options:

* Weather entity
* Number of forecast days to check
* Ignore today after a configurable hour
* Precipitation penalty
* UV index bonus
* Update interval

---

## Installation

### Manual installation

1. Download or clone this repository.
2. Copy the folder into your Home Assistant `custom_components` directory:

```text
custom_components/sonnigster_tag
```

Your structure should look like this:

```text
config/
└── custom_components/
    └── sonnigster_tag/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── manifest.json
        ├── sensor.py
        ├── strings.json
        └── translations/
            ├── de.json
            └── en.json
```

3. Restart Home Assistant.
4. Go to:

```text
Settings → Devices & services → Add integration
```

5. Search for:

```text
Sonnigster Tag
```

6. Select your weather entity and save.

---

## HACS

This integration can also be added to HACS as a custom repository.

1. Open HACS.
2. Go to the three-dot menu in the top right.
3. Select `Custom repositories`.
4. Add this repository URL.
5. Select category `Integration`.
6. Install the integration.
7. Restart Home Assistant.

---

## Example use cases

You can use the created sensors for:

* Dashboard cards
* Weather overview panels
* Notifications
* Garden planning
* Solar or outdoor activity planning
* Automations based on the best weather day

Example automation idea:

```text
Send a notification when the sunniest day of the week changes.
```

---

## Requirements

* Home Assistant with weather forecast support
* At least one configured weather entity
* A weather integration that provides daily forecasts

---

## Notes

The quality of the result depends on the selected weather provider.
Some providers may not expose all values, such as UV index or precipitation.

---

## License / Lizenz

MIT License
