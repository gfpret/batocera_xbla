#!/usr/bin/env python3
"""
Universal XBLA Extraction Tool
Works on Windows, Linux, and macOS
Supports RAR, ZIP, and 7z archives
"""

import os
import sys
import shutil
import subprocess
from alive_progress import alive_bar
from tkinter import Tk, filedialog

# Fix for Windows Unicode issues
if sys.platform == "win32":
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # If this fails, continue anyway

# Supported archive extensions
SUPPORTED_EXTENSIONS = ['.rar', '.zip', '.7z']

def is_tool_available(tool_name):
    """Check if a command-line tool is available."""
    try:
        subprocess.run([tool_name, '--version'], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                      timeout=5)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        return False

def get_archive_extractor():
    """Get the best available archive extractor for the current platform."""
    extractors = []
    
    # Check for platform-specific tools
    if sys.platform == "win32":
        if is_tool_available('unrar'):
            extractors.append(('unrar', 'x'))
        if is_tool_available('7z'):
            extractors.append(('7z', 'x'))
    else:
        # Linux/macOS
        if is_tool_available('unrar'):
            extractors.append(('unrar', 'x'))
        if is_tool_available('7z'):
            extractors.append(('7z', 'x'))
        if is_tool_available('unzip'):
            extractors.append(('unzip', ''))
    
    # Always add patoolib as fallback
    try:
        import patoolib
        extractors.append(('patoolib', None))
    except ImportError:
        pass
    
    return extractors

def extract_archive(archive_path, extract_to, archive_name):
    """Extract archive using the best available method."""
    extractors = get_archive_extractor()
    
    if not extractors:
        raise RuntimeError("No archive extraction tools available. Please install unrar, 7z, or patoolib.")
    
    # Try each extractor in order
    for extractor_name, extractor_cmd in extractors:
        try:
            if extractor_name == 'patoolib':
                import patoolib
                # Disable file command on Windows to avoid errors
                if sys.platform == "win32":
                    os.environ['PATOOL_FILE_CMD'] = ''
                patoolib.extract_archive(archive_path, outdir=extract_to, verbosity=-1)
                return True
            else:
                # Use command-line tool
                if extractor_name == 'unrar':
                    cmd = [extractor_name, extractor_cmd, '-o-', archive_path, extract_to]
                elif extractor_name == '7z':
                    cmd = [extractor_name, extractor_cmd, '-o' + extract_to, archive_path]
                elif extractor_name == 'unzip':
                    cmd = [extractor_name, archive_path, '-d', extract_to]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    return True
                else:
                    print(f"{extractor_name} failed: {result.stderr}")
        except Exception as e:
            print(f"Error with {extractor_name}: {e}")
            continue
    
    return False

def find_innermost_file(directory):
    """Find the innermost file in a directory structure."""
    deepest_file = None
    max_depth = -1
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            # Calculate depth (number of subdirectories from the starting directory)
            depth = file_path[len(directory):].count(os.sep)
            
            if depth > max_depth:
                max_depth = depth
                deepest_file = file_path
    
    return deepest_file

def clean_filename(filename, replace_spaces=True, space_replacement="_"):
    """Clean filename by removing extension and optionally replacing spaces.
    
    Args:
        filename: The original filename
        replace_spaces: Whether to replace spaces in filenames
        space_replacement: Character to use for space replacement (default: "_")
    
    Returns:
        Cleaned filename suitable for use as a game name
    """
    # Remove archive extension
    for ext in SUPPORTED_EXTENSIONS:
        if filename.lower().endswith(ext):
            filename = filename[:-len(ext)]
            break
    
    # Optional: Replace spaces
    if replace_spaces:
        filename = filename.replace(" ", space_replacement)
    
    # Remove or replace other problematic characters
    # Keep only alphanumeric, spaces (if not replaced), and basic punctuation
    import re
    # Allow letters, numbers, spaces (if not replaced), and basic punctuation
    if replace_spaces:
        # If spaces are replaced, be more restrictive
        # First replace spaces, then clean up other characters
        filename = re.sub(r'[^\w\-\(\)\[\]\{\}\s]+', space_replacement, filename)
        # Then replace any remaining spaces
        filename = filename.replace(" ", space_replacement)
    else:
        # If keeping spaces, allow them but remove other special chars
        filename = re.sub(r'[^\w \-\(\)\[\]\{\}]+', '', filename)
    
    # Remove any double replacements (only if space_replacement is not empty)
    if space_replacement:
        filename = re.sub(f'{re.escape(space_replacement)}{{2,}}', space_replacement, filename)
    
    # Strip any remaining unwanted characters from start/end
    filename = filename.strip(".-_ ")
    
    return filename

