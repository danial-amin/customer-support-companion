"""SharePoint integration service for document retrieval."""
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import logging
import io
from pathlib import Path

logger = logging.getLogger(__name__)

# Import for type hints only
if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.files.file import File

# Runtime imports
try:
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.files.file import File
    SHAREPOINT_AVAILABLE = True
except ImportError:
    SHAREPOINT_AVAILABLE = False
    # Create a type alias for when library is not available
    ClientContext = Any  # type: ignore
    ClientCredential = Any  # type: ignore
    File = Any  # type: ignore
    logger.warning("Office365-REST-Python-Client not available. SharePoint features will be disabled.")


class SharePointService:
    """Service for connecting to SharePoint and retrieving documents."""
    
    def __init__(self):
        self.available = SHAREPOINT_AVAILABLE
    
    def is_available(self) -> bool:
        """Check if SharePoint service is available."""
        return self.available
    
    def connect(
        self,
        site_url: str,
        tenant_id: str,
        client_id: str,
        client_secret: str
    ) -> Optional[ClientContext]:
        """
        Connect to SharePoint using app-only authentication.
        
        Args:
            site_url: SharePoint site URL (e.g., https://tenant.sharepoint.com/sites/sitename)
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application (client) ID
            client_secret: Azure AD client secret
        
        Returns:
            ClientContext if successful, None otherwise
        """
        if not self.available:
            raise RuntimeError("SharePoint library not available. Please install Office365-REST-Python-Client.")
        
        try:
            credentials = ClientCredential(client_id, client_secret)
            ctx = ClientContext(site_url).with_credentials(credentials)
            # Test connection by getting web
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            logger.info(f"Successfully connected to SharePoint: {site_url}")
            return ctx
        except Exception as e:
            logger.error(f"Failed to connect to SharePoint: {e}")
            raise
    
    def get_documents_from_library(
        self,
        ctx: ClientContext,
        library_name: str = "Documents",
        folder_path: Optional[str] = None,
        file_extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents from a SharePoint document library.
        
        Args:
            ctx: SharePoint client context
            library_name: Name of the document library (default: "Documents")
            folder_path: Optional folder path within the library
            file_extensions: Optional list of file extensions to filter (e.g., ['.pdf', '.docx'])
        
        Returns:
            List of document dictionaries with 'name', 'content', and 'metadata' keys
        """
        if not self.available:
            raise RuntimeError("SharePoint library not available.")
        
        if file_extensions is None:
            file_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.csv']
        
        documents = []
        
        try:
            # Get the document library
            doc_library = ctx.web.lists.get_by_title(library_name)
            
            # Build folder path
            if folder_path:
                folder = doc_library.root_folder.folders.get_by_url(folder_path)
            else:
                folder = doc_library.root_folder
            
            # Get files in folder
            files = folder.files
            ctx.load(files)
            ctx.execute_query()
            
            logger.info(f"Found {len(files)} files in SharePoint library '{library_name}'")
            
            # Process each file
            for file in files:
                try:
                    file_name = file.properties["Name"]
                    file_extension = Path(file_name).suffix.lower()
                    
                    # Filter by extension if specified
                    if file_extensions and file_extension not in file_extensions:
                        continue
                    
                    # Download file content
                    # Office365 library's file.read() returns bytes
                    file_content = file.read()
                    ctx.execute_query()
                    
                    # Ensure content is bytes
                    if isinstance(file_content, str):
                        file_content = file_content.encode('utf-8')
                    elif not isinstance(file_content, bytes):
                        # Handle other types (e.g., bytearray, memoryview)
                        try:
                            file_content = bytes(file_content)
                        except (TypeError, ValueError):
                            logger.error(f"Unable to convert file content to bytes for {file_name}")
                            continue
                    
                    documents.append({
                        "name": file_name,
                        "content": file_content,
                        "extension": file_extension,
                        "metadata": {
                            "source": f"sharepoint://{library_name}/{file_name}",
                            "file_type": file_extension,
                            "library": library_name,
                            "folder": folder_path or "root"
                        }
                    })
                    
                    logger.info(f"Retrieved document: {file_name}")
                    
                except Exception as e:
                    logger.error(f"Error retrieving file {file.properties.get('Name', 'unknown')}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents from SharePoint: {e}")
            raise
    
    def retrieve_and_process_documents(
        self,
        site_url: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        library_name: str = "Documents",
        folder_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Connect to SharePoint and retrieve documents in one call.
        
        Returns:
            List of document dictionaries
        """
        ctx = self.connect(site_url, tenant_id, client_id, client_secret)
        return self.get_documents_from_library(ctx, library_name, folder_path)


# Global instance
sharepoint_service = SharePointService()

