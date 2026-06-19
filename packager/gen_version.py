"""
gen_version.py <project_root> <output_file>
Reads APP_VERSION from server.py and writes a PyInstaller Windows version file.
"""
import re
import sys
from pathlib import Path

root        = Path(sys.argv[1])
output_file = Path(sys.argv[2])

server_src = (root / "src" / "phantom_clock" / "server.py").read_text(encoding="utf-8")
m = re.search(r"APP_VERSION\s*=\s*['\"]([^'\"]+)['\"]", server_src)
if not m:
    print("ERROR: APP_VERSION not found in server.py", file=sys.stderr)
    sys.exit(1)

version = m.group(1)
parts   = version.split(".")
while len(parts) < 4:
    parts.append("0")
ver_tuple = f"({parts[0]}, {parts[1]}, {parts[2]}, {parts[3]})"
ver_str   = f"{version}.0"

content = f"""\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={ver_tuple},
    prodvers={ver_tuple},
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
  ),
  kids=[
    StringFileInfo([StringTable(u'040904B0', [
      StringStruct(u'CompanyName',      u'PhantomLabs'),
      StringStruct(u'FileDescription',  u'Phantom Clock'),
      StringStruct(u'FileVersion',      u'{ver_str}'),
      StringStruct(u'InternalName',     u'phantom-clock'),
      StringStruct(u'LegalCopyright',   u''),
      StringStruct(u'OriginalFilename', u'phantom-clock.exe'),
      StringStruct(u'ProductName',      u'Phantom Clock'),
      StringStruct(u'ProductVersion',   u'{ver_str}')])]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

output_file.write_text(content, encoding="utf-8")
print(f"Generated {output_file} for version {version}")
