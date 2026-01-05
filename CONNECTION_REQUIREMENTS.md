# Connection Requirements Guide

This document lists all the information you need to connect to SharePoint and external SQL databases.

**🇫🇷 Version Française :** [CONNECTION_REQUIREMENTS_FR.md](./CONNECTION_REQUIREMENTS_FR.md)

## 📋 SharePoint Connection Requirements

To connect to SharePoint and retrieve documents, you need the following information from your SharePoint/Azure AD administrator.

### Required Information

#### 1. SharePoint Site URL
**What it is**: The URL of your SharePoint site  
**Format**: `https://yourtenant.sharepoint.com/sites/sitename` or `https://yourtenant.sharepoint.com`  
**Example**: `https://contoso.sharepoint.com/sites/TotalEnergies`  
**Where to find it**: 
- Open your SharePoint site in a browser
- Copy the URL from the address bar
- Or ask your SharePoint administrator

#### 2. Azure AD Tenant ID
**What it is**: Your organization's Azure Active Directory tenant identifier  
**Format**: GUID (e.g., `12345678-1234-1234-1234-123456789012`)  
**Where to find it**:
- Azure Portal → Azure Active Directory → Overview → Tenant ID
- Or ask your Azure AD administrator

#### 3. Azure AD Application (Client) ID
**What it is**: The ID of the Azure AD app registration used for authentication  
**Format**: GUID (e.g., `87654321-4321-4321-4321-210987654321`)  
**Where to find it**:
- Azure Portal → Azure Active Directory → App registrations → Your app → Overview → Application (client) ID
- Or ask your Azure AD administrator

#### 4. Azure AD Client Secret
**What it is**: A secret key for the Azure AD application  
**Format**: String (e.g., `abc123~XYZ789~secret-key`)  
**Where to find it**:
- Azure Portal → Azure Active Directory → App registrations → Your app → Certificates & secrets → Client secrets
- **Note**: You can only see the secret value when it's first created. If lost, create a new secret.
- Or ask your Azure AD administrator

#### 5. Document Library Name (Optional)
**What it is**: The name of the SharePoint document library to access  
**Default**: `Documents`  
**Examples**: `Documents`, `Shared Documents`, `Fuel Management Docs`  
**Where to find it**: SharePoint site → Look at the left navigation or document libraries

#### 6. Folder Path (Optional)
**What it is**: Specific folder path within the document library  
**Format**: `FolderName/SubFolderName`  
**Example**: `Fuel Reports/2024`  
**Where to find it**: Navigate to the folder in SharePoint and note the path

### How to Set Up Azure AD App Registration

If you need to create the Azure AD app registration:

1. **Go to Azure Portal** → Azure Active Directory → App registrations
2. **Click "New registration"**
3. **Fill in**:
   - Name: `Total Energies Fuel Management AI`
   - Supported account types: Your organization only
   - Redirect URI: Leave blank (not needed for app-only auth)
