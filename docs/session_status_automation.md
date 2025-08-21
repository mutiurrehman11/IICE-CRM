# Session Status Automation Documentation

## Overview
This document describes the automatic session status transition system that marks sessions as 'Completed' when their end date has passed.

## Components

### 1. Management Command
**File:** `Admin/management/commands/complete_expired_sessions.py`

**Purpose:** Batch process to update expired sessions to 'Completed' status.

**Usage:**
```bash
python manage.py complete_expired_sessions
```

### 2. Middleware
**File:** `Admin/middleware.py`

**Purpose:** Real-time session status updates on every web request.

**Configuration:** Added to `MIDDLEWARE` in `settings.py` as `Admin.middleware.SessionStatusMiddleware`

## Automated Scheduling Setup

### Option 1: Windows Task Scheduler (Recommended for Windows)

1. **Open Task Scheduler:**
   - Press `Win + R`, type `taskschd.msc`, and press Enter

2. **Create Basic Task:**
   - Click "Create Basic Task" in the Actions panel
   - Name: "Complete Expired Sessions"
   - Description: "Automatically mark expired sessions as completed"

3. **Set Trigger:**
   - Choose "Daily"
   - Set start time (recommended: 12:01 AM)
   - Recur every: 1 day

4. **Set Action:**
   - Choose "Start a program"
   - Program/script: `C:\path\to\python.exe` (your Python installation)
   - Arguments: `manage.py complete_expired_sessions`
   - Start in: `C:\Users\Afnan Awan\Downloads\CRM\IICE-CRM`

5. **Finish and Test:**
   - Review settings and click "Finish"
   - Right-click the task and select "Run" to test

### Option 2: PowerShell Scheduled Job

```powershell
# Create a scheduled job that runs daily at midnight
$trigger = New-JobTrigger -Daily -At "12:01 AM"
$scriptBlock = {
    Set-Location "C:\Users\Afnan Awan\Downloads\CRM\IICE-CRM"
    python manage.py complete_expired_sessions
}

Register-ScheduledJob -Name "CompleteExpiredSessions" -ScriptBlock $scriptBlock -Trigger $trigger
```

### Option 3: Batch Script with Task Scheduler

1. **Create batch file** (`complete_sessions.bat`):
```batch
@echo off
cd /d "C:\Users\Afnan Awan\Downloads\CRM\IICE-CRM"
python manage.py complete_expired_sessions
```

2. **Schedule the batch file** using Task Scheduler (follow Option 1 steps but use the .bat file)

## Monitoring and Logging

### System Notifications
- Automatic notifications are created for the superuser when sessions are completed
- Check the notifications panel in the admin dashboard

### Django Logging
- The middleware logs session completion activities
- Check Django logs for detailed information about processed sessions

### Manual Verification
- Visit the "Completed Sessions" page in the admin panel
- Check that sessions with past end dates have 'Completed' status

## Troubleshooting

### Common Issues

1. **Command not found:**
   - Ensure Python is in your system PATH
   - Use full path to Python executable

2. **Permission errors:**
   - Run Task Scheduler as Administrator
   - Ensure the user account has necessary permissions

3. **Database connection issues:**
   - Verify Django settings are correct
   - Check database connectivity

### Testing the Setup

1. **Test the management command manually:**
   ```bash
   python manage.py complete_expired_sessions
   ```

2. **Create a test session with past end date:**
   - Add a session with end_date in the past
   - Run the command or wait for middleware to process
   - Verify status changes to 'Completed'

3. **Check notifications:**
   - Look for system notifications about completed sessions
   - Verify notification content is accurate

## Best Practices

1. **Run daily:** Schedule the command to run once per day during off-peak hours
2. **Monitor logs:** Regularly check logs for any errors or issues
3. **Backup data:** Ensure regular database backups before status changes
4. **Test changes:** Always test in a development environment first

## Security Considerations

- The scheduled task should run with minimal required permissions
- Ensure the Django application has proper database access controls
- Monitor for any unauthorized access to the management command

## Support

For issues with the session status automation system:
1. Check the Django application logs
2. Verify the scheduled task is running correctly
3. Test the management command manually
4. Review the middleware configuration in settings.py