
# Django CSS Downsizer

**Django CSS Downsizer** is a Python script designed to optimize and reduce the size of CSS files in Django projects. It identifies unused styles by analyzing your HTML files and then generates a minimized CSS file, leading to a significant reduction in file size (often between 50-90%, depending on the project). Additionally, the script compresses the reduced CSS file using GZIP, further minimizing the size for optimized loading in production environments.

## Features:
- **CSS Optimization**: Automatically removes unused styles, leaving only the CSS needed for your application.
- **Compression**: Uses GZIP to compress the purged CSS file, reducing bandwidth usage and load times.
- **Django-Specific**: Specifically targets and processes HTML files within specified Django app directories.
  
## How It Works:
1. **PurgeCSS**: The script runs PurgeCSS via `npx` to analyze the project's HTML files and eliminate unused styles.
2. **GZIP Compression**: The remaining CSS is then compressed into a `.gz` file, ready for efficient deployment.

## Requirements:
Before running the script, ensure that the following dependencies are installed:

1. **Node.js**: Download and install from [Node.js Official Website](https://nodejs.org/).
2. **npx**: Bundled with Node.js.
3. **PurgeCSS**: Install globally using the following command:
   ```bash
   npm install -g @fullhuman/postcss-purgecss
   ```

4. **Python Dependencies**: The script uses standard Python libraries (`os`, `subprocess`, `gzip`, etc.). Make sure you have a working Python environment.

## Installation:

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/DartLazer/DjangoCSSDownsizer.git
   ```

2. Ensure you have all the [required dependencies](#requirements) installed.

3. Edit the `settings.cfg` file to configure the paths to your Django project and CSS files.

## Configuration:

The script uses a config file (`settings.cfg`) to manage paths for the CSS files and Django project directories. Here's an example of how to set it up:

```ini
[SETTINGS]
django_directory = /path/to/your/django/project
input_css_files = /path/to/your/css/main.css, /path/to/your/css/other.css
output_directory = /path/to/output/directory
django_apps = app1, app2, app3
```

- **`django_directory`**: Path to your Django project root.
- **`input_css_files`**: Comma-separated paths to the CSS files you want to optimize.
- **`output_directory`**: Directory where the optimized CSS files will be saved.
- **`django_apps`**: Comma-separated list of Django app directories to scan for HTML files.

## Usage:

1. Run the script:
   ```bash
   python downsizer.py
   ```

2. The script will process the CSS files, remove unused styles, and output the purged and compressed CSS files in the specified `output_directory`.

## Best Practices:

- **Backup your CSS**: It's a good practice to save the original, unoptimized CSS file in case you need to revert or add new classes.
- **Do not overwrite the original CSS**: Always output the reduced CSS to a new file, such as `theme-reduced.min.css`, to ensure you can modify the original if necessary.
- **Focus on specific apps**: The script scans specified Django app directories for HTML files. Ensure you only target relevant apps to avoid processing unnecessary directories.

## Common Issues:

### 1. Missing Dynamically Generated Classes
#### Issue

When using frameworks like Django with Bootstrap alerts (or similar dynamically assigned classes), CSS classes may not be statically present in the HTML templates. For instance, if you dynamically assign classes like alert-warning, alert-danger, or alert-success based on a Django message's context, these classes might never appear in the HTML files scanned by PurgeCSS. Consequently, PurgeCSS removes them from the final CSS file, causing unexpected display issues (like missing alert styling).

#### Example Scenario:
A Django project with the following block of code in messages_toast.html dynamically assigns a Bootstrap alert class based on the message type.
```
{% if messages %}
  <div class="container mt-3">
    {% for message in messages %}
      <div class="alert alert-{{ message.tags }}" role="alert">
        {{ message }}
      </div>
    {% endfor %}
  </div>
{% endif %}
```

Since alert-warning, alert-danger, and similar classes are assigned conditionally, PurgeCSS might not detect these in its scan, leading to missing CSS for these alert types.

#### Suggested Workaround
To prevent PurgeCSS from removing these essential classes, you can create a dummy HTML file, e.g., purge-css-extra.html, that includes all the alert classes needed for your project. This file is never used in the actual application but serves as a reference for PurgeCSS.
By adding this dummy file, PurgeCSS will identify these classes and retain the corresponding CSS in the final optimized file, ensuring your dynamically assigned classes display as expected.

**Dummy file sample:**
```
<!-- purge-css-extra.html -->
<!-- This file is for PURGECSS to register class names that are otherwise dynamically generated by Django -->

<div class="container mt-3">
  <div class="alert alert-warning" role="alert">
    Empty
  </div>
</div>

<div class="container mt-3">
  etc...
```




## Credits:
- **Author**: Rik Beernink, [Sky-T](https://github.com/DartLazer)
- **PurgeCSS**: This script uses [PurgeCSS](https://purgecss.com/) to detect and remove unused styles. Full credit to the PurgeCSS team for their amazing work.

## License:
This project is licensed under the MIT License. See the LICENSE file for details.
