"""
Módulo de gestión de Google Drive
Maneja la búsqueda y descarga de archivos PDF desde Google Drive
"""

import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import pandas as pd
from typing import List, Dict, Optional
import zipfile
from datetime import datetime
import time

class DriveManager:
    """Gestiona la búsqueda y descarga de facturas desde Google Drive"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self):
        """Inicializa la conexión con Google Drive"""
        self.service = None
        self.folder_id = st.secrets.get("drive_folder_id", "")
        self.creds = None
        
        # Intentar restaurar credenciales si existen
        if 'google_drive_creds' in st.session_state:
            try:
                self.creds = st.session_state.google_drive_creds
                self.service = build('drive', 'v3', credentials=self.creds)
            except:
                pass
    
    def authenticate(self):
        """Autentica con Google Drive usando OAuth"""
        
        # Verificar si ya hay credenciales en session_state
        if 'google_drive_creds' in st.session_state:
            try:
                self.creds = st.session_state.google_drive_creds
                self.service = build('drive', 'v3', credentials=self.creds)
                return True
            except Exception as e:
                st.error(f"Error al restaurar credenciales: {str(e)}")
                if 'google_drive_creds' in st.session_state:
                    del st.session_state.google_drive_creds
        
        # Mostrar instrucciones de autenticación
        st.info("🔐 Necesitas autorizar el acceso a Google Drive")
        
        with st.expander("📖 ¿Cómo autorizar?", expanded=True):
            st.markdown("""
            **Sigue estos pasos:**
            
            1. Click en el botón "Generar URL de autorización"
            2. Copia la URL que aparece abajo
            3. Pégala en una nueva pestaña del navegador
            4. Inicia sesión con: **maleja8005@gmail.com**
            5. Acepta los permisos
            6. Copia el código que aparece
            7. Pégalo en el campo de abajo
            """)
        
        if st.button("🔑 Generar URL de autorización", type="primary", key="btn_gen_auth_url"):
            try:
                # Verificar que las credenciales existan
                if not st.secrets.get("client_id") or not st.secrets.get("client_secret"):
                    st.error("❌ Faltan credenciales en secrets.toml")
                    return False
                
                # Crear configuración del cliente
                client_config = {
                    "installed": {
                        "client_id": st.secrets["client_id"],
                        "client_secret": st.secrets["client_secret"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
                    }
                }
                
                # Crear flujo de OAuth
                flow = InstalledAppFlow.from_client_config(
                    client_config,
                    scopes=self.SCOPES
                )
                
                # Generar URL de autorización - método manual
                flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
                auth_url, _ = flow.authorization_url(
                    access_type='offline',
                    prompt='consent'
                )
                
                # Guardar flow en session state
                st.session_state.oauth_flow = flow
                
                # Mostrar URL para copiar
                st.success("✅ URL generada correctamente")
                st.markdown("### 📋 Copia esta URL y ábrela en una nueva pestaña:")
                st.code(auth_url, language=None)
                
                # Botón para abrir directamente
                st.markdown(f"O haz click aquí: [Abrir en nueva pestaña]({auth_url})")
                
                st.warning("⚠️ Después de autorizar con **maleja8005@gmail.com**, Google te mostrará un código. Cópialo y pégalo abajo.")
                
            except Exception as e:
                st.error(f"❌ Error al generar URL: {str(e)}")
                st.code(f"Detalles del error:\n{str(e)}")
                
                # Mostrar información de debug
                with st.expander("🔍 Información de debug"):
                    st.write("Client ID:", st.secrets.get("client_id", "NO ENCONTRADO")[:50] + "...")
                    st.write("Client Secret:", "****" + st.secrets.get("client_secret", "NO ENCONTRADO")[-4:] if st.secrets.get("client_secret") else "NO ENCONTRADO")
                
                return False
        
        # Campo para pegar el código
        if 'oauth_flow' in st.session_state:
            st.markdown("---")
            st.markdown("### 🔑 Paso 2: Ingresa el código de autorización")
            
            auth_code = st.text_input(
                "Pega el código aquí:",
                type="default",
                key="auth_code_input",
                help="Copia el código que Google te mostró después de autorizar"
            )
            
            if st.button("✅ Conectar con este código", type="primary", key="btn_submit_code"):
                if not auth_code:
                    st.warning("⚠️ Por favor ingresa el código primero")
                else:
                    try:
                        with st.spinner("Conectando con Google Drive..."):
                            flow = st.session_state.oauth_flow
                            
                            # Obtener token con el código
                            flow.fetch_token(code=auth_code.strip())
                            
                            self.creds = flow.credentials
                            st.session_state.google_drive_creds = self.creds
                            self.service = build('drive', 'v3', credentials=self.creds)
                            
                            # Limpiar flow
                            if 'oauth_flow' in st.session_state:
                                del st.session_state.oauth_flow
                            
                            st.success("✅ ¡Conectado exitosamente a Google Drive!")
                            st.balloons()
                            
                            # Pequeño delay para que se vea el mensaje
                            time.sleep(1)
                            
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error al autorizar: {str(e)}")
                        
                        error_msg = str(e).lower()
                        
                        if "invalid_grant" in error_msg or "code" in error_msg:
                            st.warning("💡 El código puede haber expirado o ser inválido. Genera uno nuevo.")
                            if st.button("🔄 Generar nuevo código", key="btn_retry"):
                                if 'oauth_flow' in st.session_state:
                                    del st.session_state.oauth_flow
                                st.rerun()
                        else:
                            st.info("Verifica que:")
                            st.markdown("- El código esté completo (sin espacios extra)")
                            st.markdown("- No haya pasado más de 10 minutos desde que lo generaste")
                            st.markdown("- Hayas usado la cuenta **maleja8005@gmail.com** para autorizar")
        
        return False
    
    def is_authenticated(self) -> bool:
        """Verifica si hay una conexión activa"""
        try:
            return self.service is not None
        except:
            return False
    
    def search_invoices_by_numbers(self, invoice_numbers: List[str]) -> List[Dict]:
        """Busca facturas específicas por sus números"""
        if not self.is_authenticated():
            return []
        
        try:
            invoices_found = []
            
            for invoice_num in invoice_numbers:
                query_parts = [
                    f"name contains '{invoice_num}'",
                    "trashed=false"
                ]
                
                if self.folder_id:
                    query_parts.append(f"'{self.folder_id}' in parents")
                
                query = " and ".join(query_parts)
                
                results = self.service.files().list(
                    q=query,
                    pageSize=5,
                    fields="files(id, name, createdTime, size, webViewLink, mimeType)",
                    orderBy="createdTime desc"
                ).execute()
                
                files = results.get('files', [])
                
                for file in files:
                    invoices_found.append({
                        'numero_factura': invoice_num,
                        'id': file['id'],
                        'nombre': file['name'],
                        'fecha_creacion': file.get('createdTime', ''),
                        'tamano': self._format_size(file.get('size', 0)),
                        'link_ver': file.get('webViewLink', ''),
                        'tipo': file.get('mimeType', ''),
                        'encontrado': True
                    })
            
            # Marcar no encontradas
            found_numbers = [inv['numero_factura'] for inv in invoices_found]
            for invoice_num in invoice_numbers:
                if invoice_num not in found_numbers:
                    invoices_found.append({
                        'numero_factura': invoice_num,
                        'id': None,
                        'nombre': f"{invoice_num} - No encontrado",
                        'encontrado': False
                    })
            
            return invoices_found
            
        except Exception as e:
            st.error(f"Error al buscar facturas: {str(e)}")
            return []
    
    def search_invoices(
        self, 
        query: str = None,
        invoice_numbers: List[str] = None,
        date_from: str = None,
        date_to: str = None
    ) -> List[Dict]:
        """Búsqueda general de facturas"""
        
        if invoice_numbers:
            return self.search_invoices_by_numbers(invoice_numbers)
        
        if not self.is_authenticated():
            return []
        
        try:
            search_query = ["trashed=false"]
            
            if self.folder_id:
                search_query.append(f"'{self.folder_id}' in parents")
            
            if query:
                search_query.append(f"name contains '{query}'")
            
            if date_from:
                search_query.append(f"createdTime >= '{date_from}T00:00:00'")
            if date_to:
                search_query.append(f"createdTime <= '{date_to}T23:59:59'")
            
            final_query = " and ".join(search_query)
            
            results = self.service.files().list(
                q=final_query,
                pageSize=100,
                fields="files(id, name, createdTime, modifiedTime, size, webViewLink, webContentLink)",
                orderBy="name"
            ).execute()
            
            files = results.get('files', [])
            
            invoices = []
            for file in files:
                invoices.append({
                    'id': file['id'],
                    'nombre': file['name'],
                    'fecha_creacion': file.get('createdTime', ''),
                    'tamano': self._format_size(file.get('size', 0)),
                    'link_ver': file.get('webViewLink', ''),
                    'encontrado': True
                })
            
            return invoices
            
        except Exception as e:
            st.error(f"Error al buscar: {str(e)}")
            return []
    
    def download_file(self, file_id: str, file_name: str) -> Optional[bytes]:
        """Descarga un archivo individual"""
        if not self.is_authenticated() or not file_id:
            return None
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            return file_buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error al descargar {file_name}: {str(e)}")
            return None
    
    def download_multiple_files(self, invoices: List[Dict]) -> Optional[bytes]:
        """Descarga múltiples archivos en ZIP"""
        if not self.is_authenticated():
            return None
        
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for invoice in invoices:
                    if invoice.get('encontrado') and invoice.get('id'):
                        file_content = self.download_file(invoice['id'], invoice['nombre'])
                        if file_content:
                            zip_file.writestr(invoice['nombre'], file_content)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            st.error(f"Error al crear ZIP: {str(e)}")
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """Formatea tamaño de archivo"""
        try:
            size_bytes = int(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        except:
            return "N/A"


def get_invoice_numbers_from_dataframe(df, column_name: str = 'numero_factura') -> List[str]:
    """Extrae números de factura únicos de un DataFrame"""
    if df is None or df.empty:
        return []
    
    if column_name not in df.columns:
        alt_names = ['Número de Documento', 'Numero', 'numero_documento', '# Factura']
        for alt_name in alt_names:
            if alt_name in df.columns:
                column_name = alt_name
                break
        else:
            return []
    
    invoice_numbers = df[column_name].dropna().unique().tolist()
    invoice_numbers = [str(num).strip() for num in invoice_numbers if str(num).strip()]
    
    return invoice_numbers