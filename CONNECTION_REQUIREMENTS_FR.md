# Guide des Exigences de Connexion

Ce document liste toutes les informations nécessaires pour se connecter à SharePoint et aux bases de données SQL externes.

**🇬🇧 English Version :** [CONNECTION_REQUIREMENTS.md](./CONNECTION_REQUIREMENTS.md)

## 📋 Exigences de Connexion SharePoint

Pour vous connecter à SharePoint et récupérer des documents, vous avez besoin des informations suivantes de votre administrateur SharePoint/Azure AD.

### Informations Requises

#### 1. URL du Site SharePoint
**Qu'est-ce que c'est** : L'URL de votre site SharePoint  
**Format** : `https://yourtenant.sharepoint.com/sites/sitename` ou `https://yourtenant.sharepoint.com`  
**Exemple** : `https://contoso.sharepoint.com/sites/TotalEnergies`  
**Où le trouver** : 
- Ouvrez votre site SharePoint dans un navigateur
- Copiez l'URL depuis la barre d'adresse
- Ou demandez à votre administrateur SharePoint

#### 2. ID de Locataire Azure AD
**Qu'est-ce que c'est** : L'identifiant du locataire Azure Active Directory de votre organisation  
**Format** : GUID (ex. `12345678-1234-1234-1234-123456789012`)  
**Où le trouver** :
- Portail Azure → Azure Active Directory → Vue d'ensemble → ID de locataire
- Ou demandez à votre administrateur Azure AD

#### 3. ID d'Application Azure AD (Client)
**Qu'est-ce que c'est** : L'ID de l'enregistrement d'application Azure AD utilisé pour l'authentification  
**Format** : GUID (ex. `87654321-4321-4321-4321-210987654321`)  
**Où le trouver** :
- Portail Azure → Azure Active Directory → Inscriptions d'applications → Votre application → Vue d'ensemble → ID d'application (client)
- Ou demandez à votre administrateur Azure AD

#### 4. Secret Client Azure AD
**Qu'est-ce que c'est** : Une clé secrète pour l'application Azure AD  
**Format** : Chaîne de caractères (ex. `abc123~XYZ789~secret-key`)  
**Où le trouver** :
- Portail Azure → Azure Active Directory → Inscriptions d'applications → Votre application → Certificats et secrets → Secrets clients
- **Note** : Vous ne pouvez voir la valeur du secret que lors de sa création. S'il est perdu, créez un nouveau secret.
- Ou demandez à votre administrateur Azure AD

#### 5. Nom de la Bibliothèque de Documents (Optionnel)
**Qu'est-ce que c'est** : Le nom de la bibliothèque de documents SharePoint à accéder  
**Par défaut** : `Documents`  
**Exemples** : `Documents`, `Documents partagés`, `Documents Gestion Carburant`  
**Où le trouver** : Site SharePoint → Regardez la navigation de gauche ou les bibliothèques de documents

#### 6. Chemin du Dossier (Optionnel)
**Qu'est-ce que c'est** : Chemin de dossier spécifique dans la bibliothèque de documents  
**Format** : `NomDossier/SousDossier`  
**Exemple** : `Rapports Carburant/2024`  
**Où le trouver** : Naviguez vers le dossier dans SharePoint et notez le chemin

### Comment Configurer l'Enregistrement d'Application Azure AD

Si vous devez créer l'enregistrement d'application Azure AD :

