# Apprentice Email Automation System - Complete Documentation

## Project Overview

The Apprentice Email Automation System is a Python-based desktop application designed to automate email communications with apprentices based on their training progress. The system categorizes apprentices by their off-the-job training hours and attendance, then sends targeted emails using customizable templates.

## Architecture Overview

```
Email_Auto/
├── Logic/
│   ├── core/                    # Core business logic
│   │   ├── data_processor.py    # Data processing and categorization
│   │   ├── email_manager.py     # Email sending functionality
│   │   └── template_manager.py  # Email template management
│   ├── ui/                      # User interface components
│   │   ├── main_window.py       # Main application window
│   │   ├── file_upload_tab.py   # File upload interface
│   │   ├── templates_tab.py     # Template editing interface
│   │   ├── send_emails_tab.py   # Email sending interface
│   │   ├── status_tab.py        # Status and reporting
│   │   ├── sending_splash.py    # Progress dialog
│   │   └── splash_screen.py     # Loading screen
│   ├── main.py                  # Application entry point
│   └── email_templates.json     # Saved email templates
```

## Core Components

### 1. DataProcessor (`core/data_processor.py`)

**Purpose**: Handles data loading, preprocessing, and categorization of apprentices.

**Key Methods**:
- `load_file(file_path)`: Loads CSV/Excel files containing apprentice data
- `preprocess_data(data)`: Cleans and standardizes data columns
- `categorize_off_the_job(hrs, dys)`: Categorizes apprentices based on training metrics
- `get_category_data(category)`: Retrieves apprentices in specific categories

**Data Processing Flow**:
1. Load raw data from CSV/Excel files
2. Standardize column names (e.g., "off the job" → "off_the_job")
3. Clean numeric data (remove non-digit characters)
4. Apply categorization logic:
   - **Significantly off-track**: ≥30 hours behind AND >30 days absent
   - **Moderately off-track**: ≥15 hours behind
   - **Slightly off-track**: >10 hours behind
   - **On track**: ≤10 hours behind

**Data Structure**:
```python
{
    "name": "old new",
    "email": "old.new@domain.com",
    "off_the_job": 25,           # Hours behind
    "last_attended": 15,         # Days since last attendance
    "off_track_category": "moderately",
    "hours_behind": 25,          # Alias for templates
    "days_absent": 15            # Alias for templates
}
```

### 2. EmailManager (`core/email_manager.py`)

**Purpose**: Manages SMTP configuration and bulk email sending with progress tracking.

**Key Methods**:
- `configure(config)`: Sets up SMTP server configuration
- `send_bulk_emails(data, templates, progress_callback)`: Sends emails to multiple recipients
- `get_status()`: Returns current sending statistics
- `generate_report()`: Creates detailed sending report

**Email Sending Process**:
1. Establish SMTP connection with configured server
2. For each recipient:
   - Determine appropriate template based on category
   - Replace placeholders with recipient data
   - Send email with error handling
   - Update progress and log results
3. Generate comprehensive sending report

**Status Tracking**:
```python
{
    "total": 100,     # Total emails to send
    "sent": 85,       # Successfully sent
    "failed": 15      # Failed to send
}
```

### 3. TemplateManager (`core/template_manager.py`)

**Purpose**: Manages email templates with dynamic placeholder replacement.

**Built-in Templates**:

1. **Significantly Off-Track**:
   - Subject: "Attendance and OTJ Logging - Action Required"
   - Includes manager escalation and meeting requirement

2. **Moderately Off-Track**:
   - Subject: "OTJ Logging - Power Hour Session"
   - Schedules mandatory training session with opt-out option

3. **Slightly Off-Track**:
   - Subject: "OTJ Logging Required"
   - Provides deadline for logging hours

4. **On Track**:
   - Subject: "Great Progress - Keep It Up!"
   - Positive reinforcement message

**Placeholder System**:
- `{name}`: Apprentice name
- `{off_the_job}`: Hours behind
- `{last_attended}`: Days since attendance
- `{power_hour_date}`: Auto-calculated date (5 days from today)
- `{deadline_date}`: Auto-calculated date (7 days from today)

## User Interface Components

### 1. MainWindow (`ui/main_window.py`)

**Purpose**: Main application container with DPI scaling and tab management.

**Features**:
- Responsive design with DPI awareness
- Tab-based interface
- Component coordination and callbacks
- Window resize handling

