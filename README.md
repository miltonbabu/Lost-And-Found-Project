# Lost and Found Management System

A beginner-friendly web application built with Python, Flask, and SQLite for managing lost and found items in educational institutions, offices, or communities.

## Features

- 🔍 **Report Lost Items**: Users can report lost items with detailed descriptions
- 📦 **Report Found Items**: Users can report items they have found
- 🏆 **Claim Items**: Users can claim items that belong to them
- 📊 **Admin Dashboard**: Management interface for administrators
- 💾 **SQLite Database**: Lightweight, file-based database
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔐 **Status Tracking**: Track item status (unclaimed, claimed, returned)

## Project Structure

```
Lost And Found Project/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── schema.sql            # SQL schema and sample data
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page
│   ├── lost_items.html  # Lost items listing
│   ├── found_items.html # Found items listing
│   ├── report_lost.html # Report lost item form
│   ├── report_found.html # Report found item form
│   ├── view_lost_item.html # Lost item details
│   ├── view_found_item.html # Found item details
│   ├── claim_item.html  # Claim item form
│   └── admin.html       # Admin dashboard
├── static/              # Static files (CSS, JS)
│   ├── css/
│   └── js/
└── README.md           # This file
```

## Database Schema

The system uses three main tables:

### lost_items
- Stores information about reported lost items
- Fields: item_name, category, description, lost_date, location, contact_info, status

### found_items  
- Stores information about reported found items
- Fields: item_name, category, description, found_date, location, contact_info, status

### claims
- Tracks claims made on lost and found items
- Fields: item_type, item_id, claimant_info, claim_description, status

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
Download the project files to your local machine.

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python init_db.py
```
This will create the SQLite database (`lost_and_found.db`) and populate it with sample data.

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Usage

### For Users

1. **Home Page**: View recent lost and found items, and system statistics
2. **Report Lost Item**: Click "Report Lost" and fill in the form with item details
3. **Report Found Item**: Click "Report Found" and fill in the form with item details  
4. **Browse Items**: View all lost or found items in the respective sections
5. **Claim Item**: If you find your item, click "Claim Item" and provide your information

### For Administrators

1. **Admin Dashboard**: Access via the "Admin" link in the navigation
2. **Manage Items**: Update item statuses (unclaimed → claimed → returned)
3. **View Claims**: Monitor and manage item claims
4. **Statistics**: Track overall system performance

## Key Features Explained

### Reporting Process
- Users can report lost items with categories, descriptions, dates, and locations
- Users can report found items with similar details
- Contact information is stored for verification

### Claim Process
- Users provide detailed information to prove ownership
- Claims are stored for administrative review
- Item status is automatically updated when claimed

### Status Management
- **Unclaimed**: Item is available for claiming
- **Claimed**: Item has been claimed but not yet returned
- **Returned**: Item has been successfully returned to owner

## Customization

### Adding Categories
Edit the `category` select options in:
- `templates/report_lost.html`
- `templates/report_found.html`

### Modifying Styles
All styles are included in `templates/base.html`. The design uses clean, modern CSS with:
- Responsive grid layouts
- Card-based components
- Color-coded status badges
- Mobile-friendly navigation

### Database Modifications
To modify the database schema:
1. Update `schema.sql` with your changes
2. Run `python init_db.py` to recreate the database
3. Note: This will delete all existing data

## Sample Data

The system comes with pre-loaded sample data for testing:
- 2 lost items (Wallet, Phone)
- 2 found items (Umbrella, Keys)

## Security Considerations

- Change the `secret_key` in `app.py` for production use
- Implement user authentication for the admin panel in production
- Validate and sanitize all user inputs
- Use HTTPS in production environments

## Troubleshooting

### Common Issues

1. **Database Error**: Make sure you've run `python init_db.py`
2. **Import Error**: Ensure all dependencies are installed via `pip install -r requirements.txt`
3. **Permission Error**: Check file permissions, especially on Windows systems
4. **Port Already in Use**: Change the port in `app.py` or stop other applications using port 5000

### Debug Mode
The application runs in debug mode by default. For production deployment:
```python
app.run(debug=False)
```

## Production Deployment

For production deployment, consider:
1. Using a production-ready WSGI server (Gunicorn, uWSGI)
2. Setting up a reverse proxy (Nginx, Apache)
3. Implementing user authentication
4. Using a production database (PostgreSQL, MySQL)
5. Configuring proper logging
6. Setting up monitoring and backups

## Educational Value

This project is designed to teach:
- Flask web framework fundamentals
- Database operations with SQLite
- CRUD (Create, Read, Update, Delete) operations
- HTML templating with Jinja2
- Form handling and validation
- Web application security basics
- Project organization and structure

## Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Verify all files are in the correct locations
3. Ensure Python and all dependencies are properly installed

## License

This project is provided for educational purposes. Feel free to modify and use it according to your needs.

---

**Happy Coding! 🚀**