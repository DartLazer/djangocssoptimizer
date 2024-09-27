import gzip
import os
import platform
import shutil
import subprocess
from configparser import ConfigParser
from typing import List, Optional, Tuple


def main() -> None:
    """
    Main function to load configuration, process CSS files, and run PurgeCSS.

    This function loads the settings from the config file, processes the CSS files,
    and runs the PurgeCSS command to remove unused CSS from HTML files in the Django project.
    It also compresses the resulting purged CSS file.
    """
    config = load_and_check_config('settings.cfg')
    if not config:
        print(f'Config file set incorrectly.')
        return
    django_project_directory = config.get('SETTINGS', 'django_directory')

    # Define the paths for the original CSS file and the output file
    css_files = config.get('SETTINGS', 'input_css_files')
    css_files = [file.strip(' ') for file in css_files.split(',')]
    output_dir = config.get('SETTINGS', 'output_directory')

    # Define the Django apps to look for in HTML files
    django_apps = config.get('SETTINGS', 'django_apps')
    django_apps = [django_app.strip(' ') for django_app in django_apps.split(',')]

    # Collect unique directories containing HTML files, excluding directories with "around"
    html_glob_patterns = []

    # Loop through the project directories to find HTML files
    for root, dirs, files in os.walk(django_project_directory):
        # Check if any of the include directories are in the current root path
        if any(app in root for app in django_apps) and "around" not in root:
            # Check if there are any HTML files in the current directory
            if any(file.endswith('.html') for file in files):
                html_glob_patterns.append(f"{root}/*.html")

    for css_file in css_files:
        purge_result, purged_filename = purge_css_file(html_glob_patterns, css_file, output_dir)
        # Check the output and log accordingly
        if purge_result.stdout == "" and purge_result.stderr == "":
            print("PurgeCSS command completed successfully.")
            print(f'Purged CSS file saved to: {purged_filename}')
            compressed_file = compress_purged_file(output_dir, purged_filename)
            print(f'Compressed file saved as: {compressed_file}')
        else:
            print("PurgeCSS output:")
            print(purge_result.stdout)
            print("PurgeCSS errors:")
            print(purge_result.stderr)


def purge_css_file(glob_patterns: List[str], css_file: str, output_dir: str) -> Tuple[subprocess.CompletedProcess, str]:
    """
    Run PurgeCSS on a given CSS file and return the result.

    This function runs the PurgeCSS command to remove unused CSS from the specified
    CSS file based on the content found in HTML files matching the glob patterns.

    :param glob_patterns: List of glob patterns to match HTML files.
    :param css_file: Path to the input CSS file.
    :param output_dir: Directory where the purged CSS file will be saved.
    :return: A tuple containing the subprocess result and the output filename.
    """
    # Extract the filename without the directory path
    css_filename = os.path.basename(css_file)

    # Remove the '.css' extension to create the output filename prefix
    css_filename_prefix = css_filename.split('.css')[0]

    # Define the output filename for the purged CSS file
    output_filename = f"{css_filename_prefix}-purged.css"

    purgecss_command = (
        f"purgecss --css {css_file} "
        f"--content {' '.join(glob_patterns)} "
        f"--output {output_dir}/{output_filename}"
    )

    # Check if CSS file exists before running the command
    if not os.path.isfile(css_file):
        print(f"Error: CSS File {css_file} does not exist. Please check the file paths.")
    else:
        print(f"Running PurgeCSS command: {purgecss_command}")

    # Detect the operating system and adjust npx command accordingly
    if platform.system() == 'Windows':
        npx_command = f"npx {purgecss_command}"
    else:
        npx_command = f"bash -c 'source $HOME/.nvm/nvm.sh && npx {purgecss_command}'"

    # Run the command and capture the output
    result = subprocess.run(npx_command, shell=True, text=True, capture_output=True)
    return result, output_filename


def compress_purged_file(output_dir: str, purged_file: str) -> str:
    """
    Compress the purged CSS file using gzip.

    This function compresses the purged CSS file into a gzip format.

    :param output_dir: Directory where the purged CSS file is located.
    :param purged_file: Name of the purged CSS file to be compressed.
    :return: The name of the compressed file.
    """
    filepath = f'{output_dir}/{purged_file}'
    with open(filepath, 'rb') as f_in:
        with gzip.open(f'{filepath}.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return filepath


class InvalidConfigFile(Exception):
    """
    Exception raised for invalid configuration file.

    This exception is raised when the configuration file is missing, malformed, or contains
    invalid data.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


def load_and_check_config(filename: str) -> Optional[ConfigParser]:
    """
    Load and validate the configuration file.

    This function loads the configuration file and checks if all required fields are present.

    :param filename: Path to the configuration file.
    :return: ConfigParser object if the file is valid, otherwise None.
    """
    config_object = ConfigParser()

    try:
        with open(filename, 'r') as f:
            config_object.read_file(f)
    except FileNotFoundError:
        raise InvalidConfigFile(f"Config file {filename} not found.")
    except Exception as e:
        raise InvalidConfigFile(f"An error occurred while reading the config file: {e}")

    if check_config(config_object):
        return config_object
    else:
        raise InvalidConfigFile(f"Invalid configuration in {filename}")


def check_config(config_object: ConfigParser) -> bool:
    """
    Validate the contents of the configuration file.

    This function ensures that the required fields are present in the configuration file.

    :param config_object: The loaded ConfigParser object.
    :return: True if the config is valid, False otherwise.
    """
    try:
        # Check required fields exist in the config file
        options_required_keys = ["input_css_files", "output_directory", "django_directory", "django_apps"]
        for key in options_required_keys:
            if not config_object.has_option('SETTINGS', key) or not config_object.get('SETTINGS', key):
                raise InvalidConfigFile(f"Missing or empty key {key} in [OPTIONS]")
        return True

    except Exception as e:
        raise InvalidConfigFile(f"Error while checking config: {str(e)}")


if __name__ == "__main__":
    main()