def main():
    print("Universal XBLA Extraction Tool")
    print("=" * 40)
    print(f"Platform: {sys.platform}")
    print(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
    print()
    
    # Filename formatting options
    print("Filename Formatting Options:")
    print("1. Keep spaces (e.g., 'Game Name')")
    print("2. Replace spaces with underscores (e.g., 'Game_Name')")
    print("3. Replace spaces with dashes (e.g., 'Game-Name')")
    print("4. Remove spaces entirely (e.g., 'GameName')")
    
    while True:
        choice = input("\nChoose filename format (1-4, default 2): ").strip()
        if choice in ['', '2']:
            replace_spaces = True
            space_replacement = "_"
            break
        elif choice == '1':
            replace_spaces = False
            space_replacement = " "
            break
        elif choice == '3':
            replace_spaces = True
            space_replacement = "-"
            break
        elif choice == '4':
            replace_spaces = True
            space_replacement = ""
            break
        else:
            print("Please enter 1, 2, 3, or 4.")
    
    print(f"\nUsing filename format: {'no spaces' if not replace_spaces else f'spaces replaced with \"{space_replacement}\"'}")
    print()
    
    # Get input and output directories
    print("Please choose your input folder containing game archives:")
    xbla_dir = filedialog.askdirectory(title="Select Input Folder")
    
    if not xbla_dir:
        print("No input folder selected. Exiting.")
        return
    
    print("Please choose your output folder:")
    xbla_unpacked_dir = filedialog.askdirectory(title="Select Output Folder")
    
    if not xbla_unpacked_dir:
        print("No output folder selected. Exiting.")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(xbla_unpacked_dir, exist_ok=True)
    
    # Get list of supported archive files
    archive_files = []
    for ext in SUPPORTED_EXTENSIONS:
        archive_files.extend([f for f in os.listdir(xbla_dir) 
                            if f.lower().endswith(ext)])
    
    if not archive_files:
        print(f"No supported archive files found in {xbla_dir}")
        print(f"Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}")
        return
    
    print(f"Found {len(archive_files)} archive files to process...")
    
    # Process each archive file
    try:
        with alive_bar(len(archive_files)) as bar:
            for archive in archive_files:
                archive_path = os.path.join(xbla_dir, archive)
                game_name = clean_filename(archive, replace_spaces, space_replacement)
                # Use a temporary directory for extraction to avoid path conflicts
                game_dir = os.path.join(xbla_unpacked_dir, game_name + "_temp")
                
                try:
                    print(f"Processing {archive}...")
                    
                    # Create game directory
                    os.makedirs(game_dir, exist_ok=True)
                    
                    # Extract the archive
                    if extract_archive(archive_path, game_dir, archive):
                        # Find the innermost file (should be the PIRS file)
                        innermost_file = find_innermost_file(game_dir)
                        
                        if innermost_file:
                            # Move the file to the output directory
                            final_file_path = os.path.join(xbla_unpacked_dir, game_name)
                            
                            # Move and rename the file
                            shutil.move(innermost_file, final_file_path)
                            
                            # Clean up the temporary directory
                            shutil.rmtree(game_dir)
                            
                            # Create the .xbox360 text file
                            with open(final_file_path + ".xbox360", "w") as f:
                                f.write(game_name)
                        else:
                            print(f"Warning: Could not find innermost file in {game_dir}")
                    else:
                        print(f"Warning: Failed to extract {archive}")
                    
                except Exception as e:
                    print(f"Error processing {archive}: {e}")
                
                bar()  # Update progress bar
    except UnicodeEncodeError:
        # Fallback for Windows Unicode issues
        print("Progress bar disabled due to Unicode encoding issues.")
        for i, archive in enumerate(archive_files):
            archive_path = os.path.join(xbla_dir, archive)
            game_name = clean_filename(archive, replace_spaces, space_replacement)
            # Use a temporary directory for extraction to avoid path conflicts
            game_dir = os.path.join(xbla_unpacked_dir, game_name + "_temp")
            
            try:
                print(f"Processing {archive}... ({i+1}/{len(archive_files)})")
                
                # Create game directory
                os.makedirs(game_dir, exist_ok=True)
                
                # Extract the archive
                if extract_archive(archive_path, game_dir, archive):
                    # Find the innermost file (should be the PIRS file)
                    innermost_file = find_innermost_file(game_dir)
                    
                    if innermost_file:
                        # Move the file to the output directory
                        # Remove .pirs extension from the final filename (as per original script)
                        final_file_path = os.path.join(xbla_unpacked_dir, game_name)
                        
                        print(f"Moving {innermost_file} to {final_file_path}")
                        
                        # Move and rename the file
                        try:
                            # The destination should be the final path without .pirs extension
                            shutil.move(innermost_file, final_file_path)
                            print(f"✓ Successfully moved {game_name}")
                        except Exception as e:
                            print(f"✗ Failed to move {innermost_file}: {e}")
                            # Try copying instead
                            try:
                                shutil.copy2(innermost_file, final_file_path)
                                os.remove(innermost_file)
                                print(f"✓ Successfully copied {game_name}")
                            except Exception as copy_error:
                                print(f"✗ Failed to copy {innermost_file}: {copy_error}")
                                continue
                        
                        # Clean up the temporary directory
                        try:
                            shutil.rmtree(game_dir)
                            print(f"✓ Cleaned up {game_dir}")
                        except Exception as e:
                            print(f"⚠ Failed to clean up {game_dir}: {e}")
                        
                        # Create the .xbox360 text file
                        try:
                            with open(final_file_path + ".xbox360", "w") as f:
                                f.write(game_name)
                            print(f"✓ Created {game_name}.xbox360")
                        except Exception as e:
                            print(f"✗ Failed to create .xbox360 file: {e}")
                    else:
                        print(f"Warning: Could not find innermost file in {game_dir}")
                else:
                    print(f"Warning: Failed to extract {archive}")
                
            except Exception as e:
                print(f"Error processing {archive}: {e}")
    
    print("\nUnpacking complete!")
    
    # Ask if user wants to delete the original archives
    while True:
        delete_choice = input("Would you like to delete the original archive files? (Y/N): ").strip().upper()
        if delete_choice in ['Y', 'N']:
            break
        print("Please enter Y or N.")
    
    if delete_choice == 'Y':
        try:
            for archive in archive_files:
                os.remove(os.path.join(xbla_dir, archive))
            print("Original archive files have been deleted.")
        except Exception as e:
            print(f"Error deleting archive files: {e}")

if __name__ == "__main__":
    # Check for required dependencies
    try:
        from alive_progress import alive_bar
        from tkinter import filedialog
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install with: pip install alive-progress")
        sys.exit(1)
    
    main()
