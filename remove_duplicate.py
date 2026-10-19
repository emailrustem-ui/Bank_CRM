with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Находим и удаляем дублирующийся маршрут /jobs/
new_lines = []
skip_until_next_route = False
found_first_jobs = False

for i, line in enumerate(lines):
    if '@app.route("/jobs/<job_id>")' in line:
        if not found_first_jobs:
            found_first_jobs = True
            new_lines.append(line)
        else:
            # Это дубликат, пропускаем его и следующие строки до следующего @app.route или def
            skip_until_next_route = True
            continue
    
    if skip_until_next_route:
        if line.strip().startswith('@app.route') or (line.strip().startswith('def ') and 'job_status' not in line):
            skip_until_next_route = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("DUBLIKAT UDALEN! Proveryaem...")