4. **Click "Register"**
5. **Note the Application (client) ID** and **Directory (tenant) ID**
6. **Create Client Secret**:
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: `Fuel Management AI`
   - Expires: Choose appropriate duration
   - **Copy the secret value immediately** (you won't see it again!)
7. **Grant API Permissions**:
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Microsoft Graph" or "SharePoint"
   - Choose "Application permissions"
   - Add: `Sites.Read.All` or `Sites.ReadWrite.All`
   - Click "Grant admin consent"

### SharePoint Connection Summary

**Required Fields:**
- ✅ SharePoint Site URL
- ✅ Azure AD Tenant ID
- ✅ Azure AD Client ID
- ✅ Azure AD Client Secret

**Optional Fields:**
- Document Library Name (defaults to "Documents")
- Folder Path (if you want a specific folder)

---

## 🗄️ External SQL Database Connection Requirements

To connect to an external SQL database (PostgreSQL, MySQL, SQL Server, etc.), you need the following information.

### Required Information

#### Option 1: Using DATABASE_URL (Single Connection String)

**Format**: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

**Example**: `postgresql://myuser:mypass@db.example.com:5432/mydb`

**Components needed:**
- Database type (postgresql, mysql, mssql, etc.)
- Username
- Password
- Host (server address)
- Port
- Database name

#### Option 2: Using Individual Variables (Recommended)

#### 1. Database Host
**What it is**: The server address or hostname of your database  
**Format**: IP address or domain name  
**Examples**: 
- `db.example.com`
- `192.168.1.100`
- `postgres.railway.internal` (for Railway internal)
- `localhost` (for local databases)

**Where to find it**: Ask your database administrator or check your database hosting provider

#### 2. Database Port
**What it is**: The port number the database listens on  
**Common ports**:
- PostgreSQL: `5432` (default)
- MySQL: `3306` (default)
- SQL Server: `1433` (default)
- Oracle: `1521` (default)

**Where to find it**: Usually the default for your database type, or ask your DBA

#### 3. Database Name
**What it is**: The name of the specific database to connect to  
**Format**: Alphanumeric string (no spaces usually)  
**Examples**: `customersupport`, `fuel_management`, `production_db`  
**Where to find it**: Ask your database administrator

#### 4. Database Username
**What it is**: The username for database authentication  
**Format**: String (usually alphanumeric)  
**Examples**: `postgres`, `admin`, `app_user`  
**Where to find it**: Provided by your database administrator

#### 5. Database Password
**What it is**: The password for database authentication  
**Format**: String (can contain special characters)  
**Where to find it**: Provided by your database administrator  
**⚠️ Security**: Never share or commit passwords to git!

#### 6. SSL Mode (For Cloud/Remote Databases)
**What it is**: Whether to use SSL encryption for the connection  
**Options**:
- `require` - Requires SSL (most cloud databases)
- `prefer` - Prefers SSL, falls back if not available
- `disable` - No SSL (local/trusted networks only)

**Where to find it**: Usually `require` for cloud databases, `disable` for local

### Database Connection Summary

**Required Fields (using DATABASE_URL):**
- ✅ Full connection string: `postgresql://user:pass@host:port/dbname`

**Required Fields (using individual variables):**
- ✅ DB_HOST (database server address)
- ✅ DB_PORT (database port number)
- ✅ DB_NAME (database name)
- ✅ DB_USER (database username)
- ✅ DB_PASSWORD (database password)

**Optional Fields:**
- SSL mode (usually `require` for cloud databases)

---

## 📝 Quick Checklist

### For SharePoint Connection

- [ ] SharePoint Site URL
- [ ] Azure AD Tenant ID
- [ ] Azure AD Client ID
- [ ] Azure AD Client Secret
- [ ] Document Library Name (optional)
- [ ] Folder Path (optional)
- [ ] API Permissions granted (Sites.Read.All)

### For External SQL Database Connection

- [ ] Database Host
- [ ] Database Port
- [ ] Database Name
- [ ] Database Username
- [ ] Database Password
- [ ] SSL Mode (if required)

---

## 🔐 Security Best Practices

### SharePoint Credentials

1. **Store securely**: Use environment variables, never hardcode
2. **Rotate secrets**: Regularly rotate client secrets
3. **Least privilege**: Grant only necessary permissions (Sites.Read.All minimum)
4. **Monitor access**: Review app registrations regularly

### Database Credentials

1. **Strong passwords**: Use complex, randomly generated passwords
2. **Environment variables**: Never commit to git
3. **SSL required**: Always use SSL for remote/cloud databases
4. **Separate users**: Use dedicated database user for application (not admin)
5. **Regular rotation**: Change passwords periodically

---

## 🚀 How to Use These Credentials

### SharePoint Connection

**Via API:**
```json
POST /api/v1/rag/sharepoint
{
  "site_url": "https://yourtenant.sharepoint.com/sites/sitename",
  "tenant_id": "12345678-1234-1234-1234-123456789012",
  "client_id": "87654321-4321-4321-4321-210987654321",
  "client_secret": "your-client-secret",
  "library_name": "Documents",
  "folder_path": "Fuel Reports"
}
```

**Via Frontend:**
- Go to Documents page
- Click "SharePoint" tab
- Fill in the form with the credentials above

### Database Connection

**Via Environment Variables:**

**Option 1: DATABASE_URL**
```bash
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

**Option 2: Individual Variables**
```bash
DB_HOST=your-db-host.com
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

**For Railway:**
- Go to service → Variables tab
- Add the variables above
- Railway will auto-redeploy

---

## 📞 Who to Contact

### For SharePoint Access

- **SharePoint Administrator**: For site URLs and library names
- **Azure AD Administrator**: For tenant ID, client ID, and client secret
- **IT Support**: For app registration setup and permissions

### For Database Access

- **Database Administrator (DBA)**: For all database connection details
- **DevOps Team**: For cloud database credentials
- **IT Support**: For network/firewall access if needed

---

## ❓ Common Questions

### SharePoint

**Q: Do I need admin access to SharePoint?**  
A: No, you just need an Azure AD app registration with appropriate permissions.

**Q: Can I connect to multiple SharePoint sites?**  
A: Yes, use different app registrations or grant access to multiple sites.

**Q: What permissions do I need?**  
A: Minimum: `Sites.Read.All` for reading documents. `Sites.ReadWrite.All` for write access.

### Database

**Q: Can I connect to multiple databases?**  
A: The current setup supports one database connection. For multiple databases, you'd need to modify the code.

**Q: What database types are supported?**  
A: PostgreSQL (primary), but SQLAlchemy supports many databases (MySQL, SQL Server, Oracle, etc.).

**Q: Do I need SSL for local databases?**  
A: No, SSL is only required for remote/cloud databases for security.

---

## 🔍 Verification

### Test SharePoint Connection

1. Use the API endpoint or frontend form
2. Check logs for: "Successfully connected to SharePoint"
3. Verify documents are retrieved

### Test Database Connection

1. Check backend logs for: "Database connection initialized"
2. Test health endpoint: `/api/v1/health` → Should show `"database": true`
3. Try a simple query via the SQL agent

---

## 📚 Additional Resources

- **SharePoint API Documentation**: [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/api/resources/sharepoint)
- **Azure AD App Registration**: [Azure Portal](https://portal.azure.com)
- **PostgreSQL Connection Strings**: [PostgreSQL Docs](https://www.postgresql.org/docs/current/libpq-connect.html)
- **SQLAlchemy Connection**: [SQLAlchemy Docs](https://docs.sqlalchemy.org/en/20/core/engines.html)

---

## 📋 Request Template

Use this template when requesting credentials from your IT team:

### SharePoint Connection Request

```
Subject: SharePoint API Access Request for Fuel Management AI

Hi IT Team,

I need the following information to connect our Fuel Management AI system to SharePoint:

1. SharePoint Site URL: [Please provide]
2. Azure AD Tenant ID: [Please provide]
3. Azure AD Application (Client) ID: [Please provide]
4. Azure AD Client Secret: [Please provide]

Required Permissions:
- Sites.Read.All (minimum) or Sites.ReadWrite.All

Document Library: Documents (or specify if different)
Folder Path: [If specific folder needed]

Please create an Azure AD app registration with the above permissions if one doesn't exist.

Thank you!
```

### External Database Connection Request

```
Subject: Database Connection Details Request for Fuel Management AI

Hi Database Team,

I need the following information to connect our Fuel Management AI system to the external database:

1. Database Host: [Please provide]
2. Database Port: [Please provide - usually 5432 for PostgreSQL]
3. Database Name: [Please provide]
4. Database Username: [Please provide]
5. Database Password: [Please provide]
6. SSL Required: [Yes/No]

Database Type: PostgreSQL (or specify if different)

Please ensure:
- Database user has read access (and write if needed)
- Firewall rules allow connections from [your deployment location]
- SSL is enabled if this is a cloud/remote database

Thank you!
```

---

**Need Help?** Contact your IT administrator or database administrator to obtain these credentials.

