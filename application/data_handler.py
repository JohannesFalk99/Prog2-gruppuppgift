# import os
# import json
# import webbrowser
# from datetime import datetime

# #Display charts with the electricity prices data using chart.js and elpriser_data.json

# def _find_json_path(filename="elpriser_data.json"):
# 	# Search common locations: same directory, parent, cwd
# 	candidates = [
# 		os.path.join(os.path.dirname(__file__), filename),
# 		os.path.join(os.path.dirname(__file__), "..", filename),
# 		os.path.join(os.getcwd(), filename),
# 		filename,
# 	]
# 	for p in candidates:
# 		p = os.path.abspath(p)
# 		if os.path.isfile(p):
# 			return p
# 	raise FileNotFoundError(f"{filename} not found in expected locations: {candidates}")

# def _extract_records(obj):
# 	# If top-level is a list, that's likely our records.
# 	if isinstance(obj, list):
# 		return obj
# 	# If it's a dict, try to find the first list value (common wrappers)
# 	if isinstance(obj, dict):
# 		for k, v in obj.items():
# 			if isinstance(v, list) and v:
# 				return v
# 	# Fallback: wrap single dict into list
# 	return [obj] if isinstance(obj, dict) else []

# def _guess_keys(record):
# 	# Find probable timestamp and value keys by name heuristics.
# 	if not isinstance(record, dict):
# 		return None, None
# 	keys = list(record.keys())
# 	lower = [k.lower() for k in keys]
# 	time_key = None
# 	value_key = None
# 	for k, lk in zip(keys, lower):
# 		if any(tok in lk for tok in ("time", "date", "timestamp", "datetime", "hour")):
# 			time_key = k
# 			break
# 	for k, lk in zip(keys, lower):
# 		if any(tok in lk for tok in ("price", "value", "sek", "kwh", "amount")):
# 			value_key = k
# 			break
# 	# If not found, fall back to first string-like and first numeric-like keys
# 	if time_key is None:
# 		for k in keys:
# 			if isinstance(record[k], str):
# 				time_key = k
# 				break
# 	if value_key is None:
# 		for k in keys:
# 			if isinstance(record[k], (int, float)):
# 				value_key = k
# 				break
# 	return time_key, value_key

# def _format_label(val):
# 	# Try to parse ISO-like datetimes to shorter labels, otherwise use raw string
# 	if not isinstance(val, str):
# 		return str(val)
# 	for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
# 		try:
# 			d = datetime.fromisoformat(val) if "T" in val else datetime.strptime(val, fmt)
# 			return d.strftime("%Y-%m-%d %H:%M") if fmt != "%Y-%m-%d" else d.strftime("%Y-%m-%d")
# 		except Exception:
# 			continue
# 	return val

# def generate_chart_html(json_path=None, out_html="elpriser_chart.html", title="Elpriser"):
# 	"""
# 	Read JSON (autodetect structure), generate an HTML file with a Chart.js line chart,
# 	and open it in the default browser.
# 	"""
# 	if json_path is None:
# 		json_path = _find_json_path()
# 	with open(json_path, "r", encoding="utf-8") as f:
# 		obj = json.load(f)

# 	records = _extract_records(obj)
# 	if not records:
# 		raise ValueError("No records found in JSON.")

# 	# Guess keys from the first record
# 	time_key, value_key = _guess_keys(records[0])
# 	if value_key is None:
# 		raise ValueError("Could not detect a numeric value key in the JSON records.")

# 	labels = []
# 	values = []
# 	for r in records:
# 		# allow for non-dict items
# 		if isinstance(r, dict):
# 			t = r.get(time_key) if time_key else None
# 			v = r.get(value_key)
# 		else:
# 			# if records are simple pairs like [ [time, value], ... ]
# 			try:
# 				t, v = r[0], r[1]
# 			except Exception:
# 				continue
# 		if v is None:
# 			continue
# 		labels.append(_format_label(t) if t is not None else "")
# 		# convert values to floats when possible
# 		try:
# 			values.append(float(v))
# 		except Exception:
# 			# skip non-numeric entries
# 			continue

# 	# Build minimal HTML with Chart.js (CDN)
# 	html = f"""<!doctype html>
# <html>
# <head>
#   <meta charset="utf-8"/>
#   <title>{title}</title>
#   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
#   <style>
#     body {{ font-family: sans-serif; padding: 20px; }}
#     canvas {{ max-width: 100%; height: 400px; }}
#   </style>
# </head>
# <body>
#   <h2>{title}</h2>
#   <canvas id="priceChart"></canvas>
#   <script>
#     const labels = {json.dumps(labels)};
#     const data = {{
#       labels: labels,
#       datasets: [{{
#         label: "Price",
#         data: {json.dumps(values)},
#         fill: false,
#         borderColor: "rgb(75, 192, 192)",
#         tension: 0.1
#       }}]
#     }};
#     const config = {{
#       type: "line",
#       data: data,
#       options: {{
#         scales: {{
#           x: {{
#             display: true,
#             title: {{ display: true, text: "Time" }},
#             ticks: {{ maxRotation: 45, minRotation: 0 }}
#           }},
#           y: {{
#             display: true,
#             title: {{ display: true, text: "Price" }}
#           }}
#         }},
#         responsive: true,
#         maintainAspectRatio: false
#       }}
#     }};
#     const ctx = document.getElementById("priceChart").getContext("2d");
#     new Chart(ctx, config);
#   </script>
# </body>
# </html>
# """
# 	# Write and open
# 	out_path = os.path.abspath(out_html)
# 	with open(out_path, "w", encoding="utf-8") as f:
# 		f.write(html)
# 	webbrowser.open("file://" + out_path)
# 	print(f"Chart generated: {out_path}")

# if __name__ == "__main__":
# 	# Example usage: python data_handler.py [optional_path_to_json]
# 	import sys
# 	arg = sys.argv[1] if len(sys.argv) > 1 else None
# 	generate_chart_html(json_path=arg)
