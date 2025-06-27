import json
import re
from collections import Counter

# Carrega os eventos
with open("all_events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

# Conta quantas vezes cada eventIdentifier aparece
event_names = [event.get("eventIdentifier", "") for event in events if "eventIdentifier" in event]
counter = Counter(event_names)

# 1. Eventos duplicados
duplicados = [
    {"eventIdentifier": name, "count": count}
    for name, count in counter.items() if count > 1
]

# 2. Eventos com nomes "bizarros"
bizarros = []
for name in set(event_names):
    if (
        len(name) < 4 or
        re.fullmatch(r"\d+", name) or
        re.search(r"[^a-zA-Z0-9 _\-|]", name) or
        name.lower() in {"test", "teste", "ok", "yes", "no", "true", "false", "event", "data"} or
        re.fullmatch(r"[a-zA-Z]{1,2}", name)
    ):
        bizarros.append({"eventIdentifier": name})

# Salva em JSON
with open("eventos_duplicados.json", "w", encoding="utf-8") as f:
    json.dump(duplicados, f, indent=2, ensure_ascii=False)

with open("eventos_bizarros.json", "w", encoding="utf-8") as f:
    json.dump(bizarros, f, indent=2, ensure_ascii=False)

print("Saída gerada em eventos_duplicados.json e eventos_bizarros.json")
