#!/bin/bash

# --- Config ---
LEADS_CSV="/Users/ecohandel.nl/.openclaw/workspace/ecohandel/lead-generation/leads/LEADS.csv"
RESEARCH_LOG="/Users/ecohandel.nl/.openclaw/workspace/ecohandel/lead-generation/leads/RESEARCH_LOG.md"
DEYE_SCRAPER="/opt/homebrew/lib/node_modules/openclaw/skills/deye-price-guard/scripts/scrape_competitors.py"

# Ensure leads directory exists
mkdir -p /Users/ecohandel.nl/.openclaw/workspace/ecohandel/lead-generation/leads

# Initialize CSV header if file does not exist
if [ ! -f "$LEADS_CSV" ]; then
  echo "BEDRIJF;PROVINCIE;WEBSITE;TELEFOON;EMAIL;CONTACTPERSOON;BATTERIJ_ERVARING;DEYE_KENNIS;WARMTE;BRON;NOTITIES;DATUM_GEVONDEN" > "$LEADS_CSV"
fi

log_research() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" >> "$RESEARCH_LOG"
}

add_lead() {
  local company="$1"
  local province="$2"
  local website="$3"
  local phone="$4"
  local email="$5"
  local contact="$6"
  local battery_exp="$7"
  local deye_knowledge="$8"
  local warmth="$9"
  local source="${10}"
  local notes="${11}"
  local date_found="$(date '+%Y-%m-%d')"
  echo "\"$company\";\"$province\";\"$website\";\"$phone\";\"$email\";\"$contact\";\"$battery_exp\";\"$deye_knowledge\";\"$warmth\";\"$source\";\"$notes\";\"$date_found\"" >> "$LEADS_CSV"
}

# --- Prioriteit 1: Deye-gerelateerde Leads (Warmste) ---

log_research "Start: Deye-gerelateerde Leads"

# Task: Zoek "Deye installateur Nederland"
SEARCH_QUERY="\"Deye installateur Nederland\""
log_research "Searching: $SEARCH_QUERY"
RESULTS=$(web_search query="$SEARCH_QUERY" count=10)
log_research "Found: $(echo "$RESULTS" | grep -c 'url') results for $SEARCH_QUERY"
# (In a real scenario, parse RESULTS for leads and add to CSV)

# Task: Zoek "Deye servicepunt Nederland"
SEARCH_QUERY="\"Deye servicepunt Nederland\""
log_research "Searching: $SEARCH_QUERY"
RESULTS=$(web_search query="$SEARCH_QUERY" count=5)
log_research "Found: $(echo "$RESULTS" | grep -c 'url') results for $SEARCH_QUERY"
# (In a real scenario, parse RESULTS for leads and add to CSV)

# Task: Scrape Deye-gerelateerde concurrenten
log_research "Scraping Deye competitors: nkon.nl, sunnergie.nl, etronixcenter.com"
# (This part would require running the python script, which might involve more complex parsing and error handling)
# python3 "$DEYE_SCRAPER"
# For now, just log the intent.
log_research "Placeholder: Competitor scraping script would run here."


# --- Prioriteit 2: Thuisbatterij Installateurs (Middelwarm) ---

log_research "Start: Thuisbatterij Installateurs"

# Task: Zoek "thuisbatterij installateur Nederland"
SEARCH_QUERY="\"thuisbatterij installateur Nederland\""
log_research "Searching: $SEARCH_QUERY"
RESULTS=$(web_search query="$SEARCH_QUERY" count=15)
log_research "Found: $(echo "$RESULTS" | grep -c 'url') results for $SEARCH_QUERY"

# Task: Zoek "zonnepaneel thuisbatterij installateur [provincie]" - roteer provincies
PROVINCES=("Noord-Holland" "Zuid-Holland" "Utrecht" "Noord-Brabant" "Gelderland" "Overijssel" "Friesland" "Groningen" "Drenthe" "Flevoland" "Zeeland" "Limburg")
CURRENT_PROVINCE_INDEX_FILE="/tmp/current_province_index.txt"
CURRENT_PROVINCE_INDEX=0
if [ -f "$CURRENT_PROVINCE_INDEX_FILE" ]; then
  CURRENT_PROVINCE_INDEX=$(cat "$CURRENT_PROVINCE_INDEX_FILE")
fi

PROVINCE=${PROVINCES[CURRENT_PROVINCE_INDEX]}
SEARCH_QUERY="\"zonnepaneel thuisbatterij installateur $PROVINCE\""
log_research "Searching: $SEARCH_QUERY"
RESULTS=$(web_search query="$SEARCH_QUERY" count=5)
log_research "Found: $(echo "$RESULTS" | grep -c 'url') results for $SEARCH_QUERY"

NEW_PROVINCE_INDEX=$(( (CURRENT_PROVINCE_INDEX + 1) % ${#PROVINCES[@]} ))
echo "$NEW_PROVINCE_INDEX" > "$CURRENT_PROVINCE_INDEX_FILE"


# --- Prioriteit 3: Algemene Zonnepaneel Installateurs (Koud) ---

log_research "Start: Algemene Zonnepaneel Installateurs"

# Task: Zoek "zonnepaneel installateur Nederland"
SEARCH_QUERY="\"zonnepaneel installateur Nederland\""
log_research "Searching: $SEARCH_QUERY"
RESULTS=$(web_search query="$SEARCH_QUERY" count=20)
log_research "Found: $(echo "$RESULTS" | grep -c 'url') results for $SEARCH_QUERY"

log_research "End: Lead Generatie Run"

# Note: Parsing logic for search results and adding to CSV needs to be implemented. 
# This script currently only logs searches. Manual parsing/refinement needed for actual lead data.
