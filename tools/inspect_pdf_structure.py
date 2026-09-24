import pypdf

reader = pypdf.PdfReader('latex/main.pdf')
print(f"Total pages: {len(reader.pages)}")

# Print outline
for item in reader.outline:
    if isinstance(item, list):
        for sub in item:
            if hasattr(sub, 'title'):
                print(f"   -- {sub.title}")
    elif hasattr(item, 'title'):
        print(f"{item.title}")
