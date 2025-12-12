# Universal XBLA Extraction Tool

A cross-platform tool for extracting and organizing Xbox Live Arcade games for Batocera/EmulationStation.

## Features

- **Cross-platform**: Works on Windows, Linux, and macOS
- **Multi-format support**: Handles RAR, ZIP, and 7z archives
- **Automatic tool detection**: Uses the best available extraction tool
- **Robust error handling**: Gracefully handles extraction failures
- **User-friendly**: GUI folder selection and progress reporting

## Requirements

### All Platforms
- Python 3.6+
- pip (Python package manager)

### Recommended Tools (automatically detected)
- **Windows**: WinRAR (for `unrar` command) or 7-Zip
- **Linux/macOS**: `unrar`, `7z`, or `unzip` command-line tools

## Installation

1. **Install Python** (if not already installed):
   - Windows: Download from https://www.python.org/downloads/ (check "Add Python to PATH")
   - Linux: `sudo apt install python3 python3-pip` (Debian/Ubuntu)
   - macOS: `brew install python` (if using Homebrew)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install recommended tools** (optional but recommended):
   - **Windows**: Install WinRAR or 7-Zip
   - **Linux**: `sudo apt install unrar p7zip-full unzip`
   - **macOS**: `brew install unrar p7zip unzip`

## Usage

1. **Prepare your game archives**:
   - Place all your XBLA game archives (RAR, ZIP, or 7z) in a folder
   - Make sure archive names match the game titles

2. **Run the tool**:
   ```bash
   python extract.py
   ```

3. **Follow the prompts**:
   - Select your input folder (containing game archives)
   - Select your output folder (where extracted games will go)
   - Wait for extraction to complete
   - Choose whether to delete original archives

## How It Works

1. **Detects available tools**: Automatically finds the best extraction tool for your system
2. **Extracts archives**: Processes each game archive to find the PIRS file
3. **Organizes files**: Moves and renames files for Batocera compatibility
4. **Creates metadata**: Generates `.xbox360` text files for EmulationStation
5. **Cleans up**: Removes temporary directories

## Supported Archive Formats

- `.rar` - WinRAR archives
- `.zip` - ZIP archives  
- `.7z` - 7-Zip archives

## Platform-Specific Notes

### Windows
- Recommends using WinRAR's `unrar` command for best compatibility
- Falls back to `patoolib` if command-line tools aren't available
- Disables Unix `file` command usage to avoid errors

### Linux/macOS
- Uses native command-line tools (`unrar`, `7z`, `unzip`) when available
- Falls back to `patoolib` if needed
- Supports standard Unix file commands

## Troubleshooting

### "No archive extraction tools available"
Install one of the recommended tools:
- Windows: Install WinRAR or 7-Zip
- Linux: `sudo apt install unrar p7zip-full unzip`
- macOS: `brew install unrar p7zip unzip`

### Extraction failures
- Make sure your archive files aren't corrupted
- Try extracting manually to test the archive
- Check file permissions on Linux/macOS

### GUI issues
If the folder selection dialog doesn't appear:
- Make sure you're running in a graphical environment
- Try running from a terminal/command prompt

## Command-Line Options

The tool can also be run with command-line arguments:

```bash
python extract.py input_folder output_folder
```

## Output Structure

For each game archive `Game Name.rar`, the tool creates:
- `output_folder/Game_Name` (the extracted PIRS file)
- `output_folder/Game_Name.xbox360` (metadata file for EmulationStation)

## License

Same as the original project.

## Contributing

Pull requests and bug reports are welcome! Please test on multiple platforms before submitting changes.

## Credits

- Original concept: XBLA-Automation project
- Universal compatibility: Added cross-platform support and multi-format handling