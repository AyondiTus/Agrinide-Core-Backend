import subprocess

def generate_changelog():
    try:
        # Menjalankan perintah git log
        result = subprocess.run(
            ['git', 'log', '--date=short', '--pretty=format:%cd|%h|%s|%an'],
            capture_output=True, text=True, check=True
        )
        
        commits = result.stdout.strip().split('\n')
        changelog_lines = [
            "# Changelog\n\n", 
            "Semua perubahan penting pada project ini didokumentasikan di file ini.\n\n"
        ]
        
        current_date = ""
        for commit in commits:
            if not commit: continue
            parts = commit.split('|', 3)
            if len(parts) == 4:
                date, hash_id, message, author = parts
                
                # Mengelompokkan berdasarkan tanggal
                if date != current_date:
                    changelog_lines.append(f"\n## {date}\n")
                    current_date = date
                    
                changelog_lines.append(f"- {message} (`{hash_id}`) - *{author}*\n")
                
        with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
            f.writelines(changelog_lines)
            
        print("✅ File CHANGELOG.md berhasil dibuat!")
        
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")

if __name__ == "__main__":
    generate_changelog()
