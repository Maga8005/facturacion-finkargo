"""
Módulo de gestión de Google Drive
Maneja la búsqueda y descarga de archivos PDF desde Google Drive
"""

import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials
import io
import pandas as pd
from typing import List, Dict, Optional
import zipfile
from datetime import datetime
import time
import os
import json

class DriveManager:
    """Gestiona la búsqueda, descarga y subida de archivos en Google Drive"""

    # Permisos completos para leer facturas existentes y crear archivos maestros
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Nombres de carpetas y archivos
    FOLDER_REPORTES = "Reportes Facturación"
    FOLDER_FACTURACION = "Facturación"
    FOLDER_FACTURAS_PDF = "Facturas PDF"
    MASTER_FILE_NAME = "Archivo control facturacion mensual Finkargo Def"

    def __init__(self):
        """Inicializa la conexión con Google Drive"""
        self.service = None
        self.folder_id = st.secrets.get("drive_folder_id", "")
        self.creds = None
        self.token_file = 'token.json'  # Archivo para persistir credenciales

        # Intentar cargar credenciales desde archivo primero
        self._load_credentials_from_file()

        # Si no hay en archivo, intentar desde session_state
        if not self.creds and 'google_drive_creds' in st.session_state:
            try:
                self.creds = st.session_state.google_drive_creds
                self.service = build('drive', 'v3', credentials=self.creds)
                # Guardar en archivo para próximas sesiones
                self._save_credentials_to_file()
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

                            # Guardar credenciales en archivo para persistencia
                            self._save_credentials_to_file()

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

    def _save_credentials_to_file(self):
        """Guarda las credenciales en un archivo JSON para persistencia"""
        if not self.creds:
            return

        try:
            creds_data = {
                'token': self.creds.token,
                'refresh_token': self.creds.refresh_token,
                'token_uri': self.creds.token_uri,
                'client_id': self.creds.client_id,
                'client_secret': self.creds.client_secret,
                'scopes': self.creds.scopes
            }

            with open(self.token_file, 'w') as token:
                json.dump(creds_data, token)

            # Mensaje solo para debug
            # st.info(f"🔐 Credenciales guardadas en {self.token_file}")
        except Exception as e:
            # Solo log, no mostrar error al usuario
            pass

    def _load_credentials_from_file(self):
        """Carga las credenciales desde archivo JSON si existe"""
        if not os.path.exists(self.token_file):
            return

        try:
            with open(self.token_file, 'r') as token:
                creds_data = json.load(token)

            self.creds = Credentials(
                token=creds_data.get('token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri'),
                client_id=creds_data.get('client_id'),
                client_secret=creds_data.get('client_secret'),
                scopes=creds_data.get('scopes')
            )

            # Construir servicio
            self.service = build('drive', 'v3', credentials=self.creds)

            # Guardar en session_state también
            st.session_state.google_drive_creds = self.creds

        except Exception as e:
            # Si hay error al cargar, eliminar archivo corrupto
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
            self.creds = None
            self.service = None

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

    def create_folder_if_not_exists(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Crea una carpeta en Drive si no existe, o retorna el ID si ya existe"""
        if not self.is_authenticated():
            return None

        try:
            # Buscar si la carpeta ya existe
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()

            files = results.get('files', [])

            if files:
                # La carpeta ya existe
                return files[0]['id']

            # Crear nueva carpeta
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            return folder.get('id')

        except Exception as e:
            st.error(f"Error al crear carpeta: {str(e)}")
            return None

    def upload_file(self, file_content: bytes, file_name: str, folder_id: str = None) -> Optional[Dict]:
        """Sube un archivo a Google Drive"""
        if not self.is_authenticated():
            return None

        try:
            from googleapiclient.http import MediaIoBaseUpload

            file_metadata = {'name': file_name}

            if folder_id:
                file_metadata['parents'] = [folder_id]
            elif self.folder_id:
                file_metadata['parents'] = [self.folder_id]

            # Crear media desde bytes
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                resumable=True
            )

            # Subir archivo
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, createdTime, size'
            ).execute()

            return {
                'id': file.get('id'),
                'nombre': file.get('name'),
                'link': file.get('webViewLink'),
                'fecha_creacion': file.get('createdTime'),
                'tamano': self._format_size(file.get('size', 0))
            }

        except Exception as e:
            st.error(f"Error al subir archivo: {str(e)}")
            return None

    def get_master_file_metadata(self) -> Optional[Dict]:
        """Busca el archivo Master en la carpeta de Facturación y devuelve su metadata"""
        if not self.is_authenticated():
            return None

        try:
            # Buscar carpeta "Facturación"
            folder_query = f"name='{self.FOLDER_FACTURACION}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

            # Si hay un folder_id configurado, buscar dentro de él
            if self.folder_id:
                folder_query += f" and '{self.folder_id}' in parents"

            folder_results = self.service.files().list(
                q=folder_query,
                pageSize=1,
                fields="files(id, name)"
            ).execute()

            folders = folder_results.get('files', [])
            if not folders:
                st.warning(f"⚠️ No se encontró la carpeta '{self.FOLDER_FACTURACION}'")
                return None

            facturacion_folder_id = folders[0]['id']

            # Buscar el archivo Master dentro de la carpeta Facturación
            # Usar "contains" para ser más flexible con el nombre exacto y extensiones
            file_query = f"name contains '{self.MASTER_FILE_NAME}' and trashed=false and '{facturacion_folder_id}' in parents"

            file_results = self.service.files().list(
                q=file_query,
                pageSize=10,  # Traer hasta 10 resultados por si hay múltiples versiones
                fields="files(id, name, createdTime, modifiedTime, size, webViewLink)",
                orderBy="modifiedTime desc"  # Ordenar por fecha de modificación (más reciente primero)
            ).execute()

            files = file_results.get('files', [])
            if not files:
                # Si no se encuentra, intentar búsqueda más amplia
                st.info(f"🔍 Buscando variaciones del nombre del archivo...")

                # Listar todos los archivos Excel en la carpeta para debug
                all_files_query = f"(mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='application/vnd.ms-excel') and trashed=false and '{facturacion_folder_id}' in parents"

                all_files_results = self.service.files().list(
                    q=all_files_query,
                    pageSize=20,
                    fields="files(id, name)",
                    orderBy="modifiedTime desc"
                ).execute()

                all_files = all_files_results.get('files', [])

                if all_files:
                    st.warning("📋 Archivos Excel encontrados en la carpeta 'Facturación':")
                    for f in all_files[:10]:  # Mostrar hasta 10
                        st.caption(f"  • {f['name']}")
                    st.info("💡 Verifica el nombre exacto del archivo y actualiza la configuración si es necesario.")

                return None

            # Tomar el archivo más reciente
            file = files[0]

            # Si hay múltiples archivos, avisar
            if len(files) > 1:
                st.info(f"ℹ️ Se encontraron {len(files)} archivos que coinciden. Usando el más reciente: {file['name']}")

            return {
                'id': file['id'],
                'nombre': file['name'],
                'fecha_creacion': file.get('createdTime', ''),
                'ultima_modificacion': file.get('modifiedTime', ''),
                'tamano': self._format_size(file.get('size', 0)),
                'link': file.get('webViewLink', '')
            }

        except Exception as e:
            raise Exception(f"Error al buscar archivo Master: {str(e)}")

    def read_master_file(self) -> Optional[Dict[str, pd.DataFrame]]:
        """Lee el archivo Master de Google Drive y devuelve un diccionario con los DataFrames por hoja"""
        if not self.is_authenticated():
            return None

        try:
            # Obtener metadata del archivo
            master_metadata = self.get_master_file_metadata()
            if not master_metadata:
                return None

            # Descargar el archivo
            file_content = self.download_file(master_metadata['id'], master_metadata['nombre'])
            if not file_content:
                return None

            # Leer el Excel desde bytes
            excel_file = io.BytesIO(file_content)

            # SOLO leer las dos hojas específicas de facturas
            hojas_a_leer = [
                "Relacion facturas costos fijos",
                "Relacion facturas mandato"
            ]

            excel_data = pd.ExcelFile(excel_file)
            dataframes = {}

            # Leer solo las hojas específicas
            # IMPORTANTE: header=2 porque las columnas están en la fila 3 (pandas cuenta desde 0)
            for sheet_name in hojas_a_leer:
                if sheet_name in excel_data.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=2)
                    dataframes[sheet_name] = df
                    st.info(f"✅ Hoja '{sheet_name}' cargada: {len(df):,} registros")
                else:
                    st.warning(f"⚠️ Hoja '{sheet_name}' no encontrada en el archivo")

            if not dataframes:
                st.error("❌ No se encontraron las hojas esperadas en el archivo")
                st.info("📋 Hojas disponibles en el archivo:")
                for name in excel_data.sheet_names:
                    st.caption(f"  • {name}")
                return None

            return dataframes

        except Exception as e:
            st.error(f"Error al leer archivo Master: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return None

    def save_processed_data(self, consolidated_data: pd.DataFrame, datos_por_hoja: Dict,
                           stats: Dict, metadata: Dict, folder_id: str) -> Optional[str]:
        """Guarda un snapshot de los datos procesados como JSON en Drive"""
        if not self.is_authenticated():
            return None

        try:
            # Crear un diccionario con toda la información
            snapshot = {
                'metadata': metadata,
                'stats': stats,
                'datos_por_hoja_info': {
                    hoja: {
                        'registros': len(df),
                        'columnas': list(df.columns)
                    }
                    for hoja, df in datos_por_hoja.items()
                }
            }

            # Convertir a JSON
            json_content = json.dumps(snapshot, indent=2, default=str)
            json_bytes = json_content.encode('utf-8')

            # Nombre del archivo snapshot
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            snapshot_name = f"Snapshot_Data_{timestamp}.json"

            # Subir a Drive
            result = self.upload_file(json_bytes, snapshot_name, folder_id)

            if result:
                return result['id']
            return None

        except Exception as e:
            st.error(f"Error al guardar snapshot: {str(e)}")
            return None

    def search_pdfs_in_facturas_folder(self, invoice_numbers: List[str]) -> List[Dict]:
        """Busca PDFs específicamente en la carpeta 'Facturas PDF'"""
        if not self.is_authenticated():
            return []

        try:
            # Buscar carpeta "Facturas PDF"
            folder_query = f"name='{self.FOLDER_FACTURAS_PDF}' and mimeType='application/vnd.google-apps.folder' and trashed=false"

            # Si hay un folder_id configurado, buscar dentro de él
            if self.folder_id:
                folder_query += f" and '{self.folder_id}' in parents"

            folder_results = self.service.files().list(
                q=folder_query,
                pageSize=1,
                fields="files(id, name)"
            ).execute()

            folders = folder_results.get('files', [])
            if not folders:
                st.warning(f"⚠️ No se encontró la carpeta '{self.FOLDER_FACTURAS_PDF}'")
                return []

            facturas_folder_id = folders[0]['id']

            # Buscar PDFs dentro de la carpeta
            invoices_found = []

            for invoice_num in invoice_numbers:
                try:
                    # Buscar el PDF por nombre
                    query = f"name contains '{invoice_num}' and mimeType='application/pdf' and trashed=false and '{facturas_folder_id}' in parents"

                    results = self.service.files().list(
                        q=query,
                        pageSize=1,
                        fields="files(id, name, size, webViewLink)"
                    ).execute()

                    files = results.get('files', [])

                    if files:
                        file = files[0]
                        invoices_found.append({
                            'numero_factura': invoice_num,
                            'encontrado': True,
                            'id': file['id'],
                            'nombre': file['name'],
                            'tamano': self._format_size(file.get('size', 0)),
                            'link_ver': file.get('webViewLink', '')
                        })
                    else:
                        invoices_found.append({
                            'numero_factura': invoice_num,
                            'encontrado': False
                        })

                    # Pequeña pausa para no saturar la API
                    time.sleep(0.1)

                except Exception as e:
                    invoices_found.append({
                        'numero_factura': invoice_num,
                        'encontrado': False,
                        'error': str(e)
                    })

            return invoices_found

        except Exception as e:
            st.error(f"Error al buscar en carpeta Facturas PDF: {str(e)}")
            return []

    def list_master_files(self, folder_id: str = None, limit: int = 10) -> List[Dict]:
        """Lista archivos maestros generados (con timestamp en el nombre)"""
        if not self.is_authenticated():
            return []

        try:
            # Buscar archivos que contengan "Maestro" en el nombre
            query = "name contains 'Maestro' and trashed=false"

            if folder_id:
                query += f" and '{folder_id}' in parents"
            elif self.folder_id:
                query += f" and '{self.folder_id}' in parents"

            results = self.service.files().list(
                q=query,
                pageSize=limit,
                fields="files(id, name, createdTime, modifiedTime, size, webViewLink)",
                orderBy="createdTime desc"
            ).execute()

            files = results.get('files', [])

            archivos = []
            for file in files:
                archivos.append({
                    'id': file['id'],
                    'nombre': file['name'],
                    'fecha_creacion': file.get('createdTime', ''),
                    'fecha_modificacion': file.get('modifiedTime', ''),
                    'tamano': self._format_size(file.get('size', 0)),
                    'link': file.get('webViewLink', '')
                })

            return archivos

        except Exception as e:
            st.error(f"Error al listar archivos maestros: {str(e)}")
            return []


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