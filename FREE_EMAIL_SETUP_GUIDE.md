# Free Email Setup Guide - No Paid Services Required

This guide shows you how to set up email functionality using completely free email providers without any trials, subscriptions, or paid services.

## Option 1: Gmail SMTP (Recommended - Completely Free)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", enable "2-Step Verification"
4. Follow the setup process

### Step 2: Generate App Password
1. After enabling 2FA, go back to Security settings
2. Under "Signing in to Google", click "App passwords"
3. Select "Mail" as the app and "Other" as the device
4. Enter "Django CRM" as the device name
5. Click "Generate" and copy the 16-character password

### Step 3: Update Django Settings
In your `settings.py`, the Gmail configuration is already set up:
```python
EMAIL_HOST_USER = 'callmemutiurrehman@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'your-gmail-app-password'  # Replace with the App Password
```

**Important**: Use the App Password, NOT your regular Gmail password!

### Step 4: Test Email
Run the test command:
```bash
python manage.py test_email_and_fees
```

## Option 2: Outlook/Hotmail SMTP (Completely Free Alternative)

If Gmail doesn't work, you can use Outlook/Hotmail:

### Step 1: Update settings.py
Comment out Gmail settings and uncomment Outlook settings:
```python
# EMAIL_HOST = 'smtp.gmail.com'  # Comment this
EMAIL_HOST = 'smtp-mail.outlook.com'  # Uncomment this
EMAIL_HOST_USER = 'your-email@outlook.com'  # Your Outlook email
EMAIL_HOST_PASSWORD = 'your-outlook-password'  # Your Outlook password
```

### Step 2: Enable Less Secure Apps (if needed)
1. Go to Outlook.com security settings
2. Enable "Less secure app access" if prompted

## Option 3: Yahoo SMTP (Completely Free Alternative)

### Step 1: Generate App Password
1. Go to Yahoo Account Security: https://login.yahoo.com/account/security
2. Enable 2-Step Verification
3. Generate an App Password for "Mail"

### Step 2: Update settings.py
```python
# EMAIL_HOST = 'smtp.gmail.com'  # Comment this
EMAIL_HOST = 'smtp.mail.yahoo.com'  # Uncomment this
EMAIL_HOST_USER = 'your-email@yahoo.com'  # Your Yahoo email
EMAIL_HOST_PASSWORD = 'your-yahoo-app-password'  # Yahoo App Password
```

## Troubleshooting

### If emails still don't send:

1. **Check Windows Firewall**: Make sure ports 587 and 465 are allowed
2. **Try different ports**:
   - Gmail: Try port 465 with `EMAIL_USE_SSL = True` and `EMAIL_USE_TLS = False`
   - Outlook: Try port 25 or 465

3. **Network Issues**: 
   - Try using mobile hotspot
   - Contact your ISP about SMTP blocking
   - Use a VPN if corporate network blocks SMTP

4. **Alternative Free Providers**:
   - ProtonMail Bridge (free tier)
   - Zoho Mail (free tier: 5GB, 25MB attachments)
   - GMX Mail (completely free)

## Why This Solution is Better

✅ **Completely Free**: No trials, no subscriptions, no hidden costs
✅ **No Third-Party Dependencies**: Uses Django's built-in email backend
✅ **Reliable**: Gmail/Outlook/Yahoo have 99.9% uptime
✅ **High Limits**: Gmail allows 500 emails/day, Outlook allows 300/day
✅ **No API Keys**: No need to manage API keys or tokens
✅ **Works Offline**: No internet dependency for configuration

## Security Notes

- Always use App Passwords, never regular passwords
- Keep your App Passwords secure and don't share them
- Enable 2-Factor Authentication for better security
- Consider using environment variables for passwords in production

## Testing

After setup, test with:
```bash
python manage.py test_email_and_fees
```

This will show you if emails are being sent successfully and identify any students with pending fees.