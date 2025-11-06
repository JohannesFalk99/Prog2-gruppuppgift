from pathlib import Path
import json
from datetime import datetime

class ElpriserService:
    """Service responsible for fetching and parsing elpriser payloads.

    Public methods:
    - parse_raw_payload(payload) -> (labels, values, summary)
    - load_persisted(path) -> payload (reads elpriser_data.json)
    """

    @staticmethod
    def parse_raw_payload(priser):
        # Normalize possible payload shapes into a list of items
        if isinstance(priser, dict) and 'data' in priser and isinstance(priser['data'], list):
            items = priser['data']
        elif isinstance(priser, list):
            items = priser
        else:
            items = priser.get('hours', []) if isinstance(priser, dict) else []

        labels = []
        values = []
        for idx, item in enumerate(items):
            h = None
            p = None
            if isinstance(item, dict):
                h = item.get('time_start') or item.get('time') or item.get('start') or item.get('date') or item.get('t') or item.get('hour')
                p = item.get('SEK_per_kWh') or item.get('price') or item.get('value') or item.get('spot_price') or item.get('SpotPrice')
            else:
                p = item

            label = ''
            if h:
                try:
                    dt = datetime.fromisoformat(h)
                    label = dt.strftime('%H:%M')
                except Exception:
                    label = str(h)
            else:
                label = str(idx)

            val = None
            try:
                if p is not None and p != '':
                    val = float(p) * 100.0
            except Exception:
                val = None

            if val is not None:
                labels.append(label)
                values.append(round(val, 2))

        summary = {'avg': None, 'min': None, 'max': None}
        if values:
            summary = {
                'avg': round(sum(values) / len(values), 2),
                'min': round(min(values), 2),
                'max': round(max(values), 2),
            }
        return labels, values, summary

    @staticmethod
    def load_persisted(project_root: Path):
        path = project_root / 'elpriser_data.json'
        if not path.exists():
            return None
        try:
            with path.open('r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception:
            return None
