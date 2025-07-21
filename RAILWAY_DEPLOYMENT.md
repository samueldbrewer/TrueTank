# Railway Sample Data Deployment Guide

## Overview
This guide walks you through deploying the TrueTank sample data from your local development environment to your Railway production database.

## Sample Data Contents
The export contains **94 total records**:
- 4 Locations (Pewee Valley, KY area)
- 4 Team Members (with certifications)
- 4 Trucks (fully equipped)
- 25 Customers (Kentucky area)
- 18 Septic Systems (realistic data)
- 39 Tickets (today/tomorrow schedule)

## Pre-Deployment Checklist

### 1. Files Ready for Deployment
Ensure these files are in your project:
- ✅ `sample_data_export_20250711_084627.json` (78KB export file)
- ✅ `import_sample_data.py` (import script)
- ✅ `deploy_sample_data.py` (Railway deployment script)

### 2. Railway Environment Setup
Your Railway project should have:
- PostgreSQL database addon
- Environment variables configured
- Latest code deployed

## Deployment Methods

### Method 1: Railway CLI (Recommended)
```bash
# 1. Login to Railway
railway login

# 2. Link to your project
railway link

# 3. Run the deployment script
railway run python deploy_sample_data.py
```

### Method 2: Railway Dashboard
1. Go to your Railway project dashboard
2. Navigate to the "Deployments" tab
3. Click "Deploy" > "Deploy from GitHub"
4. The deployment script will run automatically if configured

### Method 3: Manual Database Connection
If you have direct database access:
```bash
# 1. Get your Railway PostgreSQL connection string
railway variables

# 2. Set the DATABASE_URL environment variable
export DATABASE_URL="your_railway_postgres_url"

# 3. Run the import script directly
python import_sample_data.py sample_data_export_20250711_084627.json
```

## What the Deployment Script Does

1. **Environment Detection**: Checks if running on Railway
2. **File Discovery**: Finds the latest `sample_data_export_*.json` file
3. **Data Import**: Calls the import script to populate the database
4. **Verification**: Confirms all records were imported successfully

## Expected Output
```
🚀 TrueTank Sample Data Deployment
==================================================
🌐 Environment: production
📁 Using data file: sample_data_export_20250711_084627.json
🗑️  Clearing existing data...
  ✅ Existing data cleared
📍 Importing locations...
  ✅ Imported 4 locations
👥 Importing team members...
  ✅ Imported 4 team members
🚛 Importing trucks...
  ✅ Imported 4 trucks
👨‍👩‍👧‍👦 Importing customers...
  ✅ Imported 25 customers
🏠 Importing septic systems...
  ✅ Imported 18 septic systems
🎫 Importing tickets...
  ✅ Imported 39 tickets
🎉 Import completed successfully!
✅ Sample data deployment completed!
🌐 Ready for testing on Railway!
```

## Post-Deployment Verification

### 1. Test the Job Board
Visit your Railway app URL and check:
- Job board loads with today's date
- Tickets are properly distributed across truck columns
- Map functionality works for each truck
- Drag and drop works between columns

### 2. Verify Database Records
Check that all data imported correctly:
- Customers have proper addresses in Kentucky
- Septic systems are linked to customers
- Tickets have proper scheduling for today/tomorrow
- Team members have certifications and home addresses

### 3. Test Core Features
- Create new tickets
- Assign trucks to different dates
- Use the map feature
- Drag tickets between columns

## Troubleshooting

### Common Issues

**Issue**: "No sample data export files found"
**Solution**: Ensure the JSON file is deployed with your app code

**Issue**: "Database connection failed"
**Solution**: Verify your Railway PostgreSQL addon is active and DATABASE_URL is set

**Issue**: "Import failed - foreign key constraint"
**Solution**: The script clears existing data first, this should not happen

### Getting Help
If deployment fails:
1. Check Railway logs in the dashboard
2. Verify your database addon is running
3. Ensure all required environment variables are set
4. Try the manual database connection method

## Data Reset
To reset the data in the future:
```bash
# Re-run the deployment script to clear and reload all data
railway run python deploy_sample_data.py
```

## Security Notes
- The sample data uses realistic but fictional information
- No real customer data is included
- All coordinates are approximate locations in Kentucky
- Phone numbers and emails are test data only

---

**Ready to deploy?** Use Method 1 (Railway CLI) for the best experience!