1. **Allez sur le Portail Azure** → Azure Active Directory → Inscriptions d'applications
2. **Cliquez sur "Nouvelle inscription"**
3. **Remplissez** :
   - Nom : `Total Energies Fuel Management AI`
   - Types de comptes pris en charge : Uniquement les comptes de cet annuaire organisationnel
   - URI de redirection : Laissez vide (pas nécessaire pour l'authentification app-only)
4. **Cliquez sur "Inscrire"**
5. **Notez l'ID d'application (client)** et l'**ID de répertoire (locataire)**
6. **Créez un Secret Client** :
   - Allez dans "Certificats et secrets"
   - Cliquez sur "Nouveau secret client"
   - Description : `Fuel Management AI`
   - Expire : Choisissez une durée appropriée
   - **Copiez la valeur du secret immédiatement** (vous ne la reverrez plus !)
7. **Accordez les Permissions API** :
   - Allez dans "Permissions API"
   - Cliquez sur "Ajouter une permission"
   - Sélectionnez "Microsoft Graph" ou "SharePoint"
   - Choisissez "Permissions d'application"
   - Ajoutez : `Sites.Read.All` ou `Sites.ReadWrite.All`
   - Cliquez sur "Accorder le consentement administrateur"

### Résumé de la Connexion SharePoint

**Champs Requis :**
- ✅ URL du Site SharePoint
- ✅ ID de Locataire Azure AD
- ✅ ID Client Azure AD
- ✅ Secret Client Azure AD

**Champs Optionnels :**
- Nom de la Bibliothèque de Documents (par défaut "Documents")
- Chemin du Dossier (si vous voulez un dossier spécifique)

---

## 🗄️ Exigences de Connexion Base de Données SQL Externe

Pour vous connecter à une base de données SQL externe (PostgreSQL, MySQL, SQL Server, etc.), vous avez besoin des informations suivantes.

### Informations Requises

#### Option 1 : Utiliser DATABASE_URL (Chaîne de Connexion Unique)

**Format** : `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

**Exemple** : `postgresql://myuser:mypass@db.example.com:5432/mydb`

**Composants nécessaires :**
- Type de base de données (postgresql, mysql, mssql, etc.)
- Nom d'utilisateur
- Mot de passe
- Hôte (adresse du serveur)
- Port
- Nom de la base de données

#### Option 2 : Utiliser des Variables Individuelles (Recommandé)

#### 1. Hôte de la Base de Données
**Qu'est-ce que c'est** : L'adresse du serveur ou le nom d'hôte de votre base de données  
**Format** : Adresse IP ou nom de domaine  
**Exemples** : 
- `db.example.com`
- `192.168.1.100`
- `postgres.railway.internal` (pour Railway interne)
- `localhost` (pour bases de données locales)

**Où le trouver** : Demandez à votre administrateur de base de données ou vérifiez votre fournisseur d'hébergement de base de données

#### 2. Port de la Base de Données
**Qu'est-ce que c'est** : Le numéro de port sur lequel la base de données écoute  
**Ports courants** :
- PostgreSQL : `5432` (par défaut)
- MySQL : `3306` (par défaut)
- SQL Server : `1433` (par défaut)
- Oracle : `1521` (par défaut)

**Où le trouver** : Généralement la valeur par défaut pour votre type de base de données, ou demandez à votre DBA

#### 3. Nom de la Base de Données
**Qu'est-ce que c'est** : Le nom de la base de données spécifique à laquelle se connecter  
**Format** : Chaîne alphanumérique (généralement sans espaces)  
**Exemples** : `customersupport`, `fuel_management`, `production_db`  
**Où le trouver** : Demandez à votre administrateur de base de données

#### 4. Nom d'Utilisateur de la Base de Données
**Qu'est-ce que c'est** : Le nom d'utilisateur pour l'authentification de la base de données  
**Format** : Chaîne (généralement alphanumérique)  
**Exemples** : `postgres`, `admin`, `app_user`  
**Où le trouver** : Fourni par votre administrateur de base de données

#### 5. Mot de Passe de la Base de Données
**Qu'est-ce que c'est** : Le mot de passe pour l'authentification de la base de données  
**Format** : Chaîne (peut contenir des caractères spéciaux)  
**Où le trouver** : Fourni par votre administrateur de base de données  
**⚠️ Sécurité** : Ne partagez jamais et ne commitez jamais les mots de passe dans git !

#### 6. Mode SSL (Pour Bases de Données Cloud/Distantes)
**Qu'est-ce que c'est** : S'il faut utiliser le chiffrement SSL pour la connexion  
**Options** :
- `require` - Exige SSL (la plupart des bases de données cloud)
- `prefer` - Préfère SSL, revient en arrière si non disponible
- `disable` - Pas de SSL (réseaux locaux/de confiance uniquement)

**Où le trouver** : Généralement `require` pour les bases de données cloud, `disable` pour les locales

### Résumé de la Connexion Base de Données

**Champs Requis (en utilisant DATABASE_URL) :**
- ✅ Chaîne de connexion complète : `postgresql://user:pass@host:port/dbname`

**Champs Requis (en utilisant des variables individuelles) :**
- ✅ DB_HOST (adresse du serveur de base de données)
- ✅ DB_PORT (numéro de port de la base de données)
- ✅ DB_NAME (nom de la base de données)
- ✅ DB_USER (nom d'utilisateur de la base de données)
- ✅ DB_PASSWORD (mot de passe de la base de données)

**Champs Optionnels :**
- Mode SSL (généralement `require` pour les bases de données cloud)

---

## 📝 Liste de Vérification Rapide

### Pour la Connexion SharePoint

- [ ] URL du Site SharePoint
- [ ] ID de Locataire Azure AD
- [ ] ID Client Azure AD
- [ ] Secret Client Azure AD
- [ ] Nom de la Bibliothèque de Documents (optionnel)
- [ ] Chemin du Dossier (optionnel)
- [ ] Permissions API accordées (Sites.Read.All)

### Pour la Connexion Base de Données SQL Externe

- [ ] Hôte de la Base de Données
- [ ] Port de la Base de Données
- [ ] Nom de la Base de Données
- [ ] Nom d'Utilisateur de la Base de Données
- [ ] Mot de Passe de la Base de Données
- [ ] Mode SSL (si requis)

---

## 🔐 Bonnes Pratiques de Sécurité

### Identifiants SharePoint

1. **Stockage sécurisé** : Utilisez des variables d'environnement, ne jamais coder en dur
2. **Rotation des secrets** : Faites tourner régulièrement les secrets clients
3. **Principe du moindre privilège** : Accordez uniquement les permissions nécessaires (Sites.Read.All minimum)
4. **Surveillance de l'accès** : Examinez régulièrement les enregistrements d'applications

### Identifiants Base de Données

1. **Mots de passe forts** : Utilisez des mots de passe complexes générés aléatoirement
2. **Variables d'environnement** : Ne jamais commiter dans git
3. **SSL requis** : Utilisez toujours SSL pour les bases de données distantes/cloud
4. **Utilisateurs séparés** : Utilisez un utilisateur de base de données dédié pour l'application (pas admin)
5. **Rotation régulière** : Changez les mots de passe périodiquement

---

## 🚀 Comment Utiliser Ces Identifiants

### Connexion SharePoint

**Via API :**
```json
POST /api/v1/rag/sharepoint
{
  "site_url": "https://yourtenant.sharepoint.com/sites/sitename",
  "tenant_id": "12345678-1234-1234-1234-123456789012",
  "client_id": "87654321-4321-4321-4321-210987654321",
  "client_secret": "your-client-secret",
  "library_name": "Documents",
  "folder_path": "Rapports Carburant"
}
```

**Via Interface Frontend :**
- Allez à la page Documents
- Cliquez sur l'onglet "SharePoint"
- Remplissez le formulaire avec les identifiants ci-dessus

### Connexion Base de Données

**Via Variables d'Environnement :**

**Option 1 : DATABASE_URL**
```bash
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

**Option 2 : Variables Individuelles**
```bash
DB_HOST=your-db-host.com
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

**Pour Railway :**
- Allez dans service → Onglet Variables
- Ajoutez les variables ci-dessus
- Railway redéploiera automatiquement

---

## 📞 Qui Contacter

### Pour l'Accès SharePoint

- **Administrateur SharePoint** : Pour les URLs de sites et noms de bibliothèques
- **Administrateur Azure AD** : Pour l'ID de locataire, l'ID client et le secret client
- **Support IT** : Pour la configuration de l'enregistrement d'application et les permissions

### Pour l'Accès Base de Données

- **Administrateur de Base de Données (DBA)** : Pour tous les détails de connexion à la base de données
- **Équipe DevOps** : Pour les identifiants de base de données cloud
- **Support IT** : Pour l'accès réseau/firewall si nécessaire

---

## ❓ Questions Fréquentes

### SharePoint

**Q : Ai-je besoin d'un accès administrateur à SharePoint ?**  
R : Non, vous avez juste besoin d'un enregistrement d'application Azure AD avec les permissions appropriées.

**Q : Puis-je me connecter à plusieurs sites SharePoint ?**  
R : Oui, utilisez différents enregistrements d'applications ou accordez l'accès à plusieurs sites.

**Q : Quelles permissions ai-je besoin ?**  
R : Minimum : `Sites.Read.All` pour lire les documents. `Sites.ReadWrite.All` pour l'accès en écriture.

### Base de Données

**Q : Puis-je me connecter à plusieurs bases de données ?**  
R : La configuration actuelle prend en charge une connexion de base de données. Pour plusieurs bases de données, vous devriez modifier le code.

**Q : Quels types de bases de données sont pris en charge ?**  
R : PostgreSQL (principal), mais SQLAlchemy prend en charge de nombreuses bases de données (MySQL, SQL Server, Oracle, etc.).

**Q : Ai-je besoin de SSL pour les bases de données locales ?**  
R : Non, SSL est uniquement requis pour les bases de données distantes/cloud pour la sécurité.

---

## 🔍 Vérification

### Tester la Connexion SharePoint

1. Utilisez le point de terminaison API ou le formulaire frontend
2. Vérifiez les logs pour : "Successfully connected to SharePoint"
3. Vérifiez que les documents sont récupérés

### Tester la Connexion Base de Données

1. Vérifiez les logs backend pour : "Database connection initialized"
2. Testez le point de terminaison de santé : `/api/v1/health` → Devrait afficher `"database": true`
3. Essayez une requête simple via l'agent SQL

---

## 📚 Ressources Supplémentaires

- **Documentation API SharePoint** : [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/api/resources/sharepoint)
- **Enregistrement d'Application Azure AD** : [Portail Azure](https://portal.azure.com)
- **Chaînes de Connexion PostgreSQL** : [Documentation PostgreSQL](https://www.postgresql.org/docs/current/libpq-connect.html)
- **Connexion SQLAlchemy** : [Documentation SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/engines.html)

---

## 📋 Modèle de Demande

Utilisez ce modèle lors de la demande d'identifiants auprès de votre équipe IT :

### Demande de Connexion SharePoint

```
Objet : Demande d'Accès API SharePoint pour Fuel Management AI

Bonjour Équipe IT,

J'ai besoin des informations suivantes pour connecter notre système Fuel Management AI à SharePoint :

1. URL du Site SharePoint : [Veuillez fournir]
2. ID de Locataire Azure AD : [Veuillez fournir]
3. ID d'Application Azure AD (Client) : [Veuillez fournir]
4. Secret Client Azure AD : [Veuillez fournir]

Permissions Requises :
- Sites.Read.All (minimum) ou Sites.ReadWrite.All

Bibliothèque de Documents : Documents (ou spécifiez si différent)
Chemin du Dossier : [Si dossier spécifique nécessaire]

Veuillez créer un enregistrement d'application Azure AD avec les permissions ci-dessus si un n'existe pas.

Merci !
```

### Demande de Connexion Base de Données Externe

```
Objet : Demande de Détails de Connexion Base de Données pour Fuel Management AI

Bonjour Équipe Base de Données,

J'ai besoin des informations suivantes pour connecter notre système Fuel Management AI à la base de données externe :

1. Hôte de la Base de Données : [Veuillez fournir]
2. Port de la Base de Données : [Veuillez fournir - généralement 5432 pour PostgreSQL]
3. Nom de la Base de Données : [Veuillez fournir]
4. Nom d'Utilisateur de la Base de Données : [Veuillez fournir]
5. Mot de Passe de la Base de Données : [Veuillez fournir]
6. SSL Requis : [Oui/Non]

Type de Base de Données : PostgreSQL (ou spécifiez si différent)

Veuillez vous assurer :
- L'utilisateur de la base de données a un accès en lecture (et en écriture si nécessaire)
- Les règles de pare-feu permettent les connexions depuis [votre emplacement de déploiement]
- SSL est activé si c'est une base de données cloud/distante

Merci !
```

---

**Besoin d'Aide ?** Contactez votre administrateur IT ou votre administrateur de base de données pour obtenir ces identifiants.