### 2. FileUploadTab (`ui/file_upload_tab.py`)

**Purpose**: File selection and data preview interface.

**Functionality**:
- File browser for CSV/Excel files
- Data preview with scrollable table
- File validation and error handling
- Integration with DataProcessor

### 3. SendEmailsTab (`ui/send_emails_tab.py`)

**Purpose**: Email configuration and sending interface.

**Features**:
- SMTP server configuration
- Category-specific sending buttons
- Progress tracking per category
- Bulk email sending option

**UI Layout**:
- Email configuration section (SMTP settings)
- Overall progress section
- Category-specific sections with individual progress bars
- Send buttons for targeted campaigns

### 4. TemplatesTab (`ui/templates_tab.py`)

**Purpose**: Email template editing and management.

**Features**:
- Template selection dropdown
- Subject and body editing
- Live preview with sample data
- Template validation
- Save/load functionality

### 5. StatusTab (`ui/status_tab.py`)

**Purpose**: Email sending status and reporting.

**Features**:
- Status overview cards (Total, Sent, Failed)
- Detailed report generation
- Success rate calculation
- Error analysis

## Data Flow

1. **Data Loading**:
   ```
   User selects file → FileUploadTab → DataProcessor.load_file()
   → Data preprocessing → Category assignment → UI update
   ```

2. **Email Sending**:
   ```
   User configures SMTP → Selects category → SendEmailsTab
   → EmailManager.send_bulk_emails() → Template processing
   → SMTP sending → Progress updates → Status reporting
   ```

3. **Template Management**:
   ```
   User selects template → TemplatesTab → TemplateManager
   → Edit content → Preview → Save → JSON persistence
   ```

## Configuration

### SMTP Configuration
```python
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@domain.com",
    "sender_password": "app-password"
}
```

### File Format Requirements
- **CSV/Excel files** with columns:
  - Name/First Name/Apprentice (apprentice name)
  - Email/email (email address)
  - "off the job"/"Off the Job" (hours behind)
  - "last attended"/"Last Attended" (days since attendance)

## Error Handling

### Data Processing Errors
- Invalid file formats
- Missing required columns
- Data type conversion errors
- Empty datasets

### Email Sending Errors
- SMTP authentication failures
- Invalid email addresses
- Network connectivity issues
- Server rate limiting

### UI Error Handling
- User-friendly error messages
- Progress indication during long operations
- Graceful degradation for missing data

## Security Considerations

- Email passwords stored in memory only (not persisted)
- SMTP connections use TLS encryption
- Input validation for all user data
- Error messages don't expose sensitive information

## Performance Optimizations

- Threaded email sending to prevent UI blocking
- Progress callbacks for user feedback
- Data caching to avoid reprocessing
- Efficient pandas operations for large datasets

## Extension Points

### Adding New Categories
1. Update `categorize_off_the_job()` logic in DataProcessor
2. Add new template in TemplateManager
3. Update UI components to handle new category

### Custom Templates
1. Templates stored in JSON format
2. Placeholder system supports dynamic content
3. Template validation ensures required fields

### Additional Data Sources
1. Extend DataProcessor to support new file formats
2. Add data validation for new column types
3. Update UI to handle new data structures

## Dependencies

- **customtkinter**: Modern UI framework
- **pandas**: Data processing and analysis
- **openpyxl**: Excel file support
- **smtplib**: Email sending (built-in)
- **threading**: Concurrent operations (built-in)
- **tkinter**: Base UI framework (built-in)

## Usage Workflow

1. **Setup**: Launch application, configure SMTP settings
2. **Data Import**: Upload apprentice data file (CSV/Excel)
3. **Review**: Preview data and verify categorization
4. **Customize**: Edit email templates if needed
5. **Send**: Choose category-specific or bulk sending
6. **Monitor**: Track progress and review results
7. **Report**: Generate and export sending reports

## Troubleshooting

### Common Issues
- **File not loading**: Check file format and column names
- **Emails not sending**: Verify SMTP configuration and credentials
- **Template errors**: Check placeholder syntax and required fields
- **UI not responding**: Large datasets may require processing time

### Debug Information
- Console output shows detailed error messages
- Sending log tracks all email attempts
- Status tab provides comprehensive reporting

This documentation provides a complete overview of the system architecture, functionality, and usage patterns for the Apprentice Email Automation System.
