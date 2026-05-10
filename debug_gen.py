from generator import generate_study_material
print("Generating...")
res = generate_study_material("Computer Networks", "OSI Model")
with open("debug_out.txt", "w", encoding="utf-8") as f:
    f.write("RAW DICT:\n")
    for k, v in res.items():
        f.write(f"{k}: {len(v)} chars\n")
        f.write(f"--- {k} ---\n{v}\n\n")
print("Done!")
