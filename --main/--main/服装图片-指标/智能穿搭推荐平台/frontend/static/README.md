# Frontend Static Files

This directory contains all frontend static assets:

- `css/` - Stylesheets
- `js/` - JavaScript files
- `images/` - Image assets
- `uploads/` - User uploaded files

## Usage

In HTML templates, reference static files using Flask's `url_for`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```
